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

Run this as **one** `execute_tool_script` through the MCP dispatcher. Each
individual tool call is a round trip; batching them keeps the answer in one
message.

```python
import json

def T(tool, **kw):
    r = execute_tool(tool, json.dumps(kw))
    if isinstance(r, dict) and "returnValue" in r:
        return r["returnValue"]
    return r

def rp(o):
    if isinstance(o, dict):
        try:
            return o["refPath"]
        except Exception:
            return str(o)
    return str(o)

BP = "/Game/<Folder>/<AssetName>"          # the asset path

def run():
    out = {}
    bp   = T("editor_toolset.toolsets.asset.AssetTools.load_asset", asset_path=BP)
    cdo  = T("editor_toolset.toolsets.blueprint.BlueprintTools.get_default_object", blueprint=bp)
    out["parent_class"] = rp(T("editor_toolset.toolsets.object.ObjectTools.get_class", instance=bp))
    out["graphs"] = [rp(g).split(":")[-1] for g in
                     T("editor_toolset.toolsets.blueprint.BlueprintTools.list_graphs", blueprint=bp)]
    comps = T("editor_toolset.toolsets.actor.ActorTools.get_components", actor=cdo)
    out["components"] = [rp(c).split(".")[-1] for c in (comps if isinstance(comps, list) else [])]
    out["variables"] = [str(v) for v in
                         T("editor_toolset.toolsets.blueprint.BlueprintTools.list_variables", blueprint=bp)]
    # decompile one graph
    graphs = T("editor_toolset.toolsets.blueprint.BlueprintTools.list_graphs", blueprint=bp)
    eg = [g for g in graphs if rp(g).endswith(":EventGraph")]
    if eg:
        out["event_graph"] = str(T("editor_toolset.toolsets.blueprint.BlueprintTools.read_graph_dsl",
                                   graph=eg[0]))[:4000]
    return out
```

### Reading the component list

Component names differ by context and that trips people up:

| Context | Example name |
|---|---|
| CDO of a blueprint | `SpringArmComponent_0__A9892D03` (mangled SCS name) |
| CDO of a *child* blueprint | `SpringArmComponent_0__A9892D03` (inherited, same name) |
| Live instance in PIE | `CameraBoom` (the variable name) |

Always compare on the **last `.`-segment**, and expect the *instance* to use
the variable name rather than the SCS name.

### Reading the graph logic

`read_graph_dsl` returns a readable S-expression:

```
(event InputAxisMoveForward (AxisValue)
  (Pawn|Input|AddMovementInput
    (Math|Vector|GetForwardVector (Math|Rotator|MakeRotator 0.0 0.0 (.yaw (Pawn|GetControlRotation))))
    AxisValue))
```

From it you can see at a glance: which input events exist, what they call, and
whether the character uses legacy axis events (`InputAxis*`) or Enhanced Input
(`Get Enhanced Input Component` / `AddMappingContext`).

`read_graph_dsl` also tells you the **exact axis names** the blueprint expects
— those are the names your mappings must use.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `get_properties` says "could not be read: X" | X is not a Blueprint-visible property | use a different property or a different tool |
| `get_properties` demands a `properties` argument | it is required, not optional | always pass `properties=[...]` |
| `find_nodes` demands a `title` argument | required | pass `title=""` for all nodes |
| `find_node_types` fails on missing `context_pins` | it is required despite the default | always pass `context_pins=[]` |
| `get_components` returns names you cannot match later | CDO vs instance naming | compare the last `.`-segment |
| `get_parent_component` raises on a component | it only accepts `SceneComponent`s | skip non-scene components (movement, arrow) |
| A component looks absent but exists | it is inherited from the parent | read the *parent* blueprint's components |

**Reading a parent blueprint's CDO is the way to see inherited components.**
A child blueprint's `get_components` includes them, but the *definition*
(where it came from) only exists in the parent.

**Component properties are readable on the CDO** (`RelativeLocation`,
`TargetArmLength`, `bUsePawnControlRotation`, `FieldOfView`, `MaxWalkSpeed`).
`Visibility` and `SkeletalMesh` are not readable through this tool — read
those from the asset on disk instead.

## Output contract

A single message answering: parent class, graph list, component list,
variable list, and the decompiled EventGraph — enough to decide the next step
without a second round trip.

## Related

- `ue-op-create-blueprint` — make the thing to inspect
- `ue-op-add-component` — add what inspection showed was missing
- `ue-op-wire-graph` — change the logic inspection revealed
