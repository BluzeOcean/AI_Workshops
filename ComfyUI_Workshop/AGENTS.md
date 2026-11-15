# AGENTS.md — ComfyUI_Workshop

**This workspace generates assets with ComfyUI. Any agent can open this folder, read this
file, and be productive — no tutorial, no prior context, no hand-holding needed.**

Read this file completely before touching anything. It is the entire onboarding.

You do not need to know ComfyUI. You need to know **where the files go**, **how to bring
the server up**, and **how not to waste ten minutes on a mistake**. Those three things are
below.

---

## 1. The map

| Path | What it is |
|---|---|
| `.skills/` | **Procedures.** One folder per skill, each with a `SKILL.md`. A skill is a repeatable task — "generate a mech concept sheet", "swap a background", "batch a sheet". Read `.skills/README.md` before writing one. |
| `.vault/` | **The memory bank.** A log of what worked and what did not — lessons, decisions, model notes, recipes. It is **written after a task, not read before one** (see §7). |
| `tools/` | The scripts. `boot-comfyui.ps1` brings the stack up, `stop-comfyui.ps1` closes it and frees the RAM/VRAM, `build-moss-graph.mjs` builds a runnable graph, `comfy-boot.cmd` is the detached launcher. |

**`.vault/` is a memory bank, not a checklist.** You do not read it at the start of a task —
that would waste context on a log that is mostly irrelevant to what you are doing right now.
You *write* to it when a task ends, and you *search* it when something breaks or the user asks
whether it has happened before.

### This workspace holds no media

**No images, no video, no audio, no meshes, no model files — ever.** This workspace is
instructions, skills and a memory bank. Generated media goes to the **destination outside
this folder**, and the workspace only ever keeps the *text* that describes how it was made.

Concretely:

- Never write a `.png`, `.jpg`, `.webp`, `.mp4`, `.wav`, `.glb`, `.safetensors` or any other
  binary into this tree.
- A recipe in `.vault/recipes/` is **text**: the prompt, the layout boxes, the settings, the
  seed. Not the picture it produced.
- If a task produces media, the media lives in the destination the user confirmed, and this
  workspace keeps the recipe that produced it.
- Intermediate graph JSON is scratch. Build it in `work/` (git-ignored), not in `.vault/`.

---

## 2. The destination — read this twice

**The destination is the folder generated files land in. You must know it BEFORE you generate.**

- If the user gave you a destination → use **exactly** that path. Character for character.
- If the user did **not** → **ASK.** Do not guess. Do not fall back to a default. Do not reuse
  the destination from an earlier task in this session.

This is not politeness, it is a hard constraint:

> ComfyUI's `folder_paths.get_save_image_path()` calls `is_within_directory(output_dir, ...)`
> and **raises** `"Saving image outside the output folder is not allowed"` for anything outside
> `--output-directory`. The destination is therefore fixed **at server boot**, and changing it
> requires a restart.

So the order is always: **confirm destination → boot → generate.**

```
pwsh -File tools\boot-comfyui.ps1 -OutputDir "<destination>"
```

If the server is already up but was started with a different destination, `boot-comfyui.ps1`
says so in a warning. That warning is real — take it seriously, and either use the server's
existing destination (if the user agrees) or restart it with `-Restart`.

---

## 3. Bringing up the stack (headless)

ComfyUI here is **a server, not an app**. It runs with no browser and no console window.

```powershell
# boot it, pointed at the task's destination
pwsh -File tools\boot-comfyui.ps1 -OutputDir "V:\04_Projects\EpicJam2026\MechConcept Art"

# check it
node D:\ComfyUI\harness\comfyctl.mjs health
```

The boot script does the whole sequence, in the only order that works:

1. Probe `http://127.0.0.1:8188/system_stats`. **If it answers, leave it alone.** Never kill
   or restart a server someone else started.
2. If down, launch it detached and silent via `tools\comfy-boot.cmd`.
3. Wait for it to answer (it has to load every custom node first — 30–90 s).
4. Ensure the MCP bridge is up on `http://127.0.0.1:9000/mcp`.
5. Print health.

**ComfyUI must come up before the MCP bridge.** The MCP server exits after 60 s if ComfyUI is
not reachable, and its supervisor respawns it every 60 s forever. If the MCP port is dead and
ComfyUI is also dead, that is the reason — fix ComfyUI first, and the MCP will bind itself.

Two more things about the boot:

- **It is silent.** `comfy-boot.cmd` uses `start "" /B` — no console window, no browser
  (`--disable-auto-launch`). If you ever see a terminal flashing open and closing, something
  launched ComfyUI *without* `/B`. That is a bug; do not copy that pattern.
- **It survives your session.** The process is detached from the shell that started it, so it
  keeps serving after your tool call returns and after the session ends. That is deliberate:
  a second task in the same session finds a warm server instead of paying the boot again.
- **The script may never return.** `boot-comfyui.ps1` has been observed to hang indefinitely
  after the boot has actually succeeded (the MCP supervisor respawns its child forever, so
  any wait on it never completes). A timed-out boot is **not** a failed boot — check
  `node D:\ComfyUI\harness\comfyctl.mjs health` and the `--output-directory` echoed by
  `GET /system_stats`. **Do not re-run it** to "fix" the hang: that starts a second ComfyUI
  on port 8188. See `.vault/lessons/2026-11-14-boot-script-may-not-return.md`.

