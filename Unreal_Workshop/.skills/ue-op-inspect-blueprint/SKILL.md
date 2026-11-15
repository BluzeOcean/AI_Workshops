---
name: ue-op-inspect-blueprint
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to read a blueprint's structure — graphs, components, variables, parent class, or the logic inside a graph — before changing it. Skip if no UE MCP connection, or if the task is to author or edit content rather than read it.
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

# ue-op-inspect-blueprint — read a blueprint before changing it

Most UE bugs are "I assumed the blueprint had X and it didn't". This skill
answers *what is actually there* in one compact pass.

## When to apply

- Before authoring anything into an existing blueprint
- To find out which input style a character uses (legacy vs Enhanced)
- To find the name of an existing component so you do not add a duplicate
- To see what a graph actually does before rewriting it
- To check whether a component is already present

## When NOT to apply

- Blueprint does not exist yet → `ue-op-create-blueprint`
- The blueprint lives in another project that is not open → use
  `ue-op-find-assets`

---

## Procedure

Run this as **one** `execute_python` call. It chains
`GetDefaultObject -> GetComponents` and `GetDefaultObject -> ListGraphs ->
BlueprintDslToolset.Read`, and those chains are why it is Python and not a
handful of one-hop calls: the CDO reference has to be carried from one tool to
the next.

`script` is a CodeBlock struct, `{"content": "<source>", "language": "Python"}`;
a bare string is rejected with *"Unable to import JSON string into CodeBlock"*.
Inside the source `unreal` is preimported, top-level `await` works, and every
tool is reachable as `await call_tool("<Toolset>.<Tool>", **kwargs)`.

```powershell
$mcp = "V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py"
$py = @'
import json

BP = "/Game/Jam/Core/BP_MechPawn.BP_MechPawn"          # <- the asset path to read

def ref(o):
    return o["refPath"] if isinstance(o, dict) else str(o)

bp     = await call_tool("EditorToolset.AssetToolset.LoadAsset", assetPath=BP)
cdo    = await call_tool("BlueprintToolsets.BlueprintToolset.GetDefaultObject", blueprint=BP)
parent = await call_tool("BlueprintToolsets.BlueprintToolset.GetParent", blueprint=BP)
graphs = await call_tool("BlueprintToolsets.BlueprintToolset.ListGraphs", blueprint=BP)
comps  = await call_tool("EditorToolset.ActorToolset.GetComponents", actor=cdo)
vars_  = await call_tool("BlueprintToolsets.BlueprintToolset.ListVariables",
                         blueprint=BP, bIncludeInherited=True)
dsl    = await call_tool("BlueprintToolsets.BlueprintDslToolset.Read",
                         assetPath=BP, scope="EventGraph")

json.dumps({
    "blueprint": ref(bp),
    "generated_class": ref(await call_tool("EditorToolset.ObjectToolset.GetClass", instance=BP)),
    "parent_class": ref(parent),
    "graphs": [ref(g).split(":")[-1] for g in graphs],
    "components": [ref(c).split(":")[-1] for c in comps],
    "variables": [v["name"] for v in vars_ if not v["name"].startswith("/")],
    "inherited_variables": len([v for v in vars_ if v["name"].startswith("/")]),
    "event_graph_dsl": dsl["dsl"],
    "revision": dsl["revision"],
}, indent=1)
'@
$body = @{ script = @{ content = $py; language = "Python" } } | ConvertTo-Json -Compress
python $mcp call editor_toolset.toolsets.python_scripting.PythonScriptingTools execute_python $body
```

Real output, `BP_MechPawn`, 2026-11-15:

```json
{
 "blueprint": "/Game/Jam/Core/BP_MechPawn.BP_MechPawn",
 "generated_class": "/Game/Jam/Core/BP_MechPawn.BP_MechPawn_C",
 "parent_class": "/Script/EpicJam2026.JamPawn",
 "graphs": ["UserConstructionScript", "EventGraph"],
 "components": ["SceneRoot", "BattleCamera", "PathPreview", "PathPreviewMarker", "FacingArrow"],
 "variables": [],
 "inherited_variables": 37,
 "event_graph_dsl": "(event `self.ReceiveBeginPlay`)\n\n(event `self.ReceiveActorBeginOverlap`\n  (params (OtherActor :type \"Actor Object Reference\")))\n\n(event `self.ReceiveTick`\n  (params (DeltaSeconds :type \"Float (single-precision)\")))\n",
 "revision": "75dfc6c263"
}
```

`"variables": []` is a real answer: this blueprint declares no member variables of
its own. An empty list is success, not a failed call — the variable *count* that
matters is the 37 inherited members. `revision` is the token
`BlueprintDslToolset.Edit` wants if you go on to change that graph.

