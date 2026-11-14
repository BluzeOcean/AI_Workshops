# A weapon or a machine part must be described BY ITS PARTS, or it renders as an ambiguous blob

**Date:** 2026-11-14
**Symptom:** round 04's one keeper, `r04_02` (the quadrupedal war hound), was rejected on
two counts by the user: *"the right arm weapon it is holding — currently it looks very
ambiguous and not sure what it is holding"* and *"a more defined parts on the shoulder
because there are just random spike sticking out"*.

**Cause:** the prompt named the **things** but not their **construction**.

- The arm was described as *"one long blade arm"*. A blade with no stated geometry has
  nothing to draw but a flat slab, so the model drew an unidentifiable wedge.
- The shoulders were described as *"angular armour blades sweeping back over the
  shoulders"*. A blade sweeping back is a spike, so the model drew spikes — three of
  them, at random angles, with nothing to anchor them to the body.

**Fix — describe the assembly, not the label.** Name the weapon *and* its parts, and
build the shoulder as a stack of plates that has a reason to exist:

| instead of | write |
|---|---|
| "a long blade arm" | "a heavy rotary cannon, a cluster of six short barrels arranged around a central spindle with a boxy breech block and a slotted muzzle shroud" |
| "angular armour blades sweeping back over the shoulders" | "square bevelled shoulder pauldrons, each built from two stacked plates with a recessed circular housing on the outer face and a raised ridge running along the top edge, and a hard shoulder cap over the joint" |

The rule: **if a reader could not sketch it from the words, the model will not either.**
"Rotary cannon" alone is a label; "six short barrels around a central spindle" is a
sketch. The same applies to every part of a machine — the number of parts, their
arrangement, and what they attach to.

**Also: a weapon needs a stated ORIENTATION and a stated MOUNT.** "held pointing down and
forward away from the body so its whole shape is clear" is what keeps a long gun from
ending up edge-on and unreadable, and "a squared shoulder mount" is what stops it
floating.

**Applies when:** writing any prompt for a machine, robot or vehicle, and whenever a draw
is rejected for being "ambiguous" or for having "random spikes".