### Closing the stack — after every task

**When the task is finished, close the headless ComfyUI and its MCP port, and release the
RAM and VRAM.** Do not leave a 12 GB VRAM / 22 GB RAM server running for a task that is over.

```powershell
pwsh -File tools\stop-comfyui.ps1
```

It stops the MCP supervisor first (otherwise it respawns its child and port 9000 never
closes), then the ComfyUI server, then reports how much VRAM and RAM came back. Measured
on 2026-11-14: **13.2 GB of VRAM and ~15 GB of RAM released**, ports 8188 and 9000 both
free. (The VRAM figure varies with what else the machine is running.)

The stack is detached and long-lived precisely so it can *survive* until the task is done —
not so it can outlive it. Leaving it up burns 12 GB of VRAM that another local model could
use, and 22 GB of RAM that the rest of the machine wants.

Scope: this only ever stops what **this workspace** started (tracked in
`tools\.comfyui.pid`). A ComfyUI the user started themselves is never touched — the script
says so and leaves it running.

---

## 4. Two ways to talk to it

### 4a. The MCP bridge (preferred — 44 tools)

`http://127.0.0.1:9000/mcp`, streamable HTTP, stateless. Register it and you get
`mcp__comfyui__*` tools: `generate_image`, `generate_song`, `regenerate`, `view_image`,
`list_assets`, `get_asset_metadata`, `get_queue_status`, `get_job`, `cancel_job`,
`list_models`, `get_defaults`, `set_defaults`, `list_workflows`, `run_workflow`,
`get_publish_info`, `set_comfyui_output_root`, `publish_asset`, and more.

`.mcp.json` in this folder registers it for agents that support MCP.

> **The MCP tool list freezes when your session starts.** If the server was down when the
> session opened, `mcp__comfyui__*` never appears — for the rest of that session. This is not
> a bug you can fix by restarting. **Use `comfyctl` instead; it always works.**

### 4b. `comfyctl` — the escape hatch that always works

Zero-dependency Node CLI, no install, no handshake, works from any directory:

```powershell
node D:\ComfyUI\harness\comfyctl.mjs health          # ComfyUI + MCP liveness
node D:\ComfyUI\harness\comfyctl.mjs tools            # full tool surface
node D:\ComfyUI\harness\comfyctl.mjs schema <tool>    # input schema
node D:\ComfyUI\harness\comfyctl.mjs call <tool> '{}' # invoke a tool
node D:\ComfyUI\harness\comfyctl.mjs get /object_info # raw ComfyUI REST
node D:\ComfyUI\harness\comfyctl.mjs submit graph.json # run a raw graph, wait, print outputs
```

### 4c. Raw ComfyUI REST

`http://127.0.0.1:8188` — `GET /system_stats`, `GET /object_info`, `POST /prompt`,
`GET /history/<prompt_id>`, `GET /queue`, `POST /interrupt`.

**Use `127.0.0.1`, never `localhost`.** On this machine `localhost` costs ~2050 ms per request
because of the IPv6→IPv4 fallback stall. The MCP server makes two ComfyUI calls per tool call,
so it was adding ~4 s of dead time to *every* call.

---

## 5. Generating an asset

### The MOSS-Image workflow (this workspace's default)

Source of truth: `D:\ComfyUI\ComfyUI\user\default\workflows\moss_image_t2i_bbox_8_steps.json`
(canvas format). The runnable form is generated from it — never hand-edit a canvas JSON.

**One image:**

```powershell
node tools\build-moss-graph.mjs `
  --prompt "<PROMPT>" `
  --layout .vault\recipes\<layout>.json `
  --width 960 --height 1280 --seed <SEED> `
  --prefix <name> `
  --out work\graph.json

node D:\ComfyUI\harness\comfyctl.mjs submit work\graph.json
```

**A set of images — one submission, one model load.** The UNET, LoRA, CLIP and VAE are
shared across every branch, so a 9.7 GB model is loaded once and the whole set renders
back to back:

```powershell
node tools\build-moss-set.mjs `
  --recipe .vault\recipes\<set>.json `
  --out work\set.json

node D:\ComfyUI\harness\comfyctl.mjs submit work\set.json
```

**Review the set by opening the images themselves.** Do **not** build a contact sheet —
the user does not want one, and tiling the set into a single montage costs tokens and
delivers a summary of something they can already see. Open the renders and look at
them.

If you ever need a contact sheet, `tools\contact-sheet.py` exists, but it is **not**
part of the workflow and must not be run without being asked:

```powershell
D:\ComfyUI\python_embeded\python.exe tools\contact-sheet.py `
  --dir "<DESTINATION>" --out "<TEMP>\sheet.png" --cols 5 --label
```

### Variations of a reference model — use the reference IMAGE, not the prompt

