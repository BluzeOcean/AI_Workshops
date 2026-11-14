---
name: moss-reference-variation
description: Generate new variations of an existing model or image by feeding the reference PNG into MOSS-Image with the edit LoRA, so the design is inherited from the picture instead of re-described in a prompt. Use when asked for "another set of the same model", "variations of this reference", or when a prompt-only round was rejected as "not the sample".
---

# Variations of a reference model, via the reference image

## The problem this solves

A text-to-image prompt can only *describe* a design. Ask for "the same machine as this
picture" in words and the model gives you a machine that resembles the picture in **one**
attribute — the palette, the art style, the silhouette — while the chassis, the head and
the signature hardware are all invented. Three rounds in this workspace failed exactly
that way and were rejected with "not the sample":

| Round | What the prompt carried over | What it lost |
|---|---|---|
| 07 | the reference's **palette** | chassis, head, art style |
| 08 | the reference's **art style** | chassis, head, silhouette |
| 09 | the reference's **design**, hand-transcribed into the prompt | the model's own drawing of it |

Round 09 got close because the design was transcribed by hand, feature by feature, into
the shared prompt. But it was still the model *imagining* the reference from words.

The **right** way is to put the reference image into the model. MOSS-Image ships an
instruction-edit LoRA and ComfyUI has native support for it (PR #17296, ComfyUI ≥ 0.42.1):

- `TextEncodeMOSSImageEdit` — encodes an edit instruction **together with the reference
  image**; the reference reaches the DiT as reference latents.
- `LoraLoaderModelOnly` — loads the edit LoRA onto the diffusion model.

Now the picture is the source of the design and the prompt only says what to **change**.

## Requirements

| What | Where | Check |
|---|---|---|
| ComfyUI ≥ 0.42.1 | the install | `comfyctl get /system_stats` → `comfyui_version` |
| Edit LoRA | `D:\.models\loras\MOSS-Image-Edit\moss_image_edit_lora_rank_64_bf16.safetensors` | `comfyctl get /object_info/LoraLoaderModelOnly` must list it |

If the LoRA is missing, download it (297,382,216 bytes, sha256
`17a48b8c605dcffdedb92a2b887d18cf316505be90802717669fb6556098dcdf` — byte-identical to
`chinoll/Moss-Image-Edit` and `Comfy-Org/MOSS-Image`):

```powershell
& "D:\tools\aria2\aria2c.exe" --console-log-level=warn -x8 -s8 -k4M `
  -d "D:\.models\loras\MOSS-Image-Edit" `
  -o "moss_image_edit_lora_rank_64_bf16.safetensors" `
  "https://huggingface.co/Comfy-Org/MOSS-Image/resolve/main/loras/moss_image_edit_lora_rank_64_bf16.safetensors"
```

The LoRA is a **model-only** adapter: `LoraLoaderModelOnly`, never `LoraLoader`, and it
must **not** be combined with the 8-step acceleration LoRA (that one is distilled for 8
steps; this path runs 30).

## 1. Confirm the destination — always

Same rule as every generation: the destination is fixed when the server boots, and the
reference image has to be readable by the server. See `.skills/comfyui-generate/SKILL.md`.

## 2. Write the recipe

`.vault/recipes/<name>.json`:

```json
{
  "reference": "moss_mech_r04_02_hound_tracker_00001_.png [output]",
  "width": 960,
  "height": 1280,
  "steps": 30,
  "cfg": 4.0,
  "sampler": "euler",
  "scheduler": "normal",
  "edit_format": "Moss-Image-Edit",
  "image_strength": 1.0,
  "negative": "nsfw, worst quality, bad anatomy, watermark, jpeg artifact",
  "prefix": "moss_mech_r10",
  "concepts": [
    { "name": "01_biped_hound", "seed": 5132916189649, "instruction": "Change the war machine so that ..." }
  ]
}
```

**`reference` accepts a directory annotation.** `LoadImage` resolves
`"name.png [output]"` against the server's **output** directory and `"name.png [input]"`
against the **input** directory, so a reference that already sits in the destination can
be used with no copying at all. Use a forward-slash subfolder path for the input dir
(`"Mech Concept Art/ref.png [input]"`).

**The extension does not matter.** The existence check is `os.path.exists`, and PyAV opens a
`.webp` as a video stream with codec `webp`, so a `.webp` reference loads fine. It is worth
knowing because the user's own art arrives as `.webp` — and the **canvas workflow's `LoadImage`
widget wants a plain filename**, which resolves against the **input** dir, so copy the
reference there once if it is not already listed in the picker.

Seeds are random 48-bit values, drawn once and baked into the recipe.

## 3. Build and submit

```powershell
node tools\build-moss-edit-set.mjs `
  --recipe .vault\recipes\<recipe>.json `
  --out work\<name>.json

node D:\ComfyUI\harness\comfyctl.mjs submit work\<name>.json
```

One graph, one submission: the UNET, the edit LoRA, the CLIP, the VAE and the scaled
reference are shared, so the model loads **once** and every concept renders back to back.
`submit` really runs the job — say so before you do.

## 3b. Hand the user a CANVAS workflow they can open in ComfyUI

When the user wants to **run the round themselves**, an API graph is not enough — ComfyUI's UI
opens **canvas** workflows. `tools\build-moss-edit-workflow.mjs` emits **both** from one
recipe: the API graph for `comfyctl submit`, and the canvas workflow for the UI.

```powershell
node tools\build-moss-edit-workflow.mjs `
  --recipe .vault\recipes\<recipe>.json `
  --out-graph work\<name>.graph.json `
  --out-workflow "D:\ComfyUI\ComfyUI\user\default\workflows\<Name>.json" `
  --reference "<file the LoadImage picker should show>"
```

- The canvas file must be written into `D:\ComfyUI\ComfyUI\user\default\workflows\` — that is
  where the UI reads its workflow list from.
- `--reference` overrides the recipe's `reference` with a **plain filename**, because the
  `LoadImage` widget's dropdown lists the **input** dir. Copy the reference there first if it
  is not already listed.
- Name the workflow so it is **findable**: the user searches for it by name. Descriptive beats
  terse — `MOSS-Image-Edit-Class-Variations-S01.json`.
- Confirm it landed: `GET /userdata?dir=workflows&recurse=true` returns the **names** as a
  plain array of strings (not objects).

**Canvas format notes** (a hand-edited canvas JSON is a silent failure):

- top level: `id, revision, last_node_id, last_link_id, nodes[], links[], groups[], config{},
  extra{}, version`.
- a node needs `id, type, pos, size, flags, order, mode, inputs, outputs, properties,
  widgets_values, widgets_values_named`.
- a link is `[id, srcNode, srcSlot, dstNode, dstSlot, type]`.
- `order` is **topological** — a node must come after everything it depends on.
- `widgets_values` is **positional** and must match the node's `INPUT_TYPES` order, or the
  value lands in the wrong widget.

## The instruction — the one thing that decides the result

The LoRA was trained on a specific phrasing:

> **"Change only the X to Y. Keep \<list of things\> unchanged."**

Three rules. Each one exists because a render failed without it.

### 1. Change ONE thing, and name that thing precisely

"Change only the X to Y" — **not** "change the machine so that it is Y".

A broad phrasing is a *redefinition*, and the model answers it by inventing a new
machine that merely resembles the reference. Round 10's first biped said *"Change the
war machine so that it is a bipedal humanoid machine standing upright on two legs"*
and the result was a completely different model that did not absorb the reference's
style at all. The same round's livery edit and weapon swap — both narrow — kept the
reference almost intact.

**Ask for the part, not the machine:** *"Change only the legs so that it stands on two
legs instead of four."*

### 2. The keep-list is a DESCRIPTION of the machine, measured from the picture

The picture carries the design. The keep-list's job is to say **what the machine is**, in
words the model can hold onto — the camera, the pose, the proportions, the plate shapes, the
material, the head — all **measured from the reference image**, never guessed and never copied
from a house rule.

**A vague keep-list is worse than no keep-list.** Silence means the model fills the gap with
its default; a vague keep-list means the model fills the gap with its default *according to
your wrong words*. Round 13 said *"relaxed upright standing pose"* and *"overlapping curved
armour plates"* about a reference that is a **hunched** machine with **flat angular** plates —
and the set came back as upright, orange-and-cream knight mannequins. See
`.vault/lessons/2026-11-14-a-vague-keep-list-is-worse-than-none.md`.

Cover these six, every time:

1. **The camera** — *"the same high three-quarter front view from above with the camera looking
   down on the machine at a steep angle so the tops of its shoulders and its back are visible
   and the whole machine sits small in the frame with air around it"*. An unmentioned camera
   becomes the default straight-on eye-level view, and a hunched machine shot from eye level
   reads as a toy figurine on a table.
2. **The pose** — the stance, joint by joint: *"hunched prowling stance with the torso pitched
   forward, the head thrust forward and down between the raised shoulders, the arms hanging
   down and forward with heavy clenched grippers, and the short thick legs crouched and splayed
   wide with the broad feet planted far apart"*.
3. **The proportions** — measured, not stock phrases. *"compact dense proportions, about five
   and a half heads tall, short thick legs and a broad deep torso"*; not *"broad heavy frame"*,
   which is the model's own mannequin.
4. **The plate shapes** — flat or curved, faceted or moulded, and where they sit. *"the
   overlapping flat angular shoulder slabs stepping down and out over the upper arms with rivet
   rows along their edges"*; not *"overlapping curved armour plates"*, which is a knight's
   pauldron.
5. **The material vocabulary** — *"hard-edged bevelled steel armour, angular and faceted with
   sharp corners and no rounded moulded forms … the exposed black mechanical structure between
   the plates — hydraulic pistons, actuators, hose bundles and cable looms"*. This is the
   single strongest defence against the smooth-plastic / retro-appliance read.
6. **The head** — size, shape, and where it sits. *"the small dark cowled head module thrust
   forward and low with a narrow dark visor and two amber optic eyes"*; not *"helmet"*, which
   buys a big humanoid head standing above the shoulders.

**Write it as a description, not as a list of features to preserve.** A bulleted inventory of
the reference's distinctive features reads as an order to *rebuild* each of them, and the model
draws its own version of the part. That is what round 10 did:

Bad keep-list — a feature inventory, so the model rebuilds it:

> "keep its heavy rust orange and charcoal armour, the same low wide head with its
> single visor band and cheek tusk spurs, the same pair of huge flat dorsal fins, the
> same row of weapon tubes along the spine"

Good keep-list — a continuous description of the machine you can see (round 14's, trimmed):

> "Keep the same high three-quarter front view from above with the camera looking down on
> the machine at a steep angle so the tops of its shoulders and its back are visible …
> Keep its hunched prowling stance with the torso pitched forward, the head thrust forward
> and down between the raised shoulders, the arms hanging down and forward with heavy
> clenched grippers, and the short thick legs crouched and splayed wide … Keep its compact
> dense proportions, about five and a half heads tall … Keep the hard-edged bevelled steel
> armour, angular and faceted with sharp corners and no rounded moulded forms, the
> overlapping flat angular shoulder slabs stepping down and out over the upper arms with
> rivet rows along their edges, the small dark cowled head module thrust forward and low
> with a narrow dark visor and two amber optic eyes, the exposed black mechanical structure
> between the plates — hydraulic pistons, actuators, hose bundles and cable looms …"

Round 14 put that description in front of all six concepts and got **six good renders on the
first try** — the only round in this series that has managed that.

### 2b. Class hardware is built from the MACHINE's vocabulary

A new part described in **borrowed** vocabulary inherits that vocabulary's associations.
Round 13 asked for *"a bulky rectangular rangefinder pod with a big glass lens"* and got a
**grey appliance box with a camera lens**; *"a long horizontal row of small glass sensor
lenses in a recessed strip"* came back as a **chrome speaker grille**. "Rectangular pod, big
lens" is the vocabulary of a camera; the reference's vocabulary is hard-edged bevelled steel,
angular and faceted, dusty, chipped at the edges.

So the class hardware is described with the machine's construction words:

- *"a slim folded sensor mast — a narrow vertical column of dark hardware with a small glass
  lens at its top"*
- *"a long cylindrical sighting pod with a glass lens at its front end … mounted on a short
  black bracket, angled forward and down"*
- *"a long low ranging scope cowled directly above the visor — a narrow horizontal tube of
  dark hardware with a glass lens at its front end, on a short arm"*

Carrying words: **dark hardware, narrow column, short black bracket, cowl, faceted wedge of
dark steel, low, narrow**. Breaking words: **bulky, rectangular pod, big lens, unit, box,
module, housing** (unless it is a machined recess).

The class hardware does **not** go on the head: the head keeps its own optics, and asking for a
scope in the visor while keeping the visor lights made round 13 draw one wide cartoon visor
band. Put it on the chest, shoulder, forearm or back. See
`.vault/lessons/2026-11-14-class-hardware-must-use-the-machines-own-vocabulary.md`.

### 3. NEVER name an artifact — clean the reference instead

The edit model reproduces the reference's surface faithfully, **including the parts you
do not want**. The r04_02 reference carries a painted trident emblem, a vent unit on
its upper back, a grid panel on its far shoulder and a small recessed square on its hip
plate. "Keep everything unchanged" copies all four into every output.

The tempting fix — naming them in the instruction — **backfires**:

> "Remove the small painted emblem on the chest plate, the small rectangular screen on
> the upper back and the small square grid panel on the flank, leaving every armour
> plate plain and unmarked."

Round 10 revision 2 used exactly that wording, and the outputs came back with a blue
screen on the upper back that the reference did not even have, and an emblem on the
shoulder. **Naming an artifact teaches the model what that artifact looks like**, and
"leaving every armour plate plain and unmarked" reads as an instruction to mark things.

So the artifact is removed from the **reference**, before it ever reaches the model:

```bash
python tools/clean-reference-artifacts.py --spec work/clean-ref.json
```

The tool flattens each greeble's interior to the colour of its own surrounding frame,
with luminance grain and a gradient fitted from that frame, so the plate keeps its
material and the greeble's silhouette disappears. See **Cleaning a reference** below.

The negative prompt is the right place for artifact words, because a negative says
"do not produce this" and not "produce this":

`emblem, insignia, decal, symbol, lettering, numbers, screen, readout`

### The artifact checklist — look for these in every render

painted emblems and insignia · letter-like marks and pseudo-text · small readout
screens and square grid panels · fake UI overlays · watermark-like stamps ·
decal-shaped patches on armour. Any of these is usually **inherited from the
reference** — so look at the reference, and clean it. Never add a removal clause.

## When the change is structural

A structural edit — sweeping the dorsal fins back, replacing a limb — is the largest
change the model can be asked for, and the one most likely to redraw the machine. Three
rules hold it together.

### 0. First: LOOK at the reference and write down what it already is

**This is where round 10 revision 2 failed, and it is the cheapest mistake to make.**
Its first concept asked the model to *"change only the legs so that the machine stands
upright on two legs instead of four"*. But r04_02 **is already a bipedal humanoid
mech** — two digitigrade legs, a blade arm, a claw arm, a wedge head. The instruction
asked for a change that was not a change. With no coherent edit to make, the model
redrew the machine from scratch and produced "a completely different model".

So before writing any instruction, **open the reference and describe it to yourself**:
how many legs, how many arms, what is in each hand, where the big flat shapes are,
what colour it is. A reference read at full resolution takes ten seconds and saves a
render. Do not trust a description of the reference — especially one written from
memory or from an earlier note.

### 1. Scope it to the part (rule 1 above)

*"Change only the two large flat fins on the machine's back so that they lie swept
backward along the spine and close against the body, instead of standing up and out
from the shoulders."* — never *"give it swept-back fins"* or *"make the fins smaller"*.

### 2. The change must be something the reference demonstrably does NOT already have

If the reference already sweeps its fins back, asking for swept-back fins is the same
dead end as the legs were. Pick a change you can point at in the picture and say
"that is different".

### 3. Point the concept at a reference that already has the target structure

A concept may name its own reference, and it gets its own scale + size + latent chain,
so its output size follows its own reference:

```json
{ "name": "01_biped_hound",
  "reference": "some_bipedal_hound.png [output]",
  "instruction": "Change only the livery to ..." }
```

Editing a near-match is far safer than asking for a structural transformation.

## Cleaning a reference

The reference is the model. Anything on it — a greeble, an emblem, a screen, a letter
— is a thing every output will carry. Clean the reference *before* the first render,
not after.

```bash
python tools/clean-reference-artifacts.py --spec work/clean-ref.json
```

The original file is never modified; the tool writes a new one, which then becomes the
reference (`"<name>.png [output]"` resolves against the output directory, so no copying
is needed).

The spec is a list of regions, each a hole to fill:

```json
{
  "image": "<reference.png>",
  "out":   "<clean.png>",
  "regions": [
    { "fill_box": [518, 462, 554, 505], "ring_box": [511, 455, 561, 512],
      "mode": "flat_grain", "exclude": "saturated", "thr": 90,
      "feather": 3, "max_noise": 3.0,
      "_what": "orange trident emblem -> the bare chest plate" }
  ]
}
```

- `fill_box` — the pixels to replace. Cover the greeble **whole**, rim included, and
  **plus a margin**: the feather band blends the original back in, so a greeble edge
  that falls inside the feather survives as a ghost outline. Filling only the
  *interior* of a raised unit is worse than not filling it at all — a flat face
  inside a raised rim is the shape of a **monitor bezel**, and the model draws a
  screen.
- `ring_box` — where the replacement material is measured from. **It must not overlap
  `fill_box`**: the tool excludes the fill area from the ring, because sampling the
  greeble's own bright edges pollutes the colour estimate and drags the greeble's
  colour back into the plate.
- `exclude` — `dark` (drop the shadowed pixels), `saturated` (drop the painted
  colour) or `none`. Choose the one that isolates the *material* around the hole.
- `mode` — `flat_grain` is the one that works: the hole is filled with the frame's own
  colour, a **plane fitted by least squares** to the frame's value against (x, y), and
  **luminance** grain sized from the frame's residuals around that plane. Per-channel
  noise reads as coloured static; per-row and per-column means read as ribs.

**The repair must be less interesting than the material it replaces.** Anything the
model can read as a pattern — ribs, stripes, a frame, a bezel — becomes an artifact
in the output, because the edit model treats a fine repeating structure in the
reference as *material* and amplifies it.

`material_fill` (OpenCV inpaint, then texture from a material-matched patch) is the
fallback for a hole in a busy area; `context_clone` (Poisson blend of a patch found by
surrounding context) is the weakest of the three — it matches the *neighbourhood* of a
patch, not the material inside it, and will happily paste a rival colour into a plate.

**Always review the cleaned reference at 4–6× zoom before rendering from it.** The
whole point is that it looks like ordinary armour.

### The reference's own backdrop

The edit path re-renders the backdrop, so the **prompt's** house style does not govern
it — the reference picture does. That cuts both ways:

- A reference with a **pool of light** in the corner of its floor (the r04_02 reference
  had one: an orange bottom-left corner, 33 units warmer and 38 units brighter than the
  rest of the floor) comes out **clean** here, because the model paints the backdrop
  afresh. Do not assume it will be inherited.
- A reference whose backdrop is genuinely part of the design — a hangar, a ruined street —
  **is** inherited. For concept art that is the wrong backdrop; use a reference with a
  clean studio backdrop.

Either way, run `tools\check-studio-backdrop.py` on the outputs — the edit path is not
exempt, and the check costs a second.

## Weapon-free concept art

The user's rule: **concept art carries no weapons.** The machine is a design asset; a
weapon is a separate asset, generated on its own when wanted. A concept render shows
the machine **empty-handed** — no blade, no claw, no gun, no shield — with blunt
armoured fists.

If the source reference carries hand-held weapons, **make a weapon-free copy of it
first** and make every variation from that copy. Do not ask one instruction to remove
the weapons *and* change something else — that is two changes, and the second one
collapses the design.

Remove them **one weapon per edit, chained**:

```
pass 1  reference = <clean reference>          change only the long sword-like blade
pass 2  reference = <pass 1's output>          change only the three-talon claw
```

Two rules for the instruction:

- **Identify the weapon by what it is**, never by which side of the picture it is on.
  *"the long sword-like blade"* works; *"the machine's right hand"* does not — the
  model took the other hand.
- **Do not put weapon words in the negative prompt.** The negative is a second
  `TextEncodeMOSSImageEdit` carrying the same reference; a list of weapon words in it
  handed the model the concept of weapons, and the output grew a rack of barrels.

Chassis hardware is not a hand-held weapon: the r04_02 row of barrels along the spine
is part of the machine's silhouette and stays.

## Three things that break this

1. **The reference and the output must be the same size.** The LoRA was trained with
   source and target at one size; with a smaller reference the scene zooms out and the
   edit fails. The builder handles this: `ImageScaleToTotalPixels` scales the reference
   to the target size (snapped to 16 px) and `GetImageSize` drives
   `EmptyFlux2LatentImage`, so the output *is* the reference size. `megapixels` is
   computed as `width * height / 1048576`.

2. **`edit_format` must match the LoRA.** `"Moss-Image-Edit"` for the chinoll / Comfy-Org
   rehost; `"ai-toolkit"` or `"ai-toolkit (kv_cache off)"` for LoRAs trained with
   ai-toolkit. The format decides where the reference lands in the token stream — the
   wrong format means the reference is ignored and you get an ordinary t2i render.

3. **The autogrow slot is `images.image_0`.** `TextEncodeMOSSImageEdit` takes the
   references through a COMFY_AUTOGROW input whose slots are numbered from 0 and whose
   first slot is **required**. Posting `images.image_1` is rejected with
   `required_input_missing` / `"image_0"` and the whole graph is refused before anything
   runs.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `required_input_missing`, `image_0`, `input_name "images.image_0"` | the reference was wired to `images.image_1` | use `images.image_0` |
| The output ignores the reference completely and looks like a fresh t2i render | `edit_format` does not match the LoRA, or the edit LoRA is not loaded | check `edit_format`; check `LoraLoaderModelOnly` lists the file |
| The whole scene is zoomed out / the edit "did not happen" | the reference reached the DiT smaller than the output | let the builder derive the latent size from the scaled reference |
| The machine is redrawn with a new design | the instruction re-describes the subject instead of naming a change, **or it asks for a change the reference already has** | rewrite as "Change only the X to Y. Keep … unchanged."; and open the reference first and write down what it already is |
| The output has screens, emblems or decals that the reference does not have, or has MORE of them than the reference | the instruction **named** the artifact to remove | never name an artifact. Clean the reference with `tools/clean-reference-artifacts.py` and leave the instruction free of removal clauses |
| The edited object is missing or half-drawn | the change asked for a new object rather than a restyle | the edit LoRA is good at colour, outfit, lighting, season and style — it is not documented for adding new objects |
| The set reads as a **different product category** — toy, action figure, knight armour, samurai, retro appliance, mannequin | the keep-list was **vague or false** about the reference: it never mentioned the camera, or it named a pose and plate shape the reference does not have | write the keep-list as a description **measured from the picture**: camera, pose, proportions, plate shapes, material vocabulary, head. Add the drift terms to the negative: `upright posture, standing straight, plate armour, knight, medieval, samurai, action figure, toy, mannequin, smooth plastic, beige plastic, consumer electronics, retro appliance, rounded discs, flat blank panels, human face, anime face` |
| The machine came out **spindly, lanky, anime** | the instruction used a **whole-frame proportion word** ("taller and leaner", "lean and narrow") — the edit path reads it as an order to thin the machine | never describe the frame's proportions as the change. Change **one part**, and restate the mass in the keep-list. See `2026-11-14-the-edit-path-has-a-pull-toward-thinness.md` |
| The new class hardware reads as a **consumer product** — a grey box with a camera lens, a chrome speaker grille | the part was described in **borrowed** vocabulary ("bulky rectangular pod with a big glass lens") | build it from the machine's own vocabulary: "a narrow vertical column of dark hardware", "a long cylindrical sighting pod on a short black bracket", "a low narrow tube cowled above the visor" |
| `500` on submit | the graph dict holds a non-node key | the graph must contain **only** node entries; metadata goes in the sidecar |

## After the task

Close the stack, then log the memory:

```powershell
pwsh -File tools\stop-comfyui.ps1
```

Write the recipe's outcome to `.vault/recipes/<name>-what-worked.md`, and any new
failure mode to `.vault/lessons/`.

**Related:** `.vault/lessons/2026-11-14-a-variation-is-the-design-not-the-palette.md` ·
`.vault/lessons/2026-11-14-a-vague-keep-list-is-worse-than-none.md` ·
`.vault/lessons/2026-11-14-class-hardware-must-use-the-machines-own-vocabulary.md` ·
`.vault/lessons/2026-11-14-the-edit-path-has-a-pull-toward-thinness.md` ·
`.skills/comfyui-generate/SKILL.md`

**Best round so far:** `.vault/recipes/moss-mech-r14-set.json` — the corrected class-variation
set, six concepts, six good renders on the first try.
