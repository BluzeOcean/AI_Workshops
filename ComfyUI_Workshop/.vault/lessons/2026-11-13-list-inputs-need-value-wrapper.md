# A list literal in an API graph must be wrapped as `{"__value__": [...]}`

**Date:** 2026-11-13
**Symptom:** Submitting a graph containing a `CreateBoundingBoxes` node was rejected with:

```
"message": "Bad linked input, must be a length-2 list of [node_id, slot_index]: editor_state"
"received_value": []
```

The input was simply `[]`.

**Cause:** ComfyUI's `execution.py` validator treats **every** list value as a node link:

```python
val = inputs[x]
if isinstance(val, list):
    if len(val) != 2:
        error = {"type": "bad_linked_input", ...}
```

There is no branch for "this is a literal list". A bare `[]` has length 0, so it is read as
a malformed link and rejected. The escape hatch is documented a few lines further down:

```python
# Unwraps values wrapped in __value__ key or typed wrapper.
# This is used to pass list widget values to execution,
# as by default list value is reserved to represent the connection between nodes.
if isinstance(val, dict):
    if "__value__" in val:
        val = val["__value__"]
```

**Fix:** wrap list literals.

```json
"editor_state": { "__value__": [] }
```

**Applies when:** any node input whose type is a list (`BOUNDING_BOXES`, `ARRAY`, …) needs a
literal value in an API graph. A non-list type (e.g. `STRING`) is unaffected.

**Cheap to test:** validation happens at queue time, before the model is loaded — a bad
graph costs seconds, not a 9.7 GB model load. Iterate on the graph freely before
submitting for real.