If the brief names a reference model or attaches a reference picture, do **not** try to
rebuild it out of prompt text. MOSS-Image has an instruction-edit LoRA and ComfyUI has
native support for it (ComfyUI ≥ 0.42.1): `TextEncodeMOSSImageEdit` encodes the edit
instruction **together with the reference image**, and the reference reaches the DiT as
reference latents. The picture is then the source of the design and the prompt only says
what to **change**.

```powershell
node tools\build-moss-edit-set.mjs `
  --recipe .vault\recipes\<recipe>.json `
  --out work\set.json

node D:\ComfyUI\harness\comfyctl.mjs submit work\set.json
```

- Edit LoRA: `D:\.models\loras\MOSS-Image-Edit\moss_image_edit_lora_rank_64_bf16.safetensors`,
  loaded with `LoraLoaderModelOnly` — **model only**, and **not** together with the 8-step LoRA.
- `edit_format`: `Moss-Image-Edit` for this LoRA; `ai-toolkit` for ai-toolkit-trained ones.
- 30 steps, cfg 4.0, `euler` / `normal`, skip layer 22, `0 → 1`.
- The **reference and the output must be the same size** — the builder scales the reference
  to the target size and derives the latent from it.
- The instruction follows the training phrasing: *"Change only the X to Y. Keep \<list\>
  unchanged."* Describe only the change, then list what must survive it.
- `LoadImage` resolves `"name.png [output]"` / `"name.png [input]"` against those
  directories, so a reference already in the destination needs no copying.
  **The extension does not matter** — the existence check is `os.path.exists`, and PyAV opens a
  `.webp` as a video stream with codec `webp`, so a `.webp` reference loads fine.

**Never describe the whole frame's proportions in an edit instruction.** The edit path has a
strong pull toward thinness: "the frame is taller and leaner" and "the frame is lean and
upright but narrow" both produced spindly anime mechs that had lost the reference's build. A
whole-frame proportion word is read as an instruction to change the frame. So:

- **Describe ONE part and keep the frame.** *"Change only the machine's chest and one shoulder
  so that it reads as a long-range sniper: a long horizontal row of small glass sensor lenses is
  set into a recessed strip across its upper chest plate, and a bulky rectangular rangefinder pod
  with a big glass lens at its front is bolted flat onto one shoulder. Keep its broad heavy frame
  with a deep chest carried low and thick digitigrade legs, ..."*
- **The keep-list must RESTATE the mass and the signature hardware by name.** Silence is not a
  keep — an unmentioned part is not guaranteed, and the model fills the gap with the house
  average. Name the frame's bulk and every part that must survive, every time.
- **The class is carried by SENSOR HARDWARE, not by silhouette.** A rangefinder pod, a sighting
  pod, a row of glass lenses, a dorsal sensor mast. Adding hardware reads; subtracting mass does
  not. A sniper reads as a sniper because of the pod, not because it is tall and thin.
- **Never contradict the head in the same instruction.** Probe 1 asked for "one wide horizontal
  telescopic optic lens" AND to keep "two amber optic lenses" and got a cartoon visor band.
  Class hardware goes on the chest / shoulder / forearm / back; the head keeps its own optics.
- Add the drift terms to the **negative**: `thin spindly limbs, spindly, lanky, skinny legs,
  stick limbs, anime, chibi, cute, toy, cartoon, glossy candy paint`.
