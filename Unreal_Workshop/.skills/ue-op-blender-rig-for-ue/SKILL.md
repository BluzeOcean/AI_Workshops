---
name: ue-op-blender-rig-for-ue
description: Consolidate a Blender character onto ONE armature with one name before FBX export - the root-cause fix for duplicate-root skeletons in Unreal.
---

# One armature, one name

## The fact this skill exists for

In Blender the **armature object becomes a root bone in Unreal**. Export meshes
from three differently-named armatures (`Armature`, `Armature-Merged`,
`Armature-Low`) and each FBX gets a *different root bone*. The meshes then cannot
share a skeleton, and UE reports:

```
The Skeleton <SKEL> is missing bones that SkeletalMesh <MESH> needs.
Missing bone name(s): Armature-Low
LogAnimation: Invalid animation skeleton
```

Every downstream symptom — animations that deform the mesh to infinity, invalid
animation skeleton warnings, bones silently added to a shared skeleton on load —
traces back to here.

## Consolidate

1. Pick one armature as the master (typically the one the primary mesh is bound
   to).
2. Rename it **deliberately** — that name becomes the root bone. One extra root
   named for the character is fine; three different ones are not.
3. Un-parent it from any empty, so the armature is the top of the FBX hierarchy.
4. Point every mesh's `ARMATURE` modifier at the master.
5. Re-parent every mesh to the master with an identity parent inverse.
6. Delete the other armature objects.
7. Save the .blend.

Bind poses must agree. If the armatures were copies of one source, repointing is
safe. If a mesh was bound to a genuinely different rest pose, re-bind it instead.

## Export

Export each variant as its own FBX, **all from that same armature**:

- `apply_scale_options='FBX_SCALE_ALL'`, `global_scale=1.0`
- `axis_forward='-Y'`, `axis_up='Z'`
- `add_leaf_bones=False`
- `use_mesh_modifiers=False` — skinning must export as skin, not be baked in
- selection per file: master armature + that variant's meshes

## Verify before leaving Blender

- exactly one armature object remains
- its name is the one you chose
- transform is identity, no parent
- every mesh's armature modifier points at it

The Unreal-side check is in
[ue-op-skeletal-import-and-skeleton](../ue-op-skeletal-import-and-skeleton/SKILL.md).
