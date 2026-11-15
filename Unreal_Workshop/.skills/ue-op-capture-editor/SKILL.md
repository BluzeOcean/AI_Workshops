---
name: ue-op-capture-editor
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to capture what the Unreal editor looks like — a viewport screenshot, a full editor window image, or an asset thumbnail — so the result can be shown or inspected. Skip if no UE MCP connection, or if numeric verification is enough.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - mcp__unreal-mcp__call_tool
---

# ue-op-capture-editor — screenshot the editor through MCP

## Two tools, two very different results

| Tool | Captures | Notes |
|---|---|---|
| `CaptureEditorImage` | the whole editor OS window | works only when PIE is **not** running |
| `CaptureViewport` | a free-floating viewport camera | renders the **editor** world, not the PIE world |

**`CaptureViewport` cannot see PIE actors.** It renders the editor's level, so
a pawn that exists only in the PIE world is invisible in the capture. Verify
PIE state numerically instead (`ue-op-test-pie`).

---

## Procedure

### 1. Capture

```python
r = execute_tool("EditorToolset.EditorAppToolset.CaptureEditorImage", "{}")
```

or, for a specific viewpoint:

```python
r = execute_tool("EditorToolset.EditorAppToolset.CaptureViewport", json.dumps({
    "captureTransform": {
        "location": {"x": -150.0, "y": 0.0, "z": 120.0},
        "rotation": {"pitch": -8.0, "yaw": 0.0, "roll": 0.0},
        "scale":    {"x": 1, "y": 1, "z": 1},
    },
    "annotations": {"gridSpacing": 0.0, "gridExtent": 0.0,
                    "gridHeight": 0.0, "maxLabelDistance": 0.0},
}))
```

### 2. Unwrap the payload

The image comes back as **base64 inside a JSON-wrapped text block**, not as an
image content block:

```json
{"result": {"content": [{"type": "text",
  "text": "{\"returnValue\":{\"image\":{\"mimeType\":\"image/png\",\"data\":\"iVBOR...\"}}}"}]}}
```

So: parse the outer JSON → take `result.content[0].text` → parse *that* as
JSON → reach `result.image.data` → base64-decode → write the file.

The in-editor sandbox (`ProgrammaticToolset`) **forbids `base64`**
(allowed: `copy`, `datetime`, `time`, `json`, `math`, `re`). Decoding has to
happen outside the editor — use `mcp_call.py` from Bash, which has no such
restriction:

```bash
cd "V:/04_Projects/Workshops/Unreal_Workshop/.skills/ue-op-mcp-connect"   # where mcp_call.py lives
python - <<'PY'
import base64, json, sys
sys.path.insert(0, '.')
from mcp_call import MCPClient

def find_data(o):
    if isinstance(o, dict):
        if isinstance(o.get("data"), str) and len(o["data"]) > 100: return o
        for v in o.values():
            r = find_data(v)
            if r: return r
    elif isinstance(o, list):
        for v in o:
            r = find_data(v)
            if r: return r
    return None

c = MCPClient(); c.initialize()
r = c.call_tool("EditorToolset.EditorAppToolset", "CaptureEditorImage", {})
txt = r["result"]["content"][0]["text"]
hit = find_data(json.loads(txt))
if hit:
    open("D:/UE/shot.png", "wb").write(base64.b64decode(hit["data"]))
    print("saved")
PY
```

Then read the PNG with the Read tool to look at it.

---

## Required parameters

`CaptureViewport` rejects calls that omit parameters even when the schema
shows defaults — it will ask for them one at a time:

1. `captureTransform` — a full transform (location, rotation, scale)
2. `annotations` — the overlay config; all-zero values disable the grid and
   actor labels

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `input param "captureTransform" needs a default value` | optional params must still be passed | supply a full transform |
| `input param "annotations" needs a default value` | same | pass the annotations object |
| `CaptureEditorImage` → "Failed to capture any editor windows" | unsupported while PIE is running | capture before PIE, or use `CaptureViewport` |
| The image is a giant base64 string in the transcript | not unwrapped | decode it to a PNG file |
| `Import of 'base64' is not permitted` | the in-editor sandbox restricts imports | decode outside the editor (Bash) |
| The capture shows an empty level | `CaptureViewport` renders the editor world | PIE actors are not there |
| The picture is enormous | full resolution | crop/downscale with PIL before reading it |

**Crop before reading.** A 1280×732 PNG is fine, but a 4K capture floods the
context. Use PIL to crop to the region of interest and upscale a small region
to read text.

**`CaptureEditorImage` grabs the editor window including panels** — useful for
reading a tab strip or a Details panel. `CaptureViewport` is a clean 3D view
without UI chrome.

## Output contract

- A PNG written to disk
- Read with the Read tool to visually confirm
- Scratch images deleted afterwards

## Related

- `ue-op-test-pie` — numeric verification, which usually pairs with a capture
