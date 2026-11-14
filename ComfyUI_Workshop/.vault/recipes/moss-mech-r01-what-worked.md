# MOSS-Image concept set — 10 mechs, one submission, one model load

**Date:** 2026-11-13
**Status:** active
**What was run:** MOSS-Image t2i with layout boxes, via
`tools/build-moss-set.mjs` → `comfyctl submit`.

```
node tools\build-moss-set.mjs --recipe .vault\recipes\moss-mech-r01-set.json --out work\moss-mech-r01.json
node D:\ComfyUI\harness\comfyctl.mjs submit work\moss-mech-r01.json
```

- Model: `moss_image_sft_bf16.safetensors` + `MOSS-Image-8-step\lora.safetensors`
- CLIP: `qwen3.5_9b_bf16.safetensors` (type `moss_image`) — 18.4 GB, staged for dynamic VRAM
- VAE: `flux2-vae.safetensors`
- `SkipLayerGuidanceDiTSimple` single layer `22`, `0 → 0.5`
- KSampler: 8 steps, cfg 2.5, `er_sde` / `simple`, denoise 1
- 960 × 1280 (3:4 portrait), 10 concepts, seeds 81001–81010
- Destination: `V:\04_Projects\EpicJam2026\MechConcept Art`

**Result:** 10 files, 960×1280, ~1.2–1.5 MB each. All ten read as a designed roster on the
same silver-grey studio backdrop — the set is consistent in finish, lighting and framing,
while the silhouettes are clearly distinct (scout / artillery / stealth / shield / flyer /
sniper / duelist / support / heavy / hover).

**Throughput:** ~7 s per render at 8 steps after the model was loaded (~2 min to load the
9.7 GB UNET + 18.4 GB text encoder). The whole set took ~2.5 minutes.

**Reuse when:** starting any concept set. Three things that carried the result:

1. **One graph, one submission, one model load.** Ten KSampler branches share the UNET,
   LoRA, CLIP and VAE. Ten separate submissions would reload ~28 GB of weights ten times.
2. **A layout box per concept** — a full-frame backdrop box and a subject box. Every mech
   is framed full-body with a contact shadow and nothing else in frame, with no
   composition drift between the ten.
3. **A shared `styleSuffix` + `promptPrefix`** in the recipe, so the finish, the lighting
   and the backdrop are identical across the set while only the subject changes. That
   shared tail is what makes ten images read as one roster rather than ten unrelated
   pictures.

**Recipe:** `.vault/recipes/moss-mech-r01-set.json` — edit the `concepts` array to change
the roster; the framing and finish stay put.

**Weakness spotted for round 02:** the two weapons that should read as *held guns* — the
artillery cannon on `02_lance_artillery` and the marksman rifle on `06_warden_marksman` —
came out as thin bare poles. The word "rifle"/"cannon" in the caption is not enough to make
the model draw a weapon body. Fix: name the weapon's *parts* ("a long rifle with a
rectangular receiver and a folded stock") or drop the weapon and give the silhouette a
different read.
