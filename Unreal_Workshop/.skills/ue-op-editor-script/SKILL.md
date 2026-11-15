---
name: ue-op-editor-script
description: Use when the task is to make the live Unreal editor do something its toolsets cannot express — run a Python script inside the editor, read a scene as data, batch-edit assets, or capture a render. Skip for plain Blueprint graph authoring (use ue-op-wire-graph) or when no editor is running.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# ue-op-editor-script — drive the live editor with Python

The toolset registry covers most editor work: `BlueprintToolsets.BlueprintToolset`
(graphs, nodes, pins, variables), `BlueprintToolsets.BlueprintDslToolset` (graph DSL),
`EditorToolset.{Asset,Actor,Object,Level}Toolset`. **Use those first** — a tool call is
cheaper and more predictable than a script.

This skill is for the rest: work no tool expresses, a batch over hundreds of assets,
a computation you want returned as data, or an `unreal.*` API the toolsets do not wrap.
Two routes run your Python — pick by size:

| Route | Use when |
|---|---|
| `PythonScriptingTools.execute_python` | a short script, result wanted inline (it returns the last expression). No file juggling |
| `RunConsoleCommand` with `py <file>` | a long script, or one you want to keep and re-run from `<project>\Saved\` |

---

## When to apply

- no toolset tool expresses the operation you need
- the task is a batch operation over many assets/actors
- you need the result of a computation (bounds, counts, transforms) as data
- a skill you would otherwise use needs a fallback

## When NOT to apply

- Blueprint graph authoring → `ue-op-wire-graph` (`BlueprintToolsets.BlueprintToolset`)
- the editor is not running → start it first, and never during the user's
  working hours if it would steal focus

---

## Procedure

### 1. Check the editor and the MCP port

```powershell
Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" | Select-Object ProcessId, CommandLine
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

The port must be owned by an editor that has **this** project open — another
project's editor answers on 8000 and looks healthy while pointing at the wrong
content. Check the `CommandLine` for the `.uproject` path.

### 2. Write the script to a file

Put it under `<project>/Saved\` (never in `Content\`), and have it **write its
result to a JSON file** instead of relying on console output:

```python
import unreal, json
res = {"items": []}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    res["items"].append(a.get_actor_label())
with open(r"D:\UE\EpicJam2026\Saved\result.json", "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, default=str)
unreal.log("DONE %d" % len(res["items"]))
```

Console output is truncated and interleaved with engine logs; a file is
reliable.

### 3. Run it in the editor through the MCP bridge

```powershell
python V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py meta RunConsoleCommand `
  '{"command":"py D:/UE/EpicJam2026/Saved/my_script.py"}'
```

- `meta` calls a **top-level** tool (`RunConsoleCommand`, `TriggerMRGRender`,
  `GetViewportCamera`); `call` only reaches **toolset** tools.
- The command string is `py <path>` — UE's Python commandlet-style invocation.
- The reply is `{command, handled, output}`. `handled: false` means the console command
  was not recognised — that is how you test whether a console command exists at all
  (compare against a deliberately bogus command as a control). Short `print`/`unreal.log`
  output **does** come back in `output`; it is capped, so a long result still goes to a file.

### 4. Read the result file

```powershell
Get-Content D:\UE\EpicJam2026\Saved\result.json -Raw | ConvertFrom-Json
```

### 5. Save what changed, and confirm it landed

```python
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.EditorAssetLibrary.save_asset("/Game/Path/Asset", only_if_is_dirty=False)
```

Saving pops a **"Unable to Check Out From Revision Control"** dialog when the
map is not checked out. It is dismissed automatically and **the save still
completes** — verify by timestamp rather than by the absence of a dialog:

```powershell
Get-Item 'D:\UE\EpicJam2026\Content\Map\MeshTerrain.umap' | Select-Object LastWriteTime,Length
```

### 6. Capture a render (only useful for content, not for terrain)

```powershell
python V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py meta TriggerMRGRender '{}'
# -> D:\UE\EpicJam2026\Saved\UnrealCanvasBridgeRender\beauty.png
```

The viewport camera can be read with `meta GetViewportCamera '{}'` and restored
afterwards if you moved it.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `Toolset 'editor_toolset.toolsets.blueprint.BlueprintTools' is not registered` | the pre-5.9 toolset name | the live name is `BlueprintToolsets.BlueprintToolset` — see `ue-op-mcp-connect/references/calling-tools-in-this-build.md` |
| console output truncated or missing | the reply's `output` field is capped | write JSON to `<project>\Saved\` and read the file |
| `mcp_call.py call …` fails for a top-level tool | `call` only reaches toolset tools | use `meta <tool_name>` |
| script ran but produced no output | it only wrote to the console | write a JSON file and read it back |
| `handled: false` for a console command | the command name does not exist | test it against a bogus command as a control |
| the editor froze during the script | a modal dialog is up | close it from outside (EnumWindows → `WM_CLOSE`) |
| a save dialog complains about source control | the asset is not checked out | ignore it; verify the file timestamp |
| `unreal.Rotator(…)` produced a wrong rotation | it is **(roll, pitch, yaw)** | keep that order |
| iterating a `Vector`/`Rotator` raised | they are not iterable | use `.x/.y/.z` |
| `unreal.Component` does not exist | it does not | use `unreal.ActorComponent` |
| `GeometryScript*List` would not iterate | it is a wrapper | call `convert_<x>_to_array()` |
| `MeshNaniteSettings` field not found | UE python drops the `b` prefix | the field is `enabled` |
| `spawn_actor_from_class` ignored the location | the passed location is not honoured | call `set_actor_location` afterwards |
| `rename_asset` → "An asset already exists at this location" | the destination is taken | `EditorAssetLibrary.delete_asset()` first |
| `AssetImportTask` created an unexpected asset name | the asset is named after the **file** | rename deliberately afterwards |
| `save_assets` failed while PIE was running | PIE still active | stop PIE first (`ue-op-test-pie`) |

---

## Output contract

- the editor-side change is applied **and saved to disk** (timestamp confirmed)
- the computation's result is available as JSON on disk
- no modal dialog left blocking the editor

## Related

- `ue-op-test-pie` — run the result and verify it behaves
- `ue-op-capture-editor` — screenshot the editor/viewport
- `ue-op-mcp-connect` — the bridge itself
