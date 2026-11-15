---
name: ue-op-wire-graph
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to create, connect or delete nodes in a blueprint graph — wiring input events to function calls, adding a sprint toggle, patching an existing chain. Skip if no UE MCP connection, or if the task is only to read a graph.
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

# ue-op-wire-graph — create and connect blueprint nodes

Every call below is one hop: `python mcp_call.py call <Toolset> <Tool>
'<json arguments>'`. The parameters are UE camelCase, and the toolset is
`BlueprintToolsets.BlueprintToolset` — not the old
`editor_toolset.toolsets.blueprint.BlueprintTools`, which is not registered in
this build.

## The core mechanic

`PinID` identifies one pin on one node:

```json
{"node": "<node refPath>", "indexId": <int>, "direction": "EGPD_Input"}
```

- `indexId` is camelCase. The old `index_id` is rejected by the schema.
- `direction: "EGPD_Output"` + `indexId` → a source pin
- `direction: "EGPD_Input"` + `indexId` → a destination pin

Connect with `ConnectPins(outputPin=..., inputPin=...)`; set a default value
with `SetPinValue(pin=..., value="900.0")`.

**Pin indices are per-node**, so you do not guess them: you read them back from
`GetNodeInfos`, where the index lives at `pin["pinId"]["indexId"]` and the
direction at `pin["pinId"]["direction"]`.

---

## Procedure

Every block below assumes one shell variable for the client:

```powershell
$mcp = "V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py"
```

### 0. Resolve the graph you are editing

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset ListGraphs '{"blueprint":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn"}'
```

```json
{"returnValue":[{"refPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:UserConstructionScript"},
                {"refPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph"}]}
```

Every later step wants `eg`, the graph whose refPath ends in `:EventGraph`.
The graph is addressed by that refPath string, not by the blueprint.

`ListGraphs` returns the blueprint's **own** graphs only — a child's
EventGraph is its own graph, the parent's nodes are not in it, and the parent's
graph still runs. An `(event ...)` line with no body in the DSL means the
override exists but does nothing yet.

### 1. Find the node types you need

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset FindNodeTypes '{"graph":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph","typeIdFilter":"SetMaxWalkSpeed"}'
```

```json
{"returnValue":["Class|CharacterMovementComponent|SetMaxWalkSpeed",
                "Class|CharacterMovementComponent|SetMaxWalkSpeedCrouched"]}
```

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset FindNodeCategories '{"graph":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph","categoryFilter":"Development"}'
```

```json
{"returnValue":["Development","Development|Editor"]}
```

`contextPins` is **optional** (default null) — leave it out unless you are
filtering by compatible types. The catalogue is the editor's whole palette, not
the graph's contents: 2484 categories come back on an EventGraph that holds
three event nodes, and `Class|CharacterMovementComponent|SetMaxWalkSpeed` is
offered in a Pawn graph.

A trailing pipe lists a whole category — `"typeIdFilter":"Utilities|FlowControl|"`
→ 1421 ids.

### 2. Create the nodes

*(write step — signature-verified, not executed)*

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset CreateNode '{"graph":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph","typeId":"Development|PrintString","pos":{"x":-300,"y":300}}'
```

`pos` is an `IntPoint`: `{"x": -300, "y": 300}`. The call returns the new
node, and its `refPath` is what you feed to the next step and to `ConnectPins`
— it is resolved as a plain string, so nothing has to stay in memory between
calls. `CreateNode(graph, typeId, pos, declaringClass=null)`; set
`declaringClass` only to disambiguate a `typeId` two classes both offer.

### 3. Read their pins

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset GetNodeInfos '{"nodes":["/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph.K2Node_Event_0"]}'
```

```json
{"returnValue":[{"typeId":"AddEvent|EventBeginPlay",
  "node":{"refPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph.K2Node_Event_0"},
  "position":{"x":0,"y":0},
  "inputPins":[],
  "outputPins":[
    {"name":"OutputDelegate","typeId":"Delegate",
     "pinId":{"node":{"refPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph.K2Node_Event_0"},
              "indexId":0,"direction":"EGPD_Output"},
     "connectedPins":[],"value":""},
    {"name":"then","typeId":"Exec",
     "pinId":{"node":{"refPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph.K2Node_Event_0"},
              "indexId":1,"direction":"EGPD_Output"},
     "connectedPins":[],"value":""}]}]}
```

Read the pin list and match on `name` / `typeId` **before** using an index:
here index 0 is a `Delegate` and index 1 is the exec `then` pin. When you
write a PinID by hand you may pass the node as a plain refPath string; the
`{"refPath": …}` object that comes back reads the same way.

### 4. Wire

*(write step — signature-verified, not executed)*

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset ConnectPins '{"outputPin":{"node":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph.K2Node_Event_0","indexId":1,"direction":"EGPD_Output"},"inputPin":{"node":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph.K2Node_CallFunction_0","indexId":0,"direction":"EGPD_Input"}}'
```

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset SetPinValue '{"pin":{"node":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph.K2Node_CallFunction_0","indexId":1,"direction":"EGPD_Input"},"value":"900.0"}'
```

`value` is always a **string**, formatted for the pin's type (`"900.0"`,
`"true"`, `"Hello"`, `"/Game/Path/Asset.Asset"`). `SetPinValue` only works on
an input pin that supports default values.

### 5. Compile and save

*(write step — signature-verified, not executed)*

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset CompileBlueprint '{"blueprint":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn"}'
python $mcp call EditorToolset.AssetToolset SaveAsset '{"assetPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn"}'
```

