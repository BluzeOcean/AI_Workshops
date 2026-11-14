# A light SOURCE in the scene rakes the studio floor — describe lights as properties

**Date:** 2026-11-14
**Supersedes:** `2026-11-14-a-warm-rim-light-puts-a-pool-of-light-in-the-corner.md`

**Symptom:** the user's comparison of two renders — *"the one on the left created unnecessary
lighting on the ground reflection at the bottom left corner"* — was only **half** fixed by
removing the warm rim light and the floor bounce. The warmth went away (the corner went
from +33 warm to +0.7) but the corner stayed **bright**: still +22, then +14.8, then +15.7
levels above the rest of the floor after three successive rewrites of the lighting clause.

**Cause:** the first fix blamed the **colour** of the light. The real cause is the word
**source**. A light described as a thing *in the scene* gets a **position**, and a positioned
light rakes an infinite studio floor. Changing "warm golden rim light" to "crisp neutral
white rim light" keeps the light in the scene — only its colour changed — so it kept
spilling onto the floor.

The clause that finally worked stops describing a light at all:

> a bright thin edge highlight running down the left side of the machine

That is a **property of the machine**, not a source in the room. A property cannot spill.

**Fix:** three things together, and all three are needed.

| Lever | bottom-left excess vs the floor (worst of 3 seeds) |
|---|---|
| rim as a light source, lateral key | **+14.8 (FAIL)** |
| rim as a machine property (an edge highlight) | +10.4 |
| …plus a **layout box for the floor strip** | +9.0 |
| …plus the **stronger negative prompt** | **+5.7 (PASS)** |

1. The lighting clause describes the rim as an **edge highlight on the machine**.
2. Every studio recipe carries a **third layout box** for the floor strip (`y` 0.87–1.0),
   inserted between the backdrop box and the subject box, with the subject's
   `characterBoxes` shifting from `"2"` to `"3"`. The floor is a region of the frame that
   otherwise has no instruction of its own, and the layout is the strongest lever there is.
3. The house negative gains `vignette, corner glow, glow in the corner, hotspot on the
   floor, floor hotspot, bright lower corner, hot spot in the corner, uneven corner
   lighting, shadow gradient across the floor`.

The same final clause on three seeds measured **+2.1 / +5.7 / +1.6**. The original artifact
measured **+38 bright and +33 warm**.

**Applies when:** any studio-backdrop concept art, and any prompt that says where light
comes from. The general rule: **a light described as a source becomes a thing in the room
with a position, and it will paint that position onto every surface. Describe the effect on
the subject as a property of the subject.**

Two traps that cost the most time here:

- **One seed is not a result.** The spread between seeds is as large as the spread between
  wordings: the *same* clause measured +6.7 on one seed and +14.8 on another. A single-seed
  probe picked the **losing** wording; the winner only appeared when both candidates were
  re-rendered on all three seeds. Always re-render a candidate on a seed that **already
  failed**, or you cannot tell a fix from a lucky seed.
- **Rewording the lighting sentence has a floor of its own.** Three different ways of
  describing the floor ("one uniform matte neutral grey", "identical from edge to edge",
  "one continuous flat matte grey lit by a single even frontal source") all landed within
  0.3 units of the same number. When the wording stops moving the number, the wording is
  exhausted — change a different lever (the layout, the negative), not the sentence again.
