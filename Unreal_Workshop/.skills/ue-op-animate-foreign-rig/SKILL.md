---
name: ue-op-animate-foreign-rig
description: Retargeting an animation onto an AI-generated rig fails; here is the evidence, and the authoring recipe that actually drives the mesh.
---

# Animating a rig you did not author

## Why this skill exists

AI auto-rigs (Tripo and similar) use UE-Mannequin bone **names** — `root`,
`pelvis`, `spine_01..05`, `neck_01`, `head`, `clavicle_l`, `upperarm_l`,
`lowerarm_twist_01_l`, `thigh_l`, `calf_l`, `ball_l` — but **not Mannequin bone
orientations**, and they omit `ik_foot_*` / `ik_hand_*`.

So a clip whose bone *names* match will still rotate the wrong axes and tear the
mesh apart. Sharing a skeleton between your own meshes is fine; borrowing a clip
from a different rig is not.

## What does not work

All of these were tried, and are recorded so nobody repeats them:

| attempt | outcome |
|---|---|
| direct FBX import of a Mannequin clip onto the AI skeleton | hard error: `Unable to retrieve bone index for track: ik_foot_l` |
| IK Retargeter (IKRig + RTG + auto-align) | builds ~29 chains, reports success, emits a clip that deforms the mesh into a degenerate shape |
| `enable_root_motion = False` | stops the actor drifting; mesh still broken |
| `force_root_lock = True` | no effect — it governs root-motion **extraction**, not the pose |
| deleting the root bone track | no effect |
| per-chain `RetargetTranslationMode.NONE` | property is **deprecated**, silently ignored |
| disabling retarget ops | `get/set_retarget_op_enabled` return null |

If you find yourself patching the clip, stop and author instead. The bone axes
are the problem, not the clip.

## The recipe that works

Author the motion on the target skeleton, computing each bone's local rotation
from a **world-space** axis:

```python
# bone rest orientation in armature space
basis = bone.matrix_local.to_3x3()
R_world = Matrix.Rotation(angle, 3, 'X')     # the swing axis
R_local = basis.inverted() @ R_world @ basis
pose_bone.rotation_quaternion = R_local.to_quaternion()
```

Determine the swing axis from the mesh: a character facing Y with its widest
extent on X swings its legs about **world X**.

Then:

1. Set `rotation_mode = 'QUATERNION'` on every bone you touch.
2. Keyframe `rotation_quaternion` (and `location` for the pelvis) across a loop.
3. Set the scene frame range and fps so the loop is exact.
4. Bake-export FBX: `bake_anim=True`, `bake_anim_use_all_bones=True`,
   `bake_anim_force_startend_keying=True`.
5. Import that FBX as an **animation onto the skeleton**: `import_mesh=False`,
   `import_animations=True`, `skeleton=<target>`.

A procedurally generated gait is often the better result for a mech or creature
anyway — authored for its proportions instead of adapted from a human.

## Playing it in a level

`SkeletalMeshComponent`: set `animation_mode = ANIMATION_SINGLE_NODE`, then set
`animation_data` with `anim_to_play`, `saved_looping`, `saved_playing`,
`saved_position`, `saved_play_rate`. Those field names matter — see
[ue-op-python-gotchas](../ue-op-python-gotchas/SKILL.md).

If the actor drifts away each loop, root motion is baked into the clip; disable it
or lock the root.

## Prove it animates

Importing is not animating. Capture the same camera at two `saved_position` values
and diff the images — see
[ue-op-offscreen-verify](../ue-op-offscreen-verify/SKILL.md).
