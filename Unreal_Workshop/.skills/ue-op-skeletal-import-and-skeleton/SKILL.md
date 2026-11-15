---
name: ue-op-skeletal-import-and-skeleton
description: Import skeletal meshes so they genuinely share one skeleton in Unreal, and verify it instead of assuming it.
---

# Import a skeletal mesh and verify the skeleton

## Import settings that matter

For a Tripo-class delivery:

- **Normal Import Method: Import Normals** — not Compute. The source's split
  normals are part of the look.
- **Compute Weighted Normals: off** — it re-smooths hard-surface armour.
- **Material Import Method: Do Not Create Material** — the auto-created graph
  usually leaves metallic/roughness unwired, and on a 68-part mesh that is 68 junk
  materials.
- **Create Physics Asset: off** until you want one deliberately.
- **No animations** on the mesh import; the clip is imported separately (see
  [ue-op-animate-foreign-rig](../ue-op-animate-foreign-rig/SKILL.md)).

## Make several variants share one skeleton

Import the first mesh (it creates the skeleton), then pass
`skeleton=<that asset>` on every subsequent import. Do not let each import create
its own.

Two gotchas:

- Interchange's `combine_skeletal_meshes_behavior = BY_SKELETON` silently merges a
  multi-object import into one mesh. If you are deliberately testing a "modular"
  variant, that is exactly what must not happen.
- Re-importing does **not** fix a bad skeleton. If the rig came from differently
  named armatures, fix it in Blender first.

## Verify — do not assume

Two checks, both cheap:

1. **Same asset, not "same look":**
   ```python
   a = mesh_a.get_editor_property("skeleton")
   b = mesh_b.get_editor_property("skeleton")
   assert a == b
   ```
2. **No missing-bones warning** for that skeleton. Grep the editor log for
   `missing bones` and `Invalid animation skeleton`.

If check 2 fails, stop. The rig is inconsistent and
[ue-op-blender-rig-for-ue](../ue-op-blender-rig-for-ue/SKILL.md) is the fix.
Continuing past that point wastes hours — the mesh may still render, and the
failure only shows up later as an animation that destroys the mesh.

## Re-assigning materials after a re-import

A re-import drops material assignments. Rebuild the array with fresh
`unreal.SkeletalMaterial()` structs — see
[ue-op-python-gotchas](../ue-op-python-gotchas/SKILL.md) for why mutating the
array in place silently does nothing.
