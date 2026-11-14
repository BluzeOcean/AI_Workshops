# Round 06 — FIVE humanoid war mechs, R02's roster as field-worn military hardsuits

**Date:** 2026-11-14
**Status:** active — rendered, staged for user review
**What was run:** Round 06 of the EpicJam2026 concept set — five images, one submission.

```
node tools\build-moss-set.mjs --recipe .vault\recipes\moss-mech-r06-set.json --out work\moss-mech-r06.json
node D:\ComfyUI\harness\comfyctl.mjs submit work\moss-mech-r06.json
```

- Same model stack, 960×1280, 8 steps, cfg 2.5, `er_sde` / `simple`
- **Random 48-bit seeds**, drawn once and baked into the recipe: 113868691105654,
  124919031846948, 42627144287711, 12269784593990, 278469611900304
- Destination: `V:\04_Projects\EpicJam2026\MechConcept Art`
- `_contact_sheet_r06.png` written alongside the images

### Redraw

Four of the five images were replaced after the first pass, at the user's request:

- **`01_recon_sniper`** — the rifle grew a stray thin rod from the barrel down to the
  floor. Fixed by shouldering the rifle and pointing it forward: *"one arm shouldering a
  long sniper rifle held high and pointing forward past the body, a compact scope mounted
  on a short top rail above the barrel"*. The rod is gone.
- **`02_bunker_bulwark`** — the shield was on the wrong arm. Fixed by naming the sides
  explicitly: *"its left arm carrying a towering slab shield that reaches above the head,
  its right hand holding a heavy short rifle at the low ready"*. The model followed
  literally, so the shield is now the machine's left arm and the rifle its right hand.
- **`03_plasma_duelist`** — took **three** draws. The first leaned forward with the saber
  drooping across the legs (*"it has the wrong pose"*); the second was a coiled fighting
  stance with the saber swept up in a rising guard (*"the sword is blocking the view. For
  concept art, i prefer a more relaxed standing pose like the others"*). The keeper is the
  third: *"a relaxed upright standing pose with the weight even on both legs, feet planted
  slightly apart, the body held square and tall, both arms lowered at the sides"* and the
  saber *"hanging straight down at its side, the blade running parallel to the leg and
  clear of the body"*.

Every redraw was disposed and re-rendered with a **fresh random seed** from a carved
reduced-concept recipe that copied `styleSuffix` / `backdropDesc` / `prefix`
**byte-identically** from the round recipe, so the redrawn images match the keepers
exactly. Procedure:
`.vault/lessons/2026-11-14-redraw-part-of-a-round.md`. Pose rule:
`.vault/lessons/2026-11-14-concept-art-wants-a-relaxed-standing-pose.md`.

**The brief came from the user, in their own words:**

> "sci fi, humanoid form, mech, no drone, no hound like four leg mech, no spider mech. two
> legs, two arms, can use rifle, shield, plasma sword/saber, missle. no crossbow, flamer,
> brawler. R02 set looks better than R01, so if you have to choose, pick from r02. and i
> like the r04_02 style too. r04_04 is fine. r02_01 is fine but wrong weapon (if it is slim
> body size, then the weapon should be a sniper rifle)."

## The roster

| # | Class | Source | Weapon | Accent |
|---|---|---|---|---|
| 01 | `recon_sniper` | R02 `01_scout_skirmisher` | long sniper rifle | amber |
| 02 | `bunker_bulwark` | `r04_04` (shielded assault walker) | tower shield + heavy rifle | crimson |
| 03 | `plasma_duelist` | R02 `07_demon_duelist` | curved plasma saber + piston fist | crimson + teal emitter |
| 04 | `missile_artillery` | R02 `02_lance_artillery` | shoulder box missile bank | amber |
| 05 | `wing_striker` | R02 `05_harrier_striker` | wing-root missile rack + rifle | crimson |

Every machine is humanoid — two legs, two arms, a head — and every weapon is from the
user's list. `01_recon_sniper` is the user's own correction: R02's `01_scout_skirmisher`
had a blade arm on a slim body, and they said a slim body should carry a sniper rifle.

## What made it work

**One locked production line.** Every machine is matte hardened bone-white composite with
sand-olive drab panels over a near-black frame, chunky exposed hardsuit joints, the same
angular sensor-head family, the same uniform wear (chalky dust on upward faces, chipped
edges, grime in the recesses), the same three-quarter-front-from-the-left camera, the same
light rig, the same backdrop, and the same etched rune layer. **All of that lives in the
shared `styleSuffix`** — the per-concept sentences carry archetype, weapon, pose and one
accent colour, and nothing else.

**R02's silhouettes, r04_02's honesty.** R02's tapered hero-mecha shapes and rune layer
were the accepted base; r04_02's matte, dusty, used-not-gloss finish is what stops the set
reading as showroom renders. The two together are the "military hardsuit" the brief asked
for, and they sit visibly inside R02's world rather than beside it.

**Tall subject boxes.** All five use tall boxes (w:h 0.57–0.81), which is what produces an
upright humanoid body. Round 04's wide box produced the one quadruped that passed; round
05's wide boxes produced the all-quadruped set the user called useless.

**Auditing the style lock before rendering.** A grep of the built graph for colour,
material and weathering words in the concept prompts is a five-second check that catches
style drift before it costs a round. All five concepts came back clean.

## Reuse when

the next humanoid mech set, or any set that has come back looking like several different
franchises. Take the roster from the accepted set rather than inventing new classes, fix
the weapons to the user's list, lock the livery in the shared suffix, and use tall boxes.

## Open

Awaiting user review. Nothing has been published, uploaded or disposed — the five PNGs and
the contact sheet are staged in the destination for the user to look at.
