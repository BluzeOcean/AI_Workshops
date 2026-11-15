# The two Unreal MCP surfaces are not interchangeable

**Date:** 2026-11-15
**Status:** active
**Decision:** Unreal on this machine exposes **two distinct MCP servers**, and an agent
must identify which one it is talking to before calling anything.

- **Epic's plugin** (`Engine/Plugins/Experimental/ModelContextProtocol/`) runs **inside
  the editor process**. `serverInfo.name` = `unreal-mcp`; the version string is the
  **engine** version (`5.9.0-60351404`); it listens on `127.0.0.1:8000`; its `initialize`
  reply carries `_meta."com.epicgames.unrealengine/instance"` naming the editor's PID,
  engine directory and project file.
- **The Unreal Canvas bridge** (`unrealcanvas-server.exe`, "merlin") runs as a **separate
  process spawned by the editor**. `serverInfo.name` = `merlin`; the version is the canvas
  build (`0.21.0`); it negotiates protocol `2025-03-26`; its replies carry a
  `frontendBuild` note saying whether a canvas frontend is connected.

**The two discriminators are cheap and decisive:** the `_meta` instance block (which editor
and project) and the `frontendBuild` note (is the canvas side even alive).

**Reason:** Both were live simultaneously on 2026-11-15, both speak MCP over HTTP, both
answer on a localhost port, and both look like "the Unreal MCP" in a tool list. An agent
that conflates them debugs a canvas-tool failure against the editor plugin — or the
reverse — and never finds the cause. Worse, the canvas tools *look* callable: a canvas
tool that is listed but does nothing is a **missing frontend**, not a broken tool, and
that is only visible in the `frontendBuild` note.
**Supersedes:** —
**Superseded by:** —
