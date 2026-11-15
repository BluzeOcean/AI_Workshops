---
name: ue-op-tripo-triage-asset
description: Decide which half of a Tripo/AI hi-lo delivery is the game asset, and whether a bake is needed - by measuring, not assuming.
---

# Triage an AI character delivery

## Measure first

Tripo-class output is **all game-res**. "High poly" is a label, not a fact:

| shipped as | typical reality |
|---|---|
| high poly, rigged | ~10k tris, often 60+ separate objects, sometimes one 4K basecolour and no normal/rough/metallic |
| low poly | ~6k tris, one object, usually carries the **full PBR set** |

Get the numbers before planning anything: triangle count, object count, material
count, UV range, and which textures each mesh references.

## Which mesh is the game asset

Pick the one carrying the better texture set — frequently the **low** poly, even
though it has no rig:

- one object means one draw call
- basecolour + normal + roughness + metallic beats basecolour alone
- a rig can be transferred or authored; missing maps cannot

Do **not** assume the "high poly" is a bake source. A 1.7x triangle gap means
there is no sculpt detail to bake; baking the softer "high" onto the crisper low
usually makes it worse.

## Are they even the same design

Two sessions can produce two names (`S01-Grunt`, `S02-highpoly`). Check before
planning a weight transfer:

- compare world-space bounding boxes — within ~2% on every axis is a good sign
- if unsure, compare silhouettes from front/side/top; IoU above ~0.85 is the same
  character

## Clean up before importing

- Delete stray exported objects (`Icosphere` and friends).
- Collapse per-part materials where the delivery uses one material per part —
  dozens of materials is dozens of draw calls for no visual gain.
- Note the scale. AI exports are frequently ~1 m tall; decide the intended world
  height and fix it at the source, not in UE.

## Output of this step

A one-line verdict: *"game mesh = X (n tris, m materials), rig donor = Y, no bake
needed, target height Z m."* Everything downstream depends on it.
