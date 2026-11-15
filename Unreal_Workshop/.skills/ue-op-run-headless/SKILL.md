---
name: ue-op-run-headless
description: Use when the job needs Unreal with no GUI on screen - resaving or cooking packages, filling the DDC, dumping the asset registry, running an automation test, or executing a Python script inside the engine - especially when no editor is running or the user's editor is busy. Skip for driving a live editor (use ue-op-editor-script) or for reaching an editor over MCP (use ue-op-mcp-diagnose).
---

# ue-op-run-headless — drive Unreal with no GUI on screen

`UnrealEditor-Cmd.exe` is the escape hatch that always works: no editor running, no
desktop, no MCP. It is slower to start than the GUI, but it never touches the user's
open session.

---

## When to apply

- no editor is running, and the task does not need one
- the user's editor holds work you must not disturb — a cook or a resave must not race it
- a long operation (cook, DDC fill, bulk resave) where a visible window would just be in the way
- running an automation test
- running a Python script that only needs `unreal`, not a GUI

## When NOT to apply

- the editor is running and the task is a live-editor action → `ue-op-editor-script`
- you need to reach an editor over MCP → `ue-op-mcp-diagnose`
- you need to *author* a Blueprint graph → `ue-op-wire-graph` (needs `editor_toolset`)

---

## Step 1 — resolve the engine, do not assume it

```powershell
Get-ChildItem "C:\Program Files\Epic Games\UE_*\Engine\Build\Build.version" |
  ForEach-Object {
    $v = Get-Content $_.FullName -Raw | ConvertFrom-Json
    [pscustomobject]@{ Engine = $_.Directory.Parent.Parent.FullName
                       Version = [version]"$($v.MajorVersion).$($v.MinorVersion).$($v.PatchVersion)"
                       CL = $v.Changelist }
  } | Sort-Object Version -Descending | Select-Object -First 1
```

Take the first row. **Never read the launcher registry** — it does not list UE 5.9.

## Step 2 — the invocation

```powershell
& "<engine>\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "D:\UE\<Project>\<Project>.uproject" -run=<Commandlet> -unattended -nosplash
```

| Flag | Effect |
|---|---|
| `-run=<Commandlet>` | run a commandlet (below) |
| `-unattended` | no prompts, no dialogs — a prompt in unattended mode is a hang |
| `-nosplash` | skip the splash |
| `-NullRHI` | no rendering at all — for tests and headless analysis |
| `-ExecutePythonScript="<abs path>"` | run a Python file inside the engine |
| `-ExecCmds="<cmd>;Quit"` | run console commands, then quit |

**MCP auto-start is skipped in commandlets.** A cook or a build racing the editor for
port 8000 is the usual symptom. Pass `-ModelContextProtocolStartServer` to force it on,
or run with the editor closed.

## Step 3 — commandlets verified in 5.9

From `Engine/Source/Editor/UnrealEd/Classes/Commandlets/`:

| Commandlet | What it does |
|---|---|
| `-run=ResavePackages` | resave assets; narrow with `-PackageFilter=` |
| `-run=Cook` | cook content for a target platform |
| `-run=DerivedDataCache -fill` | pre-fill the DDC |
| `-run=DumpAssetRegistry` | dump the asset registry |

## Step 4 — automation tests are NOT a commandlet

There is **no `AutomationCommandlet`** in 5.9 and no `RunUreal` AutomationTool script.
Run them from the editor console:

```
Automation RunTests <TestName>
```

or headless:

```powershell
UnrealEditor-Cmd.exe "D:\UE\<Project>\<Project>.uproject" `
  -ExecCmds="Automation RunTests <TestName>;Quit" -unattended -nosplash -NullRHI
```

## Step 5 — Python inside the engine

Needs the `PythonScriptPlugin` (present in 5.8 and newer):

```powershell
UnrealEditor-Cmd.exe "D:\UE\<Project>\<Project>.uproject" `
  -ExecutePythonScript="D:\UE\<Project>\Saved\script.py" -unattended
```

- Unreal's Python is **3.11.8**, at
  `<engine>\Engine\Binaries\ThirdParty\Python3\Win64\python.exe`. `import unreal` works
  **only** inside the editor or a commandlet — a bare system Python cannot import it.
- **The script's working directory is the launch directory, not the script's folder.**
  Use absolute paths inside scripts.
- **Nothing persists between runs except what you save.**
- Write the result to a JSON file under the project's `Saved/` folder rather than relying
  on console output — it is truncated and interleaved with engine logs.

---

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| the command hangs with no output | a modal prompt in unattended mode | add `-unattended`; a commandlet that wants a prompt needs different flags |
| `ImportError: No module named 'unreal'` | ran the script with system Python | use `UnrealEditor-Cmd.exe -ExecutePythonScript=`, or the engine's own python.exe |
| the script cannot find its input file | cwd is the launch directory, not the script folder | use absolute paths |
| the cook fails on port 8000 | the commandlet's MCP auto-start raced the editor | close the editor, or pass `-ModelContextProtocolStartServer` |
| `Automation RunTests` reports "unknown command" | there is no `AutomationCommandlet` | use `-ExecCmds="Automation RunTests <Name>;Quit"` |
| the command reports success but nothing changed | nothing was saved | save explicitly and verify the file timestamp |

---

## Related

- `ue-op-editor-script` — drive the **live** editor over the MCP bridge
- `ue-op-mcp-diagnose` — which editor and which MCP server answered
- `.vault/model-notes/2026-11-15-ue-installs-and-mcp-capability.md` — the capability
  matrix and the verified commandlet list
