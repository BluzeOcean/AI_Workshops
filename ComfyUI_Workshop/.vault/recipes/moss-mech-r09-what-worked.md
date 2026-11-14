# Round 09 — the humanoid form of r04_02, one chassis in five colourways

**Date:** 2026-11-14
**Status:** active — rendered, staged for user review
**What was run:** Round 09 of the EpicJam2026 concept set — five images, one submission.

```
node tools\build-moss-set.mjs --recipe .vault\recipes\moss-mech-r09-set.json --out work\moss-mech-r09.json
node D:\ComfyUI\harness\comfyctl.mjs submit work\moss-mech-r09.json
```

- Same model stack, 960×1280, 8 steps, cfg 2.5, `er_sde` / `simple`
- **Random 48-bit seeds**, drawn once and baked into the recipe: 252020977179918,
  64464134455130, 99148141368387, 41907256052939, 189175544177539
- Destination: `V:\04_Projects\EpicJam2026\MechConcept Art`
- `_contact_sheet_r09.png` written alongside the images

**The brief, in the user's words:**

> "Negative. This round did not produce the result i'm asking for. i asked to use this (attached)
> image ref as the base, to draw another sets of the same variation of this model, the r07 result
> was just applying the color of the ref image into the other r06 units. and thats not what i
> asked for!!"

## The correction

Two rounds in a row copied **one attribute** of the reference model and missed the rest:

| Round | What it copied | What it missed |
|---|---|---|
| 07 | r04_02's **palette** | the chassis, the head, the art style, the silhouette |
| 08 | r04_02's **art style** | the chassis, the head, the silhouette |

Round 09 copies the **DESIGN** — the reference model's actual chassis, transcribed feature by
feature — and puts it on two legs.

**Verified before rendering**, by shared 6-word shingles against the intended source:

| Compared with | overlap |
|---|---|
| **R04** (the intended basis) | **92.9 %** |

**And the reference model's signature features were ticked off against the recipe** before
submitting, so a missing feature would have been caught in the recipe rather than in the
image: forward-thrusting wedge torso · low wide armoured head with a single wide visor band ·
cheek tusk spurs · two huge flat dorsal fins sweeping up and out from the shoulders · a row of
short cylindrical weapon tubes along the spine · an underslung mechanical pod below the belly ·
heavy digitigrade legs with broad clawed feet · double-chevron angular shin plates · right arm
ending in a long combat blade · left arm ending in a three-talon claw.

All five layout subject boxes are **tall** (w:h ratios 0.76–0.88), which is what makes the
machine build upright instead of low and horizontal.

## The set — one chassis, five colourways

| Unit | Livery | Accent |
|---|---|---|
| `01_rust_hound` | rust orange over near-black | amber bands across the dorsal fins |
| `02_sand_hound` | pale desert sand over dark olive drab | ochre double chevrons on the shin plates |
| `03_slate_hound` | gunmetal blue-grey over matte black | hazard orange stripe along the spine tubes |
| `04_bone_hound` | bone white over charcoal | crimson band across the forward chest plate |
| `05_moss_hound` | moss green over dark grey | pale sand bands around the hip joints |

**All five are bipedal** — two legs, two arms, a head between the shoulders. The chassis,
arms, head, fins, spine rack, belly pod and legs are identical on every unit; only the hues
and the placement of the accent colour change. That is what makes them read as the same model
rather than five different mechs.

**The dorsal fins were the hard part.** In r04_02 they are the model's signature, but the
reference is a quadruped and the fins sweep up and out from a horizontal back — left alone on
an upright machine they turn into random spikes, which is exactly the fault the user
complained about in round 07 ("there are just random spike sticking out"). So each fin is now
**given a construction**: *a broad bevelled plate with a raised central spine ridge, a
recessed mounting socket at the base and a squared root fairing where it meets the back
plate*.

**Pose.** Relaxed standing, weight even on both legs, feet planted slightly apart, arms
lowered, the combat blade hanging straight down at the right side running parallel to the leg
and clear of the body — the house rule, so the chest and leg construction stay readable.

## Reuse when

a brief attaches a reference image and asks for "another set of the same variation of this
model". Transcribe the reference's **design**, not one attribute of it: list the signature
features, put them in the shared clause, tick each one off against the recipe, and shingle-check
the style against the reference's own round before rendering. Then vary only the axis the brief
names.

**Related:** `.vault/lessons/2026-11-14-a-variation-is-the-design-not-the-palette.md` ·
`.vault/lessons/2026-11-14-reuse-the-style-suffix-not-just-the-silhouette.md` ·
`.vault/lessons/2026-11-14-describe-parts-not-labels.md` ·
`.vault/lessons/2026-11-14-concept-art-wants-a-relaxed-standing-pose.md`

## Open

Awaiting user review. Nothing has been published, uploaded or disposed — the five PNGs and
the contact sheet are staged in the destination.

**Two decisions still with the user:**

1. **The variation axis.** Round 09 varies the **livery** (one chassis, five colourways). If
   "variations" was meant as *different builds or loadouts of the hound* — different weapon
   arms, different head, different shoulder hardware, five separate machines on one chassis
   family — that needs a per-concept **build** clause, not a colour clause. The chassis
   transcription and the shared style would carry over unchanged; only the per-concept clause
   changes.
2. **Disposal.** The four rejected round 04 images and the five round 08 images are still in
   the destination. Round 07 was explicitly kept. Nothing has been deleted.
