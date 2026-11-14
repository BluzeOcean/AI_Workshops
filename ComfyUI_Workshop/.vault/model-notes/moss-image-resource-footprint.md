# MOSS-Image on this machine: measured VRAM and RAM, and how to share the GPU

**Date:** 2026-11-13
**What was run:** A cold boot of ComfyUI through a first render, sampled every 200 ms
(`tools/measure-resources.ps1`), then a `POST /free` and a timed reload.

Hardware: **RTX 4090, 24,564 MiB (24 GB) VRAM** · **63.8 GB RAM** · i9-14900K · torch 2.11.0+cu130 · ComfyUI 0.45.3.

---

## The weights

| Component | File | Size |
|---|---|---|
| UNET | `moss_image_sft_bf16.safetensors` | 9,693 MB |
| Text encoder | `qwen3.5_9b_bf16.safetensors` | 18,411 MB |
| VAE | `flux2-vae.safetensors` | 160 MB |
| **Total** | | **28,264 MB (27.6 GB)** |

**27.6 GB of weights on a 24 GB card.** ComfyUI's DynamicVRAM keeps what fits on the GPU and
stages the rest in RAM, paging on demand. That is why the RAM number is large and the VRAM
number is *not* 27.6 GB.

---

## Measured footprint

**Baseline first: this machine's own apps already use 7,884 MiB (7.7 GB) of VRAM** —
UnrealEditor (the EpicJam project), Chrome, Steam, DeepSeek Harness, MiniMax Code. That
number is the one people forget. ComfyUI is not starting from zero.

| Phase | Card used | ComfyUI's share | ComfyUI RAM (private) | Card free |
|---|---|---|---|---|
| **No ComfyUI** | 7,884 MiB | — | — | 16.7 GB |
| Cold boot, server up | ~8,400 MiB | ~0.5 GB | ~3.4 GB | ~15.7 GB |
| **Model load spike (peak)** | **20,603 MiB** | ~12.7 GB | **23.25 GB** | **3.9 GB** |
| **Steady, models cached** | 19,725 MiB | **~11.8 GB** | **22.25 GB** | 4.8 GB |
| **After `POST /free`** | **8,508 MiB** | **~0.6 GB** | **5.52 GB** | **15.6 GB** |

Working Set (RAM actually resident) peaks at **8.64 GB**; private bytes reach 23.25 GB
because that is the *reserved* staging area for the weights.

---

## Timing

| Action | Time |
|---|---|
| Cold boot → first render finished | **35 s** (16 s to serve 8188, ~19 s to load models and render) |
| Render, models warm | **8.3 s** |
| Render after `POST /free` (full reload) | **14.1 s** |
| 10-image set, one model load | **120 s** (12 s/image amortised) |

---

## The lever: `POST /free`

```
POST http://127.0.0.1:8188/free
{"unload_models": true, "free_memory": true}
```

**Releases 11.2 GB of VRAM and 16.7 GB of RAM in ~8 seconds**, dropping ComfyUI back to a
0.6 GB VRAM / 5.5 GB RAM idle server and freeing **15.6 GB of the card**.

The reload cost is only ~6 s extra on the next render (14.1 s vs 8.3 s) — the weights come
back from NVMe fast. **Time-sharing the GPU is cheap.** Measured with
`tools/free-vram.ps1`.

Related boot flags, if a different balance is wanted:

- `--disable-smart-memory` — aggressively offload to RAM instead of keeping models in VRAM.
- `--cpu-vae` — run the VAE on CPU.
- `--vram-headroom N` (currently 3) — keep N GB of VRAM free for other apps.
- `--highvram` — the opposite of what you want here.
- `--lowvram` — **does nothing** while dynamic VRAM is enabled (it is, by default).

---

## Sizing a local model alongside it

Two workable arrangements on this box:

**A. Time-share the GPU (recommended).** Call `POST /free` before LLM work, render after.
Leaves **~15.6 GB VRAM** and ~50 GB RAM for the LLM — room for a 14B Q4 fully on GPU, or a
20-30B Q4 partly offloaded. Cost: ~6 s per render extra.

**B. LLM on CPU + a few GPU layers.** Run the LLM mostly in the ~30 GB of free RAM with
llama.cpp `--n-gpu-layers 8` (~2-3 GB VRAM). ComfyUI keeps its full 11.8 GB cache and never
needs freeing. Slower inference, zero interference.

**Not viable:** a >4B model on the GPU *while ComfyUI is warm*, because only 3.9 GB is free
once your other apps are counted.

**Note:** no LLM runtime is installed on this machine yet — no ollama, llama.cpp, LM Studio
or koboldcpp.

---

## Trap: ComfyUI's execution cache returns identical results

Re-submitting the **same graph with the same seed** returns a byte-identical image in ~0.6 s,
because ComfyUI caches node outputs across prompts. It is not a fast render.

**Fix:** change the seed to measure a real render. A timing run with the same seeds produced
a `_00002_` copy of every image, byte for byte.

---

## Tooling added

- `tools/measure-resources.ps1` — samples VRAM + process RAM on an interval; follows the
  process by command line so it survives a cold boot (the pid changes).
- `tools/free-vram.ps1` — measures VRAM/RAM before and after `POST /free`.

**Reuse when:** sizing a new model or task against the GPU, or deciding what else can run
alongside ComfyUI.
