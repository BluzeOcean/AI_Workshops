---
name: ue-op-tripo-pipeline
description: Entry point for bringing a Tripo/AI-generated character into Unreal - the ordered pipeline, the rules that are never optional, and which sub-skill to read next.
---

# Tripo / AI character into Unreal

Route, don't read everything. Each step lives in its own skill; read the one you
are about to attempt.

## Order of operations

1. **Triage the delivery** — decide which mesh is the game asset, and whether a
   bake is needed at all.
   → [ue-op-tripo-triage-asset](../ue-op-tripo-triage-asset/SKILL.md)
2. **Consolidate the rig in Blender** — one armature, one name, before any export.
   → [ue-op-blender-rig-for-ue](../ue-op-blender-rig-for-ue/SKILL.md)
3. **Import and verify the skeleton** — the meshes must share ONE skeleton asset.
   → [ue-op-skeletal-import-and-skeleton](../ue-op-skeletal-import-and-skeleton/SKILL.md)
4. **Animate it** — retargeting fails on these rigs; author instead.
   → [ue-op-animate-foreign-rig](../ue-op-animate-foreign-rig/SKILL.md)
5. **Make it look right on a web budget.**
   → [ue-op-browser-look-budget](../ue-op-browser-look-budget/SKILL.md)
6. **Verify with a render, not an opinion.**
   → [ue-op-offscreen-verify](../ue-op-offscreen-verify/SKILL.md)

## The rules that are never optional

1. **One armature object per character, one name.** In Blender the armature
   object becomes a root bone in UE; different names give different roots, the
   meshes cannot share a skeleton, and every animation symptom downstream is a
   consequence. This is the highest-cost mistake in the pipeline.
2. **Never name-match an animation onto an AI rig.** Bone *names* match the UE
   Mannequin; bone *axes* do not. See step 4.
3. **Measure before you bake.** A Tripo "high poly" is ~10k tris. There is
   usually nothing to bake down.
4. **Verify with a render.** "It imported fine" and "it renders" are different
   claims. Use step 6.
5. **Save the asset, then confirm.** Editor changes are not on disk until saved.

## Routing

| if you are about to… | read first |
|---|---|
| assume the high poly is the game asset | [triage](../ue-op-tripo-triage-asset/SKILL.md) |
| add a second armature, or duplicate a rig | [blender rig](../ue-op-blender-rig-for-ue/SKILL.md) |
| retarget a Mannequin clip | [animate](../ue-op-animate-foreign-rig/SKILL.md) — this is where hours disappear |
| set a material's metallic by eye | [look budget](../ue-op-browser-look-budget/SKILL.md) |
| claim "it works" without seeing it | [offscreen verify](../ue-op-offscreen-verify/SKILL.md) |

When a UE Python snippet silently does nothing, check
[ue-op-python-gotchas](../ue-op-python-gotchas/SKILL.md) before rewriting it.
