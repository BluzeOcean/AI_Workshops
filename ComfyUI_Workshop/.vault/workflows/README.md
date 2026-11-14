# `.vault/workflows/` — known-good graphs

**Empty on purpose.** This folder is reserved for **known-good ComfyUI graphs** (API
format) plus the notes on when to use them.

A graph that reliably produces a good result belongs here, next to the note that says
*when* it is the right tool:

```
.vault/workflows/
  README.md
  <workflow-name>.json      <- API-format graph (not canvas format)
  <workflow-name>.md        <- when to use it, the settings, the failure mode
```

## What belongs here, and what does not

| | |
|---|---|
| **A graph that is worth reusing** | ✅ here — a stable graph that renders well and is needed again. |
| **A one-off graph for a single task** | ❌ `work/` — it is scratch, and `work/` is git-ignored. |
| **A canvas workflow** | ❌ here — those live in `D:\ComfyUI\ComfyUI\user\default\workflows\`, where the ComfyUI UI reads them. |
| **A prompt + layout + settings** | ❌ here — that is a **recipe**, and it goes in `.vault/recipes/`. |

**No media in this folder.** A graph is JSON (text). The images it produces live in the
destination the user confirmed.

## Format

**API format**, not canvas format. `tools\build-moss-graph.mjs` and friends emit API-format
graphs; a canvas JSON is a silent failure when submitted to `POST /prompt`. The canvas
source of truth is `D:\ComfyUI\ComfyUI\user\default\workflows\moss_image_t2i_bbox_8_steps.json`.

When you add one, record it here rather than only in the graph's own JSON:

```markdown
# <one-line title>

**Date:** YYYY-MM-DD
**What it does:** ...
**Settings:** the sampler, cfg, steps, LoRAs — the numbers that matter.
**Result:** what came out, and where it landed.
**Reuse when:** the situation where this is the right starting point.
```
