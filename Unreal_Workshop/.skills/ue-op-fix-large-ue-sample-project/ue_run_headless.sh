#!/bin/bash
# ue_run_headless.sh - run a Python script inside the Unreal editor without a
# visible window, so it never takes over the user's screen.
#
#   ./ue_run_headless.sh <project.uproject> <script.py>
#
# Environment:
#   UE_EDITOR     path to UnrealEditor.exe. If unset, the script picks the
#                  engine that matches the PROJECT's EngineAssociation, then
#                  the newest installed version.
#   UE_MAP        map to operate on (read by the bundled scripts)
#   UE_OUT        where to write reports
#   UE_LOG        where to write the editor log
#   UE_TIMEOUT    watchdog seconds before the editor is force-quit (default 1800)
#   UE_EXTRA_ARGS extra command line arguments for the editor
#   Any other UE_* variables are passed through to the editor script and
#   are visible there as os.environ.
#
# Examples:
#   UE_MAP=/Game/Maps/MyMap ./ue_run_headless.sh /d/proj/My.uproject ue_map_inventory.py
#
# NOTE 1: the script uses -ExecCmds, NOT -ExecutePythonScript. With
# -ExecutePythonScript the editor quits the moment the script returns, which
# silently truncates any work the script started on a tick callback.
#
# NOTE 2: the script path is resolved to an ABSOLUTE path before it is handed
# to the editor. The editor's working directory is the project folder, not
# where you launched from, so a relative path fails with FileNotFoundError.
#
# NOTE 3: a tiny launcher registers a tick watchdog before running the target
# script. Without it, a script that raises leaves an idle editor running
# forever, holding the map file open.

set -u

PROJ="${1:?usage: ue_run_headless.sh <project.uproject> <script.py>}"
SCRIPT="${2:?usage: ue_run_headless.sh <project.uproject> <script.py>}"
shift 2

WANT=""
if [ -f "$PROJ" ]; then
  WANT=$(grep -o '"EngineAssociation"[[:space:]]*:[[:space:]]*"[^"]*"' "$PROJ" \
         | head -1 | sed 's/.*"\([^"]*\)"$/\1/')
fi

# ---- find the editor -----------------------------------------------------
if [ -n "${UE_EDITOR:-}" ]; then
  EXE="$UE_EDITOR"
