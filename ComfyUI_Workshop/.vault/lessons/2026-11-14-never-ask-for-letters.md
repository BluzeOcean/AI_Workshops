# Never tell a diffusion model to draw "letters" — it will invent pseudo-text

**Date:** 2026-11-14
**Symptom:** On `moss_mech_r02_04_bulwark_vanguard`, the shield panel came out with two
rows of marks that read as letters — something like `RODGE` / `AMMOR` rather than runes.
The rest of the set was clean.

**Cause:** the prompt said **"Bold, heavy runic capitals are cut across the face of the
tall shield panel in two rows"**. The model read "capitals" as *letters* and drew letter
forms. A diffusion model has no concept of an invented alphabet, so anything that names a
writing system collapses toward the nearest thing it knows: actual text.

**Fix:** describe the **shape**, never the **category**. Words to avoid: *capitals,
script, lettering, inscription, typography, text, alphabet, words, numbers*. Words that
work: *glyphs, marks, sigils, angular geometric forms, hooked strokes, non-linguistic
carvings, an alphabet that never existed*.

Say it explicitly too: "abstract and non-linguistic — they read as ancient symbols, never
as letters, words or numbers". That negation was already in the shared rune style in this
round and it is what kept the other nine clean; the one concept that asked for *capitals*
is the one that failed.

**Applies when:** any prompt involving runes, glyphs, sigils, tribal markings, alien
writing, UI text, logos, signage or heraldry. Also: the same trap produces garbled
pseudo-text on any prompt that mentions a "brand", "label" or "logo".

**Cost:** one image out of ten, and a concept-art sheet where the hero prop has fake text
on it — the kind of detail a client spots immediately.
