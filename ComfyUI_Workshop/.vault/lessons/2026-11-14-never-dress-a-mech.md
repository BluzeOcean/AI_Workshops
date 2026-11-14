# Never draw a mech wearing cloth — no capes, shrouds, robes, cloaks, tabards or rags

**Date:** 2026-11-14
**Symptom:** round 04's `r04_03` (shroud reaver) was rejected outright as illogical. The
prompt had asked for *"layered ragged shroud plates that hang like a torn cloak"* and the
model duly produced a mech wearing a cloak. The user's words: *"illogical because mech
wearing cape or clothes is not the direction that I want"*.

**Cause:** draped fabric on a machine reads as the machine **wearing a garment**. A war
machine wearing a garment is a costume, not a machine — and it drags the whole design
towards character-costume illustration instead of hard-surface concept art. The words
*shroud* and *cloak* in the prompt are enough to trigger it; the model does not need a
fabric noun to draw one, a request for hanging plates will supply it.

**Fix:** keep every fabric word out of the prompt. Banned: cloak, cape, shroud, robe,
tabard, mantle, banner, pennant, skirt *(as cloth)*, rag, rags, tatters, cloth, canvas,
linen, draping, flowing, hanging like a cloak.

If a layered or hanging silhouette is wanted, **describe it as armour**, never as cloth:

- "overlapping segmental carapace plates stepping down the spine" → good, reads as armour
- "layered skirt armour of rigid plate" → good
- "ragged shroud plates hanging like a torn cloak" → bad, reads as a garment

The word "hanging" and "draping" are also fabric cues on their own — say "stepping down",
"overlapping", "stacked" instead.

**Applies when:** writing any prompt for a machine, robot or vehicle. Also watch
*tattered*, *ragged*, *torn* and *flowing* — they pull in the same direction.
