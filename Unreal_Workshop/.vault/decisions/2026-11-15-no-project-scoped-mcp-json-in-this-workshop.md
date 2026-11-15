# No project-scoped `.mcp.json` in this workshop

**Date:** 2026-11-15
**Status:** active
**Decision:** This workshop ships `.mcp.json.example`, **not** `.mcp.json`. The live bridge
stays registered with Claude Code at **user scope** — verify with `claude mcp list`; the
entry is named `unreal-mcp` and points at the editor's own MCP route,
`http://127.0.0.1:8000/mcp`.

**Reason:** A user-scope entry is visible from every directory in every session on the
machine and needs no approval. Adding a project-scoped copy of the same server here would
register it twice, show as "⏸ Pending approval", and shadow the working entry — a
self-inflicted breakage of the one bridge that already works.

Use `.mcp.json.example` only to recover the server definition if the user-scope entry is
lost (`claude mcp add --scope user --transport http unreal-mcp
http://127.0.0.1:8000/mcp`), or to register a **second** editor on its own port (every
editor defaults to 8000, so a second one cannot bind it — see
`.vault/lessons/2026-11-15-verify-the-port-and-its-owner-before-trusting-an-mcp-connection.md`).
**Supersedes:** —
