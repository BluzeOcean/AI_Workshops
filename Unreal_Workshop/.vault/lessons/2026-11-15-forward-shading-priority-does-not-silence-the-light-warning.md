# ForwardShadingPriority does not silence the competing-directional-light warning

**Date:** 2026-11-15
**Status:** active

## Symptom

Three directional lights in one Blueprint (a key plus two fills, one per wall run).
In play the screen fills with:

    Multiple directional lights are competing to be the single one used for forward
    shading, translucent, water or volumetric fog. Please adjust their
    ForwardShadingPriority. As a fallback, the main directional light will be selected
    based on overall brightness.

## What was tried and did not work

`ForwardShadingPriority = 1` on the key and `0` on the two fills. The values are
definitely on the components - read back from the placed instances in all three maps -
and a fresh PIE still draws the message. Whatever the engine is comparing, unique
priorities are not the whole rule in this build.

## What did work

**One directional light.** The two fills existed to light the two walls' inward faces,
which face each other, so one sun always leaves one back-facing and black. A SkyLight
does that job with no competition: it is cubemap ambient sampled by each surface normal,
so it lifts both faces at once. SkyLight intensity 0.95 -> 2.8 took over the fills' share
and the warning is gone.

## The trade

Ambient is flatter than two directional fills: the walls read, but the shading is less
directional. If the flatness becomes a problem, the next step is RectLights along each
wall - not a second sun, which brings the warning back.

## Cost of getting here

Two rebuild-and-restamp cycles, each of which orphans the placed instances (a rebuilt
Blueprint is a deleted-and-recreated asset). Re-stamp the maps after every rebuild, and
check the stamp landed - one run silently failed on the first map and left it with no
arena at all.