# Redrawing part of a round: dispose first, then render a CARVED recipe

**Date:** 2026-11-14
**Symptom:** two images in a finished round need replacing (`r06_01` had a stray rod
sticking out of its rifle; `r06_03` had the wrong pose). Re-submitting the whole round
would touch the three keepers.

**Cause:** two separate traps.

1. **ComfyUI's `SaveImage` picks its number by scanning the output folder** for files
   matching the prefix. If `moss_mech_r06_01_recon_sniper_00001_.png` still exists and
   that concept re-renders, the new file is written as `_00002_` — so the folder ends up
   with both the old and the new image.
2. **Re-submitting the whole round is not free either.** Unchanged concepts hit
   ComfyUI's execution cache, but if they do re-execute they write `_00002_` duplicates
   too, and the keepers' filenames change under the user's feet.

**Fix — in this order:**

1. **Dispose the images being replaced first** (`mavis-trash`, recoverable). The
   counter scan then finds nothing and the redraw lands back on `_00001_`.
2. **Carve a reduced recipe** containing only the concepts being redrawn. Copy it
   verbatim from the round recipe so `styleSuffix`, `backdropDesc` and `prefix` are
   byte-identical — the redraws must match the keepers exactly. Verify with a string
   comparison; do not retype the shared blocks.
3. **Change only what is wrong** in the concept text, and draw **fresh random seeds**.
4. Build and submit the carved graph, then regenerate the contact sheet.

`work/carve-redraw.mjs` does step 2 and prints the three identity checks.

**Why not just re-submit the round:** the keepers would be re-rendered (or renamed), and
a failure would cost the whole round instead of two images.

**Applies when:** the user asks to redraw or replace specific images in a round that is
otherwise good. Also: *dispose before render*, always, when the filename must not change.

**Related tool trap:** `build-moss-set.mjs` used to compute its sidecar path as
`outPath.replace(/\.json$/, '.meta.json')`, which silently returns `outPath` unchanged
when the output path does not end in `.json` — so `--out set.json.graph` wrote the
**metadata over the graph** and the submit failed with a misleading error. The tool now
appends `.meta.json` when the path does not end in `.json`. Always give `--out` a path
ending in `.json`.
