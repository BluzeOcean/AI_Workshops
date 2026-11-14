# Never ask for a change the reference already has

**Date:** 2026-11-14
**Symptom:** Round 10 revision 2's first concept asked the model to *"change only the
legs so that the machine stands upright on two legs instead of four"*. The user
rejected the result as *"a completely different model that doesn't really absorb the
style of the ref image"*. The machine in the output was a different design entirely.

**Cause:** **the reference r04_02 is already a bipedal humanoid mech** — two digitigrade
legs, a blade arm, a claw arm, a forward-thrusting wedge head with a visor. It has
never been a quadruped. The instruction asked for a change that was not a change, so
the model had no coherent edit to make and fell back to the only thing it could do:
redraw the machine from scratch. A **false premise** in an instruction is worse than a
vague one, because it forces a full re-generation.

Note that the *notes* for this round had carried r04_02 as a "quadrupedal war hound"
for several rounds — a description written from memory that had never been checked
against the picture.

**Fix:** before writing any instruction, **open the reference and write down what it
already is** — how many legs, how many arms, what is in each hand, where the big flat
shapes are, what colour it is. Then pick a change you can point at in the picture and
say "that is different". A ten-second look saves a render.

**Applies when:** any reference-driven edit, and any brief that names a structure to
add or remove. Verify the structure is absent in the reference before asking for it.
