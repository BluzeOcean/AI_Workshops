# In a top-down arena the floor is the mood

**Date:** 2026-11-16
**Status:** active

## The observation

Three missions share one arena prefab (`BP_MissionEnv`): same deck, walls,
fortress, skyline. Giving Mission2 and Mission3 a different mood was done with
values only, and the first attempt failed in a specific way — it looked like "the
same map through a coloured filter" rather than a different place.

The reason is the camera. At pitch -32 deg, 9000 cm out, with a 6400 cm view width,
**the deck fills roughly 80% of the frame** and the horizon is never visible
(see `model-notes/2026-11-15-the-mission-camera-shows-no-horizon.md`). Meanwhile
the deck is metallic 0.55 with a top face the camera looks straight down at, so the
directional light's specular never comes back to the eye and its diffuse has almost
no facing ratio to work with. **The sun mostly does not touch the floor.**

## Consequence — the levers, in order of effect

1. **The SkyLight.** It is the ambient the floor actually receives, so its colour and
   intensity are the mood of the picture. Sky 2.8 white -> 2.25 `(0.36, 0.54, 1.00)`
   is what turned Mission2 blue; pulling it to 3.4 keeping it pale is what made the
   first inferno pass read as pale terracotta daylight.
2. **The floor's own albedo.** A `Tint` parameter multiplied into the plate's
   BaseColor and driven from a material instance per mission. This is the cheapest
   dial that is visible at all, and it needs no new material.
3. **The key light** — shape and shadow direction, not mood. Lowering it and swinging
   it to the other quadrant did more for "this is a different battlefield" than any
   colour change.
4. Grade, fog, sky scattering: finishing, in that order.

## Watch out

Making the floor *darker* to get "night" collides with unit readability: the roster's
enemy mechs are orange-red, and on a mid-red floor they camouflage. The inferno pass
that reads best keeps the **walls brighter than the floor** (they are the silhouette)
and lets the floor fall dark, instead of tinting everything warm.

## Also

`PostProcessVolume`/`PostProcessComponent` grading needs each setting's
`bOverride` flag; from Python they are `override_<setting>` bools. Sky colour for
the atmosphere has to come from `SkyAtmosphereComponent` (**not** the actor — the
actor exposes none of it): `rayleigh_scattering` (RGB coefficients) and
`rayleigh_scattering_scale` are the red/violet dials, and `ground_albedo` is an
`FColor` — passing a `LinearColor` raises.
