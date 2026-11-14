# An upright bipedal humanoid reads as a generic stock mech — the SILHOUETTE is what makes a concept specific

> **SUPERSEDED (2026-11-14). This lesson drew the wrong conclusion and cost a round.**
>
> It concluded that the upright bipedal form must be banned. **It must not.** The user
> wants **humanoid mechs**, and rounds 01–02 were humanoid and were accepted. The real
> cause of round 04's three "too generic / similar to previous rounds" rejects was that
> their **archetype class had already been made in round 01** — a second titan, a second
> shielded vanguard, a second lancer. The only keeper was the one machine whose class was
> new.
>
> Acting on this lesson produced round 05: a set of quadrupeds and hexapods that the user
> called *"useless"*, and that was disposed of.
>
> Read
> [`2026-11-14-similar-means-repeating-an-archetype.md`](2026-11-14-similar-means-repeating-an-archetype.md)
> instead. It keeps the two sound observations below — that surface detail does not fix a
> generic read, and that the layout box aspect ratio steers the machine's build — but
> replaces the rule with: **keep the humanoid form, vary the archetype.**
>
> The text below is preserved as the record of what was believed then, and why it stopped
> being true.

**Date:** 2026-11-14
**Symptom:** round 04 produced five war mechs on the house studio backdrop. The user kept
**exactly one**: `r04_02` (the quadrupedal war hound). `r04_01` (colossal bipedal siege
walker), `r04_04` (shielded bipedal assault walker) and `r04_05` (spindly bipedal lancer)
were rejected as *"too generic / similar to previous rounds"*.

**Cause:** all three rejects share one shape — an upright body, two legs, two arms, a head
sitting above a torso. That is **the stock mech silhouette**: it is in every mech game and it
is also round 01's own lineup, so the model has a well-worn default to fall into on. The
quadruped had no such default — a long horizontal body carried low on four digitigrade legs
reads as a machine built for a specific job (run down infantry), so the model had to invent
it rather than recite it.

**Surface detail does not fix this.** A rivet-studded, hydraulically-exposed, battle-scarred
Titan is still a Titan. Rivets, rust, palette, weapon and camera are all *surface*. The
generic read comes from the *outline*.

### The LAYOUT BOX is a silhouette lever, and it may matter more than the prompt

Round 04's five layout boxes correlate **perfectly** with the verdict:

| Concept | SUBJECT box | Outcome |
|---|---|---|
| `r04_01` bastion titan | 0.72 × 0.89 — **tall** | upright humanoid, reject |
| `r04_02` hound tracker | 0.80 × 0.64 — **wide** | quadruped, **pass** |
| `r04_03` shroud reaver | 0.56 × 0.86 — **tall** | upright humanoid, reject |
| `r04_04` vanguard colossus | 0.68 × 0.88 — **tall** | upright humanoid, reject |
| `r04_05` wraith lancer | 0.56 × 0.88 — **tall** | upright humanoid, reject |

Every reject had a **tall** box; the only pass had the only **wide** one. The layout box is
a spatial instruction, so a tall narrow box literally asks the model for a vertical mass —
and it wins over the prompt text.

**Fix:** when the set must not read as humanoid, make every SUBJECT box **wider than it is
tall** (w:h ≥ 1.0, ideally ≥ 1.2), even for a machine whose description mentions a mast, a
rider or a raised weapon. A wide short box buys a horizontal machine for free.

**Confidence:** n=5, one variable — suggestive, not proven. Round 05 tests it: every box is
wide-dominant while the prompts vary. If the set comes back horizontal, the lever is real.

**Fix:** break the stock silhouette in the brief itself, per concept. Every machine in a set
that has to look designed rather than generic must refuse the "head on shoulders, two arms,
two legs" outline. Options that stay inside the mech / war machine / robot category:

- low and wide, or long and horizontal mass — the body reads as a machine, not a person
- non-humanoid leg counts: quadruped, hexapod, low crawler
- a body that reads as a machine *part* — turret on legs, tracked spine, segmented trunk

Pair every concept with a **named combat role and a named weapon** ("built to run down
infantry, carries a recessed rotary cannon pod"). Role + weapon is what makes a machine
specific instead of generic; silhouette alone only removes the stock shape.

**Applies when:** a mech set comes back and the complaint is "generic", "looks like every
other mech", or "similar to the previous round". The fix is silhouette, not finish, not
palette, not more detail.

**Related:** `2026-11-14-different-is-not-a-different-category.md` — the category stays
fixed while the look varies. This lesson says which part of the look carries the most weight.
