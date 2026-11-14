# The API graph dict must contain node entries only

**Date:** 2026-11-13
**Symptom:** Submitting a graph returned a bare `500 Internal Server Error` with the body
`"Server got itself in trouble"` — no node errors, no hint of what was wrong.

**Cause:** The server log had the real story:

```
File "D:\ComfyUI\ComfyUI\app\node_replace_manager.py", line 65, in apply_replacements
    if "class_type" not in node_struct or "inputs" not in node_struct:
TypeError: argument of type 'int' is not iterable
```

`server.py` iterates the whole prompt dict and treats **every value** as a node:

```python
for node_id, node_struct in prompt.items():
    if "class_type" not in node_struct or "inputs" not in node_struct:
```

The builder had written three convenience keys next to the nodes —
`__width`, `__height`, `__count` — and their values are ints. `"class_type" not in 960`
raises `TypeError`.

**Fix:** the graph file contains **node entries and nothing else**. Metadata goes to a
sidecar (`<graph>.meta.json`), which `tools/build-moss-set.mjs` now writes.

**Applies when:** a submit returns a 500 with no `node_errors` — read the ComfyUI log at
`D:\ComfyUI\harness\comfyui-headless.log`, the HTTP body alone tells you nothing.

**Applies when:** writing any tool that emits an API-format graph.

**Cost:** two failed submissions, ~4 minutes.
