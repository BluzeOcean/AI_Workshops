# Layout boxes must be ELEMENTS — plain boxes silently lose their caption

**Date:** 2026-11-13
**Symptom:** Bounding boxes supplied to `CreateBoundingBoxes` were rejected with
`"bboxes dict must be a bounding box (x, y, width, height) or an element (with a 'bbox')"`,
and the element form (`{"bbox": [...]}`) used a different coordinate convention than the
one written down.

**Cause:** the node accepts two shapes and decides between them by inspection
(`comfy_extras/nodes_bounding_boxes.py`):

- **Element** — `{"bbox": [y0, x0, y1, x1], "type": "text"|"obj", "desc": "...", "text": "...",
  "color_palette": ["#RRGGBB"]}`. Coordinates are **0–1000 and Y FIRST**. This is the only
  form that carries a caption.
- **Plain box** — `{"x", "y", "width", "height"}` in **pixels**. `normalize_incoming_boxes()`
  copies only those four keys plus `metadata`; a `desc` on a plain box is **dropped
  silently**, and the element ends up with no caption.

So a box written as fractions `{x, y, w, h}` is neither of the two accepted shapes, and a
box written as a plain pixel box loses the text that tells the model what is in it.

**Fix:** recipes are written in human fractions `{x, y, w, h}` (0..1) and the builder
converts them:

```js
bbox = [round(y*1000), round(x*1000), round((y+h)*1000), round((x+w)*1000)]
```

`tools/build-moss-set.mjs` does this in `fracToBbox()`. Always use the element form so the
caption survives.

**Applies when:** supplying layout boxes, especially when a caption/palette matters.

**Related:** `MOSSImageLayoutPrompt` reads `el["desc"]`, `el["type"] == "text"`,
`el["text"]` and `el["color_palette"]`. A box with no `desc` renders as an unnamed object.
