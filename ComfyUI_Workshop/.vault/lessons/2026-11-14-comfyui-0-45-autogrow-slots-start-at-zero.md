# ComfyUI 0.45's autogrow slots start at 0, and slot 0 is required

**Date:** 2026-11-14
**Symptom:** a graph using `TextEncodeMOSSImageEdit` was rejected before it ran:

```json
{ "type": "required_input_missing",
  "message": "Required input is missing",
  "details": "image_0",
  "extra_info": { "input_name": "images.image_0" } }
```

The reference image had been wired to `images.image_1`.

**Cause:** the node's `images` input is a `COMFY_AUTOGROW_V3` input declared as
`TemplatePrefix(input=Image, prefix="image_", min=1)`. Autogrow slots are numbered from
**0**, and `min=1` makes slot 0 **required**. So `images.image_1` is slot *one*, not an
alternative to slot zero — wiring the reference to it leaves slot 0 missing and the whole
graph is refused before the GPU is touched.

The API key for an autogrow slot is dotted: `<autogrow input name>.<slot name>`, e.g.
`images.image_0`.

**Fix:** wire the first reference to `images.image_0`. When an autogrow input is rejected
for a missing slot, read the error's `details` field — it names the exact slot the node
wants, so there is nothing to guess.

**Applies when:** any node with a `COMFY_AUTOGROW_V3` input —
`TextEncodeMOSSImageEdit` (reference images), the autogrow nodes in
`comfy_extras/nodes_logic.py`, Bernini's `reference_images`.

**Related:** `.skills/moss-reference-variation/SKILL.md` carries this trap in its
failure-mode table.
