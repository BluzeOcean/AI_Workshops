---
name: comfyui-generate
description: Turn an asset request into a confirmed destination, a valid ComfyUI graph and a rendered file, including MOSS-Image layout control for concept art. Use when asked to generate, render, illustrate, concept-art or otherwise produce images, meshes or audio with ComfyUI.
---

# Generating an asset

## 1. Confirm the destination — always

The destination is the folder the finished files land in. It is a **server-level** setting:
ComfyUI's `folder_paths.get_save_image_path()` refuses to write outside `--output-directory`,
so the destination is fixed when the server boots.

- User gave one → use it exactly.
- User did not → **ask.** Never default, never guess, never reuse a previous destination.

Then make sure the running server agrees with it:

```powershell
pwsh -File tools\boot-comfyui.ps1 -OutputDir "<DESTINATION>"
```

The script warns loudly if the server is up with a *different* destination. That warning is
correct — resolve it before generating, because the files would land in the wrong place.

## 2. Write the recipe before you write the graph

A recipe is text — prompt, layout boxes, settings, seed — and it belongs in
`.vault/recipes/`. It is what makes a run reproducible, and what the memory bank needs when
the next agent asks "what worked?".

## 3. Build the graph

### A single image

```powershell
node tools\build-moss-graph.mjs `
  --prompt "<PROMPT>" `
  --layout .vault\recipes\<layout>.json `
  --width 960 --height 1280 --seed <SEED> `
  --prefix <name> `
  --out work\graph.json
```

### A set of images (one submission, one model load)

```powershell
node tools\build-moss-set.mjs `
  --recipe .vault\recipes\<set>.json `
  --out work\set.json
