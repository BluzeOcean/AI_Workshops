# Round 13 FAILED — the keep-list was written from house rules, not from the reference

**Date:** 2026-11-14
**Status:** rejected by the user, superseded by round 14

---

## What the user said

> "I don't like the R13 generations. They look like the Mac in the 80s, more like a plate
> armour than a mech machine."

Six renders were delivered: `moss_mech_r13_01_sniper_rangefinder_00001_.png` through
`moss_mech_r13_06_stealth_low_crouch_00001_.png`.

## The cause was MY keep-list, not the model

Put the reference and the output side by side, and the difference is not subtle:

| | reference `S01-front.webp` | round 13 output |
|---|---|---|
| camera | **high three-quarter, looking DOWN** at the machine | straight-on eye-level front |
| pose | **hunched forward**, head thrust down, prowling | standing upright, arms at sides |
| proportions | **compact and dense**, ~5.5 heads tall | tall, ~7 heads, upright |
| shoulder plates | **flat angular faceted slabs** flaring up and out | **round overlapping discs** |
| head | **small dark cowled module**, thrust forward and low | **big humanoid helmet** on a neck |
| surface | hard-edged bevelled steel, exposed actuators, hose bundles, cable looms, dust in the recesses | **smooth rounded blank panels** |
| read | a heavy war machine | a plastic armour figurine |

Every one of those is a line I wrote into the keep-list.

### The specific errors

1. **"its relaxed upright standing pose with feet apart and arms lowered"** — that is a
   *direct instruction to stand upright*. The reference is hunched forward with its head
   thrust down. I asked for the opposite of the reference and the model obeyed me.
2. **"the three overlapping curved armour plates stacked on each shoulder"** — *curved*
   produced round overlapping discs, which is a knight's pauldron. S01's plates are flat,
   angular and faceted, flaring up and out.
3. **"the small head set low between the shoulders"** — still produced a big humanoid helmet
   standing above the shoulders. S01's head is a small dark **cowled** module thrust forward
   and down.
4. **"its satin painted-metal finish"** with no hard-edge vocabulary gave smooth rounded
   forms with big blank panels — the 80s consumer-plastic read. S01 is hard-edged bevelled
   steel with exposed black mechanical structure.
5. **"its broad heavy frame"** was too vague, so the model used its own default: a stocky
   upright mannequin.
6. **The camera was never mentioned at all**, so the model reverted to its default
   straight-on eye-level front view — which is not the reference's camera.

## The rule

**Write the keep-list from the reference, measured from the picture — never from a house
rule, and never from memory.**

This is the same lesson as
`.vault/lessons/2026-11-14-check-what-the-reference-already-is.md`, but it bit in the
opposite direction. That lesson said *"do not ask for what the reference already has."*
This one says *"do not describe the reference as something it is not."* The house keep-list
for the r04_02 reference said *"relaxed upright standing pose"*, and S01 is not upright, so
copying that phrase in was wrong.

**A vague keep-list is worse than no keep-list.** The model fills the gap with its own
defaults, and its defaults are an upright armour mannequin with smooth plastic plates.
"broad heavy frame" is a gap. "compact and dense, about five and a half heads tall, short
thick legs, crouched and splayed wide" is a keep.

### The three keep-list things to write down, every time

1. **The camera.** Where is it, how high, what angle? S01: *"the same high three-quarter
   front view from above with the camera looking down on the machine at a steep angle so the
   tops of its shoulders and its back are visible and the whole machine sits small in the
   frame with air around it."*
2. **The pose and the proportions.** S01: *"its hunched prowling stance with the torso
   pitched forward, the head thrust forward and down between the raised shoulders... its
   compact dense proportions, about five and a half heads tall."*
3. **The material and the plate shapes.** S01: *"hard-edged bevelled steel armour, angular
   and faceted with sharp corners and no rounded moulded forms... exposed black mechanical
   structure between the plates - hydraulic pistons, actuators, hose bundles and cable
   looms."*

### And the negative needs the new failure mode

Round 13's negative had the thinness terms. It did not have the terms for what the output
actually did wrong. Added for round 14:

```
upright posture, standing straight, vertical stance, facing the camera squarely,
plate armour, plate armor, knight armour, knight armor, medieval armour, samurai armour,
medieval, samurai, paladin, action figure, toy, figurine, mannequin, model kit,
plastic model, smooth plastic, glossy plastic, injection moulded plastic, beige plastic,
consumer electronics, retro appliance, retro computer, vintage computer case,
soft rounded moulded shapes, rounded discs, round overlapping discs, rounded pauldron discs,
balloon, bulbous, flat blank panels, large untextured surfaces,
human face, anime face, cartoon face, cute face
```

## The other thing that went wrong

The class was carried by **sensor hardware**, and that worked — but the hardware was
described in words the model could read as *appliance*:

- *"a bulky rectangular rangefinder pod with a big glass lens at its front"* → a **grey
  box with a camera lens**, which is what a rangefinder on a Mac would look like.
- *"a long horizontal row of small glass sensor lenses set into a recessed strip across its
  upper chest plate"* → a **row of chrome circles**, which reads as a speaker grille or a
  floppy-disk slot.
- The final sniper reads as a **product photograph of a machine**, not a war machine,
  because every added element was a clean grey box with a glass circle.

The class hardware has to be **part of the machine's own construction vocabulary** — the
same bevelled steel, the same black hardware, the same dusty finish — not a plastic box
bolted on. Round 14 describes it that way: *"a slim folded sensor mast... a narrow vertical
column of dark hardware"*, *"a long cylindrical sighting pod... mounted on a short black
bracket"*.

## What survives

- The **edit path itself** works. The reference carried the art direction, the panel
  language, the rivet rows, the studio backdrop and the lighting through every one of the
  six renders, and the floor measured evenly lit on all six.
- The **class is carried by hardware, not proportion** — confirmed twice.
- The **keep-list naming the signature parts** works — the tube clusters, the layered
  shoulder plates and the head all survived.

## What goes in the vault instead of the images

The six renders are rejected work. They are disposed. The measurement that matters is the
one in this file.

Related: `.vault/lessons/2026-11-14-the-edit-path-has-a-pull-toward-thinness.md` ·
`.vault/lessons/2026-11-14-check-what-the-reference-already-is.md` ·
`.vault/recipes/moss-mech-r13-set.json`
