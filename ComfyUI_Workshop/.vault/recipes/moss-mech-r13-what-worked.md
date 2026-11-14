# Round 13 — Class variations of the user's FINAL S01 design

**Date:** 2026-11-14
**Destination:** `V:\04_Projects\EpicJam2026\MechConcept Art`
**Status:** in progress (probe round)

---

## What happened before this round

Round 12 was an attempt to correct the round-10 `r04_02` model: fix the head so it read like
the original, replace mud/rusty dirt with runic decoration, and make the finish metallic rather
than plastic. Nine probe renders were made (`moss_mech_r12_probe_*`).

**The user took a different route.** They adjusted the machine themselves and delivered the final
art as four views placed in the destination folder:

| File | View | Size |
|---|---|---|
| `S01-front.webp` | front, feet apart, arms lowered | 768x1024 |
| `S01-back.webp` | back | 768x1024 |
| `S01-right.webp` | three-quarter rear-right | 768x1024 |
| `S01-left.webp` | three-quarter rear-left | 768x1024 |

These are the **art-style and body-shape reference** for this round. Round 12's probes were
disposed (the user's adjustment superseded them) — nine files, recoverably trashed.

---

## The design, transcribed from the reference

Read off `S01-front.webp` / `S01-back.webp` / `S01-right.webp` by eye. This is what the
reference **already is**, so no instruction may ask for it to change.

**Proportions and pose**
- Bipedal humanoid, roughly 7 heads tall, heavy-set, legs slightly wider than the torso.
- Relaxed upright standing pose, feet planted apart, arms lowered at the sides.
- Digitigrade legs: a long thigh, a reverse-bent knee, a long shin into a broad flat foot.
- Broad, deep chest carried low, with the head **sunk between the shoulders** rather than
  standing on top of them.

**Head**
- Small, low, tucked into the chest below the shoulder line.
- A dark visor recess with **two amber optic lenses** side by side.
- Above and behind the head, on the upper back, **four dark barrel/tube clusters** in a row
  (two pairs), and a boxy sensor module with small amber lights on one shoulder.

**Shoulders**
- Each shoulder carries a **stack of three overlapping curved plates** stepping down over the
  upper arm — the round-10 `03_layered_pauldrons` design, now the house shape.
- The plates are rounded and riveted along their edges.

**Torso**
- Chest: broad orange plates with a dark charcoal central sternum block.
- A dense cluster of **twin large thruster bells** on the upper back, pointing up and back,
  with an iridescent heat-tint inside the cones.
- A **rifle hangs between the legs** (front view) — this is the r04_02 lineage's weapon, still
  present in this final art.
- The right arm (in the three-quarter views) carries a **three-bladed claw**.

**Finish**
- Bright rust-orange painted armour panels over dark charcoal structural parts and joints.
- Crisp bevelled panel lines, visible rows of rivets, a satin painted-metal finish with light
  edge wear — **not** plastic, **not** muddy.
- Studio backdrop: seamless neutral silver-grey, soft even light, soft contact shadow.

---

## Why the edit path, not the text path

The text-to-image path has a documented failure: it drifts into grimdark power armour and
invents its own design (see `2026-11-14-the-text-path-drifts-into-grimdark-power-armour.md`).
Round 08 copied the art style onto generic mechs and the user rejected it with "not the sample".

The user said explicitly: *"you can use this as a image ref for the art style / body shape, and
then design the prompt."* So the reference **image** carries the art direction and the prompt
carries the class. This is the `TextEncodeMOSSImageEdit` path:

- reference `S01-front.webp [output]`
- edit LoRA `moss_image_edit_lora_rank_64_bf16.safetensors`, `edit_format` `Moss-Image-Edit`
- 30 steps, cfg 4.0, `euler` / `normal`, skip layer 22 `0 -> 1`
- **no** 8-step acceleration LoRA on this path

### Load order note (new)

`LoadImage` in ComfyUI 0.45.3 resolves `"name [output]"` against the **output** directory, so a
reference already sitting in the destination needs no copying. The path check is
`folder_paths.exists_annotated_filepath`, which only checks `os.path.exists` — the extension is
irrelevant, so **`.webp` references work**.

The loader first tries `InputImpl.VideoFromFile(...).get_components()`, which opens the file
with PyAV. PyAV opens a `.webp` as a **video stream with codec `webp`** — verified working on
this machine, so the webp is decoded through the video path, not the Pillow fallback. Both
routes would have produced the pixels.

---

## The class brief

The user asked for **variations of this art style for different mech classes**, naming
**sniper** and **stealth backstabber**.

### The two rules that shape every class instruction

1. **One change per edit.** The class is the change; the art direction is the "keep" list.
   Every instruction ends with the same keep-list: the orange-over-charcoal livery, the bevelled
   panel lines and rivets, the satin painted-metal finish with light edge wear, the relaxed
   standing pose, the plain evenly lit silver-grey studio backdrop, the soft contact shadow.
2. **Never name an artifact in an instruction.** Nothing is removed by name. The weapon
   suppression lives in the **negative** prompt, where a negation means "do not produce this".

### Sniper

Tall and lean, where the reference is heavy and low. Narrow deep chest, a long horizontal row
of small glass sensor lenses across the upper chest, a slim low head with one wide horizontal
telescopic optic lens, thin stacked shoulder plates angled back, long thin arms, long
digitigrade legs with high knees and narrow clawed feet. Variant B adds a bulky rectangular
rangefinder pod with a big glass lens bolted flat to one shoulder.

### Stealth backstabber

Low, crouched and flat rather than tall. Variant A crouches forward with hunched shoulders, the
head tucked low, flat angular chamfered plates, matte graphite-and-charcoal finish with only a
narrow muted orange band across the chest, long arms with broad flat forearm shrouds, short
crouched legs with wide flat feet and hooked toe claws, a low slim dorsal fin down the spine.
Variant B is the lean upright version: slim flat shoulders with a single thin plate each, a
narrow flat chest with a recessed vertical sensor slot, a small narrow wedge head with a thin
horizontal optic slit, long thin arms with flat blade-shaped forearm shrouds, long slim legs
with narrow hooked feet.

**Stealth changes the livery on purpose.** A stealth unit that is bright orange is not stealth.
The livery change is the one place the shared keep-list does not apply — the material, the
panel language, the finish and the lighting are still locked.

---

## The negative prompt for this round

```
nsfw, worst quality, low quality, bad anatomy, deformed, extra limbs, duplicated parts,
watermark, text, lettering, signature, emblem, insignia, decal, symbol, numbers, screen,
readout, jpeg artifact, grime, caked dirt, mud, muddy streaks, corroded steel, flaking rust,
brown stain, heavy weathering, plastic toy finish, plastic sheen, injection moulded plastic,
pool of light on the floor, bright corner, dark corner, warm glow on the floor, vignette,
rifle, gun, cannon, sword, blade, spear, weapon, gun in hand, rifle held between the legs
```

This merges the round-10 edit negative (the artifact list, which is what stops an edit from
re-drawing greebles) with the house lighting terms and the new surface terms the user asked for
in round 12 (no mud, no plastic). The weapon terms are here rather than in the instructions,
per the never-name-an-artifact rule.

---

## Probe

Four probes in one submission, one model load:

| Probe | Class | Seed |
|---|---|---|
| `moss_mech_r13_probe_sniperA_00001_.png` | sniper, lean | 44328830928101 |
| `moss_mech_r13_probe_sniperB_00001_.png` | sniper, shoulder pod | 107860336004316 |
| `moss_mech_r13_probe_stealthA_00001_.png` | stealth, crouched | 148020419005064 |
| `moss_mech_r13_probe_stealthB_00001_.png` | stealth, lean | 62485731557634 |

Render → measure → dispose in the same task, per the house rule.

---

## Round numbering note

`r11` was the house-style verification set, `r12` the abandoned correction round. **Round 13 is
this round.** The r11 recipe's note — *"If a real round 11 is started, renumber these to r12 and
make room"* — is stale: r11 happened, r12 was used and is now disposed, so r13 is free.

---

## Probe 1 — the thinness drift

Four probes, one submission, one model load:

| Probe | Wording about the frame | Result |
|---|---|---|
| `sniperA` | "the frame is taller and **leaner**" | spindly, anime-ish, wrong |
| `sniperB` | "the frame is tall and **spare**" + heavy hardware named | good — bulk kept, reads as a sniper |
| `stealthA` | "the frame **crouches forward**" | good — crouched, graphite, reads as stealth |
| `stealthB` | "the frame is **lean and upright but narrow**" | spindly, thin, wrong |

**Two of the four lost the S01 body shape.** The floor measured evenly lit on all four
(bottom-left excess between -3.6 and +3.5, threshold 12), so the house backdrop survived the edit
path intact — the failure was the frame, not the lighting.

Diagnosis and the fix are written up as a lesson:
`.vault/lessons/2026-11-14-the-edit-path-has-a-pull-toward-thinness.md`.

## Probe 2 — the fix

Six probes with the corrected wording:

- **Never describe the whole frame's proportions.** Describe one part; keep the frame.
- **The keep-list restates the mass**, because silence is not a keep:
  *"its broad heavy frame with a deep chest carried low and thick digitigrade legs"*.
- **The keep-list names the signature hardware**: the three overlapping curved armour plates
  stacked on each shoulder, the small head set low between the shoulders with two amber optic
  lenses in its dark visor recess, the row of dark tube clusters above the shoulders.
- **Never contradict the head in the same instruction.** The class hardware goes on the chest,
  shoulder, forearm or back; the head keeps its own amber lenses untouched. Probe 1's `sniperA`
  asked for a wide telescopic optic *and* to keep two amber lenses and got a cartoon visor band.
- **Negative gains the drift terms**: `thin spindly limbs, spindly, lanky, skinny legs, stick
  limbs, anime, chibi, cute, toy, cartoon, glossy candy paint`.

| Probe | Class | Verdict |
|---|---|---|
| `sniperC` | chest lens row + shoulder rangefinder pod | **good** — bulk intact, reads instantly as a sniper |
| `sniperD` | chest lens row + forearm sighting pod | good — the pod reads a little like a bazooka |
| `sniperE` | chest lens row + dorsal sensor mast | **good** — the strongest of the three |
| `stealthC` | crouched, chamfered plates, graphite | **good** — the strongest of the three |
| `stealthD` | forward lean, graphite | good — reads as a standing infiltrator |
| `stealthE` | low crouch, wide dorsal fin | good — the fins read as fins, not wings |

All six kept the S01 bulk. The probes were disposed after the verdict.

## The final set

Six renders, one submission, one model load, fresh seeds:

| File | Class | Carried by |
|---|---|---|
| `moss_mech_r13_01_sniper_rangefinder_00001_.png` | sniper | chest lens row + shoulder rangefinder pod |
| `moss_mech_r13_02_sniper_mast_00001_.png` | sniper | chest lens row + dorsal sensor mast |
| `moss_mech_r13_03_sniper_sighting_pod_00001_.png` | sniper | chest lens row + forearm sighting pod |
| `moss_mech_r13_04_stealth_crouched_00001_.png` | stealth | crouched, chamfered plates, graphite |
| `moss_mech_r13_05_stealth_upright_00001_.png` | stealth | forward lean, graphite |
| `moss_mech_r13_06_stealth_low_crouch_00001_.png` | stealth | low crouch, wide dorsal fin |

Recipe: `.vault/recipes/moss-mech-r13-set.json`.

### The negative prompt

Merged from three sources, and the merge is the point:

- the **round-10 edit negative** — the artifact list (`emblem, insignia, decal, symbol,
  lettering, numbers, screen, readout`), which is what stops an edit re-drawing greebles;
- the **house lighting terms** — the floor-pool list, which the edit path inherits unchanged;
- the **new surface terms** the user asked for in round 12 — `grime, caked dirt, mud, muddy
  streaks, corroded steel, flaking rust, brown stain, heavy weathering, plastic toy finish,
  plastic sheen, injection moulded plastic`;
- the **weapon terms**, which is where the reference's rifle and claw go: `rifle, gun, cannon,
  sword, blade, spear, weapon, gun in hand, rifle held between the legs`;
- the **new drift terms** — `thin spindly limbs, spindly, lanky, skinny legs, stick limbs,
  anime, chibi, cute, toy, cartoon, glossy candy paint`.

## Result

All six delivered. Every one **kept the S01 body shape**: broad heavy frame, deep chest carried
low, thick digitigrade legs, the three overlapping curved armour plates stacked on each shoulder,
the small head set low between the shoulders with two amber optic lenses in a dark visor recess,
the row of dark tube clusters above the shoulders, crisp bevelled panel lines with rows of
rivets, and a satin painted-metal finish with light edge wear.

**Floor measurement** (`tools/check-studio-backdrop.py`, bottom-left brightness excess against
the floor, threshold 12): **-0.1, +1.6, +5.0, +1.3, +0.3, +0.9** — all six pass, all evenly lit.
The edit path inherits the house backdrop from the reference without a floor box of its own.

| Render | Class | Reads as | Notes |
|---|---|---|---|
| `01_sniper_rangefinder` | sniper | **strong** | the shoulder pod with the big glass lens is unmistakably a rangefinder |
| `02_sniper_mast` | sniper | **strong** | the dorsal mast rises behind the shoulders; cleanest of the three |
| `03_sniper_sighting_pod` | sniper | good | the forearm pod reads slightly like a bazooka — the weakest of the three |
| `04_stealth_crouched` | stealth | **strong** | the low crouch, chamfered plates and graphite finish land the class |
| `05_stealth_upright` | stealth | **strong** | a standing infiltrator; the dorsal fin is tall and clean |
| `06_stealth_low_crouch` | stealth | good | the lowest crouch; the wide dorsal fin reads as a fin, not a wing |

### What the class is carried by

- **Sniper** — sensor hardware, never proportions. A shoulder rangefinder pod, a dorsal sensor
  mast, a forearm sighting pod, and a row of small glass lenses recessed across the upper chest.
  All three snipers also kept the reference's tube clusters, which reinforces the machine family.
- **Stealth** — a **low crouched stance**, **matte graphite-and-charcoal livery** with a single
  narrow muted orange band across the chest, **flat chamfered plates** and a **dorsal fin**. The
  livery change is the one place the shared keep-list does not apply: a bright orange stealth
  unit is not stealth.

### The set reads as one production line

The three snipers share the S01's rust-orange livery, charcoal structure, panel language, rivet
rows and head. The three stealth units share a graphite livery, the same orange band, the same
panel language, the same rivets and the same head. So the set is two livery branches of **one
design standard** — which is what makes it read as a fleet rather than six unrelated machines.

---

## Reusable

- The recipe is `.vault/recipes/moss-mech-r13-set.json`. It is **re-runnable end to end**: the
  same six instructions with the same six seeds reproduce these six files.
- The reference lives in the destination as `S01-front.webp` and is referenced as
  `"S01-front.webp [output]"`. No copy into the input folder is needed.
- To extend the fleet, add a concept to the recipe with a **new sensor-hardware class** and the
  same keep-list. Do **not** describe the frame's proportions.
- The four S01 views (`S01-back.webp`, `S01-right.webp`, `S01-left.webp`) are the reference for
  any future change to the S01 design itself, and can be used as per-concept reference overrides
  in the same recipe (`"reference": "<file> [output]"`).

## The class roster

The user asked for **sniper** and **stealth backstabber**, and the message was cut off after
"and". Three designs per class were delivered so each class has a selection rather than a single
coin-flip. If more classes are wanted, the same recipe pattern extends directly — the open
archetypes left in the roster are the heavy assault, the support/artillery and the flanker.

## One thing to flag

The S01 reference carries a **rifle between the legs** and a **three-talon claw arm**. The house
rule is that concept art carries no weapons, and weapons are generated separately on request —
so the **negative prompt** suppresses both and the delivered six are empty-handed. If the user
wants the class weapons carried on these machines (a sniper rifle, a backstabber blade), that is
a separate decision and a separate render: weapons would be **added to the instruction** for
those units, not asked for by naming the reference's own weapon.

