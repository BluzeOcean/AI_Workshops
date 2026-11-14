# "Looks completely different" means a different LOOK, not a different SUBJECT

**Date:** 2026-11-14
**Symptom:** asked for "another set of 10 that looks completely different", the agent
delivered industrial machinery — a forklift, an excavator, a tunnel boring machine, a
flatbed cargo sled — and the user rejected it: *"They are not Mac robot machine that I asked
for they turn into just vehicles."* The instruction was: *"The instruction of looks
completely different does not mean a totally different type of machine. it still has to fall
under mech, war machine, robot category."*

**Cause:** the agent read "different" as "different category" and rewrote the **subject**
instead of the **look**. Changing "heroic humanoid battle mech" to "industrial utility
chassis" is not a stylistic variation — it is a different brief, and it produced vehicles.

**Fix — separate the two things a round can change:**

1. **The category — FIXED.** The subject stays inside mech / war machine / robot, always.
   This is the brief and it is not a variable.
2. **The look — variable.** Change design language (slender/riveted/brutalist), setting
   (studio void / hangar / ruined city), finish (clean / weathered / scorched), camera
   (hero 3/4 / low angle / rear), and proportion (sleek / squat / colossal).

**Guard the category in the prompt itself, every time.** Round 04 anchored all five
concepts with *"a bipedal war machine with a recessed cockpit, articulated arms and legs and
heavy mounted weapon systems"* plus a named weapon per machine. Round 03 had no such anchor,
so nothing stopped the model drifting toward plant equipment.

**Also:** the machine family is *not* a free axis. It can change **within** the category —
bipedal to quadrupedal, light scout to heavy siege walker — but it cannot leave it.

**Applies when:** asked for a variation round, a second pass, "something different", or a
redo that must still hit a stated subject category.

**Related:** `2026-11-14-a-new-round-must-change-the-brief.md` recommended changing the
machine family as one of four axes. That advice is superseded on this point — the family
may change within the category, but the category is fixed.
