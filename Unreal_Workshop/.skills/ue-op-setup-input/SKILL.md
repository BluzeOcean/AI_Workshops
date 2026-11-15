---
name: ue-op-setup-input
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to bind keys so a character responds — add or change legacy axis/action mappings for an existing blueprint, or wire Enhanced Input mappings. Skip if no UE MCP connection, if the character already uses Enhanced Input exclusively, or if the request is about camera/gameplay logic rather than bindings.
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

# ue-op-setup-input — make a character respond to keys

## The decision that saves most of the time

**Check whether the blueprint already contains legacy input events before
building anything.** A UE4-era character usually already has
`InputAxisMoveForward` / `MoveRight` / `Turn` / `LookUp` / `InputActionJump`
events, fully wired to `AddMovementInput` / `AddControllerYawInput`.

If they exist, the job is **binding keys to axis names** — a config change,
not graph work. Do not build an Enhanced Input setup.

| Blueprint uses | Work required |
|---|---|
| Legacy `InputAxis*` / `InputAction*` events | add `AxisMappings` / `ActionMappings` (this skill) |
| Enhanced Input (`Get Enhanced Input Component`, `AddMappingContext`) | create IA/IMC assets + rewrite the graph (heavier) |

Find out which with `ue-op-inspect-blueprint`.

---

## Procedure

### 1. Read the existing events

```python
# list_graphs -> get_graph(EventGraph) -> read_graph_dsl
```
Legacy events decompile as `(event InputAxisMoveForward (AxisValue) ...)`.
Note the **exact axis/action names** the blueprint expects — they must match
the mappings you create, character for character.

### 2. Write the bindings (live, no editor restart)

The `UInputSettings` CDO is reachable by path and is writable:

```
instance = "/Script/Engine.Default__InputSettings"
```

```python
ObjectTools.set_properties(
    instance="/Script/Engine.Default__InputSettings",
    values=json.dumps({
        "AxisMappings": [
            {"AxisName": "MoveForward", "Scale":  1.0, "Key": "W"},
            {"AxisName": "MoveForward", "Scale": -1.0, "Key": "S"},
            {"AxisName": "MoveRight",  "Scale":  1.0, "Key": "D"},
            {"AxisName": "MoveRight",  "Scale": -1.0, "Key": "A"},
            {"AxisName": "Turn",       "Scale":  1.0, "Key": "MouseX"},
            {"AxisName": "LookUp",     "Scale": -1.0, "Key": "MouseY"},
        ],
        "ActionMappings": [
            {"ActionName": "Jump",   "bShift": False, "bCtrl": False,
             "bAlt": False, "bCmd": False, "Key": "SpaceBar"},
        ],
    }))
```

`set_properties` marshals the plain structs for you — you do not build
`UObject`s. `UInputSettings::AxisMappings` / `ActionMappings` are
`TArray<FInputAxisKeyMapping>` / `TArray<FInputActionKeyMapping>`
(`FInputAxisKeyMapping` = `AxisName`, `Scale`, `Key`;
`FInputActionKeyMapping` = `ActionName`, `bShift`, `bCtrl`, `bAlt`, `bCmd`,
`Key`). There is no `UInputAxisMapping` class in the engine.

Read back with
`get_properties(instance="/Script/Engine.Default__InputSettings", properties=["AxisMappings"])`.
**Both arrays are empty on a fresh project** — that is the usual reason a
character does not move.

**The change reaches the running game.** `UInputSettings` notifies on change:
`UInputSettings::PostEditChangeChainProperty` calls `ForceRebuildKeymaps()`,
which walks every live `UPlayerInput` and rebuilds its key maps, and
broadcasts `OnActionAxisMappingsChanged`, which refreshes the blueprint
action database. So a live edit is not just cosmetic — the running PIE
session picks it up, and new axis/action node types appear in the editor.

### 3. Persist to the project config

The runtime CDO change is lost on editor restart. Write the same entries into
`Config/DefaultInput.ini`, section `[/Script/Engine.InputSettings]`:

