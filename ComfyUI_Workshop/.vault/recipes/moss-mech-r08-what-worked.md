# Round 08 — FIVE humanoid war mechs, the humanoid form of r04_02

**Date:** 2026-11-14
**Status:** active — rendered, staged for user review
**What was run:** Round 08 of the EpicJam2026 concept set — five images, one submission.

```
node tools\build-moss-set.mjs --recipe .vault\recipes\moss-mech-r08-set.json --out work\moss-mech-r08.json
node D:\ComfyUI\harness\comfyctl.mjs submit work\moss-mech-r08.json
```

- Same model stack, 960×1280, 8 steps, cfg 2.5, `er_sde` / `simple`
- **Random 48-bit seeds**, drawn once and baked into the recipe: 87805808400093,
  131728732499524, 69998610228624, 148191086857483, 70997266477268
- Destination: `V:\04_Projects\EpicJam2026\MechConcept Art`
- `_contact_sheet_r08.png` written alongside the images

**The brief, in the user's words:**

> "Negative. They do not look like the sample that I asked for. This generation, although it
> looks good, but it has four legs, which is not humanoid form. However, I decided to keep it,
> but I need you to generate next round with the proper instruction that gives proper
> Variations results of a humanoid form of the R04_02"

## The correction

Round 07 reused r04_02's **silhouette** but round **06's** `styleSuffix`, so it inherited
round 06's bone-white/olive hardsuit language and rounded pauldrons instead of r04_02's
brutalist rust-orange slabs. Round 08 takes **round 04's `styleSuffix` essentially
verbatim** — massive armoured slabs, thick structural ribs, visible rivets and weld seams,
exposed hydraulic actuators and cable looms, scorched and battle-damaged with soot streaks,
chipped paint showing bare steel, scorch marks and paint burns, grit caked into the lower
legs, chevron hazard stripes — and adds only what the round changes.

**Verified before rendering**, by shared 6-word shingles against both candidate sources:

| Compared with | shared shingles | overlap |
|---|---|---|
| **R04** (the intended basis) | 196 / 211 | **92.9 %** |
| R06 (the wrong one used in R07) | 107 / 318 | 33.6 % |

## The roster — five builds of one design house

| Unit | Build | Right-arm weapon |
|---|---|---|
| `01_bulwark` | heavy and wide, tower shield + rifle | heavy short rifle |
| `02_stalker` | lean, forward-leaning, long digitigrade legs | heavy machine gun, drum magazine |
| `03_marksman` | very tall and thin | long recoilless gun, ribbed heat jacket, muzzle brake |
| `04_juggernaut` | squat, deep torso, enormous pauldrons | rotary cannon, six barrels round a spindle |
| `05_carrier` | broad shoulders, missile racks across the back | twin-barrel gun |

All five humanoid — two legs, two arms, low wide visor head with cheek tusk spurs — and all
in the r04_02 art language. The palette stays inside r04_02's own rust-and-charcoal family
(rust orange, burnt sienna, scorched iron, dark ember, gunmetal), so the set reads as one
production line rather than five films.

**Carried over from the parts of round 07 that the user kept:** weapons named and described
by their parts, the defined pauldron assembly (no random spikes), and the shared livery
structure.

## Reuse when

a round is briefed as a variation of an earlier one. Copy that earlier round's `styleSuffix`
verbatim, verify the overlap against the intended source with shingle counting before
rendering, and vary the build rather than the hue if the brief says "variations".

**Related:** `.vault/lessons/2026-11-14-reuse-the-style-suffix-not-just-the-silhouette.md` ·
`.vault/lessons/2026-11-14-describe-parts-not-labels.md` ·
`.vault/lessons/2026-11-14-concept-art-wants-a-relaxed-standing-pose.md`

## Open

Awaiting user review. Nothing has been published, uploaded or disposed — the five PNGs and
the contact sheet are staged in the destination. Rounds 01, 02, 04, 06 and 07 remain in
place; the user kept round 07.
