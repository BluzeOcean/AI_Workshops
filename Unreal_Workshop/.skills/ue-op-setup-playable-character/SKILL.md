---
name: ue-op-setup-playable-character
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to make a character controllable in a level end to end — third-person movement, mouse look, jump and sprint. Orchestrates the ue-op-* primitives; reuse what the asset already has. Skip if no UE MCP connection, or if only one narrow piece (input only, camera only) is needed.
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

# ue-op-setup-playable-character — make a character playable

This is the **composite** recipe. It chains the primitives; it does not repeat
their details. Read the linked skill for each step.

| Step | Skill |
|---|---|
| 1. See what the character already has | `ue-op-inspect-blueprint` |
| 2. Repair anything that will not compile | `ue-op-fix-compile-error` |
| 3. Make a Lab copy so the source asset stays clean | `ue-op-create-blueprint` |
| 4. Bind the keys | `ue-op-setup-input` |
| 5. Add only the missing pieces | `ue-op-add-component`, `ue-op-wire-graph` |
| 6. Bind the level to the pawn | `ue-op-setup-game-mode` |
| 7. Prove it works | `ue-op-test-pie` |

---

## The order matters

**Inspect first.** The single biggest time sink is building something the
asset already has. A typical UE4-era character already contains:

- legacy `InputAxisMoveForward` / `MoveRight` / `Turn` / `LookUp` events,
  fully wired to `AddMovementInput` / `AddControllerYawInput`
- a `CharacterMovementComponent`
- a camera rig (`SpringArm` + `Camera`)

If those are present, the work is **binding keys**, not authoring a
controller — hours instead of minutes.

**Fix compile errors before anything else.** A blueprint that will not compile
blocks PIE and wedges the editor behind a modal dialog.

---

## The recipe

### 1. Inspect the source character

`ue-op-inspect-blueprint` on the character blueprint. Record:

- parent class
- graph list (is there an EventGraph with logic?)
- component list (**is there already a spring arm / camera?**)
- the decompiled EventGraph — note the exact axis and action names it expects
- whether it uses legacy input or Enhanced Input

### 2. Repair the compile errors

`ue-op-fix-compile-error`. Sample assets commonly carry a node calling a
function removed in a later engine version. This blocks everything.

### 3. Create a Lab copy

`ue-op-create-blueprint` — a child blueprint in `/Game/Lab/…`:

- the child inherits the parent's mesh, animations and logic
- the parent's EventGraph **still runs**; the child's starts empty, so you add
  only what is new
- the source asset stays pristine and the experiment is easy to delete

### 4. Bind the keys

`ue-op-setup-input`. If the character uses legacy events, add
`AxisMappings` / `ActionMappings` for exactly the names the graph expects.
Write them to `Config/DefaultInput.ini` as well as the runtime CDO.

For a third-person preset:

| Axis | Keys | Scale |
|---|---|---|
| `MoveForward` | W / S | +1 / -1 |
| `MoveRight` | D / A | +1 / -1 |
| `Turn` | MouseX | +1 |
| `LookUp` | MouseY | **-1** (mouse up pitches up) |
| `Jump` (action) | SpaceBar | — |
| `Sprint` (action) | LeftShift | — |

Verify: the blueprint must compile with **no** `references unknown Axis/Action`
warnings.

### 5. Add only what is missing

- **Camera**: if the character has no spring arm, `ue-op-add-component` — a
  `SpringArmComponent` (arm ~350–470, `bUsePawnControlRotation=True`,
  `bDoCollisionTest=True`) parented to the capsule or mesh, plus a
  `CameraComponent` parented to the arm (FOV 90). **UE 5.8 spring arms have
  no socket property** — use `RelativeLocation` to set the pivot height.
- **Sprint**: `ue-op-wire-graph` — a legacy `InputActionSprint` event whose
  `Pressed` sets `MaxWalkSpeed` to a sprint value and whose `Released`
  restores the walk value. **The two values must differ**, and the walk value
  should be ACharacter's default (600) so releasing returns to normal.

### 6. Bind the level

`ue-op-setup-game-mode` — a `BP_LabGameMode` with
`DefaultPawnClass = <your Lab character>`, and the level's
`WorldSettings.DefaultGameMode` pointed at it.

Set the **level override**, not `GlobalDefaultGameMode` — the latter's ini
takes effect on the next editor start.

The GameMode spawns the player at the level's `PlayerStart` automatically; do
not place the character in the level as well.

### 7. Prove it

`ue-op-test-pie`:

- PIE starts, log shows `Game class is 'BP_LabGameMode_C'`
- the pawn appears in `find_actors`
- inject `W` → position changes
- inject mouse movement → yaw/pitch changes
- hold LeftShift → `MaxWalkSpeed` changes

**Read the transform only after the world has ticked** — reading too early
shows pre-movement values and looks like failure.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Character spawns but will not move | axis names ≠ the graph's axis names | read the DSL, match exactly |
| Character will not spawn | wrong game mode, or no `PlayerStart` | check `Game class is '...'` in the log |
| Camera is under the floor or clipped | the boom pivots at the wrong height | set the arm's `RelativeLocation` |
| Two cameras fight / the view snaps | a camera rig already existed | remove the duplicate |
| Sprint seems to do nothing | sprint value equals the walk value | sprint 900, walk 600 |
| The camera does not follow the aim | `bUsePawnControlRotation` is off | turn it on |
| PIE uses the old game mode | the `GlobalDefaultGameMode` ini is loaded into its CDO at startup | set `WorldSettings.DefaultGameMode` |
| The editor wedges during PIE | a compile-error modal | `ue-op-fix-compile-error` |
| The pawn reads as unmoved after a keypress | read before the tick | wait, then read again |

**Do not add a second camera rig.** If `get_components` already lists a
spring arm and a camera, they are the rig — tune them instead.

**`bUseControllerRotationYaw = true`** on the character means the body turns
to face the aim direction, which suits a shooter. For a character that should
face its movement direction instead, set it false and let
`bOrientRotationToMovement` handle it.

## Output contract

- A Lab blueprint with the character, a Lab game mode, bindings in
  `Config/DefaultInput.ini`
- The blueprint compiles with no unknown-axis warnings
- PIE spawns the character; movement, look, jump and sprint are all verified
  by reading runtime state

## Related

- `ue-op-mcp-connect` — the bridge this all runs through
- `ue-op-extract-to-skill` — capture the next variation of this recipe