`SaveAsset` takes **one** path. There is no `save_assets(list)` in this build —
`search_symbols` returns zero matches for that name — so a batch save is one
call per asset.

---

## Events with several exec outputs

The old recipe here wired a legacy `InputAction` node (`Pressed` = 0,
`Released` = 1, `Key` = 2) for a hold-to-sprint toggle. **That pin table does
not hold in this build.** `FindNodeTypes` with `typeIdFilter="ActionEvents"`
returns 15 ids and every one of them is `Input|EnhancedActionEvents|<IA_Name>`;
`typeIdFilter="AxisEvents"` returns nothing at all. No `Input|ActionEvents|…`
node exists in this project's palette because it registers Enhanced Input only,
so the legacy indices could not be re-verified and are not repeated.

What is verified is the shape you must handle either way — several output pins
on one node, only one of them exec. `AddEvent|EventBeginPlay` reports
`OutputDelegate` (Delegate, indexId 0) and `then` (Exec, indexId 1). The
method is the same for an Enhanced Input action event:
`GetNodeInfos` first, match the pin `name`, then wire its `indexId`. The
Enhanced Input action events the palette offers here are
`Input|EnhancedActionEvents|<IA_Name>` — 15 of them, `IA_Pan`, `IA_Select`,
`IA_Face`, `IA_ZoomIn`, `IA_Card1` and so on, one per input action asset.

## Node type id conventions (re-derived 2026-11-15)

| What | type_id |
|---|---|
| built-in event | `AddEvent\|EventBeginPlay`, `AddEvent\|EventTick` (27 `AddEvent\|*` ids) |
| custom event | `AddEvent\|Custom\|<Name>` (the palette lists the generic `AddEvent\|AddCustomEvent...`) |
| Enhanced Input action event | `Input\|EnhancedActionEvents\|<IA_Name>` |
| class function | `Class\|CharacterMovementComponent\|SetMaxWalkSpeed`, `Class\|Character\|GetCharacterMovement` |
| ordinary function | `Development\|PrintString`, `Utilities\|FlowControl\|<Name>` |
| variable access | `Variables\|Replication\|GetReplicates` (63 `Variables\|*` ids) |

The catalogue id **is** the id the graph reports back: `GetNodeInfos` on an
existing node answers `"typeId":"AddEvent|EventBeginPlay"`, the same string
`FindNodeTypes` offers. There is no second, shorter "reported id" to match on —
copy the id from `FindNodeTypes` and use it verbatim.

The empty-class-prefix form `|SetMaxWalkSpeed` and
`Variables|Character|GetCharacterMovement` are **not** palette ids here.
Filtering `SetMaxWalkSpeed` returns exactly two ids, both
`Class|CharacterMovementComponent|…`; filtering `GetCharacterMovement` returns
exactly one, `Class|Character|GetCharacterMovement`. Those complete result lists
are the evidence — no id equal to `|SetMaxWalkSpeed` is among them.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `CreateNode` fails on the id | the id is not a palette id in that graph | `FindNodeTypes` first, copy the id verbatim |
| `FindNodeTypes` → `was called with unrecognized parameter(s) [type_id_filter]. Valid parameters: [contextPins, graph, typeIdFilter]` | parameters are camelCase | the error prints the valid names — use them |
| `ConnectPins` fails on types | incompatible pins | check `typeId` on both pins |
| Wires land on the wrong pin | indices are per-node, and index 0 is not always exec | re-read `GetNodeInfos`; match the pin `name` before using `indexId` |
| `ConnectPins` → `unrecognized parameter(s) [input_pin, output_pin]. Valid parameters: [inputPin, outputPin]` | the old snake_case names | `ConnectPins(outputPin, inputPin)`, `SetPinValue(pin, value)` |
| `save_assets` → Unknown tool | no such tool in this build | `AssetToolset.SaveAsset` one path at a time |
| Duplicate nodes accumulate | a failed script still created nodes | list nodes by type, `DeleteNode` the strays before rebuilding |
| `read_graph_dsl` → "is a plain Blueprint" | the old DSL toolset only handles Widget / Anim / level-script Blueprints | `BlueprintDslToolset.Read(assetPath, scope)` |

**Clean up before you rebuild.** A script that fails partway still leaves the
nodes it already created. List nodes by type, `DeleteNode` the strays
(`BlueprintToolsets.BlueprintToolset.DeleteNode(node: EdGraphNode)` — verified
signature), then create the final set — otherwise you get two nodes of
the same type and only one of them is wired.

**`BlueprintDslToolset.Read` is the best way to *understand* a graph**; use the
pin API to *change* one. For a plain Blueprint the DSL write path is
`BlueprintDslToolset.Write` / `Edit` (write steps), and `Edit` needs the
`revision` token from the matching `Read`.

## Output contract

- the new nodes exist in the graph with the intended connections
- `GetNodeInfos` shows non-empty `connectedPins` on the pins you wired
- the blueprint compiles and is saved

## Related

- `ue-op-inspect-blueprint` — read the graph before changing it
- `ue-op-setup-input` — create the input events this wires to
- `ue-op-fix-compile-error` — when the result does not compile