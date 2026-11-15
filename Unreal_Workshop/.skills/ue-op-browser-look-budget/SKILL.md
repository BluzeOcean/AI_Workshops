---
name: ue-op-browser-look-budget
description: Make AI-generated characters read correctly under a web/Wasm budget - metallic from the measured map, ambient instead of lights, blob shadows instead of real ones.
---

# Look, on a web budget

## Metallic must come from the map, not a guess

Sample the delivered metallic map. AI-generated characters commonly average
**~0.01** — genuinely dielectric. Setting metallic to 0.25 because the asset
"looks like metal" makes armour go dark, because a metal with nothing to reflect
renders black.

Same for roughness: read the map, or use its mean as the constant.

## Ambient is cheaper than lights

One `SkyLight` beats a rack of fill lights — a cubemap lookup, no shadow map, no
per-light loop, and it lights every surface regardless of which way it faces.

**Check it is actually contributing.** `real_time_capture = False` with
`cubemap = None` is a silent blackout: the light exists, the scene gets nothing,
and the character looks muddy for no visible reason. Also set
`lower_hemisphere_is_black = False` unless you want no bounce from below.

## A floor for the darks

`Emissive = BaseColor * ~0.1` stops shadowed panels crushing to black. It costs an
add in the pixel shader, lifts proportionally so colour separation survives, and
is the cheap stand-in for a baked irradiance map.

Tune between ~0.08 (subtle) and ~0.18 (soft). If armour goes flat and grey, it is
too high.

## Shadows: skip them

Real-time shadows are expensive on a browser target and give harsh contact
shading on hard-surface armour.

- `cast_shadow = False` on the skeletal mesh components
- one unlit + translucent radial-gradient plane per unit as a blob shadow
- keep the blob **unlit** so its darkness does not change with exposure

## Keep the comparison honest

If you are comparing several mesh variants, put them on the **same material
model**. Otherwise you are measuring shading models rather than geometry — the
comparison tells you nothing about the meshes.

Verify the result with
[ue-op-offscreen-verify](../ue-op-offscreen-verify/SKILL.md), remembering that its
exposure is fixed and only relative comparisons are meaningful.
