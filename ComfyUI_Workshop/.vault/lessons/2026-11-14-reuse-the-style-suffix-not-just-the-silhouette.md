# "Use round N as the basis" means reuse its STYLE SUFFIX, not just its silhouette

**Date:** 2026-11-14
**Symptom:** round 07 was briefed as *"use r04_02 to draw another round of 5 of the same
variation"*. The user rejected it: *"they do not look like the sample that I asked for"*. The
set was good-looking, in the right colours, with the right weapons and the right shoulders —
and it was still wrong.

**Cause:** the silhouette was copied but the **art language was not**. Round 07 was built with
round **06's** `styleSuffix` — matte ceramic composite, bone white and sand olive, rounded
forms, chalky dust. Round 06's own five machines are white-and-olive hardsuit mechs, so
round 07 came out looking like *those* machines on all fours. Round 04's `r04_02` is angular
rust-orange brutalist slab armour with rivets, weld seams, exposed hydraulics, chevron
stripes and heavy battle damage — a completely different film.

Reusing a design means reusing **the whole `styleSuffix`**, because that block *is* the art
style: materials, construction vocabulary, weathering, lighting and backdrop. Copying only
the subject description reproduces the *shape* and loses the *film*.

**Fix:** when the brief names an earlier round as the basis, copy that round's `styleSuffix`
**verbatim** and then add only what the new round changes. Do not reach for the most recent
round's suffix by habit.

**Verify before rendering.** Measure the overlap of the new suffix against the intended
source, using shared 6-word shingles:

```
R04: 196/211 shared shingles -> 92.9% overlap
R06: 107/318 shared shingles -> 33.6% overlap
```

Round 08 (the corrected round) scores **92.9 % against R04** and **33.6 % against R06** —
so the art language is provably the intended one before a single image is rendered. This
costs two seconds and catches the exact failure that cost round 07.

**Applies when:** a round is briefed as a variation of an earlier one, and especially when
the workspace now holds several distinct `styleSuffix` blocks from different rounds.

**Related:** the parts of round 07 that the user **did** keep — weapons named by their
parts, defined pauldrons, the livery structure — were carried into round 08 unchanged.
Only the style suffix was wrong.
