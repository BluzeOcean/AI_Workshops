# The MCP tool surface in this build — what is actually there

**Status:** active

**Recorded:** 2026-11-15. **Facts about the live UE 5.9 editor on this machine, not a
general statement about Unreal.**

## Correction, 2026-11-15: the tools are there, under other names

**The paragraph this replaces was wrong, and it cost a day of agents refusing work they
could do.** `editor_toolset.toolsets.blueprint.BlueprintTools` really is not registered —
but that is a **name** failure, not a missing capability. Re-probed against the same live
editor on the same day:

- `BlueprintToolsets.BlueprintToolset` — the Blueprint toolset, ~71 tools: `ListGraphs`,
  `FindNodes`, `CreateNode`, `ConnectPins`, `SetPinValue`, `CompileBlueprint`,
  `GetDefaultObject`, `Create`, `ListVariables`, `ListEvents` …
- `BlueprintToolsets.BlueprintDslToolset` — `Read` / `Write` / `Edit` / `Docs` / `Diff` /
  `Schema` / `FindNodeReferences`: the graph-DSL route.
- `EditorToolset.{AssetToolset, ActorToolset, ObjectToolset, LevelToolset,
  SkeletalMeshToolset, EditorAppToolset, …}` — assets, actors, properties, the level.
- `editor_toolset.toolsets.python_scripting.PythonScriptingTools` — `execute_python`,
  the real in-editor Python runner. (`execute_tool_script` does not exist at all.)

**So Blueprint graph authoring has a direct path:** `call_tool` with the registered name,
or `execute_python` plus `await call_tool(...)`. The name map, verified signatures and the
JSON shapes for assets, graphs, nodes and pins are in
`.skills/ue-op-mcp-connect/references/calling-tools-in-this-build.md`.

**Why the old note was wrong:** it asked for one old name, got a `not found`, and recorded
the error as a capability claim ("say so rather than silently skipping"). A name mismatch
is not an absence — enumerate the registry (`list_toolsets`) before concluding a toolset
does not exist.

## Image tools return base64 inside a JSON-wrapped text block

`CaptureEditorImage`, `CaptureViewport` and `CaptureAssetImage` do **not** return an
image content block. They return a text block whose text is itself JSON:

```
result.content[0].text
  -> {"returnValue":{"image":{"mimeType":"image/png","data":"iVBOR..."}}}
```

So the unwrap is: parse the outer JSON → take `result.content[0].text` → parse *that*
as JSON → reach `result.image.data` → base64-decode.

## `base64` is available again in `execute_python` (corrected 2026-11-15)

The old `ProgrammaticToolset` sandbox allowed only `copy`, `datetime`, `time`, `json`,
`math`, `re`. That sandbox is not in the path anymore: `execute_python` runs *"in a fresh
namespace with full interpreter access and no sandbox"* (its own `read_me`), and
`import base64; base64.b64encode(b"probe")` returned `cHJvYmU=` in this editor. It still
refuses network calls, `time.sleep`, `subprocess.run` and star imports — those are the
remaining restrictions.

## A dependency-free MCP client already exists

```
V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py
```

It handles the `initialize` → `notifications/initialized` handshake, tracks the
`Mcp-Session-Id` header and sends the correct `Accept` header — so it works from Bash
with no MCP client in the loop, and with none of the sandbox's restrictions. Use it
rather than writing another one.

```bash
cd V:/04_Projects/Workshops/Unreal_Workshop/.skills/ue-op-mcp-connect
python mcp_call.py list_toolsets
python mcp_call.py describe_toolsets EditorToolset.EditorAppToolset
python mcp_call.py call EditorToolset.EditorAppToolset GetOpenAssets
```

## `CaptureViewport` cannot see PIE actors

It renders the **editor** level, not the PIE world. A pawn that exists only in PIE is
invisible to it. Verify PIE state numerically instead.

## Reuse when

- A Blueprint graph task reports that a toolset is missing — check the name against
  `references/calling-tools-in-this-build.md` before reporting a capability gap.
- A capture returns text where an image was expected.
- An in-editor script fails on an import: `execute_python` no longer has a restricted
  sandbox, so an import that fails is a real failure, not the old sandbox.
