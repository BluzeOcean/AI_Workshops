# A variation of a reference model is the DESIGN, not one attribute of it

**Date:** 2026-11-14
**Symptom:** two consecutive rounds were briefed as *"use this image as the base, to draw
another set of the same variation of this model"*. Both were good-looking and both failed.
Round 07 was *"just applying the color of the ref image into the other r06 units"*; round 08
was *"this round did not produce the result i'm asking for"*.

**Cause:** each round copied **one layer** of the reference and ignored the rest. A reference
model is a **stack** of attributes — chassis, silhouette, head, signature hardware, weapons,
proportions, art style, palette. Round 07 copied the **palette**; round 08 copied the **art
style**; neither copied the **design**. Copying one layer of the stack is not copying the
model, and the user can tell the difference instantly because the chassis was never the thing
that varied.

**Fix:** transcribe the reference model's **design** into the shared clause, feature by
feature, before rendering. Concretely:

1. **List the reference's signature features** — the parts a viewer would name if asked what
   makes this model *this* model (for r04_02: the forward-thrusting wedge torso, the low wide
   visor-band head with cheek tusk spurs, the two huge flat dorsal fins, the row of spine
   weapon tubes, the underslung belly pod, the double-chevron shin plates, the digitigrade
   legs, the blade arm, the three-talon claw).
2. **Put them in the shared clause** so they are identical on every unit of the set. A
   feature described once in the per-concept prompt will drift between units; a feature in the
   shared clause will not.
3. **Tick each one off against the recipe before submitting.** If the head is missing from the
   recipe, the render will not have a head — and you will have paid a render to find out.
4. **Shingle-check the style against the reference's own round** (see
   `2026-11-14-reuse-the-style-suffix-not-just-the-silhouette.md`). Round 09 scored 92.9 %
   against R04.
5. **Keep the layout subject box tall** so the machine builds upright, and use a relaxed
   standing pose so the design is not hidden.

**Then vary only the axis the brief names.** A brief that says "variations" and attaches a
reference is asking for **build** differences — different weapon arms, different head, different
shoulder hardware: five machines on one chassis family. Hue differences are a **colourway
sheet**, which is a different deliverable, and round 07 already showed how that reads.

**Applies when:** a brief names an earlier round or an attached image as the basis for a new
round. Especially when a previous round with the same brief was rejected for "not the sample"
— that verdict almost always means one attribute was copied instead of the design.

**Related:** `.vault/lessons/2026-11-14-reuse-the-style-suffix-not-just-the-silhouette.md` ·
`.vault/lessons/2026-11-14-describe-parts-not-labels.md` ·
`.vault/lessons/2026-11-14-concept-art-wants-a-relaxed-standing-pose.md`
