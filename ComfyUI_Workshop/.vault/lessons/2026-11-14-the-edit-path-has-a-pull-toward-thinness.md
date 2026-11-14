# The edit path has a pull toward thinness

**Date:** 2026-11-14
**Round:** 13 probe 1
**Status:** applies to every edit-path concept

---

## What happened

Round 13 probe 1 asked the MOSS edit model to turn the user's S01 reference into a **sniper**
and a **stealth infiltrator**. Two of the four probes came back as spindly, lanky, long-legged
machines with a glossy toy finish — a completely different product from the S01 reference, which
is a broad, heavy, thick-limbed machine with a deep chest carried low.

| Probe | Wording about the frame | Result |
|---|---|---|
| `sniperA` | "the frame is **taller and leaner**", "long and thin" | spindly, lanky, anime-ish, wrong |
| `sniperB` | "the frame is **tall and spare**", but heavy hardware named | **good** — kept the bulk, read as a sniper |
| `stealthA` | "the frame **crouches forward**", "short and crouched" | **good** — crouched, graphite, read as stealth |
| `stealthB` | "the frame is **lean and upright but narrow**", "long and slim" | spindly, thin, wrong |

## Why

The model reads a **whole-frame proportion word** as an instruction to change the proportions.
Every time the instruction said the frame was lean, thin, slim or narrow, the machine lost mass.
Every time the instruction described a **specific shape or a specific piece of hardware** while
leaving the frame alone, the machine kept the reference's build.

`sniperA` and `stealthB` are not failures of wording quality — they are good sentences. They are
failures of **what the sentence describes**. "Taller and leaner" is a description of the frame, so
it changed the frame. "A bulky rectangular rangefinder pod with a big glass lens bolted flat onto
one shoulder" is a description of one part, so only that part changed.

## The rule

**Never describe the whole frame's proportions in an edit instruction. Describe one part, and
keep the frame.**

- WRONG: "Change the machine into a tall, lean, slim silhouette."
- RIGHT: "Change only the machine's chest and one shoulder so that it reads as a long-range
  sniper: a long horizontal row of small glass sensor lenses is set into a recessed strip across
  its upper chest plate, and a bulky rectangular rangefinder pod with a big glass lens at its
  front is bolted flat onto one shoulder. Keep its broad heavy frame with a deep chest carried
  low and thick digitigrude legs, ..."

The keep-list must carry the mass explicitly: **"its broad heavy frame with a deep chest carried
low and thick digitigrade legs"**. Silence is not a keep — the model fills the gap with the
house average, and the house average is thin.

## The class is carried by HARDWARE, not by silhouette

A sniper reads as a sniper because of a **rangefinder pod**, a **sighting pod**, a **row of glass
lenses** or a **sensor mast** — not because it is tall and thin. A stealth unit reads as stealth
because of a **low crouched stance**, a **matte graphite finish** and a **dorsal fin** — not
because it is narrow.

When you want the class to differ from the reference, add hardware. Never subtract mass.

## A second trap: never contradict the head in the same instruction

`sniperA` asked for "one wide horizontal telescopic optic lens set into its dark visor recess"
AND to keep "two amber optic lenses in its dark visor recess". The model resolved the conflict
by drawing a single wide cartoon visor band across the whole face.

The class hardware goes on the **chest, shoulder, forearm or back**. The head keeps its own
amber lenses, untouched, and the instruction does not mention the head's optics at all.

## Third finding: the negative prompt needs the drift terms

The model drifts toward thin and toy-like unprompted. The round-13 negative gained:

```
thin spindly limbs, spindly, lanky, skinny legs, stick limbs, anime, chibi, cute, toy,
cartoon, glossy candy paint
```

The floor measured **evenly lit on all four probe-1 renders** (bottom-left excess between
-3.6 and +3.5, threshold 12) — the house backdrop survives the edit path unchanged.

## How to apply

- Edit instructions name **one part to change**, then a keep-list that **restates the frame's
  bulk and the reference's signature hardware** by name.
- If a part must survive, **name it in the keep-list**. An unmentioned part is not guaranteed.
- Never use a whole-frame proportion word as the change.
- Never ask for the head's optics and keep the head's optics in the same sentence.