If you only need one field, one hop is enough — e.g. the parent class:

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset GetParent '{"blueprint":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn"}'
# {"returnValue":{"refPath":"/Script/EpicJam2026.JamPawn"}}
```

**`GetParent`, not `GetClass`.** `ObjectToolset.GetClass` on a Blueprint
*asset* answers with the asset's own generated class
(`/Game/Jam/Core/BP_MechPawn.BP_MechPawn_C`), which is what you pass to
`Create` later — it is not the parent. `BlueprintToolset.GetParent(blueprint)`
returns `type[Object]` and is the one that answers `/Script/EpicJam2026.JamPawn`.

### Reading the component list

On this build `GetComponents` on a Blueprint's CDO answers with the
component's **variable name** — the refPath segment after the last `:`:

| Blueprint | `GetComponents` on the CDO |
|---|---|
| `BP_MechPawn` | `SceneRoot`, `BattleCamera`, `PathPreview`, `PathPreviewMarker`, `FacingArrow` |
| `BP_Band` | `Root`, `Health`, `Units`, `BlobShadows`, `StaticSoldiers`, … (14 in all) |

On the three blueprints checked here (`BP_MechPawn`, `BP_Band`, `BP_HoundTroop`)
there is no mangled SCS name such as `SpringArmComponent_0__A9892D03`: the CDO
reports the same names the Blueprint editor's components panel shows. Comparing
the segment after the last `:` is still the right move; just do not expect it to
differ from the variable name.

`GetComponents` takes a second argument that filters by class, which is the
cheap way to answer "is there already a camera rig?":

```powershell
python $mcp call EditorToolset.ActorToolset GetComponents '{"actor":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C","componentType":"/Script/Engine.CameraComponent"}'
# {"returnValue":[{"refPath":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C:BattleCamera"}]}
```

**A child blueprint's `GetComponents` includes components inherited from its
parent chain.** `BP_HoundTroop` (parent `/Script/EpicJam2026.HoundTroop`)
answers with ACharacter's `CollisionCylinder`, `CharacterMesh0`, `CharMoveComp`
and `Arrow` alongside its own `Rifle`, `BlobShadow` and `ThrusterFx`. To see
*where* an inherited component is defined, read the parent's CDO.

### Reading the graph logic

`BlueprintDslToolset.Read(assetPath, scope)` returns
`{"dsl": ..., "revision": ...}`. `scope` is `""` for the whole asset, a graph
name like `"EventGraph"`, or `"GraphName/EntryName"` for one entry. A whole
empty EventGraph reads:

```
(event `self.ReceiveBeginPlay`)

(event `self.ReceiveActorBeginOverlap`
  (params (OtherActor :type "Actor Object Reference")))

(event `self.ReceiveTick`
  (params (DeltaSeconds :type "Float (single-precision)")))
```

That is the **current** grammar, not the old s-expression dialect — there are no
`(Pawn|Input|AddMovementInput …)` tool paths in it. Call
`BlueprintDslToolset.Docs()` for the grammar the editor will accept before you
write any DSL, and treat the returned `revision` as opaque.

From the DSL you can see at a glance which events a graph implements and what
parameters they take. What it does **not** tell you is which further events are
*available to override* — that is `ListEvents`, which on `BP_MechPawn` returns
26 entries, `bIsImplemented` true for exactly `ReceiveTick`, `ReceiveBeginPlay`
and `ReceiveActorBeginOverlap`.

For input events specifically, the palette is the source of truth:
`FindNodeTypes` on the EventGraph with `typeIdFilter="ActionEvents"` lists the
project's Enhanced Input actions as `Input|EnhancedActionEvents|<IA_Name>`.

The old spelling `editor_toolset.toolsets.blueprint.BlueprintDslTools` still
resolves, but `read_graph_dsl` on it **refuses a plain Blueprint**:

```
ToolsetToolInvocationError: "BP_MechPawn" is a plain Blueprint; use the
BlueprintDslToolset tools (Read, Write, Edit, Diff). This toolset handles Widget,
Anim and level-script Blueprints.
```

So for a plain Blueprint it is `BlueprintToolsets.BlueprintDslToolset.Read`; the
old toolset is for Widget, Anim and level-script Blueprints only.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `BlueprintDslTools.read_graph_dsl` → "is a plain Blueprint; use the BlueprintDslToolset tools" | that toolset only handles Widget / Anim / level-script Blueprints | `BlueprintToolsets.BlueprintDslToolset.Read(assetPath, scope)` |
| `GetProperties` → "the following properties could not be read: SocketName" | the name is not a UPROPERTY on that class | `ListProperties` first, then ask for real names |
| `GetProperties` demands a `properties` argument | it is required, no default | always pass `properties=[...]` |
| `FindNodes` → `unrecognized parameter(s) [entry_points_only]. Valid parameters: [bEntryPointsOnly, graph, nodeClass, title]` | parameters are camelCase | all four are optional — `FindNodes(graph)` returns every node |
| `FindNodeTypes` → `unrecognized parameter(s) [type_id_filter]. Valid parameters: [contextPins, graph, typeIdFilter]` | parameters are camelCase | `contextPins` is optional (default null) |
| `ObjectToolset.GetClass` on a blueprint answers `…_C` | that is the generated class, not the parent | `BlueprintToolset.GetParent(blueprint)` |
| A tool result is a dict, not a live UObject | `call_tool` hands back marshalled `{"refPath": …}` values | unwrap with a `ref()` helper before chaining; do not call `unreal` helpers on it |
| A component looks absent but exists | it is inherited from the parent | read the *parent* blueprint's CDO |

**Component properties are readable on the CDO.**
`GetProperties(instance="/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C:BattleCamera",
properties=["RelativeLocation","RelativeRotation","FieldOfView"])` answers
`{"RelativeLocation":{"x":0,"y":0,"z":0},"RelativeRotation":{"pitch":0,"yaw":0,"roll":0},"FieldOfView":30}`,
and the same call on the native CDO
`/Script/Engine.Default__SpringArmComponent` answers real defaults
(`TargetArmLength` 300, `ProbeSize` 12, `bDoCollisionTest` true). Read values
back this way instead of assuming a default.

## Output contract

A single message answering: parent class, generated class, graph list,
component list, variable list, and the EventGraph DSL — enough to decide the
next step without a second round trip.

## Related

- `ue-op-create-blueprint` — make the thing to inspect
- `ue-op-add-component` — add what inspection showed was missing
- `ue-op-wire-graph` — change the logic inspection revealed