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

```powershell
Select-String -Path 'D:\UE\EpicJam2026\Saved\Logs\EpicJam2026.log' -Pattern 'LogBlueprint: Error' |
  Select-Object -Last 20
# (no output = no compile errors in that session; EpicJam2026.log currently has none)
```

Typical failures:

| Error | Meaning |
|---|---|
| `Could not find a function named "X" in 'BP'` | a node calls a function removed in a later engine version |
| `In use pin <Unnamed> no longer exists on node Y` | the node's function changed shape; a link references a removed pin |
| `Input Axis Event references unknown Axis 'X' for @@` | a *warning* — the axis is not bound (see `ue-op-setup-input`). The action variant is `InputAction Event references unknown Action 'X' for @@` — note no space in `InputAction` |

### 2. Find the offending node

```powershell
# every node in the graph ("title": "" matches all titles)
python ...\mcp_call.py call BlueprintToolsets.BlueprintToolset FindNodes '{"graph":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph","title":""}'
# {"returnValue":[{"refPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph.K2Node_Event_0"}, ...]}

# then the details for the nodes you care about: typeId, pins, position
python ...\mcp_call.py call BlueprintToolsets.BlueprintToolset GetNodeInfos '{"nodes":["/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph.K2Node_Event_0"]}'
# {"returnValue":[{"typeId":"AddEvent|EventBeginPlay","node":{...},"position":{"x":0,"y":0},
#                  "inputPins":[],"outputPins":[{"name":"then","pinId":{...},...}]}]}
```

The field is **`typeId`** (`Category|Title`), not `type_id`. An unresolved
function node has an empty category, so its `typeId` reads `|MissingFunctionName`
— match on the half after the `|`.

### 3. Decide: repair or delete

**Can it be repaired?** Only if the function still exists somewhere reachable
or can be re-created with a matching signature.

`AddFunctionParam(graph, paramName, paramType, bInputParam)` takes `paramType`
as a **string**: the primitives (`bool`, `int`, `float`, `byte`, `string`,
`name`, `text`), a few structs (`Vector`, `Rotator`, `Transform`, `Vector2D`,
`LinearColor`) — **or the bare name / object path of any `UEnum` or
`UScriptStruct`**. For anything else there are two dedicated tools:
`AddStructFunctionParam(graph, paramName, structType, bInputParam)`
(`HitResult`, `GameplayTag`, custom structs) and
`AddObjectFunctionParam(graph, paramName, objectClass, bInputParam)`.
So an enum or struct parameter is no longer a reason you cannot re-stub a
missing function.

**Deleting the node is then the correct fix.** A node calling a function that
no longer exists is dead code; the blueprint cannot compile until it goes.

```powershell
# (write step — signature-verified, not executed)
python ...\mcp_call.py call BlueprintToolsets.BlueprintToolset DeleteNode `
  '{"node":"<refPath of the node from FindNodes>"}'
python ...\mcp_call.py call BlueprintToolsets.BlueprintToolset CompileBlueprint `
  '{"blueprint":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn","bWarningsAsErrors":false}'
```

**`CompileBlueprint` declares no return value, and a clean compile returns
`null`.** Do not test its result to decide whether the compile worked — a
successful compile of `/Game/Jam/Core/BP_MechPawn` came back as `null`. Read
the outcome from the log (step 1) or from the node types instead.

### 4. Clear the orphaned links

Deleting a node removes its exec link; the upstream event may now be
dangling. Re-read the graph and check nothing points at a removed pin:

```powershell
# the graph as canonical DSL (read); returns {"dsl": ..., "revision": ...}
python ...\mcp_call.py call BlueprintToolsets.BlueprintDslToolset Read '{"assetPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn","scope":"EventGraph"}'
# {"returnValue":{"dsl":"(event `self.ReceiveBeginPlay`)\n\n(event `self.ReceiveActorBeginOverlap` … )\n\n(event `self.ReceiveTick`\n
#   (params (DeltaSeconds :type \"Float (single-precision)\")))\n","revision":"75dfc6c263"}}
```

`Read` takes the **asset path plus a scope** (empty for the whole asset, a graph
name, or `Graph/Entry`), not a graph handle — and it returns a struct, not a
string. The DSL is not the old s-expression grammar: read
`BlueprintDslToolset.Docs()` before writing any.

### 5. Save

```powershell
# (write step — signature-verified, not executed)
python ...\mcp_call.py call EditorToolset.AssetToolset SaveAsset '{"assetPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn"}'
```

One path per call — there is no `save_assets(list)` in this build. Check
`EditorToolset.EditorAppToolset.IsPIERunning` first and stop PIE before saving.

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
| Cannot re-stub a function with a struct param | `AddFunctionParam` only lists five structs | `AddStructFunctionParam` (any `UScriptStruct`) or `AddObjectFunctionParam` (any class); an **enum** goes through `AddFunctionParam` by name |
| `CompileBlueprint` returns `null` after a clean compile | it declares no return value | read the log / node types, do not assert on the return |
| `read_graph_dsl` / `save_assets` → "Unknown tool" | those tools are not in this build | `BlueprintDslToolset.Read`, `AssetToolset.SaveAsset` (one path) |
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

- `CompileBlueprint` returns `null` (it declares no return value) — do not read
  success from the return
- no `LogBlueprint: Error` lines for that asset in the log
- the asset is saved

## Related

- `ue-op-wire-graph` — build the replacement logic
- `ue-op-test-pie` — confirm PIE starts afterwards
