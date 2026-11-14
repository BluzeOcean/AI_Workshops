# Round 05 — FAILED: the style lock worked, the subject form was wrong

**Date:** 2026-11-14
**Status:** FAILED — all five images disposed
**What was run:** Round 05 of the EpicJam2026 concept set — five images, one submission.

```
node tools\build-moss-set.mjs --recipe .vault\recipes\moss-mech-r05-set.json --out work\moss-mech-r05.json
node D:\ComfyUI\harness\comfyctl.mjs submit work\moss-mech-r05.json
```

- Same model stack, 960×1280, 8 steps, cfg 2.5, `er_sde` / `simple`
- **Random 48-bit seeds**, drawn once and baked into the recipe: 116467011754715,
  16298161626860, 35535740640047, 82893580031279, 231259710097532
- Destination: `V:\04_Projects\EpicJam2026\MechConcept Art`
- All five PNGs moved to trash via `mavis-trash` (recoverable). The recipe is retained as a
  marked failure record.

**Verdict:** *"negative, i need humanoid mech, this current round is useless to me, dispose it."*

---

## What worked — keep this

**The style lock is real and it works.** The complaint behind round 05 was that round 04's
machines looked like they came from five different films. The fix was to move the livery,
materials, construction vocabulary, camera and lighting **out of every concept sentence**
and into the shared `styleSuffix` alone, leaving each concept to describe only archetype,
pose and weapon.

The result was the most cohesive set so far: five visibly different machines that
unambiguously share one palette (matte gunmetal plates, charcoal underframe, one signal-amber
accent strip, bone-white ceramic panels), one construction vocabulary, one camera (three-
quarter front from the left, 50mm), one light rig and one backdrop. They read as five units
off one production line — which is exactly the goal.

**Reuse when:** any set that has come back looking like several different franchises. Audit
the built graph before rendering: no concept sentence may contain a colour, a material or a
weathering word. A quick grep over the generated prompt catches it.

## What failed — do not repeat

**The subject form.** All five concepts were non-humanoid (quadruped hunter, hexapod
artillery, tripod sentinel, heavy ram, segmented crawler) because round 04's verdict had been
misread as "ban the upright bipedal form".

It was not. The user **wants humanoid mechs** — rounds 01–02 were humanoid and were
accepted. Round 04's rejects were repeats of round-01 *archetypes*, not repeats of the
humanoid *form*. By over-correcting, round 05 lost the thing the user actually wants.

Also worth noting: locking the style so hard pulled the five silhouettes toward each other.
Three of the five came back as the same flat-topped four-legged body. **Style cohesion and
silhouette variety pull against each other** — the shared construction vocabulary needs a
counterweight in the archetype wording, not a shared body.

## The real lesson

`../lessons/2026-11-14-similar-means-repeating-an-archetype.md` — "similar to previous
rounds" means the **archetype** repeated, not the body plan. Keep the humanoid form; keep a
roster of used archetypes and never repeat one.
