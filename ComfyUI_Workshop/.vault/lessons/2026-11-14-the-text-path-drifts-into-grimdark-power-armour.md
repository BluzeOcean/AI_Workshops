# The text path drifts into grimdark power armour — the concept carries the shape

**Date:** 2026-11-14
**Symptom:** the user looked at the house-style verification renders and said most of them
*"do not look like the reference image that I gave you. Instead, they look more like Warhammer
Space Marine units, which I don't want."* They are right. The renders are rust-orange and
charcoal with rivets, weld seams and chevron plates, but they are **squat, hunched, and
carried on enormous squared pauldrons** — the Space Marine silhouette — while the r04_02
reference is a **tall, lean** bipedal with two huge flat dorsal fins up and out from the
shoulders and a low forward-thrusting wedge head.

**Cause:** two things, and only one of them is about lighting.

1. **The concept carries the shape; the style suffix carries the surface.** Every one of
   these renders used r08's `04_juggernaut` concept, whose own shape language is
   *"a very deep wide torso carried low between enormous squared pauldrons, short thick
   legs planted wide and splayed"*. That is the power-armour silhouette, written out in
   words. Pairing it with the r04_02 surface (rust over charcoal, slabs, rivets, chevrons)
   gave a machine with r04_02's **finish** and the concept's **body plan** — and the body
   plan is what the eye reads first.
2. **The text path has no image to anchor the proportions.** Round 10, which renders
   *from the reference image* through the edit LoRA, kept the reference design: the swept
   dorsal fins, the layered pauldrons and the bone-and-crimson livery all read as the same
   family as r04_02. The same style suffix, sent as **text only**, drifts to the genre
   default. A prompt can describe a design; it cannot hand over the model's whole
   interpretation of it.

**Fix:**

- When the brief names a reference model and the result must **look like it**, use the
  reference-IMAGE path (`build-moss-edit-set.mjs`), not the text path. This is the same
  rule as *"a reference model is a stack of attributes — copy the design, not one layer of
  it"*, and the same rule as *"use the reference image, not the prompt"*. The text path is
  for a design that does **not** have to match a given reference.
- When the text path is used anyway, the **concept's proportions** have to be written as
  explicitly as the reference's, or the genre default fills the space. "tall and lean with
  two huge flat dorsal fins" is a shape instruction; "enormous squared pauldrons" is the
  opposite one.
- Do not use a rejected round's concept as the test subject for a house-style change. A
  style probe renders **one approved concept**, so the only thing that varies is the thing
  under test.

**Applies when:** any text-to-image concept art, and any prompt that has to match a
reference the user has already approved.
