# Concept art wants a RELAXED STANDING pose — an action pose hides the design

> **SCOPED (2026-11-14, round 13).** This lesson is still right **on the text path** — round 06's
> saber pose is the evidence, and a text-to-image concept sheet does want a relaxed, upright
> standing subject.
>
> It is **wrong on the edit path**, and applying it there cost round 13. When the machine comes
> from a **reference image**, the reference's own pose **is** the pose: the S01 reference is a
> hunched prowling machine, and round 13's keep-list said "relaxed upright standing pose" — a
> direct instruction to stand the machine up. The model obeyed, and the set read as upright
> mannequins.
>
> On the edit path, write the reference's **measured** pose into the keep-list instead:
> *"hunched prowling stance with the torso pitched forward, the head thrust forward and down
> between the raised shoulders, the arms hanging down and forward with heavy clenched grippers,
> and the short thick legs crouched and splayed wide with the broad feet planted far apart."*
>
> Read [`2026-11-14-a-vague-keep-list-is-worse-than-none.md`](2026-11-14-a-vague-keep-list-is-worse-than-none.md).
> The text below is preserved as the record of what was believed then, and where it stops
> applying.

**Date:** 2026-11-14
**Symptom:** round 06's `03_plasma_duelist` took **three** draws to land:

1. *Forward-leaning charge, saber held low across the legs* — rejected: *"it has the
   wrong pose"*.
2. *Coiled fighting stance, saber swept up in a rising guard* — rejected: *"the sword is
   blocking the view. For concept art, i prefer a more relaxed standing pose like the
   others."*
3. *Relaxed upright standing, saber hanging down at the side* — accepted.

**Cause:** an action pose puts the weapon **across the body**, and a weapon across the body
hides the thing a concept sheet exists to show — the chest, the hips, the leg construction
and the read of the silhouette. The model obeyed perfectly every time; the brief asked for
the wrong shot. Note that the natural "fix" for "wrong pose" is to add **more** action, and
that made it worse.

**Fix:** for character and mech concept art, the default pose is a **relaxed, upright
standing pose** — weight even on both legs, feet planted slightly apart, the body square
and tall, both arms lowered, the weapon held down at the side running parallel to the leg
and clear of the body. A dynamic pose is the exception and needs a reason.

**Applies when:** writing a concept-art prompt for a machine or a character, and whenever a
draw is rejected for its pose — **do not escalate the action, stand the subject down.**

**Related:** the same logic applies to a weapon that crosses the frame in any way. Specify
where the weapon sits *relative to the body*, not just that the machine carries it.