```ini
+AxisMappings=(AxisName="MoveForward",Scale=1.000000,Key=W)
+AxisMappings=(AxisName="MoveForward",Scale=-1.000000,Key=S)
+ActionMappings=(ActionName="Jump",bShift=False,bCtrl=False,bAlt=False,bCmd=False,Key=SpaceBar)
```

`Scale` carries the sign for inverted axes. `LookUp` conventionally maps
`MouseY` with **negative** scale so mouse-up pitches up.

**Check for duplicates before writing** — the editor may re-save the CDO on
exit and append its own copies, which produces
`Duplicate mapping of key %ls for axis %ls` errors:

```bash
grep -c "^+AxisMappings" Config/DefaultInput.ini
grep -c "^+ActionMappings" Config/DefaultInput.ini
```

### 4. Verify the bindings took

**The blueprint compiler resolves legacy axis/action event nodes against
`UInputSettings`.** Compile the blueprint and check the log:

```bash
grep -E "references unknown (Axis|Action)" "D:/UE/<project>/Saved/Logs/<Project>.log"
```

No `unknown Axis 'MoveForward'` warning ⇒ the mapping is registered.
An `unknown Axis` warning means the name does not match what the blueprint
uses — compare spelling exactly.

The exact warning texts (note the trailing ` for @@`, and that the action
variant has **no space** in `InputAction`):

```
Input Axis Event references unknown Axis 'MoveForward' for @@
InputAction Event references unknown Action 'Sprint' for @@
```

**Why an axis mapping alone is enough.** The blueprint's axis event registers
a `FBlueprintInputAxisDelegateBinding`; at runtime that binding is applied
straight onto the pawn's `InputComponent->AxisBindings`. The *value* for that
axis name comes from `UPlayerInput::AxisKeyMap`, which is built from
`UInputSettings::AxisMappings`. So the only thing the blueprint needs is for
an axis of that name to exist in `UInputSettings` — no extra wiring.

A second, equally strong signal: adding a mapping makes a **new node type
appear** in the graph catalog. `find_node_types(graph, "ActionEvents")` will
now list `Input|ActionEvents|Sprint` for a mapping named `Sprint`.

### 5. Confirm in game

Use `ue-op-test-pie` to start PIE, inject the key, and read the pawn's
transform. Bindings that compile cleanly but do not move the pawn usually mean
the axis name is wrong or the event is on a different blueprint.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Character never moves, no warnings | axis name ≠ blueprint's axis name | compare `read_graph_dsl` output to your mapping |
| `Input Axis Event references unknown Axis 'X' for @@` | no mapping named `X` | add it, or rename the blueprint's event |
| Mapping works in PIE, gone next launch | only the runtime CDO was changed | also write `Config/DefaultInput.ini` |
| `Duplicate mapping of key ... for axis ...` | ini has duplicate entries | dedupe; the editor re-saved the CDO |
| `SetMaxWalkSpeed` sprint is a no-op | 600 is ACharacter's default | sprint must be a *different* value from the walk value |
| Action event never fires | the action mapping is missing even though the axis ones work | action mappings need `ActionName` + the four modifier booleans |

**`UInputSettings` is `UCLASS(config=Input, defaultconfig)`** — the config
name is `Input`, so the file is `Config/DefaultInput.ini`, not
`DefaultEngine.ini`. The ini *section* is still the class path:
`[/Script/Engine.InputSettings]`.

**Legacy axis mappings are global.** They apply to every player input
component, so one mapping set drives every character in the project.

## Output contract

- `Config/DefaultInput.ini` contains the mappings
- the runtime CDO holds the same mappings
- the target blueprint compiles with no `unknown Axis/Action` warnings
- `ue-op-test-pie` can confirm the character moves

## Related

- `ue-op-inspect-blueprint` — read which input style a blueprint uses
- `ue-op-wire-graph` — wire the events once they exist
- `ue-op-test-pie` — verify in game
