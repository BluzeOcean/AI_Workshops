# This workshop carries no MCP configuration

**Date:** 2026-11-15
**Status:** active
**Decision:** The workshop tree holds **no MCP configuration at all** — no `.mcp.json`, no
`.mcp.json.example`, and no agent-tool settings directory. The **client definition** the
agent needs to register lives with the procedure that uses it, in
`.skills/ue-op-mcp-diagnose/references/client-config.json`, and the procedure itself is
`.skills/ue-op-mcp-diagnose/SKILL.md`.

The live bridge is registered with the agent at **user scope** — check it with
`claude mcp list`; the entry is named `unreal-mcp` and points at the editor's own MCP
route, `http://127.0.0.1:8000/mcp`.

**Reason:** Two reasons, and the second is the important one.

1. A user-scope entry is visible from every directory in every session and needs no
   approval. A project-scoped copy of the same server registers it twice, shows as
   "⏸ Pending approval", and shadows the working entry — a self-inflicted breakage of the
   one bridge that already works.
2. **The workshop is agent-agnostic.** It must not carry configuration for one agent tool.
   The content — the server definition, the handshake, the diagnostics — belongs with the
   procedure that needs it; the *wiring* belongs in each agent's own configuration. A
   future agent that does not use `.mcp.json` should not find one here.

Use the skill's `references/client-config.json` to recover the definition if the
user-scope entry is lost, or to register a **second** editor on its own port (every editor
defaults to 8000, so a second one cannot bind it — see
`.vault/lessons/2026-11-15-verify-the-port-and-its-owner-before-trusting-an-mcp-connection.md`).
**Supersedes:** —
