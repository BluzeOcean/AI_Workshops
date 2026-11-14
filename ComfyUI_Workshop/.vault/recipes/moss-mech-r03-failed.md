# Round 03 — FAILED. It left the mech category and became vehicles.

**Date:** 2026-11-14
**Status:** failed — superseded by round 04
**What was run:** Round 03 of the EpicJam2026 concept set — an industrial / utility chassis
set (hexapod, tracked breacher, forklift, excavator, tunnel cutter, pressor, sensor mast,
sentry pylon, cargo sled) in a dim hangar bay.

**Result:** the set looked nothing like rounds 01–02, and that was the problem. The machines
came out as **forklifts, an excavator, a tunnel boring machine and a flatbed** — civilian
vehicles and plant equipment, not mechs. The user's verdict: *"round 3 is a Failure. They
are not Mac robot machine that I asked for they turn into just vehicles."*

The ten images were disposed of. The recipe is kept, marked failed, because the failure is
worth being able to read.

> This file replaces `moss-mech-r03-what-worked.md`, which described round 03 as a success.
> That was wrong and would have misled the next agent. The original text is still readable
> in git at commit `04084dd`.

## The mistake, precisely

**"Looks completely different" was read as "a different category".** The user asked for a
round that looked completely different — *within* the mech / war machine / robot category.
I changed the machine family instead of the look, and swapping "heroic humanoid battle
mech" for "industrial utility chassis" swapped the subject matter outright.

The earlier lesson in this vault (`2026-11-14-a-new-round-must-change-the-brief.md`) is
partly to blame: it recommended changing the "machine family" as one of four axes, and
following that advice literally produced vehicles. **The machine family is not a free axis.**
It is the brief.

## What the round did get right, and is still worth keeping

- **Random 48-bit seeds** drawn from a crypto RNG and baked into the recipe. Still correct
  practice for exploration.
- **The setting as a lever.** Swapping the studio void for a real environment (a hangar bay
  with light pools, haze and wet floor) gave depth and atmosphere that the studio backdrop
  could not. Round 04 keeps that idea but moves it to a ruined city at dusk.
- **The recipe layer structure** — `promptPrefix + concept + runes + runeStyle +
  styleSuffix` — is now a documented convention (see `.skills/comfyui-generate`).

## What round 04 does instead

Same "completely different" ambition, **same category**. Round 04 stays inside
mech / war machine / robot and changes the look by changing the design language:

| Axis | Rounds 01–02 | Round 04 |
|---|---|---|
| Category | mech / war machine | **unchanged — mech / war machine** |
| Design language | Sleek, slender, satin, elegant panels | **Brutalist siege walkers — slab armour, structural ribs, rivets, weld seams, exposed hydraulics** |
| Setting | Seamless studio void | Ruined city at dusk — rubble, smoke haze, low orange sun |
| Finish | Clean hero surface | Battle-damaged, scorched, soot-streaked, chipped to bare steel |
| Camera | One hero 3/4 | Varied, and **low angles looking up** at the mass |

Every concept in round 04 is anchored as a war machine in the prompt itself: *"a bipedal war
machine with a recessed cockpit, articulated arms and legs and heavy mounted weapon
systems"*, plus a named weapon system per machine. That is the guard that round 03 lacked.

**Reuse when:** reading round 03 as a failure, not as a recipe.
