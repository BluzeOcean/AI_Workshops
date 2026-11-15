---
name: ue-op-python-gotchas
description: Unreal Python that fails silently - struct write-back loss, wrong play-data field names, root-component moves, and Live Coding limits.
---

# Unreal Python that no-ops

These all fail **without an exception**, which is why they cost hours.

## Struct writes from a getter are discarded

```python
mats = mesh.get_editor_property("materials")
mats[i].set_editor_property("material_interface", mi)   # lost
mesh.set_editor_property("materials", mats)             # still lost
```

Build fresh structs and assign the whole array:

```python
new = []
for sm in mats:
    n = unreal.SkeletalMaterial()
    n.set_editor_property("material_slot_name",
                          sm.get_editor_property("material_slot_name"))
    n.set_editor_property("material_interface", mi)
    new.append(n)
mesh.set_editor_property("materials", new)
```

The same pattern applies to any struct array — `SingleAnimationPlayData`,
`PostProcessSettings`, retarget chain settings.

## SingleAnimationPlayData field names

Correct: `anim_to_play`, `saved_looping`, `saved_playing`, `saved_position`,
`saved_play_rate`.

Silently ignored: `loop_animation`, `playing`, `play_rate`.

## A skeletal mesh component's relative_location moves the actor

`skeletal_mesh_component` **is** the actor's root component. Setting its
`relative_location` moves the whole actor. Use `set_actor_location` on the actor.

## Live Coding cannot add a class

Live Coding patches existing code. It cannot add a new `UCLASS`, a new file, or a
new reflected `UPROPERTY` — those need the header tool and a full build:

- close the editor, then
  `Build.bat <Target> Win64 Development -Project=<uproject>`
- with the editor left open, UBT writes `UnrealEditor-<Module>-0002.dll`, which
  the editor never loads, so the change appears to vanish
- Live Coding also leaves `*.patch_N.exe` artefacts behind; delete them

## Fields and methods that are not where you expect

- Bone names are not readable: `BoneNode.name` is protected. Read animation tracks
  through `anim.controller.get_model_interface()`.
- `export_render_target` picks its format from the render target.
- `force_root_lock` affects root-motion **extraction**, not the pose — it will not
  stop a clip from deforming a mesh.
- Several retargeter chain properties are marked deprecated and are silently
  ignored when set.

When a UE Python snippet appears to do nothing, suspect this list before
rewriting the logic.
