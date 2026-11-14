# Model notes — what is in `D:\.models` and what it is good for

Text only. The model files live in `D:\.models`; nothing is stored in this workspace.

## Path mapping (from `ComfyUI\extra_model_paths.yaml`)

| Folder | Maps to | Notes |
|---|---|---|
| `checkpoints` | `D:\.models\checkpoints/` | |
| `vae` | `D:\.models\vae/` | |
| `clip` | `D:\.models\clip/` | **also mapped to `text_encoders`** |
| `text_encoders` | `D:\.models\clip/` | same folder as `clip` — look there first |
| `diffusion_models` | `D:\.models\diffusion_models/` | |
| `loras` | `D:\.models\loras/` | |
| `controlnet` / `ipadapter` / `clip_vision` / `background_removal` / `3d` | `D:\.models/<key>/` | |

> The per-install `ComfyUI\models\` folders are nearly empty. **Never conclude a model is
> missing from them** — the real library is `D:\.models`. This cost a wrong conclusion once
> (`qwen3.5_9b_bf16.safetensors` looked missing until `text_encoders` was traced to `clip/`).

---

## MOSS-Image (`moss_image_sft_bf16.safetensors`) — 9.7 GB, diffusion_models

Native ComfyUI support (`comfy_extras/nodes_moss_image.py`), added to this install on
2026-11-13. A Qwen-VL-family understanding model driving a FLUX.2-style latent pipeline.

**Required companion stack:**

| Piece | File | Where |
|---|---|---|
| UNET | `moss_image_sft_bf16.safetensors` | `diffusion_models/` |
| LoRA | `MOSS-Image-8-step\lora.safetensors` (1.1 GB) | `loras/` |
| Text encoder | `qwen3.5_9b_bf16.safetensors` (18.4 GB) | `clip/` — type **`moss_image`** |
| VAE | `flux2-vae.safetensors` | `vae/` |

**Settings that work:** 8 steps, cfg 2.5, `er_sde` / `simple`, denoise 1, plus
`SkipLayerGuidanceDiTSimple` with single layer `22` over `0 → 0.5`. ~7 s per 960×1280
render on the 4090 once loaded.

**Strengths seen:** strong, readable mecha silhouettes; good studio-lit concept-art
framing; consistent finish across a set when the style tail is shared.

**Weaknesses seen:** named *weapons* render as bare poles — name the parts instead.

**Nodes it brings:**

- `MOSSImageLayoutPrompt` — turns a prompt plus bounding boxes into a layout prompt.
- `MOSSImageControl` — colour-map / depth-map control adapter.
- `TextEncodeMOSSImageEdit` — reference-image conditioning. `edit_format` choices:
  `ai-toolkit`, `ai-toolkit (kv_cache off)`, `Moss-Image-Edit`. With **no VAE** the
  references only reach the text encoder (as "Picture N:" vision tokens) — that path works
  with the base model and needs no edit LoRA.
- `CreateBoundingBoxes` — layout authoring; see the lesson on element format.

> **No MOSS-Image-Edit LoRA is installed** — `loras/` only has `MOSS-Image-8-step`. The
> `reference_latents` path (which needs `vae`) therefore cannot be exercised until one is
> downloaded.

---

## Other models present (not yet exercised in this workspace)

| Model | File | Notes |
|---|---|---|
| Qwen-Image-Edit 2511 Lightning 4-step | `Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors` | loras/, 810 MB |
| Qwen-Image multiple angles | `qwen-image-edit-2511-multiple-angles-lora.safetensors` | loras/, 281 MB |
| Qwen-Image Lightning 4-step | `Qwen-Image-Lightning-4steps-V1.0.safetensors` | loras/, 1.6 GB |
| MiniMax H3 turbo 4-step | `minimax_h3_turbo_4step_pruned_comfyui.safetensors` | loras/, 591 MB |
| Anima turbo v0.2 | `anima-turbo-lora-v0.2.safetensors` | loras/, 142 MB |
| Qwen 3.5 9B (PE, i2i / t2i) | `qwen3.5_9b_qwen_image_2.1_pe_*.int8_convrot.safetensors` | clip/, 9 GB each |
| TRELLIS / TripoSR | under `3d/` | image → mesh |

**Still to explore:** reference-image editing through `TextEncodeMOSSImageEdit`; image → 3D
for the mech designs; the Qwen-Image multiple-angles LoRA for turnaround sheets.
