# Naming an artifact in an edit instruction ADDS that artifact

**Date:** 2026-11-14
**Symptom:** Round 10 revision 2 asked every concept to *"Remove the small painted
emblem on the chest plate, the small rectangular screen on the upper back and the
small square grid panel on the flank, leaving every armour plate plain and unmarked."*
The outputs came back with **a blue screen on the upper back that the reference did
not even have**, and a crimson emblem on a shoulder plate. Revision 1, which had no
removal clause at all, copied the reference's own three greebles faithfully — which
is what prompted the clause in the first place. Both directions failed.

**Cause:** an edit instruction is a description of the target image. Naming "the small
rectangular screen" gives the model the *concept* of a screen, and it is happy to
place one — especially anywhere you pointed. "Leaving every armour plate plain and
unmarked" reads as an instruction to mark things, not the opposite. The edit LoRA is
not a masked inpainter; it is told what the result should contain.

**Fix:** remove the artifact from the **reference image** before the model ever sees
it, and leave the instruction free of removal clauses. Use
`tools/clean-reference-artifacts.py` (`flat_grain` mode): flatten each greeble's
interior to the colour of its own surrounding frame. Artifact words belong in the
**negative** prompt, where a negation means "do not produce this":
`emblem, insignia, decal, symbol, lettering, numbers, screen, readout`.

**Applies when:** an output carries a screen, emblem, decal, pseudo-text, grid panel
or watermark that the reference does not have — or has more of than the reference
does. Look at the reference first: if it is there, clean the reference; if it is not,
the instruction named it into existence.

See also `.vault/lessons/2026-11-14-a-fill-must-be-smoother-than-the-plate.md`.
