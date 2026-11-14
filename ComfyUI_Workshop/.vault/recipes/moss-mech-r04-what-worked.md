# Round 04 — FIVE war mechs, brutalist and battle-worn, on the house studio backdrop

**Date:** 2026-11-14
**Status:** REJECTED except `r04_02` — see the verdict below
**What was run:** Round 04 of the EpicJam2026 concept set — **five** images (the user
reduced the round from 10 to 5).

```
node tools\build-moss-set.mjs --recipe .vault\recipes\moss-mech-r04-set.json --out work\moss-mech-r04.json
node D:\ComfyUI\harness\comfyctl.mjs submit work\moss-mech-r04.json
```

- Same model stack, 960×1280, 8 steps, cfg 2.5, `er_sde` / `simple`
- **Random 48-bit seeds**, drawn once and baked into the recipe: 168361823897167,
  417731753208543, 10392791762705, 437066953913735, 187313772924710
- Destination: `V:\04_Projects\EpicJam2026\MechConcept Art`

**Result:** five war machines on the seamless silver-grey studio backdrop, in a design
language that shares nothing with rounds 01–02. **The user kept only one of the five.**

### VERDICT (2026-11-14, user)

> *"only the r04_02 pass, the other mech in this gen are either too generic/similar to
> previous rounds, or illogical because mech wearing cape or clothes is not the direction
> that I want (e.g. r04_03)"*

| Concept | Verdict | Why |
|---|---|---|
| `r04_02` hound tracker | **PASS** | Low, wide, horizontal quadruped. A specific machine with a specific job. |
| `r04_01` bastion titan | reject | Upright bipedal humanoid — the stock mech silhouette, and close to round 01's own lineup. |
| `r04_04` vanguard colossus | reject | Upright bipedal humanoid — same stock silhouette. |
| `r04_05` wraith lancer | reject | Upright bipedal humanoid, and spindly like rounds 01–02. |
| `r04_03` shroud reaver | reject | Draped shroud plates read as a mech *wearing a cloak*. Illogical. |

**What this teaches:**

1. **The brutalist slab language was not the problem** — the hound used it and passed. The
   three rejects repeated **archetypes round 01 had already made** (a second titan, a second
   shielded vanguard, a second lancer), not a body plan.
2. **The user wants humanoid mechs.** The hound was not kept *because* it was a quadruped;
   it was kept because a quadrupedal war hound was a **class that had not been made yet**.
   Round 05 over-corrected this into a non-humanoid set and was rejected.
3. **Fabric on a machine reads as a costume.** Never write cloak / shroud / robe / rags.
4. The **camera variety** and the **studio backdrop** were both fine. Keep them.

See `../lessons/2026-11-14-similar-means-repeating-an-archetype.md` and
`../lessons/2026-11-14-never-dress-a-mech.md`.

| | Rounds 01–02 | Round 04 |
|---|---|---|
| Category | mech / war machine | **unchanged** |
| Design language | Slender, satin, elegant panels | **Brutalist slab armour, structural ribs, rivets, weld seams, exposed hydraulics** |
| Finish | Clean hero surface | Battle-damaged, scorched, soot-streaked, chipped to bare steel |
| Camera | One hero 3/4 | Varied, and **low angles looking up** at the mass |
| Backdrop | Seamless silver-grey studio | **unchanged — the same studio backdrop** |

---

## What fixed it

**Anchor the category in the prompt itself, in the shared prefix.** Round 04's prefix is:

> "A full-body concept-art portrait of a towering armoured battle mech, **a bipedal war
> machine with a recessed cockpit, articulated arms and legs and heavy mounted weapon
> systems**, "

Round 03 had no such anchor, so nothing stopped the model drifting toward plant equipment.
Round 04 also names a **specific weapon system per machine** — shoulder cannons, a tower
shield, a lance, spine missile racks. "It is a mech" plus "here is exactly what it carries"
is what closed the gap.

**Keep the backdrop.** The studio backdrop does not just look cleaner — it *removes the
model's excuse*. A hangar or a ruined street gives the model permission to build a machine
that belongs to that place; the studio asks for a design, and the design has to carry the
war-machine read by itself.

**Change the design language instead of the subject.** "Brutalist heavy war machine design:
massive armoured slabs and thick structural ribs, visible rivets and weld seams, exposed
hydraulic actuators and cable looms, armour scorched and battle-damaged" is a different
*language* applied to the same category — and it is enough to make the set read as
completely different from rounds 01–02.

## One wasted pass (kept for the record)

The first round-04 attempt used the **ruined-city-at-dusk backdrop** and produced five
excellent war mechs — the category anchors worked immediately. Those five were then
disposed of because the user does not want a background on character concept art. The
second attempt, same machines and same seeds, studio backdrop, is the keeper.

Useful data point: **the subject and the backdrop can be fixed independently.** The
machines were right in both passes; only the staging changed.

**Reuse when:** the next round, or any task that must stay in the mech category while
looking nothing like the last one.
