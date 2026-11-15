---
name: ue-op-test-pie
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to run and verify gameplay in Play-In-Editor — start or stop PIE, survive the modal dialogs that block it, inject synthetic keyboard/mouse input, and read back runtime state. Skip if no UE MCP connection, or if the task is only to author content.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - mcp__unreal-mcp__call_tool
---

# ue-op-test-pie — run PIE and verify it actually works

## Procedure

### 1. Start PIE

```powershell
# (write step — signature-verified, not executed; starting PIE would take over the editor)
python ...\mcp_call.py call EditorToolset.EditorAppToolset IsPIERunning   # must be false before StartPIE

python ...\mcp_call.py call EditorToolset.EditorAppToolset StartPIE `
  '{"options":{"bSimulate":false,"warmupSeconds":4}}'
```

The arguments go **nested under `options`** — `options` is one
`PIESessionOptions` parameter, not the call's parameter list. It is optional
(`= null`): unset, you get PIE in the viewport with 2 seconds of warmup. Its
fields are `bSimulate`, `playMode`, `startTransform` (`{translation, rotation,
scale3D}`) and `warmupSeconds`.

`StartPIE` raises if a session is already active or queued, and the whole
request has a **30-second** timeout.

`bSimulate: true` runs the world without a player pawn — useful for checking
initialisation, useless for testing input.

### 2. Survive the modal dialogs

PIE can wedge the editor. The tell: **MCP calls time out** and a visible
dialog sits on screen.

| Dialog | Cause | Action |
|---|---|---|
| "Blueprint Asset Compilation Error" | a blueprint does not compile | `ue-op-fix-compile-error`, then close the dialog externally |
| "Message" (Slate) | transient PIE popup | close with `WM_CLOSE` |

Close it from outside the editor:

```powershell
# EnumWindows for the editor PID -> GetWindowText matches the title
# PostMessage(hwnd, 0x0010, 0, 0)   # WM_CLOSE
```

### 3. Verify the spawn

```powershell
Select-String -Path 'D:\UE\EpicJam2026\Saved\Logs\EpicJam2026.log' -Pattern 'Game class is|Bringing World|LogSpawn' |
  Select-Object -Last 8 | ForEach-Object { "$($_.LineNumber): " + $_.Line.Trim() }
# 3063: [2026.11.15-12.42.18:122][ 40]LogLoad: Game class is 'BP_MechGameMode_C'
# 3064: ... LogWorld: Bringing World /Game/Map/UEDPIE_0_Mission1.Mission1 up for play (max tick rate 0) ...
```

- `Game class is 'BP_MechGameMode_C'` — the intended game mode is in play
- `LogSpawn: Warning: Login failed: PlayerState is null` — the game mode is
  wrong or half-configured
- The pawn itself lives in the **PIE world**, not in the level editor's scene —
  read it with step 5, not with `LevelToolset.FindActors`

### 4. Inject input

The editor may be **minimised** — synthetic input goes nowhere until it is
restored.

```python
import ctypes, ctypes.wintypes as wt, time
u = ctypes.windll.user32
u.SetProcessDPIAware()
hwnd = <editor hwnd>

u.ShowWindow(hwnd, 9)              # SW_RESTORE  (skip if already visible)
time.sleep(1.0)
u.SetForegroundWindow(hwnd)
time.sleep(0.5)

r = wt.RECT(); u.GetWindowRect(hwnd, ctypes.byref(r))
u.SetCursorPos(r.left + int((r.right-r.left)*0.52),
               r.top  + int((r.bottom-r.top)*0.45))
time.sleep(0.25)
u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(0.05)   # LEFTDOWN
u.mouse_event(0x0004, 0, 0, 0, 0); time.sleep(0.5)    # LEFTUP  -> viewport focus

