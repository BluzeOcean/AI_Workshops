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

## The core mechanic

`PinID` identifies one pin on one node:

```python
{"node": "<node refPath>", "index_id": <int>, "direction": "EGPD_Input"|"EGPD_Output"}
```

- `direction: "EGPD_Output"` + `index_id` → a source pin
- `direction: "EGPD_Input"` + `index_id` → a destination pin

Connect with `connect_pins(output_pin=..., input_pin=...)`; set a default value
with `set_pin_value(pin=..., value="900.0")`.

**Pin indices are per-node and stable**, and you learn them from
`get_node_infos`.

---

## Procedure

### 0. Resolve the graph you are editing

Every step below works on `eg`, the blueprint's EventGraph:

```python
def rp(o):
    if isinstance(o, dict):
        try:
            return o["refPath"]
        except Exception:
            return str(o)
    return str(o)

BP = "/Game/<Folder>/<AssetName>"
bp = T("editor_toolset.toolsets.asset.AssetTools.load_asset", asset_path=BP)
graphs = T("editor_toolset.toolsets.blueprint.BlueprintTools.list_graphs", blueprint=bp)
eg = [g for g in graphs if rp(g).endswith(":EventGraph")][0]
```

`list_graphs` returns the blueprint's **own** graphs. A child blueprint's
EventGraph starts empty — the parent's graph is separate and still runs.

### 1. Find the node types you need

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

T("editor_toolset.toolsets.blueprint.BlueprintTools.find_node_types", graph=eg, type_id_filter="SetMaxWalkSpeed",
  context_pins=[])
```

`context_pins=[]` is **required** even though the signature shows a default.

The catalog is seeded from the graph's own nodes, so a node type only exists
if something in the graph already uses it — or if the input mapping that
creates it exists (legacy `Input|ActionEvents|<Name>` appears once an action
mapping named `<Name>` is registered; see `ue-op-setup-input`).

### 2. Create the nodes

```python
n = T("editor_toolset.toolsets.blueprint.BlueprintTools.create_node", graph=eg, type_id=tid, pos={"x": -300, "y": 300})
```

### 3. Read their pins

```python
ni = T("editor_toolset.toolsets.blueprint.BlueprintTools.get_node_infos", nodes=[n])[0]
# ni["input_pins"] / ni["output_pins"] -> [{"name","type_id","pin_id","connected_pins","value"}]
```

Pin index lives at `p["pin_id"]["index_id"]`.

### 4. Wire

```python
def PID(node_ref, index_id, direction):
    return {"node": node_ref, "index_id": index_id, "direction": direction}

T("editor_toolset.toolsets.blueprint.BlueprintTools.connect_pins",
  output_pin=PID(sprint_ref, 0, "EGPD_Output"),   # Pressed
  input_pin=PID(setfast_ref, 0, "EGPD_Input"))    # execute

T("editor_toolset.toolsets.blueprint.BlueprintTools.set_pin_value",
  pin=PID(setfast_ref, 1, "EGPD_Input"), value="900.0")
```

### 5. Compile and save

```python
T("editor_toolset.toolsets.blueprint.BlueprintTools.compile_blueprint", blueprint=bp)
T("editor_toolset.toolsets.asset.AssetTools.save_assets", asset_paths=[bp])   # stop PIE first
```

---

## Legacy input events: the multi-exec case

A legacy `InputAction` node (`UK2Node_InputAction`) has exec outputs
**`Pressed` (0)** and **`Released` (1)**, plus a `Key` struct output (2) —
that is how hold-to-sprint works. The DSL's `(event …)` form only wires a pin
named `then`, which legacy events do not have, so wire these by hand with the
pin API above.

Its sibling, the axis event (`UK2Node_InputAxisEvent` — there is no
`UK2Node_InputAxis` class in 5.8), has three **output** pins and no exec
input:

| index | pin | type |
|---|---|---|
| 0 | `OutputDelegate` | Delegate |
| 1 | `then` | Exec |
| 2 | `AxisValue` | float |

So an axis event can be read as a data source as well as driven as a flow.

A worked sprint chain:

```
Input|ActionEvents|Sprint        Pressed  -> SetMaxWalkSpeed.execute   value 900
                                 Released -> SetMaxWalkSpeed.execute   value 600
GetCharacterMovement             CharacterMovement -> both .self pins
```

`600` is ACharacter's default walk speed — sprint must differ from it or the
toggle is invisible.

## Node type id conventions (verified)

| What | type_id |
|---|---|
| legacy action event | `Input\|ActionEvents\|<ActionName>` |
| legacy axis event | `Input\|AxisEvents\|<AxisName>` |
| component variable setter | `\|SetMaxWalkSpeed` (empty class prefix) |
| component variable getter | `Variables\|Character\|GetCharacterMovement` |
| class function | `Class\|CharacterMovementComponent\|SetMaxWalkSpeed` |
| custom event | `AddEvent\|Custom\|<Name>` |
| built-in event | `AddEvent\|EventBeginPlay`, `AddEvent\|EventTick` |

The catalog id and the id reported by `get_node_infos` differ
(`Class|CharacterMovementComponent|SetMaxWalkSpeed` → `|SetMaxWalkSpeed`).
**Match on the reported id** when looking nodes up.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `create_node` → "does not exist" | the id is not in that graph's catalog | find the real id with `find_node_types` |
| `find_node_types` fails | `context_pins` is required | pass `context_pins=[]` |
| `connect_pins` fails on types | incompatible pins | check `type_id` on both pins |
| Wires land on the wrong pin | indices are per-node | re-read `get_node_infos` after every change |
| Duplicate nodes accumulate | a failed script still created nodes | list nodes by type, delete extras before rebuilding |
| The DSL cannot wire legacy events | `(event …)` only handles a `then` pin | use the pin API |
| `save_assets` → "Asset does not exist" | PIE is running | stop PIE first |

**Clean up before you rebuild.** A script that fails partway still leaves the
nodes it already created. List nodes by type, `delete_node` the strays, then
create the final set — otherwise you get two `InputActionSprint` nodes and
only one of them is wired.

**`read_graph_dsl` is the best way to *understand* a graph**; use the pin API
to *change* one. `write_graph_dsl` exists but cannot express multi-exec
legacy events.

## Output contract

- the new nodes exist in the graph with the intended connections
- `get_node_infos` shows non-zero `connected_pins` on the pins you wired
- the blueprint compiles and is saved

## Related

- `ue-op-inspect-blueprint` — read the graph before changing it
- `ue-op-setup-input` — create the input events this wires to
- `ue-op-fix-compile-error` — when the result does not compile
