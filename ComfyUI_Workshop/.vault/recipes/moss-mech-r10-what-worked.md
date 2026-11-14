# Round 10 — variations of r04_02, made from the reference IMAGE, weapon-free

**Date:** 2026-11-14
**Status:** rendered, staged for user review
**What was run:** three images, one submission, from a weapon-free cleaned reference.

```
node tools\build-moss-edit-set.mjs --recipe .vault\recipes\moss-mech-r10-edit-set.json --out work\moss-mech-r10-edit.json
node D:\ComfyUI\harness\comfyctl.mjs submit work\moss-mech-r10-edit.json
```

- Edit LoRA: `MOSS-Image-Edit\moss_image_edit_lora_rank_64_bf16.safetensors`
  (297,382,216 bytes, sha256 `17a48b8c…9dcdf`, byte-identical to `chinoll\Moss-Image-Edit`)
- `UNETLoader` `moss_image_sft_bf16.safetensors` → `LoraLoaderModelOnly` (edit LoRA, 1.0)
  → `SkipLayerGuidanceDiTSimple` single layer `22`, `0 → 1`
- `CLIPLoader` `qwen3.5_9b_bf16.safetensors` type `moss_image` · `VAELoader` `flux2-vae.safetensors`
- `TextEncodeMOSSImageEdit` × 2 (positive + negative), `edit_format = Moss-Image-Edit`,
  `image_strength = 1.0`, reference on `images.image_0`
- `KSampler` 30 steps, cfg 4.0, `euler` / `normal`, denoise 1 · 960×1280
- **Random 48-bit seeds**: 29552778028108, 113147870550493, 40411852960137
- Reference: `moss_mech_r04_02_reference_weaponfree_01_empty_handed_00001_.png [output]`
- Destination: `V:\04_Projects\EpicJam2026\MechConcept Art`

## The final set

| File | Change | What it shows |
|---|---|---|
| `moss_mech_r10_01_bone_crimson_00001_.png` | **paint** | rust orange → bone white over charcoal, crimson shin chevrons, crimson chest band |
| `moss_mech_r10_02_swept_fins_00001_.png` | **silhouette** | the two dorsal fins swept back along the spine instead of up and out |
| `moss_mech_r10_03_layered_pauldrons_00001_.png` | **chassis detail** | the flat angular pauldron → three overlapping curved plates |

All three: **empty-handed**, no screen, no emblem, the reference's chassis, head, spine
hardware, chevron shin plates and studio backdrop intact.

## The reference went through three steps before any variation

The reference is not the raw r04_02 PNG. It is:

1. **`moss_mech_r04_02_reference_clean.png`** — the original with four surface greebles
   flattened by `tools/clean-reference-artifacts.py` (`flat_grain`): the raised vent unit
   on the upper back, the painted orange trident emblem on the chest, the raised grid
   block on the flank and the small recessed square on the hip plate.
2. **`moss_mech_r04_02_ref_weaponfree_01_no_blade_00001_.png`** — one edit: the long
   blade → a blunt armoured fist.
3. **`moss_mech_r04_02_reference_weaponfree_01_empty_handed_00001_.png`** — one more
   edit, chained from step 2: the three-talon claw → a blunt armoured fist. This is the
   reference every variation is made from.

Each step is a separate recipe in `.vault/recipes/`, and each is **one change**.

## Why it took four revisions

| Rev | What changed | What went wrong |
|---|---|---|
| 1 | reference PNG + edit LoRA | worked mechanically; the reference's own greebles were copied into every output |
| 2 | added a removal clause per unit | **backfired** — naming the artifacts made the model grow screens and emblems |
| 3 | cleaned the reference; kept the removal clause | artifacts gone, but unit 01 was still *"a completely different model"* |
| 4 | one change per unit, clean reference, no removal clause, weapon-free | ✓ |

## The three lessons that actually moved the needle

1. **Never name an artifact.** An edit instruction is a description of the target
   image; naming "the screen" teaches the model what a screen looks like. Clean the
   reference instead. → `.vault/lessons/2026-11-14-never-name-an-artifact-clean-the-reference.md`
2. **Never ask for a change the reference already has.** r04_02 is a **bipedal**
   humanoid mech — two digitigrade legs, a blade arm, a claw arm, a wedge head — and
   revision 2 asked for "two legs instead of four". With no edit to make, the model
   redrew the machine. → `.vault/lessons/2026-11-14-check-what-the-reference-already-is.md`
3. **A repair must be less interesting than the material it replaces.** A ribbed fill
   became a grille; a flat face inside a raised rim became a monitor bezel. Fill the
   unit whole, fit a plane, use luminance grain. → `.vault/lessons/2026-11-14-a-fill-must-be-smoother-than-the-plate.md`

## Reuse when

- The brief names a reference model and asks for variations → feed the PNG in with the
  edit LoRA, one change per unit, and change something the reference demonstrably
  does not already have.
- The output carries screens, emblems, decals or pseudo-text → check the reference for
  them and clean it; do not add a removal clause.
- Concept art → the machine is **empty-handed**; weapons are separate assets.

**Do not reuse** the weapon-removal instruction that asked for both weapons at once,
and do not put weapon words in the negative prompt.