u.keybd_event(0x57, 0, 0, 0); time.sleep(2.0)          # W down  (0x57)
u.keybd_event(0x57, 0, 0x0002, 0)                      # W up    (KEYEVENTF_KEYUP)
```

Order matters: **focus first, then move the cursor, then click**. A click
sent before `SetForegroundWindow` lands on whatever was under the cursor.

Virtual keys: `W` = 0x57, `A` = 0x41, `S` = 0x53, `D` = 0x44,
`SpaceBar` = 0x20, `LeftShift` = 0xA0.

### 5. Read the result back — and wait for the tick

An actor in the **editor** world is one hop — its `actorPath` from
`FindActors` is the argument:

```powershell
python ...\mcp_call.py call EditorToolset.ActorToolset GetActorTransform '{"actor":"/Game/Map/Mission1.Mission1:PersistentLevel.WorldSettings"}'
# {"returnValue":{"translation":{"x":0,"y":0,"z":0},"rotation":{"pitch":0,"yaw":0,"roll":-0},
#                  "scale3D":{"x":1,"y":1,"z":1}}}
```

The **PIE pawn** is different: it lives in a PIE world and has no content
`refPath`, so resolve it inside the editor. This is the batched case — one
Python step, two tool calls, the handle passed as a real object:

```python
import json

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()   # None outside PIE
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
t = await call_tool("EditorToolset.ActorToolset.GetActorTransform", actor=pawn)
json.dumps({"pawn": pawn.get_path_name(), "transform": t})
```

Send that source as the `script` CodeBlock — a bare string fails with
*"Unable to import JSON string into CodeBlock"*:

```powershell
python ...\mcp_call.py call editor_toolset.toolsets.python_scripting.PythonScriptingTools execute_python '{"script":{"content":"<python source above>","language":"Python"}}'
```

`unreal.get_editor_subsystem(...).get_game_world()` and
`unreal.GameplayStatics.get_player_pawn(world, index)` were both checked with
`get_symbol`; outside PIE the first returns `null` and `get_pie_worlds(False)`
returns `[]`, which is how you can prove the lookup wiring without a session.

**Read the transform only after the world has ticked.** This is the single most
common false negative in this whole workflow — a character that *did* move
reads as stationary.

Observed in the FabAssets session: input was injected, and the very next read
showed the pawn still at its spawn position; a later read showed it
displaced and rotated. The log for those PIE sessions recorded
`Bringing World ... up for play (max tick rate 3)` — later sessions recorded
`max tick rate 0`. The editor window had been **minimised** for part of that
testing, and a hidden editor does not tick normally.

So the rules are:

1. **Restore the editor window before injecting input** (step 4 does this).
   A minimised editor also receives no synthetic input at all.
2. **Wait, then read.** Give the world a moment to tick, then read; if the
   value is unchanged, read again before concluding anything.
3. Cross-check the tick rate in the log — `max tick rate 3` on a session you
   expected to be full-speed is the tell that the window was hidden.

| What changed | Proves |
|---|---|
| position | the axis mapping reached `AddMovementInput` |
| yaw / pitch | mouse look reached `AddControllerYawInput` / `AddControllerPitchInput` |
| `MaxWalkSpeed` on the movement component | a held action fired (sprint) |

### 6. Stop PIE and save

```powershell
# (write step — signature-verified, not executed)
python ...\mcp_call.py call EditorToolset.EditorAppToolset IsPIERunning   # StopPIE errors when nothing is running
python ...\mcp_call.py call EditorToolset.EditorAppToolset StopPIE
```

`StopPIE` stops PIE *or* simulation and waits for shutdown; it raises when no
session is active, so gate it on `IsPIERunning`.

**Save with PIE stopped, always** — a save does not go through while a session
is running.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `StartPIE` never returns past ~30 s | its own timeout, hit because a modal dialog is blocking the editor | close the dialog externally; fix the underlying error |
| `StartPIE` → "unrecognized parameter(s) [bSimulate, …]" | the fields were passed at the top level | wrap them: `{"options": {"bSimulate": …}}` |
| `StopPIE` errors instead of stopping | no session is active | gate it on `IsPIERunning` |
| Injecting keys does nothing | the editor is minimised | `ShowWindow(hwnd, 9)` first |
| Injecting keys does nothing | the click landed before focus | focus → move cursor → click → key |
| The pawn reads as unmoved after W | read before the world ticked | wait, then read again |
| `SaveAsset` → "Asset does not exist" | PIE still running | check `IsPIERunning`, stop PIE, then save |
| `Login failed: PlayerState is null` | wrong game mode | check `Game class is '...'` |
| the viewport capture shows no PIE actors | `SceneCaptureToolset.CaptureEditorViewport` renders the *editor* world | `SceneCaptureToolset.CaptureGameViewport(world, maxResolution)` captures the PIE viewport; or verify numerically (step 5) |
| `CaptureEditorViewport` → "… is in a background tab or a hidden or minimized window" | the level viewport is not the front tab | ask for it to be brought forward, or pass a `viewportId` from `SceneCaptureToolset.ListEditorViewports` whose `bIsVisible` is true |

**A restart of PIE is required after changing blueprints or the game mode** —
the running session keeps the old compiled state.

**Stop PIE before saving anything.** This one bites repeatedly.

## Output contract

- PIE starts and stops without wedging the editor
- the log shows the intended game mode and a spawn
- the runtime state read back matches the intended behaviour (position,
  rotation, speed)

## Related

- `ue-op-fix-compile-error` — when PIE will not start
- `ue-op-setup-game-mode` — what PIE is verifying
- `ue-op-setup-input` — the bindings being exercised
