# A translucent decal lands on a STENCIL, not on a material

**Date:** 2026-11-15
**Status:** active

## Symptom

Mission1's destination ring (the green ring and barbed wedge at the end of a drawn
move order) stopped drawing after the arena floor was replaced. The band footprint
decals kept drawing on the same floor, so 'decals do not work' was never true.

## The mechanism, from Tools/apply_decal_layers.py

Three decal mechanisms exist and they answer different questions:

| Mechanism | Applies to |
| --- | --- |
| UMaterial::MaterialDecalResponse | deferred decals |
| UPrimitiveComponent::bReceivesDecals | per object |
| **custom-depth stencil** | **translucent decals** - which IGNORE both of the above |

The ground writes `RenderCustomDepth = true` and `CustomDepthStencilValue = 1`; the
translucent decal materials test that stencil per pixel. A surface without it draws
nothing, no matter what its material says.

## Why a replacement floor loses it

The classifier is by ACTOR LABEL (`Ground`, `Floor`, `Terrain`, `Arena`). The new floor
was a component named Deck inside `BP_MissionEnv` - an actor whose label is not a ground
name - so it was classified as scenery: no stencil, and (on a re-run) MDR_NONE as well.

**A component can be ground inside an actor that is not.** Classify the component, or the
first floor that is not its own actor silently stops receiving orders.

## The fix

On the Deck component: `set_render_custom_depth(True)` and
`set_custom_depth_stencil_value(1)` - in the Blueprint AND in the placed instances. The
Blueprint template alone is not enough: instances placed before the change keep their own
serialised component state and must be set again (read the value back on the instance, do
not trust the template).

`apply_decal_layers.py` now treats a component named Deck as ground, so re-running it
cannot take the stencil away.

## The cost of not knowing it

Hours spent suspecting the deck material, the decal material, the blend mode and the
receiver's decal response - every one of which matched the working case. The one property
that differed was one nobody had looked at, because it is not on the material at all.