```

The set builder shares the UNET, LoRA, CLIP and VAE across every branch, so the 9.7 GB model
is loaded **once** and ten concepts render back to back. Ten separate submissions would
reload it ten times.

## 4. Submit

```powershell
node D:\ComfyUI\harness\comfyctl.mjs submit work\set.json
```

`submit` posts the graph, waits for completion, and prints the outputs. It is a **real
submission** — the job starts and the GPU works. Say that you are submitting before you do.

## 5. Verify

Check that the files actually landed, and look at them:

```powershell
Get-ChildItem "<DESTINATION>" | Select-Object Length, LastWriteTime, Name
```

A file that exists but is 0 bytes, or is the same size as the last render, means the
workflow did not do what you think. Open the images and look.

**Open the images themselves. Do NOT build a contact sheet.** The user does not want a
montage of the set — it costs tokens and summarises something they can already see.
`tools\contact-sheet.py` exists but is not part of the workflow; do not run it unless
it is asked for by name.

### The destination folder is the user's filing system — keep it clean

Every file in the destination is named `moss_mech_rNN_<concept>_00001_.png`. The round
number is how the user reads the folder, so **never invent a prefix** for a side render —
a house-style probe, an A/B test, a check.

- A render worth keeping gets a **round number** and a recipe that reproduces it.
- A render worth nothing is **disposed in the same task**.

**Render → measure → dispose, in one task.** A verification render is scratch: it may exist
for the minutes it takes to measure it, and not one minute longer. Keep the *measurements*
in the vault — the pixels are not evidence worth keeping. A probe that leaves thirty files
named `moss_mech_floorprobe*` in the delivery folder buries the rounds the user came to
look at and breaks the one naming convention they rely on.

And a probe renders **one approved concept** — the probe exists so that only the thing
under test varies. Using a rejected round's concept as the test subject means the probe
measures a design the user has already thrown away.

## Recipe layer structure

A concept set recipe composes the prompt from **layers**, so a round-over-round change
touches exactly one layer and the comparison stays honest:

```
promptPrefix + concept + runes + runeStyle + styleSuffix
```

| Layer | Scope | Purpose |
|---|---|---|
| `promptPrefix` | shared | The framing sentence — *"A concept-art study of"*, *"A single full-body hero concept-art portrait of"*. Joins the concept **without** a separator. |
| `concept` | per concept | What the machine is: form, function, camera, materials. |
| `runes` | per concept | An optional design layer, placed on THIS machine. |
| `runeStyle` | shared | What that layer looks like everywhere. |
| `styleSuffix` | shared | Finish, lighting, backdrop, and the prohibitions. A concept may **override** it — that is how a probe renders several variants of one concept in a single submission. |

The **prefix and concept form one grammatical unit** — never put a period between them
(*"study of. a six-legged walker"*). `joinLayers()` in `tools/build-moss-set.mjs` handles
the separators: exactly one `.` between clauses, and a leading `.` on a layer is stripped.

## Layout control — the quality lever

The MOSS-Image workflow accepts **bounding boxes** that tell the model where things go.
This is the difference between "a mech" and "a mech, framed, lit and posed".

Box coordinates are **fractions 0..1** of the canvas. Order matters: background first,
foreground last. `characterBoxes` marks a box as a character rather than an object.

```json
{
  "boxes": [
    { "x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0, "type": "obj", "desc": "BACKDROP" },
    { "x": 0.26, "y": 0.05, "w": 0.48, "h": 0.87, "type": "obj", "desc": "SUBJECT" }
  ],
  "characterBoxes": [2]
}
```

`BACKDROP` and `SUBJECT` are tokens the set builder replaces from the recipe, so ten sets of
boxes stay readable instead of repeating the same caption ten times.

## The house studio backdrop — evenly lit, no pool of light

Character concept art stands on a seamless neutral silver-grey studio backdrop. The part
that is easy to get wrong is that the **floor must be evenly lit**.

The house style used to say:

> studio key light from the upper left, cool soft fill on the camera-facing side, a warm
> golden rim light running down the left edge of the silhouette, soft bounced light from
> the grey floor

Those two phrases — a **warm** rim light from the left, and a **bounce off the floor** — let
the model place a warm light source low and to the left. It duly painted the **bottom-left
corner of the floor orange and about 40 levels brighter** than the rest of the floor, and
warmed the backdrop's left side with it. The user called it unwanted ground lighting.

Measured on the r04_02 reference, that corner was **33 units warmer and 38 units brighter**
than the rest of the floor. Every text-to-image round carried the phrasing, so every one of
them could produce it.

### The cause is the word *source*, not the colour of the light

This is the part that was wrong for three passes. Making the rim light "neutral white
instead of golden" removed the **warmth** — the corner went from +33 warm to +0.7 — but the
**bright** corner stayed, because the problem was never the colour. A light described as a
thing *in the scene* gets a **position**, and a positioned light rakes the studio floor.

So the fix is to **stop describing the rim as a light at all**. The house clause says:

> a bright thin edge highlight running down the left side of the machine

That is a **property of the machine**, not a source in the room. A property cannot spill.

Three things together hold the floor even, measured on the worst of three seeds:

| Lever | bottom-left excess vs the floor |
|---|---|
| rim as a light source, lateral key | **+14.8 (FAIL)** |
| rim as a machine property | +10.4 |
| …plus a layout box for the floor strip | +9.0 |
| …plus the stronger negative prompt | **+5.7 (PASS)** |

The same clause on three seeds measured **+2.1 / +5.7 / +1.6** — all pass. The original
artifact measured **+38 bright and +33 warm**.

### The house lighting clause, verbatim

> studio key light high above and slightly to the left, falling on the machine only, cool
> soft fill on the camera-facing side, a bright thin edge highlight running down the left
> side of the machine, flat even overhead ambient lighting on the floor, the floor a matte
> plane of one uniform neutral grey with no horizontal gradient across it, all the way to
> every edge of the frame, with no directional falloff, no pool of light, no bright corner,
> no dark corner and no reflection

**The house backdrop description, verbatim:**

> seamless neutral silver-grey studio backdrop, plain and empty, smooth vertical gradient
> from light grey at the top to mid grey at the floor, soft contact shadow pooled under the
> subject, one uniform matte neutral grey with no horizontal gradient across the floor,
> evenly lit across the whole frame with no pool of light and no bright corner, no
> landscape, no sky, no horizon, no scenery, no buildings, no props

### The floor gets its own layout box

The layout is the strongest lever, and the floor is a region of the frame that otherwise has
no instruction of its own — it is only implied by the full-frame backdrop box. Every studio
recipe carries a third box:

```json
{ "x": 0.0, "y": 0.87, "w": 1.0, "h": 0.13, "type": "obj",
  "desc": "the studio floor, a flat matte plane of one single neutral grey tone, identical from the left edge of the frame to the right edge, evenly lit, no gradient across it, no pool of light, no bright corner, no reflection" }
```

It goes **between the backdrop box and the subject box** (background first, foreground
last), and the subject's `characterBoxes` index shifts from `"2"` to `"3"`.

### The negative prompt is not optional

The text-to-image concept rounds used to run with an **empty** negative prompt — every
prohibition lived inline in the positive style suffix, where it is a suggestion rather than
a constraint. Give every concept recipe a `negative` field:

```
nsfw, worst quality, low quality, bad anatomy, deformed, extra limbs, duplicated parts,
watermark, text, lettering, signature, pool of light on the floor, bright corner, dark
corner, warm glow on the floor, lens flare, sunbeam, spotlight on the floor, directional
falloff on the floor, horizontal gradient, floor gradient, lighting gradient, uneven
lighting, mirror reflection on the floor, vignette, corner glow, glow in the corner, hotspot
on the floor, floor hotspot, bright lower corner, hot spot in the corner, uneven corner
lighting, shadow gradient across the floor
```

`mirror reflection on the floor`, never a bare `reflection` — the floor is supposed to carry
a soft **contact shadow**, and a blanket "no reflection" can take that with it.

**The edit path keeps its own negative.** The r10 edit recipes carry a *different* negative
(`emblem, insignia, decal, symbol, lettering, numbers, screen, readout`) that is what stops
an edit from re-drawing the greebles it was supposed to preserve. Do not paste the house
negative over it.

### Verify it — every render, not every other round

```powershell
D:\ComfyUI\python_embeded\python.exe tools\check-studio-backdrop.py --dir "<DESTINATION>" --pattern "moss_mech_r"
```

The checker measures the floor's bottom-left and bottom-right corners against the rest of
the floor and exits 1 when a corner is warm or bright against it. A warm corner reads as
`warmth excess` (R − B against the floor's own R − B); a bright corner reads as `value
excess`. The floor reference is the median of the band's outer thirds, so the machine's
feet and its contact shadow cannot skew it.

A failure is a **prompt** problem, not an image problem: fix the house style, then re-render.

### One seed is not a result — probe before you believe a wording

The spread between seeds is as large as the spread between wordings. The same clause measured
**+6.7 on one seed and +14.8 on another**. A single render proves nothing.

To test a wording properly, render **every variant on the same seed**, in **one submission**
so the model loads once. `build-moss-set.mjs` takes a per-concept `styleSuffix` override for
exactly this:

```json
{ "name": "variant_a", "seed": 12345, "styleSuffix": "...", "layout": { ... } }
```

Then validate the winner on **at least three seeds**, and one of them must be a seed that
**already failed** — otherwise you cannot tell a fix from a lucky seed. In this workspace a
single-seed probe picked the *losing* wording: the winner only appeared when both candidates
were re-rendered on all three seeds.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `500 Internal Server Error` on submit, `TypeError: argument of type 'int' is not iterable` | the graph dict contains a non-node key | the graph must hold **only** node entries; metadata goes in the sidecar |
| `TypeError: ... 'str' object does not support item assignment` | a node input name does not exist | check the real schema with `comfyctl get /object_info/<NodeType>` — never guess input names |
| Nothing appears in the destination | the server's `--output-directory` is not the destination | `comfyctl health`, then check the running command line; restart with `-Restart` if needed |
| One image, ten copies | one KSampler with `batch_size` 1 and one seed | give each branch its own seed |
| The subject ignores the boxes | boxes not reaching `MOSSImageLayoutPrompt` | check `CreateBoundingBoxes` output 2 feeds the `element` input |
| Job queued but nothing renders | a previous job is still running | `GET /queue`; `POST /interrupt` (**POST** — `GET /interrupt` is a 404) |
| A warm pool of light on the bottom-left corner of the floor | the house style describes a light **source** with a lateral offset, which rakes the studio floor | describe the rim as a **property of the machine** (an edge highlight), add the floor layout box, and use the house negative — then re-render and re-check |

## After the task — close the stack, then log the memory

Two closing steps, in this order.

**1. Close the headless stack and free the RAM/VRAM.**

```powershell
pwsh -File tools\stop-comfyui.ps1
```

MOSS-Image leaves ~12 GB of VRAM and ~22 GB of RAM resident in the server. A task that is
over should not keep holding them. The script stops the MCP supervisor first, then the
ComfyUI server, and reports what came back.

**2. Log the memory.**

The vault is a **memory bank** written *after* the task, not read before it. Record what
worked even when nothing broke: the model, the settings, the seed, the layout, where it
landed. That is what lets a future agent reuse the setup instead of rediscovering it.

See `.vault/README.md` for the format.
