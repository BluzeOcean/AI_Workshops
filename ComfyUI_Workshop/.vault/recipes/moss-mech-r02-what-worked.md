# Runic decoration works on MOSS-Image — but "runic capitals" produced pseudo-text

**Date:** 2026-11-14
**Status:** active
**What was run:** Round 02 of the EpicJam2026 mech concept set — the round-01 concept
prompts **verbatim**, plus a rune layer, on a different seed range.

```
node tools\build-moss-set.mjs --recipe .vault\recipes\moss-mech-r02-set.json --out work\moss-mech-r02.json
node D:\ComfyUI\harness\comfyctl.mjs submit work\moss-mech-r02.json
```

- Same model stack, 960×1280, 8 steps, cfg 2.5, `er_sde` / `simple`, seeds 82001–82010
- Destination: `V:\04_Projects\EpicJam2026\MechConcept Art`
- 10 images, ~2 minutes, one model load

**Result:** the rune layer reads clearly on all ten — knotwork bands, rune columns, circular
mandalas, chevron lattices, all as recessed channels with a faint glow. The set still reads
as one roster: same silhouettes, same finish, same studio treatment, one new design layer.

## What worked

**Keeping the prompt in layers.** The recipe composes
`promptPrefix + concept + runes + runeStyle + styleSuffix`, with `runeStyle` shared across
the set and `runes` per concept. That is what made the change legible: the concept
descriptions were copied **verbatim** from round 01, so the only variable that moved was
the decoration. It also made a wrong round cheap to spot.

**Saying where the runes go, per machine.** "Thin bright runic bands climb the shin plates
and run the full length of the blade arm" beats "the mech has runes" every time — the model
places the motif where you asked. The stealth mech (`03_phantom_infiltrator`) got
*unlit shallow carvings* and came out as barely-visible dark glyphs, which is exactly the
brief. A single shared rune description would have made all ten glow equally.

**Saying what the runes are NOT.** "Abstract and non-linguistic — they read as ancient
symbols, never as letters, words or numbers" did most of the work. See the trap below.

## The trap

**"Bold, heavy runic capitals" on the shield produced pseudo-text.** On
`04_bulwark_vanguard` the shield carries two rows of marks that read as letters — the
model tried to render *capitals* rather than glyph shapes. It is the closest thing to
readable text in the whole set, and it is exactly what the prompt asked for by saying
"capitals".

**Fix for round 03:** never use a word that means letters — *capitals, script, lettering,
inscription, typography*. Say *glyphs, marks, sigils, angular geometric forms, non-linguistic
carvings* instead, and describe the **shape** rather than the category: "angular hooked
strokes and straight angular marks, like an alphabet that never existed".

## Also worth knowing

- This is **not a strict A/B**: the seeds differ between rounds (81001–81010 vs
  82001–82010), so the underlying forms moved too. To compare one variable, hold the seed
  and change only the prompt layer — but then ComfyUI's execution cache will replay the
  cached nodes unless the changed node's inputs differ (a changed prompt does change the
  CLIPTextEncode node, so it re-renders; the KSampler cache key includes the seed only).
  Test it rather than assuming.
- The round-01 weakness is still there: `02_lance_artillery`'s cannon and
  `06_warden_marksman`'s rifle still read as bare poles. Naming a weapon's *parts* is the
  fix that was never tried.

**Reuse when:** the next concept round, or any task that adds a design layer to an existing
set.