else
  EXE=""
  # a) the version the project asks for
  if [ -n "$WANT" ]; then
    for d in "C:/Program Files/Epic Games/UE_$WANT/Engine/Binaries/Win64/UnrealEditor.exe" \
             "C:/Program Files/Epic Games/UE_$WANT/Engine/Binaries/Linux/UnrealEditor" \
             "$HOME/UnrealEngine/UE_$WANT/Engine/Binaries/Linux/UnrealEditor"; do
      [ -f "$d" ] && EXE="$d" && break
    done
    # the launcher registry, matched by version
    if [ -z "$EXE" ] && command -v powershell >/dev/null 2>&1; then
      EXE=$(powershell -NoProfile -Command "
        \$k='HKCU:\SOFTWARE\Epic Games\Unreal Engine\Builds';
        if (Test-Path \$k) {
          (Get-ItemProperty \$k).PSObject.Properties |
            Where-Object { \$_.Value -and (Test-Path (Join-Path \$_.Value 'Engine/Binaries/Win64/UnrealEditor.exe')) } |
            ForEach-Object { \$p = Join-Path \$_.Value 'Engine/Binaries/Win64/UnrealEditor.exe';
                            if (\$_.Name -eq '$WANT') { \$p } else { '' } } |
            Where-Object { \$_ -ne '' } | Select-Object -First 1
        }" 2>/dev/null | tr -d '\r')
    fi
  fi
  # b) otherwise the newest version installed
  if [ -z "$EXE" ]; then
    NEWEST=$(ls -d "C:/Program Files/Epic Games"/UE_*/Engine/Binaries/Win64/UnrealEditor.exe 2>/dev/null \
             | sed 's#.*/UE_\([0-9.]*\)/.*#\1#' | sort -V | tail -1)
    if [ -n "$NEWEST" ]; then
      EXE="C:/Program Files/Epic Games/UE_$NEWEST/Engine/Binaries/Win64/UnrealEditor.exe"
    fi
  fi
  if [ -z "$EXE" ] && command -v powershell >/dev/null 2>&1; then
    EXE=$(powershell -NoProfile -Command "
      \$k='HKCU:\SOFTWARE\Epic Games\Unreal Engine\Builds';
      if (Test-Path \$k) {
        (Get-ItemProperty \$k).PSObject.Properties |
          Where-Object { \$_.Value -and (Test-Path (Join-Path \$_.Value 'Engine/Binaries/Win64/UnrealEditor.exe')) } |
          ForEach-Object { Join-Path \$_.Value 'Engine/Binaries/Win64/UnrealEditor.exe' } |
          Select-Object -First 1
      }" 2>/dev/null | tr -d '\r')
  fi
  if [ -z "$EXE" ]; then
    echo "ue_run_headless: no UnrealEditor found. Set UE_EDITOR=/path/to/UnrealEditor" >&2
    exit 2
  fi
fi

# ---- resolve paths --------------------------------------------------------
# The editor is a Windows process: it needs a Windows path, and an absolute
# one, because its working directory is the project folder.
if [ ! -f "$SCRIPT" ]; then
  echo "ue_run_headless: script not found: $SCRIPT" >&2
  exit 2
fi
SCRIPT_ABS="$(cd "$(dirname "$SCRIPT")" && pwd)/$(basename "$SCRIPT")"
SCRIPT_WIN="$(cygpath -w "$SCRIPT_ABS" 2>/dev/null || echo "$SCRIPT_ABS")"

PROJ_DIR="$(dirname "$PROJ")"
LOG="${UE_LOG:-$PROJ_DIR/Saved/ue_op_logs/$(basename "${SCRIPT%.py}").log}"
mkdir -p "$(dirname "$LOG")"

# ---- launcher with a watchdog --------------------------------------------
LAUNCHER="$(cd "$(dirname "$LOG")" && pwd)/_ue_op_launcher.py"
LAUNCHER_WIN="$(cygpath -w "$LAUNCHER" 2>/dev/null || echo "$LAUNCHER")"

cat > "$LAUNCHER" <<PYEOF
import time
import traceback

import unreal

_T0 = time.time()
_LIMIT = ${UE_TIMEOUT:-1800}


def _watchdog(delta):
    if time.time() - _T0 > _LIMIT:
        unreal.log_warning("[ue-op] watchdog: {}s elapsed, quitting".format(_LIMIT))
        try:
            unreal.SystemLibrary.quit_editor()
        except Exception:
            pass


unreal.register_slate_post_tick_callback(_watchdog)

try:
    exec(open(r'$SCRIPT_WIN').read())
except SystemExit:
    # the script bailed out early; it never reached its own quit, so do it here
    try:
        unreal.SystemLibrary.quit_editor()
    except Exception:
        pass
except Exception:
    unreal.log_error("[ue-op] the script raised:")
    unreal.log_error(traceback.format_exc())
    try:
        unreal.SystemLibrary.quit_editor()
    except Exception:
        pass
PYEOF

# MSYS_NO_PATHCONV stops Git Bash rewriting the -ExecCmds path into
# "C:/Program Files/Git/..." - it must be set for the whole command line.
echo "ue_run_headless: project=$PROJ  wants engine '${WANT:-?}'"
echo "ue_run_headless: editor=$EXE"
echo "ue_run_headless: script=$SCRIPT_WIN"
echo "ue_run_headless: log=$LOG"

MSYS_NO_PATHCONV=1 "$EXE" "$PROJ" \
  -ExecCmds="py exec(open(r'$LAUNCHER_WIN').read())" \
  -RenderOffscreen -unattended -nosplash -NoSound -stdout -FullStdOutLogOutput \
  ${UE_EXTRA_ARGS:-} \
  > "$LOG" 2>&1

STATUS=$?
echo "ue_run_headless: exit=$STATUS  (full log: $LOG)"
exit $STATUS
