# The prefab is a Blueprint actor (for this size), not a Level Instance

**Date:** 2026-11-15
**Status:** active

## The question

A user coming from Unity asks for the Unity feature: "I just put everything into a
prefab". Unreal has three answers and they are not interchangeable.

| Unreal | What it is | Wins when |
| --- | --- | --- |
| **Blueprint actor** | components on one actor | tens of pieces, edited by hand, needs per-instance tint or exposed knobs |
| **Level Instance** | a sub-level placed as one actor | hundreds of pieces, streaming, several teams editing the same block |
| **Packed Level Actor** | a Level Instance baked to one static actor | the block is finished and draw calls matter |

## The decision here

EpicJam2026's mission arena is 14 pieces (deck, skirt, fortress, six 38 m walls, the city
plate, four lights). A Blueprint actor: every component stays visible and editable in the
Blueprint viewport, one instance per level, and the lights travel with the geometry.

A Level Instance would be the answer at a few hundred pieces, or if the arena had to
stream. A Packed Level Actor would save draw calls but freezes the block - wrong while the
design is still moving.

## What stays in the LEVEL, not the Blueprint

Spawn points, PlayerStart and the ambient sounds. They are per-mission data; putting them
in a shared Blueprint would make every mission deploy the same bands in the same places.

## Preconditions that caught this once

A Blueprint rebuilt from script **deletes and recreates** the asset, which orphans every
placed instance (they render with defaults). Re-apply the instances after a rebuild, the
same rule that already applies to rebuilt materials.
