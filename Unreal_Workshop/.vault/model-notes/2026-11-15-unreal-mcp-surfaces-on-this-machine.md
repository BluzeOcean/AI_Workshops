# The Unreal MCP surfaces — reference facts

**Status:** active

**Recorded:** 2026-11-15, by probing the running UE 5.9 editor and the canvas server.
The *rule* about telling them apart is in
`.vault/decisions/2026-11-15-the-two-unreal-mcp-surfaces-are-not-interchangeable.md`;
the *procedure* is in
`.vault/workflows/2026-11-15-identify-which-unreal-mcp-answered.md`. This file holds the
raw facts.

## Epic's built-in plugin (inside the editor)

| | |
|---|---|
| Plugin | `Engine/Plugins/Experimental/ModelContextProtocol/ModelContextProtocol.uplugin` |
| FriendlyName / author | "Unreal MCP" / "Epic Games, Inc." |
| Endpoint | `http://127.0.0.1:8000/mcp` (POST) — bound to `127.0.0.1` only |
| Transport | HTTP JSON-RPC 2.0 — no stdio bridge, nothing to install |
| `serverInfo.name` | `unreal-mcp` |
| `serverInfo.version` | the **engine** version (`5.9.0-60351404`), not a plugin version |
| Protocol versions | `2025-11-25`, `2025-06-18`, `2024-11-05` |

The `initialize` reply carries the instance identity — read it before acting:

```json
"_meta": { "com.epicgames.unrealengine/instance": {
  "instanceId": "2196bb3e-46a4-6c10-ed40-828a7d2f3ed9",
  "processId": 38212,
  "engineVersion": "5.9.0-60351404",
  "engineBranch": "//UE5/Release-5.9",
  "engineChangelist": 60351404,
  "projectName": "EpicJam2026",
  "engineDirectory": "C:/Program Files/Epic Games/UE_5.9/Engine/",
  "projectDirectory": "D:/UE/EpicJam2026/",
  "projectFile": "D:/UE/EpicJam2026/EpicJam2026.uproject" } }
```

### Tool-search indirection

With `bEnableToolSearch=True` (the default) the server registers only three meta-tools:
`list_toolsets`, `describe_toolset`, `call_tool`. Toolset tools are **not** directly
callable — `tools/call` with a qualified name returns **HTTP 400**. Dispatch through
`call_tool`, with `tool_name` as the **bare** name, no toolset prefix.

### Settings

`<project>\Saved\Config\WindowsEditor\EditorPerProjectUserSettings.ini` — per user, per
project, **not** `Default*.ini`:

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
ServerUrlPath=/mcp
ServerPortNumber=8000
bAutoStartServer=True
bEnableToolSearch=True
```

`bAutoStartServer` is **skipped in commandlets** — a cook would race the editor for the
port. Force it with `-ModelContextProtocolStartServer`.

### Console commands and CLI flags

| | |
|---|---|
| `ModelContextProtocol.StartServer [port]` | start the server |
| `ModelContextProtocol.StopServer` | stop it |
| `ModelContextProtocol.RefreshTools` | rebuild the tool list, drop cached schemas |
| `ModelContextProtocol.GenerateClientConfig <ClaudeCode\|Cursor\|VSCode\|Gemini\|Codex\|All>` | write client config |
| `-ModelContextProtocolStartServer` | force the server on at launch |
| `-ModelContextProtocolPort=<N>` | use a port other than 8000 |

## Unreal Canvas bridge (a separate process)

| | |
|---|---|
| Process | `unrealcanvas-server.exe`, spawned by the editor with `--parent-pid <editor PID>` |
| Build | `C:\Users\Bluze\AppData\Local\UnrealCanvas\Builds\v0.21.0\` |
| Version | `0.21.0` (stable) — `merlin-version.txt` |
| `serverInfo.name` | `merlin` |
| Protocol version | `2025-03-26` |
| Observed ports | `127.0.0.1:58784`, `58785` — **not** the requested 8000 |

Its replies carry a state note that says whether the canvas side is usable at all:

```json
"frontendBuild": { "known": false,
  "why": "No Unreal Canvas frontend is connected, so nothing is executing tool calls. Open the Unreal Canvas panel." }
```

Canvas-shaped tools: `TriggerMRGRender`, `TriggerSequenceRender`, `BuildAndRenderRepositionSequence`,
`SpawnMeshAt`, `SpawnCutoutFromPNG`, `SpawnGsplatFromPLY`, `RunMeshOps`, `BakeMeshTextures`,
`SetSkybox`, `ListCutouts`, `StartViewportStream`, `GetViewportCamera`, `SetViewportCamera`,
`RunConsoleCommand`, and the annotation tools (`Place3DAnnotation`,
`AssignStencilID`, `GatherVisibleAnnotations`, `SetVisibleAnnotationGroups`, …).

## Reuse when

- Deciding which surface to reach for, or explaining an unexpected tool result.
- Confirming a connection before a write.
