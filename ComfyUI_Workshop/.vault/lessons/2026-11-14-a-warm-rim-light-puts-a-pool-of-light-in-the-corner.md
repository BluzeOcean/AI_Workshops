# A warm rim light and a floor bounce put a pool of light in the corner

**SUPERSEDED (2026-11-14) by `2026-11-14-a-light-source-in-the-scene-rakes-the-studio-floor.md`.**
The fix below removed the *warmth* but not the *bright* corner: it changed the colour of the
rim light while leaving it a light SOURCE in the scene, and a positioned light still rakes
the studio floor. The clause quoted in step 1 is **not** the house style any more. Kept as
the record of what was true then.

**Date:** 2026-11-14
**Symptom:** the user compared two renders of the same machine side by side and said the
background should look like the right one, not the left one: *"the one on the left created
unnecessary lighting on the ground reflection at the bottom left corner."* The left
render's floor had a warm orange patch in its bottom-left corner, brighter than the rest
of the floor, with the backdrop's left side warm too. The right render's floor was evenly
lit and neutral everywhere.

**Cause:** two phrases in the house style, present in **every** text-to-image concept
recipe from round 01 onward:

> a warm golden rim light running down the left edge of the silhouette
> soft bounced light from the grey floor

A **warm** light from the left, plus a light **bouncing off the floor**, gives the model
permission to place a light source low and to the left — and it painted the corner of the
floor with it. It was not a reflection of anything; there was nothing there to reflect.

Measured on the r04_02 reference (`tools/check-studio-backdrop.py`): the bottom-left corner
was **33 units warmer and 38 units brighter** than the rest of the floor. On the edit-path
renders of the same machine the floor is even to within **1 unit** — the edit path
re-renders the backdrop, so it never inherited the pool.

The text-to-image rounds also ran with an **empty negative prompt**: every prohibition
lived inline in the positive style suffix, where it is a suggestion rather than a
constraint.

**Fix:**

1. The house lighting clause is now *"a crisp neutral white rim light along the left edge
   of the silhouette, lit from high above and behind, flat even studio lighting across the
   whole floor, the floor the same neutral grey all the way to every edge of the frame,
   with no pool of light, no bright corner and no reflection"*, and the backdrop
   description says *"evenly lit across the whole frame with no pool of light and no
   bright corner"*. Applied to all nine studio recipes.
2. Every concept recipe now carries a `negative` field naming the lighting artifacts.
   Use `mirror reflection on the floor`, not a bare `reflection` — the floor is supposed to
   keep its soft contact shadow.
3. `tools/check-studio-backdrop.py` measures the floor's bottom corners against the rest
   of the floor and exits 1 on a pool. Run it on **every** render, not every other round.

**Applies when:** any studio-backdrop concept art, and any prompt that describes where
light comes from. A light described as *warm*, or as *bouncing off the floor*, is an
invitation to put a visible source on the floor — and a visible light source on a seamless
backdrop is an artifact, because there is nothing in the scene for it to be.
