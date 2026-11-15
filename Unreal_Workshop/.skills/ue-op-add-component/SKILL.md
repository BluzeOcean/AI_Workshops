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

- The component already exists → configure it with
  `EditorToolset.ObjectToolset.SetProperties`
- The task is about the *behaviour* of existing components → `ue-op-wire-graph`
- You are adding a component to a **placed actor in a level** rather than to a
  blueprint — same tool, but `owner` is the actor refPath

---

## Procedure

```powershell
$mcp = "V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py"
```

### 1. Check what is already there first

A blueprint's components live on its class default object, so get the CDO and
ask it:

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset GetDefaultObject '{"blueprint":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn"}'
```

```json
{"returnValue":{"refPath":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C"}}
```

```powershell
python $mcp call EditorToolset.ActorToolset GetComponents '{"actor":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C"}'
```

```json
{"returnValue":[{"refPath":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C:SceneRoot"},
                {"refPath":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C:BattleCamera"},
                {"refPath":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C:PathPreview"},
                {"refPath":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C:PathPreviewMarker"},
                {"refPath":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C:FacingArrow"}]}
```

`GetComponents(actor, componentType = null)` takes a class filter as its second
argument — the cheap way to ask the only question that matters here:

```powershell
python $mcp call EditorToolset.ActorToolset GetComponents '{"actor":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C","componentType":"/Script/Engine.CameraComponent"}'
```

```json
{"returnValue":[{"refPath":"/Game/Jam/Core/BP_MechPawn.Default__BP_MechPawn_C:BattleCamera"}]}
```

**Adding a second camera rig when one already exists is the classic mistake** —
two spring arms fight over the view target and the result is a camera that
jitters or snaps. Read `ue-op-inspect-blueprint` and look first.

### 2. Add the component

*(write step — signature-verified, not executed)*

```powershell
python $mcp call EditorToolset.ActorToolset AddComponent '{"owner":"/Game/Lab/Characters/BP_LabTPSCharacter.BP_LabTPSCharacter","componentType":"/Script/Engine.SpringArmComponent","name":"LabSpringArm"}'
```

`AddComponent(owner, componentType, name) -> ActorComponent`. The call returns
the new component; read its name back before you configure it.

- `owner` may be a **blueprint** → the component is added to the SCS and the
  blueprint is recompiled automatically.
- `owner` may be a **`SceneComponent`** → the new component is parented to
  *that* component instead of the root.
- `owner` may be a **scene actor** → an instance component.

`componentType` is a class path — `/Script/Engine.SpringArmComponent`,
`/Script/Engine.CameraComponent`, `/Script/Engine.SkeletalMeshComponent`. A bare
name such as `"SpringArmComponent"` is rejected during parameter conversion
(*"… is not a valid object path for property 'ComponentType'"*), so the tool
never runs.

### 3. Configure the properties

*(write step — signature-verified, not executed)*

`SetProperties(instance, values)` — `values` is a **JSON string**, not a JSON
object. Build it once with `ConvertTo-Json` and you avoid hand-escaping:

```powershell
$values = @{
  TargetArmLength         = 350.0
  bUsePawnControlRotation = $true
  bDoCollisionTest        = $false
  RelativeLocation        = @{ x = 0.0; y = 0.0; z = 90.0 }
  RelativeRotation        = @{ pitch = -8.0; yaw = 0.0; roll = 0.0 }
} | ConvertTo-Json -Depth 4 -Compress
$body = @{ instance = "/Game/Lab/Characters/BP_LabTPSCharacter.BP_LabTPSCharacter:LabSpringArm"; values = $values } | ConvertTo-Json -Compress
python $mcp call EditorToolset.ObjectToolset SetProperties $body
```

Read back with `GetProperties(instance, properties=[...])` to confirm each value
landed — a silently-unset property is common, and this tool will not tell you:

```powershell
python $mcp call EditorToolset.ObjectToolset GetProperties '{"instance":"/Script/Engine.Default__SpringArmComponent","properties":["TargetArmLength","ProbeSize","bDoCollisionTest"]}'
```

```json
{"returnValue":"{\"TargetArmLength\":300,\"ProbeSize\":12,\"bDoCollisionTest\":true}"}
```

Note the shape: `returnValue` is a **JSON string**, so it needs a second parse.
That is the native CDO answering with its defaults — read your own component the
same way.

### 4. Compile and save

*(write step — signature-verified, not executed)*

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset CompileBlueprint '{"blueprint":"/Game/Lab/Characters/BP_LabTPSCharacter.BP_LabTPSCharacter"}'
python $mcp call EditorToolset.AssetToolset SaveAsset '{"assetPath":"/Game/Lab/Characters/BP_LabTPSCharacter.BP_LabTPSCharacter"}'
```

`SaveAsset` takes one path; there is no `save_assets(list)` in this build.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `SocketName` / `TargetSocket` "could not be read" | neither is a property of `USpringArmComponent` in this build | aim the boom with `SocketOffset` / `TargetOffset` |
| `Class\|CharacterMovementComponent\|GetCharacterMovement` does not exist | that function is on `ACharacter` | `Class\|Character\|GetCharacterMovement` |
| `Variables\|Character\|GetCharacterMovement` does not exist | there is no such variable-access id | `Class\|Character\|GetCharacterMovement` |
| `SetProperties` returns true but nothing changed | `values` was passed as an object, not a JSON string | encode it, then read back with `GetProperties` |
| `GetProperties` result is not a dict | `returnValue` is a JSON string | parse it a second time |
| Two cameras fight over the view | a rig already existed | `RemoveComponent(component)` the duplicate |
| Component "not found" later | you matched the wrong segment | the component name is the refPath part after the last `:` |
| `add_component` → "unrecognized parameter" | the old snake_case names | `owner`, `componentType`, `name` |

**`USpringArmComponent` properties** (read off
`/Script/Engine.Default__SpringArmComponent` on 2026-11-15): `TargetArmLength`
(300), `SocketOffset`, `TargetOffset`, `ProbeSize` (12), `ProbeChannel`
(`ECC_Camera`), `bDoCollisionTest` (true), `bUsePawnControlRotation` (false),
`bInheritPitch` / `bInheritYaw` / `bInheritRoll` (true), `bEnableCameraLag`
(false), `CameraLagSpeed` (10), `CameraRotationLagSpeed` (10).
`RelativeLocation` / `RelativeRotation` are inherited from
`USceneComponent`, not declared on the spring arm.

**A spring arm has no `SocketName` and no `TargetSocket` property.** Asking for
either answers *"the following properties could not be read: SocketName"*, and
there is nothing to set — the arm's transform plus `SocketOffset` /
`TargetOffset` is how it is aimed.

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