---
name: ue-op-add-component
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to add or configure a component on a blueprint — a spring arm, camera, mesh, or any ActorComponent — and set its properties. Skip if no UE MCP connection, if the component already exists (configure it instead), or if the task is about blueprint graph logic.
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

# ue-op-add-component — add and configure a component on a blueprint

## When to apply

- A character needs a camera rig (spring arm + camera) that it does not have
- A blueprint needs any new `ActorComponent`

## When NOT to apply

- The component already exists → configure it with `ObjectTools.set_properties`
- The task is about the *behaviour* of existing components → `ue-op-wire-graph`
- You are adding a component to a **placed actor in a level** rather than to a
  blueprint — same tool, but `owner` is the actor refPath

---

## Procedure

### 1. Check what is already there first

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

comps = T("editor_toolset.toolsets.actor.ActorTools.get_components", actor=cdo)
```

**Adding a second camera rig when one already exists is the classic mistake** —
two springs arms fight over the view target and the result is a camera that
jitters or snaps. Read `ue-op-inspect-blueprint` and look first.

### 2. Add the component

`add_component` accepts **a blueprint** as well as a scene actor:

```python
T("editor_toolset.toolsets.actor.ActorTools.add_component",
  owner="/Game/Lab/Characters/BP_LabTPSCharacter",
  component_type="/Script/Engine.SpringArmComponent",
  name="LabSpringArm")
```

- `owner` may be a **blueprint** → the component is added to the SCS and the
  blueprint is recompiled automatically.
- `owner` may be a **`SceneComponent`** → the new component is parented to
  *that* component instead of the root.
- `owner` may be a **scene actor** → an instance component.

`component_type` is a script path: `/Script/Engine.CameraComponent`,
`/Script/Engine.SkeletalMeshComponent`, …

### 3. Configure the properties

```python
T("editor_toolset.toolsets.object.ObjectTools.set_properties",
  instance=<component refPath>,
  values=json.dumps({
      "TargetArmLength": 350.0,
      "bUsePawnControlRotation": True,
      "bDoCollisionTest": False,
      "RelativeLocation": {"x": 0.0, "y": 0.0, "z": 90.0},
      "RelativeRotation": {"pitch": -8.0, "yaw": 0.0, "roll": 0.0},
  }))
```

Read back with
`get_properties(instance=<refPath>, properties=[...])` to confirm each value
landed — a silently-unset property is common.

### 4. Compile and save

```python
T("editor_toolset.toolsets.blueprint.BlueprintTools.compile_blueprint", blueprint=bp)
T("editor_toolset.toolsets.asset.AssetTools.save_assets", asset_paths=[bp])   # stop PIE first
```

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `SocketName` / `TargetSocket` "could not be read" | **UE 5.8 spring arms have no socket property** | attach to the mesh and use `RelativeLocation` |
| `Class\|CharacterMovementComponent\|GetCharacterMovement` does not exist | that function is on `ACharacter` | use `Variables\|Character\|GetCharacterMovement` |
| The requested component name is ignored | `add_component` may keep the auto-generated variable name | read the name back; do not assume |
| Two cameras fight over the view | a rig already existed | remove the duplicate (`remove_component`) |
| Component "not found" later | CDO uses the mangled SCS name, the instance uses the variable name | match on the last `.`-segment |
| `remove_component` on a CDO component | it removes the SCS node, not just the instance | re-run `get_components` to confirm |

**UE 5.8 `USpringArmComponent` properties** (verified): `TargetArmLength`,
`SocketOffset`, `TargetOffset`, `ProbeSize`, `ProbeChannel`,
`bDoCollisionTest`, `bUsePawnControlRotation`, `bInheritPitch/Yaw/Roll`,
`bEnableCameraLag`, `CameraLagSpeed`. `RelativeLocation` / `RelativeRotation`
are inherited from `USceneComponent`, not declared on the spring arm.

**A spring arm does have a `SocketName`, but it is a static `FName`
constant, not a property** — it names the arm's *own* end socket and
cannot be set. There is no `TargetSocket` UPROPERTY anywhere in the
engine in 5.8.

**Existing rigs often aim the boom with `SocketOffset`** rather than a bone
socket — the FabAssets Paragon rig uses `SocketOffset Z = 282.8` plus a camera
`RelativeRotation pitch = -28`. Check an existing rig before assuming it is
wrong.

**A spring arm attached to the capsule pivots at the capsule centre**; one
attached to the mesh pivots at the mesh origin plus `RelativeLocation`. For a
chest-height camera on a 180 cm character (capsule centre ≈ 88–94 cm), a
mesh-relative `RelativeLocation Z` of ~150 puts the pivot at shoulder height.

## Output contract

- The component exists in the blueprint's component list
- Every intended property reads back with the expected value
- The blueprint compiles and is saved

## Related

- `ue-op-inspect-blueprint` — see what already exists
- `ue-op-wire-graph` — make the new component do something
- `ue-op-test-pie` — verify the rig in game
