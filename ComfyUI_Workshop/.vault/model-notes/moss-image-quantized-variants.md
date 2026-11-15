# MOSS-Image — the quantized set, and the bf16 set that already works

**Date:** 2026-11-14

`Comfy-Org/MOSS-Image` ships two interchangeable model stacks. Both drive the same
MOSS-Image architecture; the quantized one is roughly half the weight on disk and
half the VRAM, which is why it exists.

## The bf16 stack — already installed, known-good

| Piece | File | Size | Where |
|---|---|---|---|
| UNET | `moss_image_sft_bf16.safetensors` | 10.16 GB | `D:\.models\diffusion_models\` |
| CLIP | `qwen3.5_9b_bf16.safetensors` | 19.31 GB | `D:\.models\clip\` |
| VAE | `flux2-vae.safetensors` | 336 MB | `D:\.models\vae\` |

This is the stack every house concept-art round and the whole of **r10** ran on.
It is the reference implementation — **reach for it first.** Verified complete
(no zero-holes) on 2026-11-14.

## The quantized stack — leaner, added 2026-11-14

| Piece | File | Size | Where |
|---|---|---|---|
| UNET | `moss_image_sft_int8_convrot.safetensors` | 5.41 GB | `D:\.models\diffusion_models\` |
| CLIP | `qwen3.5_9b_w4a8_gptq.safetensors` | 7.34 GB | `D:\.models\clip\` |
| VAE | `flux2-vae_small.safetensors` | 250 MB | `D:\.models\vae\` |

Roughly **12.8 GB of weights vs 29.5 GB** for the bf16 pair. On the 24 GB RTX 4090
that difference is the whole point: the bf16 CLIP alone is 19.3 GB, so the bf16
stack leans on ComfyUI's CPU offload and renders noticeably slower. The quantized
stack fits with headroom.

All three are in the Comfy-Org/MOSS-Image repo and were verified against the
published sha256 on 2026-11-14:

```
moss_image_sft_int8_convrot.safetensors
  sha256 b4d1475bc7eeffd7b809e82ea13a1fba1fb85c4e18365af3813722faa5c0fe4f
qwen3.5_9b_w4a8_gptq.safetensors
  sha256 4cc6a1543ad2061806da46f35f90cadb4801dcba246c44782cf42ec0feb6407c
flux2-vae_small.safetensors
  sha256 d8d52ba036475f5fb07c8b435e176d3d97ebfa82f0d1a1c317f9cc1e25bd013b
```

Download URLs are the `resolve/main/<folder>/<file>` form under
`https://huggingface.co/Comfy-Org/MOSS-Image/`.

## The two LoRAs are NOT interchangeable

| LoRA | File | Size | Job | Loader |
|---|---|---|---|---|
| 8-step | `MOSS-Image-8-step\lora.safetensors` | 1.19 GB | step-count **distillation** for **text-to-image** — 8 steps instead of ~30 | `LoraLoader` (model **+ clip**) |
| Edit rank 64 | `MOSS-Image-Edit\moss_image_edit_lora_rank_64_bf16.safetensors` | 297 MB | **instruction editing** against a reference image | `LoraLoaderModelOnly` (model only) |

They are different adapters trained for different objectives. The 8-step LoRA
cannot turn the model into an image editor — it has no training on
"change only X to Y, keep Z" conditioned on a reference. The edit LoRA does not
make sampling fast; the edit path runs 30 steps at cfg 4.0. They are also **not
meant to be loaded together** (`AGENTS.md` §5).

So "the MOSS model I already have" is ambiguous, and the answer splits:

- **Base models** — yes, the bf16 set works for the edit path unchanged, and did
  so for r10. Swapping the quantized set for the bf16 set is a valid fallback
  whenever the quantized files are unavailable.
- **Edit LoRA** — no, the 8-step LoRA is not a substitute for the rank-64 edit
  LoRA.