- **The keep-list is a DESCRIPTION of the machine, measured from the picture.** A vague
  keep-list is worse than none: silence means the model fills the gap with its default, a
  vague keep-list means it fills the gap with its default *according to your wrong words*.
  Round 13 said "relaxed upright standing pose" and "overlapping **curved** armour plates"
  about a reference that is **hunched** with **flat angular** plates, and never mentioned
  the camera at all — the set came back as upright orange-and-cream knight mannequins
  (*"they look like the Mac in the 80s, more like a plate armor than a mech machine"*).
  Every keep-list covers six things, **measured from the reference image**:
  **the camera** (*"the same high three-quarter front view from above with the camera
  looking down on the machine at a steep angle"*) · **the pose** (*"hunched prowling
  stance, torso pitched forward, head thrust forward and down between the raised
  shoulders"*) · **the proportions** (*"about five and a half heads tall, short thick legs,
  a broad deep torso"* — not "broad heavy frame") · **the plate shapes** (*"flat angular
  faceted slabs", not "curved"*) · **the material vocabulary** (*"hard-edged bevelled steel,
  angular and faceted with sharp corners and no rounded moulded forms, exposed black
  mechanical structure between the plates"*) · **the head** (*"small dark cowled head
  module thrust forward and low", not "helmet"*).
- **Class hardware is built from the MACHINE's own vocabulary.** A part described in borrowed
  vocabulary inherits its associations: round 13's *"bulky rectangular rangefinder pod with a
  big glass lens"* came back as a **grey appliance box with a camera lens**. Use *"a narrow
  vertical column of dark hardware"*, *"a long cylindrical sighting pod on a short black
  bracket"*, *"a low narrow tube cowled above the visor"*.
- The house **"relaxed upright standing pose"** rule is a **text-path** rule. On the edit path
  the reference's own pose IS the pose — see
  `.vault/lessons/2026-11-14-concept-art-wants-a-relaxed-standing-pose.md`.

Full procedure: `.skills/moss-reference-variation/SKILL.md`.

What the graph is:

| Node | Setting |
|---|---|
| `UNETLoader` | `moss_image_sft_bf16.safetensors` |
| `LoraLoader` | `MOSS-Image-8-step\lora.safetensors` (model + clip, 1.0) |
| `CLIPLoader` | `qwen3.5_9b_bf16.safetensors`, type `moss_image` |
| `VAELoader` | `flux2-vae.safetensors` |
| `SkipLayerGuidanceDiTSimple` | single layer `22`, `0 → 0.5` |
| `KSampler` | 8 steps, cfg 2.5, `er_sde` / `simple`, denoise 1 |
| `CreateBoundingBoxes` → `MOSSImageLayoutPrompt` | layout control (see below) |

**Layout boxes are the quality lever.** The canvas workflow's box chain is a no-op for plain
text-to-image because the canvas holds zero boxes. Supply `--layout` and the model is told
*where things go*: a background box, then a subject box. `characterBoxes` labels a subject box
as a character. Box coordinates are **fractions 0..1** of the canvas; order matters
(background first, foreground last).

### The backdrop — character concept art gets NO background

**Character concept art uses the clean studio backdrop.** No environment, no scenery, no
ground detail, no props — just the machine and its shadow on a seamless neutral
silver-grey backdrop.

The house backdrop, verbatim:

> seamless neutral silver-grey studio backdrop, plain and empty, smooth vertical gradient
> from light grey at the top to mid grey at the floor, soft contact shadow pooled under the
> subject, one uniform matte neutral grey with no horizontal gradient across the floor,
> evenly lit across the whole frame with no pool of light and no bright corner, no landscape,
> no sky, no horizon, no scenery, no buildings, no props

And the house lighting clause, verbatim:

> studio key light high above and slightly to the left, falling on the machine only, cool soft
> fill on the camera-facing side, a bright thin edge highlight running down the left side of
> the machine, flat even overhead ambient lighting on the floor, the floor a matte plane of one
> uniform neutral grey with no horizontal gradient across it, all the way to every edge of the
> frame, with no directional falloff, no pool of light, no bright corner, no dark corner and no
> reflection

**Why:** the user asked for this directly — *"for character concept art, i dont need any
background, i prefer the background of round 1 and 2"*. A backdrop competes with the subject
and makes the machines read as product shots or vehicles instead of designs.

This also **protects the category**. Round 03 changed both the subject (industrial vehicles)
and the backdrop (a ruined city) in one move, and the result read as vehicles. A hangar or a
ruined street gives the model permission to build a machine that belongs to that place. The
studio backdrop takes that permission away: it asks for *a design*, and the design has to
carry the war-machine read on its own.

So when a round must look completely different, change the **design language, the finish and
the camera** — never the subject category, and never the backdrop. The biggest lever of all
is the **archetype roster** (see below).

### The floor must be EVENLY LIT — no pool of light

The house style used to say *"a warm golden rim light running down the left edge of the
silhouette"* and *"soft bounced light from the grey floor"*. Those two phrases let the model
place a **warm light low and to the left**, and it duly painted the **bottom-left corner of
the floor orange and ~40 levels brighter** than the rest of the floor — with the backdrop's
left side warm too. The user called it unwanted ground lighting.

Measured on the r04_02 reference: the bottom-left corner was **33 units warmer and 38 units
brighter** than the rest of the floor. Every text-to-image round carried that phrasing, so
every one of them could produce the pool.

**The cause is not the colour of the light — it is the word *source*.** A light that is
described as a thing *in the scene* gets a position, and a positioned light rakes the studio
floor. So the fix is not "make the rim light white"; it is **stop describing the rim as a
light at all**. The house clause says *"a bright thin edge highlight running down the left
side of the machine"* — a **property of the machine**, not a source in the room. A property
cannot spill onto the floor.

Three things together hold the floor even (measured on the worst of three seeds):

| Lever | bottom-left excess |
|---|---|
| rim as a light source, lateral key | +14.8 (FAIL) |
| rim as a machine property | +10.4 |
| …plus a layout box for the floor | +9.0 |
| …plus the stronger negative prompt | **+5.7** (PASS) |

So the house recipe also carries **a third layout box for the floor strip** — the floor is a
region of the frame that otherwise has no instruction of its own, and the layout system is
the strongest lever available:

```json
{ "x": 0.0, "y": 0.87, "w": 1.0, "h": 0.13, "type": "obj",
  "desc": "the studio floor, a flat matte plane of one single neutral grey tone, identical from the left edge of the frame to the right edge, evenly lit, no gradient across it, no pool of light, no bright corner, no reflection" }
```

It goes **between the backdrop box and the subject box**, and the subject's `characterBoxes`
index shifts from `"2"` to `"3"`.

Give every concept recipe a `negative` field as well — the text-to-image rounds used to run
with an **empty** negative prompt, so every prohibition was only a suggestion inside the
positive style suffix. The house negative, verbatim:

```
nsfw, worst quality, low quality, bad anatomy, deformed, extra limbs, duplicated parts,
watermark, text, lettering, signature, pool of light on the floor, bright corner, dark corner,
warm glow on the floor, lens flare, sunbeam, spotlight on the floor, directional falloff on
the floor, horizontal gradient, floor gradient, lighting gradient, uneven lighting, mirror
reflection on the floor, vignette, corner glow, glow in the corner, hotspot on the floor,
floor hotspot, bright lower corner, hot spot in the corner, uneven corner lighting, shadow
gradient across the floor
```

Note `mirror reflection on the floor`, never a bare `reflection` — the floor is supposed to
carry a soft **contact shadow**, and a blanket "no reflection" can take that with it.

**The edit path keeps its own negative.** The r10 edit recipes carry a *different* negative
(`emblem, insignia, decal, symbol, lettering, numbers, screen, readout`) that is what stops
an edit from re-drawing the greebles it was supposed to preserve. Do not paste the house
negative over it.

**Verify every render**, not every other round:

```powershell
D:\ComfyUI\python_embeded\python.exe tools\check-studio-backdrop.py --dir "<DESTINATION>" --pattern "moss_mech_r"
```

It measures the floor's bottom-left and bottom-right corners against the rest of the floor
and exits 1 when a corner is warm or bright against it.

**One seed is not a result.** The spread between seeds is as large as the spread between
wordings — the same wording measured +6.7 on one seed and +14.8 on another. Any change to
the house style must be rendered on **at least three seeds** before it is believed, and the
seed that already failed must be among them. The per-concept `styleSuffix` override in
`build-moss-set.mjs` exists for exactly this: one submission, one model load, the wording as
the only variable.

### Designing a mech that is not generic

Two hard rules came out of round 04, where the user kept **one** of five machines.

**1. Never draw a mech wearing cloth.** No capes, shrouds, robes, cloaks, tabards, banners
or rags. Draped fabric on a machine reads as a costume, not a machine. If a layered or
hanging silhouette is wanted, describe **armour** — *"overlapping segmental carapace plates
stepping down the spine"*, never *"hanging like a cloak"*. The same trap is set by
*tattered*, *ragged*, *torn*, *draping* and *flowing*.

**2. Keep the humanoid form. Vary the ARCHETYPE, not the body plan.** The user wants
**humanoid mechs** — rounds 01–02 were humanoid and were accepted. *"Too generic / similar
to previous rounds"* does **not** mean *abandon* the humanoid form. It means the archetype
**repeated**: round 04's three rejects were a second titan, a second shielded vanguard and a
second lancer — all already made in round 01. The one keeper was the only machine whose
class was new.

So: keep a **running roster of archetypes already used** and never repeat one; vary the
**design language** (finish, construction vocabulary, proportions, palette) instead; and
name the archetype explicitly in every concept. Then give each machine a **combat role**
and a **weapon** — *"built to run down infantry, carries a recessed rotary cannon pod"*.

**3. Lock the style across the set.** If every concept carries its own palette and its own
weathering sentence, the model faithfully draws five machines from five different films.
Put the livery, materials, construction vocabulary, camera and lighting **only** in the
shared `styleSuffix`, and let each concept describe just archetype, pose and weapon.

*Exception — a colourway sheet.* When the user asks for **colour variations of one
approved design** (round 07), the lock moves: keep the art style, the construction
language, the camera and the lighting shared, and keep the **livery structure** shared
too (one dominant colour over one dark structural colour with one worn accent, same
stripes) — but let only the **hues** vary per concept. The set still reads as one
production line while giving five distinct colourways.

**When the brief names an earlier round as the basis, copy THAT round's `styleSuffix`
verbatim.** Reusing a design means reusing the whole suffix — the suffix *is* the art
style, and copying only the subject description reproduces the shape while losing the
film. Round 07 got this wrong: it copied r04_02's silhouette but round 06's suffix, so the
set came out looking like round 06's white-and-olive mechs on all fours. **Verify the
overlap before rendering** — count shared 6-word shingles of the new suffix against the
intended source (round 08 scored 92.9 % against R04 and 33.6 % against R06). Two seconds,
and it catches the failure before the render does.

**4. Describe every weapon and part BY ITS PARTS, never by its label.** "A long blade
arm" renders as an unidentifiable slab; "a rotary cannon — six short barrels around a
central spindle, a boxy breech, a slotted muzzle shroud" renders as a rotary cannon.
Same for machine parts: *"angular armour blades sweeping back"* becomes random spikes,
while *"square bevelled shoulder pauldrons, each built from two stacked plates with a
recessed circular housing on the outer face and a raised ridge along the top edge"* becomes
a pauldron. If a reader could not sketch it from the words, the model will not either.
Give long weapons a stated orientation and mount too, or they end up edge-on.

**5. The SUBJECT box sets the machine's build.** It is a spatial instruction: a **tall** box
(w:h ≈ 0.55–0.75) gives an upright humanoid, a **wide** box (w:h ≥ 1.2) gives a low
horizontal quadruped. Humanoid mechs need tall subject boxes.

**6. Pose the subject RELAXED and UPRIGHT.** Concept art wants the design, so the default
pose is a relaxed standing pose: weight even on both legs, feet planted slightly apart,
body square and tall, arms lowered. A weapon held across the body hides the chest, the
hips and the leg construction — which is the whole point of a concept sheet. If a draw is
rejected for its pose, **do not escalate the action; stand the subject down.** Say where the
weapon sits *relative to the body* ("the saber hanging straight down at its side, the blade
running parallel to the leg and clear of the body"), not just that the machine carries it.

**7. A reference model is a STACK of attributes. Copy the DESIGN, not one layer of it.** A
reference image or an earlier round is a stack: chassis, silhouette, head, signature hardware,
weapons, proportions, art style, palette. Two rounds failed the same brief by copying only one
layer — round 07 copied the **palette** onto round 06's units, round 08 copied the **art
style** onto generic mechs — and the user rejected both with "not the sample". When a brief
names a reference, **transcribe the design feature by feature**: list the signature features
(the parts a viewer would name if asked what makes this model *this* model), put them in the
shared clause so they are identical on every unit, and **tick each one off against the recipe
before submitting** — a missing feature in the recipe is a missing feature in the render, and
you will have paid a render to find out. Then vary only the axis the brief names: a brief that
says "variations" and attaches a reference wants **build** differences (different weapon arms,
different head, different shoulder hardware — one chassis family), while hue differences are a
**colourway sheet**, a different deliverable.

Round 04's one keeper was a quadrupedal war hound — the only *new* archetype in the set. The
four rejects were three repeated archetypes and one cloaked raider.

**8. When a reference model is NAMED, feed the reference IMAGE.** A prompt can only
*describe* a design, so a prompt-only "variation" inherits whichever single attribute the
description happened to carry — the palette in round 07, the art style in round 08 — and
invents the rest. Round 09 hand-transcribed the design feature by feature and came much
closer, but it was still the model *imagining* the reference from words. The mechanism
that actually inherits the design is `TextEncodeMOSSImageEdit` with the reference PNG
loaded as an image: the picture is the source of the chassis, the head, the signature
hardware and the livery, and the prompt only states the change. **Use the image path
whenever a reference model is named.** See §5 and
`.skills/moss-reference-variation/SKILL.md`.

**9. CLEAN THE REFERENCE BEFORE YOU USE IT, AND NEVER NAME AN ARTIFACT.** The edit
model reproduces the reference's surface faithfully — *including the parts you do not
want*. The r04_02 reference carries a painted trident emblem, a vent unit on its upper
back, a grid panel on its shoulder and a recessed square on its hip; every output
carried all four. Naming them in the instruction **backfires**: round 10 revision 2
asked for "remove the emblem, the screen and the grid panel, leaving every armour
plate plain and unmarked", and the renders came back with *more* screens and an emblem
on the shoulder. Naming an artifact teaches the model what that artifact looks like.
Remove it from the reference instead, with `tools\clean-reference-artifacts.py`, and
leave the instruction free of removal clauses. Artifact words belong in the **negative**
prompt, where a negation means "do not produce this".

**10. OPEN THE REFERENCE AND WRITE DOWN WHAT IT ALREADY IS, BEFORE YOU WRITE THE
INSTRUCTION.** Round 10 revision 2's first concept asked the model to *"change only the
legs so that the machine stands upright on two legs instead of four"* — and r04_02 **is
already a bipedal humanoid mech**: two digitigrade legs, a blade arm, a claw arm, a
wedge head. Asking for a change that is not a change leaves the model with no coherent
edit to make, so it redrew the machine from scratch — the "completely different model"
the user rejected. Ten seconds of looking at the reference saves a render. Never trust
a description of the reference, especially one written from memory.

**11. CONCEPT ART CARRIES NO WEAPONS.** The user asked for this directly: *"I prefer not
to have any weapons. The weapon will be asked to generated separately if I need it."* The
machine is a **design** asset; a weapon is a **separate** asset, generated on its own
when wanted. So a concept render shows the machine **empty-handed** — no blade, no
claw, no gun, no shield — with blunt armoured fists.

This applies to the **reference** too. If the source reference carries hand-held
weapons, make a weapon-free copy of it first and make every variation from *that*
copy — do not ask one instruction to remove the weapons *and* change something else.
Hand-held weapons come off; the chassis's own hard-mounted hardware (the r04_02 spine
barrel cluster) is part of the silhouette and stays. When the reference itself is
weapon-free, do not put weapon words in the **positive** prompt; keep them in the
**negative** prompt, where a negation means "do not produce this".

### Models

Centralised at `D:\.models`, wired in through `ComfyUI\extra_model_paths.yaml`.
`clip:` and `text_encoders:` both point at `D:\.models\clip/`. The per-install `models/`
folders are nearly empty — **do not conclude a model is missing from them.**

---

## 6. Rules that will save you the time

These are not style preferences. Each one cost real time to learn.

1. **`POST /prompt` is not a validation call — it executes.** A 200 with empty `node_errors`
   means *accepted and queued*, and the job is now running, loading a 20 GB model. To validate
   a graph without running it, compare it against `GET /object_info`. If you do POST, say so
   first.

2. **An MCP timeout is not a failure.** Read the state first (`get_queue_status`,
   `get_job`, `GET /queue`). Retry only when the state proves the action did not land. A blind
   retry after an `open_workflow` timeout produced a duplicate tab — exactly the kind of thing
   the user notices and complains about.

3. **MCP tools *return* errors, they do not raise them.** A failure arrives as
   `{"error": "..."}` with `isError: false`. A naive `isError` check reports a false success.
   `comfyctl` exits non-zero when it finds a payload-level error — check the exit code.

4. **Never kill a process you did not start.** Restarting ComfyUI is the user's call. If it is
   down, boot it. If it is up, use it.

5. **`asset_id`s are session-scoped and in-memory.** They die when the MCP server restarts.
   Never persist one across a restart.

6. **Never write a source-of-truth file into a cleanup list.** Cleanup lists get an explicit
   allowlist, one path per line.

7. **Identify files by content, not by assumption.** "Stray" is a conclusion, not an observation.
   Read a file before deleting or overwriting it — it may be another agent's work in progress.

8. **`/object_info` is the schema of record.** Never guess a node's input names. Fetch them.

9. **Custom nodes only load at ComfyUI startup.** To test a node without a restart, import the
   module directly with the embedded interpreter. A restart is still the user's call.

10. **Do not trust a fixed path to where models live.** Check `extra_model_paths.yaml` first —
    a folder that looks empty may be aliased to a populated one.

11. **Close the stack when the task is over.** A finished task ends with
    `pwsh -File tools\stop-comfyui.ps1`. MOSS-Image parks ~12 GB of VRAM and ~22 GB of
    RAM in the server; leaving that resident is stealing from whatever else the machine
    wants to do. See §3.

12. **Releasing VRAM is cheap; reloading it is too.** `POST /free` with
    `{"unload_models": true, "free_memory": true}` hands back ~11 GB of VRAM and ~17 GB of
    RAM in about 8 seconds, and the next render only costs ~6 s extra to reload. Use it
    whenever another job needs the GPU — `tools\free-vram.ps1` measures it.

13. **An autogrow input's slots start at 0, and slot 0 is required.** A `COMFY_AUTOGROW_V3`
    input (`TextEncodeMOSSImageEdit`'s `images`, the logic nodes, Bernini's
    `reference_images`) takes its values under a dotted key — `images.image_0`, not
    `images.image_1` as a substitute. Wiring the first value to slot 1 leaves slot 0
    missing and the graph is refused with `required_input_missing` before the GPU is
    touched. The error's `details` field names the exact slot the node wants.

14. **Every file in the destination is named `moss_mech_rNN_<concept>_00001_.png`.** The
    round number is how the user reads the folder, so **do not invent a prefix** for a
    side render — a house-style probe, an A/B test, a check. **Every file that lands
    there carries a round number, probes included**: a probe of round 12 is
    `moss_mech_r12_probe_head_00001_.png`, never `moss_mech_probe_head_00001_.png` and
    never `moss_something`. If it is worth keeping, give it a round number and a recipe
    that reproduces it (round 11 is exactly that: three house-style verification renders
    of one concept, documented in `.vault/recipes/moss-mech-r11-set.json`). If it is not
    worth keeping, **dispose it in the same task**. A probe that leaves thirty files named
    `moss_mech_floorprobe*` in the delivery folder is worse than no probe: it buries the
    rounds the user came to look at and it breaks the one naming convention they rely on.

    **Render → measure → dispose, in one task.** A verification render is scratch. It is
    allowed to exist for the minutes it takes to measure it, and not one minute longer.
    Keep the *measurements* in the vault; the pixels are not evidence worth keeping.

15. **A style probe renders ONE approved concept.** The probe exists so that only the
    thing under test varies. Using a **rejected** round's concept as the test subject
    means the probe is measuring a design the user has already thrown away, and the
    renders inherit its shape — which is how a floor-lighting probe ended up looking like
    Warhammer Space Marines. See
    `.vault/lessons/2026-11-14-the-text-path-drifts-into-grimdark-power-armour.md`.

---

## 7. Write back — always log the memory after a task

**When a task is complete, log the memory. This is not optional.** The vault is how this
workspace gets better instead of repeating itself.

The vault is a **memory bank**: a running record of what worked and what did not, so a future
agent can trace the history and solve a problem that has already been solved. It is
**appended to after each task**, not consulted at the start of each task.

| You learned | Put it in |
|---|---|
| A mistake that cost time, money or a wrong delivery | `.vault/lessons/YYYY-MM-DD-slug.md` |
| A decision about how this workspace works | `.vault/decisions/YYYY-MM-DD-slug.md` |
| A model that works well, and the settings that did it | `.vault/model-notes/` |
| A prompt or layout that produced something good | `.vault/recipes/` |
| A repeatable procedure worth repeating | `.skills/<name>/SKILL.md` |
| A rule about how to behave here | **this file** |

### When to write

**After every completed task.** Even a task that went fine — especially one that went fine.
"What worked" is as valuable to record as "what did not": the next agent needs to know that
*this* model at *these* settings with *that* layout produced a good result, and which seed
range and prompt shape were responsible.

Write at least one entry per task that produced a durable fact. If genuinely nothing durable
came out of a task, say so in the task summary instead of writing a filler file.

**Then commit it** — see §8. One task, one commit, and only when something substantial
landed.

### When to read

**Only when it will pay for itself:**

- **Something went wrong** and you suspect it has happened before — search the vault before
  guessing at a fix.
- **The user asks** what has worked before, what to avoid, or for a specific recipe.
- **You are about to repeat an expensive operation** (a long render, a big model load) and
  want to reuse a known-good setup.

Search it with `grep`, not by reading it end to end:

```powershell
Select-String -Path .vault\lessons\*.md -Pattern 'destination' -SimpleMatch
```

### Never overwrite a lesson

Add a new one and mark the old decision `superseded`. A later agent has to be able to see
what was true *then*, and why it stopped being true.

Format for a lesson:

```markdown
# <one-line title>

**Date:** YYYY-MM-DD
**Symptom:** what was observed, literally.
**Cause:** why it happened.
**Fix:** what to do instead — an instruction, not a story.
**Applies when:** the trigger that means this is relevant again.
```

Format for a "what worked" entry — same shape, different headings:

```markdown
# <one-line title>

**Date:** YYYY-MM-DD
**What was run:** the exact command / graph / settings.
**Result:** what came out, and where it landed.
**Reuse when:** the situation where this is the right starting point.
```

---

## 8. Commit policy

**One commit per substantial change, committed and pushed at the end of a task.** This repository is a
working record, not a commit stream — a commit should mean *something meaningful changed*,
not *the agent saved a file*.

**Commit when something substantial lands:**

- a new skill is added, or an existing skill is materially revised
- a lesson is written — something cost time, money, or a wrong delivery
- a decision is added, or an existing one is superseded
- a recipe or a workflow is added
- a tool is added, or a tool's behaviour changes
- a rule in this file changes

**Do not commit:**

- a typo, a reformat, a whitespace change
- scratch files (`work/` is git-ignored anyway)
- a file that is still being edited in this task
- the same entry rewritten three times while the agent is still figuring it out

**Cadence: one task, one commit.** If a task produced three lessons, a new skill and a
recipe, that is **one** commit, not five. If a task produced nothing substantial, do not
commit at all — an empty commit is noise.

**How:**

```powershell
cd V:\04_Projects\Workshops
git status --short              # look before staging
git add ComfyUI_Workshop        # ONLY the folder you worked in
git commit -m "<type>(workshop): <what changed>"
git push origin master          # then push it
```

- **Stage only your own workshop.** Other workshops usually have untracked files of their
  own; `git add -A` would sweep them into your commit.
- **Push after every commit.** The remote is `origin`
  (`https://github.com/BluzeOcean/AI_Workshops.git`) and `master` tracks `origin/master`.
  A commit that stays local is work the next machine does not have. If the push fails,
  report it — **never force-push**.
- Commit on the branch you are on (`master`). This is a personal working repo — do not
  create side branches unless the user asks.
- Never commit media. The `.gitignore` already excludes it; verify with `git status` after
  staging.

**Message:** `<type>(workshop): <what changed in one line>`, where the type is `feat`,
`docs`, `fix` or `chore`. Say *what* changed, not that something changed.

---

## 9. Reference

| What | Where |
|---|---|
| ComfyUI install | `D:\ComfyUI\ComfyUI\main.py` |
| Python (embedded) | `D:\ComfyUI\python_embeded\python.exe` |
| ComfyUI REST | `http://127.0.0.1:8188` |
| MCP bridge | `http://127.0.0.1:9000/mcp` |
| Zero-dep control CLI | `D:\ComfyUI\harness\comfyctl.mjs` |
| Canvas workflows | `D:\ComfyUI\ComfyUI\user\default\workflows\` |
| Models | `D:\.models` (see `extra_model_paths.yaml`) |
| Boot the stack | `tools\boot-comfyui.ps1` |
| **Close the stack (after every task)** | `tools\stop-comfyui.ps1` |
| Free VRAM without stopping | `tools\free-vram.ps1` |
| Measure VRAM / RAM | `tools\measure-resources.ps1` |
| Build one graph | `tools\build-moss-graph.mjs` |
| Build a graph set | `tools\build-moss-set.mjs` |
| Build an edit graph **+ a ComfyUI canvas workflow** | `tools\build-moss-edit-workflow.mjs` |
| Review a set | open the images — **no contact sheet** |
| Check the studio floor is evenly lit | `tools\check-studio-backdrop.py` |
| Clean greebles off a reference | `tools\clean-reference-artifacts.py` |
| Operating notes on the install itself | `D:\ComfyUI\AGENTS.md` |
| Past-mistake guards | `D:\ComfyUI\.claude\mistakes\INDEX.md` |

> `D:\ComfyUI\AGENTS.md` is a separate, older document about the ComfyUI *install*. It still
> holds true and is worth reading for the install-specific traps. This file governs *this
> workspace*. Where they disagree about process lifetime, this file is the newer one — but
> the safe reading of both is the same: **boot when down, never kill what you did not start.**
