# Round 07 — FIVE war hounds, one design line, five colourways

**Date:** 2026-11-14
**Status:** KEPT by the user, but rejected as "the sample" — see the verdict below
**Verdict (user, 2026-11-14):** *"Negative. They do not look like the sample that I asked
for. This generation, although it looks good, but it has four legs, which is not humanoid
form. However, I decided to keep it, but I need you to generate next round with the proper
instruction that gives proper Variations results of a humanoid form of the R04_02."*

**Kept** — the set is good-looking and stays in the destination. But it failed the brief in
one specific way, and the cause is now known: **it used round 06's `styleSuffix`, not round
04's.** So it inherited round 06's bone-white/olive hardsuit language and rounded
pauldrons instead of r04_02's brutalist rust-orange slabs — the silhouette was copied, the
art language was not. See
`.vault/lessons/2026-11-14-reuse-the-style-suffix-not-just-the-silhouette.md` and the
corrected round in `.vault/recipes/moss-mech-r08-what-worked.md`.

The parts of this round that the user **did** keep — weapons named by their parts, the
defined pauldron assembly, the shared livery structure — were carried into round 08
unchanged.
**What was run:** Round 07 of the EpicJam2026 concept set — five images, one submission.

```
node tools\build-moss-set.mjs --recipe .vault\recipes\moss-mech-r07-set.json --out work\moss-mech-r07.json
node D:\ComfyUI\harness\comfyctl.mjs submit work\moss-mech-r07.json
```

- Same model stack, 960×1280, 8 steps, cfg 2.5, `er_sde` / `simple`
- **Random 48-bit seeds**, drawn once and baked into the recipe: 125580903071841,
  202968268179908, 249696271772951, 120112622051732, 226441422958938
- Destination: `V:\04_Projects\EpicJam2026\MechConcept Art`
- `_contact_sheet_r07.png` written alongside the images

**The brief, in the user's words:**

> "use r04_02 to draw another round of 5 of the same variation. Particularly fix the right
> arm weapon it is holding, currently it looks very ambiguous and not sure what it is
> holding. However the silhouette of the unit is good looking but I need different color
> variations and a more defined parts on the shoulder because there are just random spike
> sticking out."

## What was kept and what was changed

**Kept — r04_02's silhouette.** The quadrupedal war hound: long armoured spine carried
low and horizontal on four digitigrade legs, sloped head with a wide visor band and cheek
tusk spurs, weapon pods along the spine, exposed cabling and hydraulics along the flanks.
The user called this silhouette good, so it is the basis of the whole round.

**Fixed — the right-arm weapon.** `r04_02` had "one long blade arm", which rendered as an
unidentifiable slab. Each of the five now carries a **named weapon described by its
parts**, so it reads unambiguously:

| Unit | Colourway | Right-arm weapon |
|---|---|---|
| `01_ember_stalker` | rust orange / near-black / brass | rotary cannon — six short barrels around a central spindle, boxy breech, slotted muzzle shroud |
| `02_dune_stalker` | desert sand / olive drab / amber | long recoilless gun — boxy breech, ribbed heat jacket, slotted muzzle brake |
| `03_slate_stalker` | gunmetal blue-grey / black / hazard orange | twin-barrel gun — two thick parallel barrels, blocky breech, squared muzzle plate |
| `04_bone_stalker` | bone white / charcoal / crimson | boxy missile pod — rectangular launch face filled with square cells, raised sight rail |
| `05_moss_stalker` | moss green / dark grey / pale sand | heavy machine gun — thick barrel, round drum magazine, boxy receiver, squared shoulder mount |

**Fixed — the shoulders.** "Angular armour blades sweeping back over the shoulders" produced
spikes. They are now a defined assembly on every unit: *"square bevelled shoulder pauldrons,
each built from two stacked plates with a recessed circular housing on the outer face and a
raised ridge running along the top edge, and a hard shoulder cap over the joint"*. The
result is a bevelled pauldron with a visible round housing — no spikes anywhere.

**Added — colour variation.** This is the one place the round-06 style lock was deliberately
relaxed, because the user asked for it. The lock is on the **art style**, the **construction
language**, the **camera** and the **lighting** — all still shared in the `styleSuffix`. The
**livery structure** is shared too: one dominant colour over one dark structural colour
with one worn accent, plus the same chevron hazard stripes. Only the **hues** vary per
unit. That keeps the set reading as one production line while giving five distinct
colourways — which is exactly what was asked for.

**Pose.** Relaxed standing, weight even on all four legs, body level, head raised — the
house rule from round 06.

## Reuse when

a variant line or colourway sheet is needed on a design the user has already approved.
Take the approved silhouette verbatim, lock the construction language and camera in the
shared suffix, vary only the hues per concept, and describe every weapon and part by its
parts rather than by its label.

**Related:** `.vault/lessons/2026-11-14-describe-parts-not-labels.md` ·
`.vault/lessons/2026-11-14-concept-art-wants-a-relaxed-standing-pose.md`

## Open

Awaiting user review. Nothing has been published, uploaded or disposed — the five PNGs and
the contact sheet are staged in the destination.
