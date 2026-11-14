# A fill must be SMOOTHER than the plate, or the model will amplify it into a grille

**Date:** 2026-11-14
**Symptom:** after the r04_02 reference was cleaned of its painted trident emblem, the
chest plate came out **ribbed** — fine vertical streaks where the emblem used to be —
and the first render made from that reference turned those streaks into a hard
**grid of small squares**, a screen-like panel that the reference never had. A second
case: flattening only the *inside* of the raised vent unit left its raised rim in
place, so the result was a flat tan face inside a dark border — literally a **monitor
bezel** — and the model duly drew a screen on the upper back.

**Cause:** two separate faults, both in the fill.

1. The fill's gradient was estimated with **per-row and per-column means**. A column's
   mean is taken from too few pixels, so the estimate carries the ring's own vertical
   structure and the fill comes out ribbed. The edit model treats any fine repeating
   structure in the reference as *material* and amplifies it.
2. **Only the interior of a raised unit was filled.** A flat face with a raised rim
   around it is the shape of a screen. The model copies the shape, not the intent.

**Fix:**

- Fit a **plane** (least squares of value against x and y) to the ring, not per-row
  and per-column means. A plane is smooth by construction.
- Size the grain from the ring's **residuals around the plane**, and make it
  **luminance** noise — independent per-channel noise reads as coloured static.
- Fill a raised unit **whole**, rim included, so no rectangle is left. A flat patch of
  the right colour is safe; a bezel is not.

**Applies when:** repairing a reference image before an edit — and generally whenever
a patch has to be painted over. The rule is: **the repair must be less interesting
than the material it replaces.** Anything the model can read as a pattern — ribs,
stripes, a frame, a bezel — becomes an artifact in the output.

See also `.vault/lessons/2026-11-14-never-name-an-artifact-clean-the-reference.md`.
