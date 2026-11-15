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

## Four tools, four very different results

| Tool | Captures | Notes |
|---|---|---|
| `EditorToolset.EditorAppToolset.CaptureEditorImage()` | the whole editor OS window | no arguments; read-only |
| `SceneCaptureToolset.CaptureEditorViewport(captureTransform, annotations, bShowUI, viewportId)` | one editor viewport — a level viewport or an asset editor | renders the **editor** world; every argument is optional |
| `SceneCaptureToolset.CaptureGameViewport(world, maxResolution)` | the Game/PIE viewport, UMG and overlays included | needs a `World` — the PIE world |
| `EditorToolset.EditorAppToolset.CaptureAssetImage(assetPath)` | an asset thumbnail | meshes, materials, textures, animations |

There is no `CaptureViewport` in this build — *"Unknown tool CaptureViewport
in toolset EditorToolset.EditorAppToolset. Closest tools: CaptureAssetImage,
CaptureEditorImage, ExitEditor"*. `CaptureEditorViewport` is its replacement.

**`CaptureEditorViewport` cannot see PIE actors.** It renders the editor's
level, so a pawn that exists only in the PIE world is invisible in the
capture; `CaptureGameViewport` is the one that renders the PIE viewport.
Verify PIE state numerically as well (`ue-op-test-pie`).

---

## Procedure

### 1. Capture

```powershell
# the whole editor window; no arguments
python ...\mcp_call.py call EditorToolset.EditorAppToolset CaptureEditorImage
# {"returnValue":"urn:toolresult:EditorToolset.EditorAppToolset.CaptureEditorImage:ea6e9dfc-…:/returnValue"}
```

or, for a specific viewpoint:

```powershell
python ...\mcp_call.py call SceneCaptureToolset.SceneCaptureToolset CaptureEditorViewport `
  '{"annotations":{"gridSpacing":0,"gridExtent":0,"gridHeight":0,"maxLabelDistance":0},"bShowUI":false}'
```

**Neither call puts the PNG in its own output.** Each prints a `urn:toolresult:`
handle and stops — the pixels are a separate block. See step 2.

### 2. Unwrap the payload

The image does **not** come back inside the JSON text block. It is a **second
MCP content block** of `type: "image"`; the `text` block carries only a handle:

```json
{"result": {"content": [
  {"type": "text",  "text": "{\"returnValue\":\"urn:toolresult:EditorToolset.EditorAppToolset.CaptureEditorImage:…\"}"},
  {"type": "image", "mimeType": "image/png", "data": "iVBOR…"}
]}}
```

So `result.structuredContent.returnValue` is a `urn:toolresult:` string, and
`mcp_call.py`'s `as_text()` keeps **only** the `type: "text"` blocks — which is
why `python mcp_call.py call … CaptureEditorImage` prints a URN and no image.
Decode `content[...]` where `type == "image"` instead:

```powershell
$py = @'
import base64, sys
sys.path.insert(0, r"V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect")
from mcp_call import MCPClient

c = MCPClient(); c.initialize()
r = c.call_tool("EditorToolset.EditorAppToolset", "CaptureEditorImage", {})
img = next(b for b in r["result"]["content"] if b.get("type") == "image")
out = r"D:\UE\EpicJam2026\Saved\shot.png"
open(out, "wb").write(base64.b64decode(img["data"]))
print(img["mimeType"], len(img["data"]), out)
'@
$py | Set-Content -Encoding utf8 "$env:TEMP\mcp_shot.py"
python "$env:TEMP\mcp_shot.py"
# image/png 426816 D:\UE\EpicJam2026\Saved\shot.png
```

The same block decodes a `CaptureEditorViewport` result — the toolset and tool
names are the only change, and `structuredContent.returnValue` then also holds
`width`, `height`, `metadata` (camera, world, frame) and `warnings`.

Then read the PNG with the Read tool to look at it.

`base64` is **not** restricted, in or out of the editor. The in-editor runner
(`PythonScriptingTools.execute_python`) says so itself in `read_me`: *"full
interpreter access and no sandbox"* — `import base64` there returns
`YWJj` for `b"abc"`. What it does reject is imports anywhere but the top of
the script, star imports, blocking network / `subprocess` / `time.sleep`
calls, and `unreal.ToolsetRegistry.execute_tool`.

---

## Optional arguments

Every `CaptureEditorViewport` argument has a default, so a call with none of
them works:

1. `captureTransform` — `{translation, rotation, scale3D}`; **not**
   `location`/`scale`, which is the older shape. Axis-aligned orthographic
   views keep their orientation.
2. `annotations` — `gridSpacing`, `gridExtent`, `gridHeight`,
   `maxLabelDistance`, `classFilter`, `maxLabels`; zeros disable the grid and
   the actor labels.
3. `bShowUI` — `false` suppresses transform widgets and selection overlays.
4. `viewportId` — from `SceneCaptureToolset.ListEditorViewports`; unset
   captures the active level viewport.

The reason to pass `viewportId` is that a viewport in a background tab is
not capturable: *"CaptureEditorViewport: the viewport Level Viewport
(Perspective) is in a background tab or a hidden or minimized window."* Pick
the entry whose `bIsVisible` is true.

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `mcp_call.py call … CaptureEditorImage` prints `urn:toolresult:…` and nothing else | `as_text()` keeps only text blocks | read `result["content"][i]` where `type == "image"` (step 2) |
| `CaptureViewport` → "Unknown tool … Closest tools: CaptureAssetImage, CaptureEditorImage, ExitEditor" | that tool does not exist in this build | `SceneCaptureToolset.CaptureEditorViewport` |
| `CaptureEditorViewport` → "… is in a background tab or a hidden or minimized window" | the target viewport is not the visible tab | bring it forward, or pass a `viewportId` whose `bIsVisible` is true |
| `ValueError: line N: imports must be at the top level of the script` | `execute_python` checks the script before running it | move every `import` to the top |
| `Unable to import JSON string into CodeBlock` | `script` was sent as a bare string | `{"script": {"content": "<source>", "language": "Python"}}` |
| `CaptureEditorImage` → "Failed to capture any editor windows" | unsupported while PIE is running | capture before PIE, or use `CaptureGameViewport` |
| The capture shows an empty level | `CaptureEditorViewport` renders the editor world | PIE actors are not there — `CaptureGameViewport(world, maxResolution)` |
| The picture is enormous | full resolution | crop/downscale with PIL before reading it |

**Crop before reading.** A 1280×732 PNG is fine, but a 4K capture floods the
context. Use PIL to crop to the region of interest and upscale a small region
to read text.

**`CaptureEditorImage` grabs the editor window including panels** — useful for
reading a tab strip or a Details panel. `CaptureEditorViewport` is a clean 3D
view without UI chrome.

## Output contract

- A PNG written to disk
- Read with the Read tool to visually confirm
- Scratch images deleted afterwards

## Related

- `ue-op-test-pie` — numeric verification, which usually pairs with a capture
