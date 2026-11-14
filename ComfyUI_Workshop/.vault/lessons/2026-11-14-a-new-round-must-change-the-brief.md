# A new round that looks like the old one is a PROBLEM-DESIGN failure, not a seed failure

> **SUPERSEDED IN PART (2026-11-14).** This lesson recommends changing the *machine family*
> as one of four axes. Following that literally in round 03 changed the **category** — the
> machines came out as forklifts and excavators and the user rejected the round. The machine
> family may change *within* the mech / war machine / robot category; the category itself is
> fixed, and so is the backdrop. Read
> [`2026-11-14-different-is-not-a-different-category.md`](2026-11-14-different-is-not-a-different-category.md)
> before acting on the axes list below.

**Date:** 2026-11-14
**Symptom:** round 02 of the mech concept set came back and it looked like round 01. Same
machines, same silhouettes, same studio backdrop, same camera — only the added rune
decoration differed. The user's reaction: *"round 2 kinda just a similar variation of round
1"*.

**Cause:** the **prompt** was the constant, not the seed. Round 02 reused round 01's concept
descriptions verbatim and added one clause. The model was asked to draw the same thing with
one more feature, so it drew the same thing with one more feature. Different seeds change
the noise; they do not change the subject.

**Fix — change the art direction, not a decoration.** Four axes, each of which alone does
most of the work:

1. **Machine family.** Different locomotion entirely (hexapod / tracks / quadruped / wheels /
   mast / static), not a variant of the same chassis.
2. **Setting.** Move out of the studio void into a real environment — a dim hangar bay with
   steel wall panels, columns receding, an overhead light pool, wet concrete and haze. This
   was the **single biggest lever** of the four.
3. **Finish.** Weathered working machinery (chipped enamel over a bare steel frame, exposed
   hydraulics, grime in the recesses) is a different *design language*, not a different paint
   job.
4. **Camera.** Vary the angle per concept — low 3/4, straight-on, side profile, 3/4 rear.
   A set where every shot is the same hero 3/4 reads as one design repeated.

Also: mix **static and mobile** machines in one set. A forklift, a pylon and a cargo sled
next to a hexapod read as an equipment roster; ten variants of one archetype read as a
colour scheme.

**Random seeds are still right** — draw them fresh per round, from a real RNG, and bake them
into the recipe so the set stays reproducible. Just do not expect them to do the work of a
new brief.

**Applies when:** a task asks for "another set", a variation round, a second pass, or
anything that should look different from what came before.

**Companion lesson:** the shared `promptPrefix` is a lever too — *"A concept-art study of"*
vs *"A single full-body hero concept-art portrait of"* changes how the model reads the whole
brief. Round 03 was the first set to change it.
