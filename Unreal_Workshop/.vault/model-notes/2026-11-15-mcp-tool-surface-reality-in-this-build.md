# The MCP tool surface in this build — what is actually there

**Recorded:** 2026-11-15. **Facts about the live UE 5.9 editor on this machine, not a
general statement about Unreal.**

## `editor_toolset` is not registered in this build

The `ue-op-*` skills that author Blueprint graphs call `editor_toolset.*` tools. **In
this build those calls fail** with `Toolset 'editor_toolset.BlueprintTools' not found`,
and retrying does not help. The toolset registry here carries the canvas toolset, not
the editor's own Blueprint/Asset/Actor toolsets.

**What does work:** the editor's own Python, driven through the MCP bridge's
console-command bridge. That covers most editor work that is not Blueprint graph
authoring. See `D:\UE\.ue-op-skillset\ue-op-editor-script\SKILL.md`.

**Blueprint graph authoring specifically still needs `editor_toolset`** — if it is
unavailable, say so rather than silently skipping the graph.

## Image tools return base64 inside a JSON-wrapped text block

`CaptureEditorImage`, `CaptureViewport` and `CaptureAssetImage` do **not** return an
image content block. They return a text block whose text is itself JSON:

```
result.content[0].text
  -> {"returnValue":{"image":{"mimeType":"image/png","data":"iVBOR..."}}}
```

So the unwrap is: parse the outer JSON → take `result.content[0].text` → parse *that*
as JSON → reach `result.image.data` → base64-decode.

## The in-editor sandbox forbids `base64`

The `ProgrammaticToolset` sandbox allows `copy`, `datetime`, `time`, `json`, `math`, `re`
— **not** `base64`. Decoding has to happen outside the editor.

## A dependency-free MCP client already exists

```
D:\UE\.ue-op-skillset\ue-mcp-connect\mcp_call.py
```

It handles the `initialize` → `notifications/initialized` handshake, tracks the
`Mcp-Session-Id` header and sends the correct `Accept` header — so it works from Bash
with no MCP client in the loop, and with none of the sandbox's restrictions. Use it
rather than writing another one.

```bash
cd D:/UE/.ue-op-skillset/ue-mcp-connect
python mcp_call.py list_toolsets
python mcp_call.py describe_toolset EditorToolset.EditorAppToolset
python mcp_call.py call EditorToolset.EditorAppToolset GetOpenAssets
```

## `CaptureViewport` cannot see PIE actors

It renders the **editor** level, not the PIE world. A pawn that exists only in PIE is
invisible to it. Verify PIE state numerically instead.

## Reuse when

- A Blueprint graph task reports that a toolset is missing.
- A capture returns text where an image was expected.
- An in-editor script fails on an import that is available in a normal Python.
