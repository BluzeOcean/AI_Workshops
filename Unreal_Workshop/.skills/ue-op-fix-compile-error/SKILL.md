---
name: ue-op-fix-compile-error
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and a blueprint will not compile — a node calls a function that no longer exists, a pin reference is stale, or the editor is wedged behind a "Blueprint Asset Compilation Error" modal. Skip if no UE MCP connection, or if the blueprint compiles but behaves wrongly at runtime.
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

# ue-op-fix-compile-error — unbreak a blueprint and unstick the editor

## Why this skill exists

A blueprint that fails to compile **blocks everything**: PIE refuses to start,
and the editor opens a **modal "Blueprint Asset Compilation Error" dialog that
blocks the game thread**. MCP calls then time out and the editor looks hung.

Recognise the symptom: the editor is unresponsive to MCP, and there is a
visible dialog.

---

## Procedure

### 1. Read the actual errors

```bash
grep -E "LogBlueprint: Error" "D:/UE/<project>/Saved/Logs/<Project>.log" | tail -20
```

Typical failures:

| Error | Meaning |
|---|---|
| `Could not find a function named "X" in 'BP'` | a node calls a function removed in a later engine version |
| `In use pin <Unnamed> no longer exists on node Y` | the node's function changed shape; a link references a removed pin |
| `Input Axis Event references unknown Axis 'X' for @@` | a *warning* — the axis is not bound (see `ue-op-setup-input`). The action variant is `InputAction Event references unknown Action 'X' for @@` — note no space in `InputAction` |

### 2. Find the offending node

```python
import json

def T(tool, **kw):
    """Call a toolset tool from inside execute_tool_script and unwrap its
    {'returnValue': ...} envelope.  Tool names are fully qualified, e.g.
    'editor_toolset.toolsets.asset.AssetTools.load_asset'."""
    r = execute_tool(tool, json.dumps(kw))
    if isinstance(r, dict) and "returnValue" in r:
        return r["returnValue"]
    return r

nodes = T("editor_toolset.toolsets.blueprint.BlueprintTools.find_nodes", graph=eg, title="")
infos = T("editor_toolset.toolsets.blueprint.BlueprintTools.get_node_infos", nodes=nodes)
# match on ni["type_id"] — the broken node shows up as "|MissingFunctionName"
```

### 3. Decide: repair or delete

**Can it be repaired?** Only if the function still exists somewhere reachable
or can be re-created with a matching signature.

`add_function_param` accepts only primitives (`bool`, `int`, `float`, `byte`,
`string`, `name`, `text`) and a few structs (`Vector`, `Rotator`, `Transform`,
`Vector2D`, `LinearColor`). **It cannot declare an enum or a custom struct
parameter.** If the missing function had one, you cannot re-stub it.

**Deleting the node is then the correct fix.** A node calling a function that
no longer exists is dead code; the blueprint cannot compile until it goes.

```python
T("editor_toolset.toolsets.blueprint.BlueprintTools.delete_node", node=broken_node)
T("editor_toolset.toolsets.blueprint.BlueprintTools.compile_blueprint", blueprint=bp)
```

### 4. Clear the orphaned links

Deleting a node removes its exec link; the upstream event may now be
dangling. Re-read the graph and check nothing points at a removed pin:

```python
out["event_graph"] = str(T("editor_toolset.toolsets.blueprint.BlueprintTools.read_graph_dsl", graph=eg))[:4000]
```

### 5. Save

```python
T("editor_toolset.toolsets.asset.AssetTools.save_assets", asset_paths=[bp])   # stop PIE first
```

---

## Unsticking a wedged editor

If the editor is already blocked behind the dialog, close it from outside:

```powershell
# 1. find the editor PID, then enumerate its top-level windows for the title
#    "Blueprint Asset Compilation Error"
# 2. PostMessage(hwnd, 0x0010, 0, 0)   # WM_CLOSE
```

Find the window with `EnumWindows` + `GetWindowText`, matching
`"Blueprint Asset Compilation Error"` and the editor's PID, then `WM_CLOSE`.

The same dialog appears for `Content Validation` failures — same title check.

**Prevention:** the dialog is a symptom, not the disease. Fix the compile error
first; otherwise the next compile re-opens it.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| MCP calls time out, editor unresponsive | modal compile-error dialog | close it externally, then fix the error |
| `Could not find a function named "ResetOrientationAndPosition"` | UE4 VRPawn function removed in UE5 | delete the node |
| Cannot re-stub a function with an enum param | `add_function_param` has no enum support | delete the node instead |
| The broken node reports type `\|MissingFunction` | the class prefix is empty for unresolved nodes | match on the trailing name |
| Errors reference the *parent* blueprint | a child's compile fails with the parent's errors | fix the parent |
| Deleting a node leaves a dangling event | the upstream event is now unconnected | re-read the DSL and tidy |
| Compile warnings about unknown Axis/Action | bindings, not errors | `ue-op-setup-input` |

**Pre-existing errors are common in imported/sample assets.** The FabAssets
Paragon character shipped with a broken UE4-VR call and had to be repaired
before PIE would run at all. When a project "suddenly" cannot start PIE, read
the log before suspecting your own changes.

**A blueprint that will not compile also blocks its children.** A child of a
broken parent cannot compile either, so fix the parent first.

## Output contract

- `compile_blueprint` returns without raising
- no `LogBlueprint: Error` lines for that asset in the log
- the asset is saved

## Related

- `ue-op-wire-graph` — build the replacement logic
- `ue-op-test-pie` — confirm PIE starts afterwards
