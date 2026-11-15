---
name: ue-op-offscreen-verify
description: Prove that a mesh renders and animates without taking a desktop screenshot - an offscreen SceneCapture that works while the user is using the machine.
---

# Verify with an offscreen render

Useful whenever you cannot or should not capture the desktop: the user is working,
the editor has focus, or you simply need a repeatable oracle.

## Capture

```python
rt = unreal.RenderingLibrary.create_render_target2d(
    world, 1200, 700, unreal.TextureRenderTargetFormat.RTF_RGBA8,
    unreal.LinearColor(0, 0, 0, 1), False, False)

cap = eas.spawn_actor_from_class(
    unreal.SceneCapture2D, loc,
    unreal.MathLibrary.find_look_at_rotation(loc, target))
cap.set_actor_label("TMP_Capture")

comp = cap.capture_component2d
comp.set_editor_property("texture_target", rt)
comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
comp.set_editor_property("capture_every_frame", False)
comp.capture_scene()          # enqueues a render - export in a LATER call
```

In a following call:

```python
unreal.RenderingLibrary.export_render_target(world, rt, dir, "name")
```

## Three things that will waste your time

1. **The exported file has no extension**, and its format follows the render
   target's. `RTF_RGBA16F` writes HDR, `RTF_RGBA8` writes PNG. Check the first
   bytes (`\x89PNG\r\n\x1a\n`) and rename to `.png`.
2. **`capture_every_frame = True` never fires in the editor world** — actors do
   not tick there. Call `capture_scene()` explicitly and export in a separate
   call so a frame has elapsed.
3. **SceneCapture ignores post-process exposure** — it renders with a fixed chain.
   Absolute brightness means nothing; a correctly lit scene can come out black.
   Geometry presence, silhouettes and *differences* are reliable; the tonemapped
   look is not.

## Prove it is animating, not just imported

Set `animation_data.saved_position` to two values, capture each, and compare:

```powershell
(Get-FileHash pose_a.png).Hash -eq (Get-FileHash pose_b.png).Hash
```

Identical hashes means the clip is not posing the mesh. Different hashes, plus a
visibly different limb position, means it works.

## Clean up

Destroy the `TMP_Capture` actor when done — a stray SceneCapture in a level keeps
rendering every frame.
