# A client registration is per agent, not per machine

**Status:** active

**Date:** 2026-11-15

**Symptom:** A session in an agent other than Claude Code (DSH) read the workshop's line
"registered at user scope — every session in every directory connects automatically", looked
for `mcp__unreal-mcp__*`, found none, and treated a healthy bridge as a broken one. The
obvious next move — "re-register it" — is the wrong one: it either does nothing, or adds a
second entry that shadows the working one.

**Cause:** Two different things were being called "the MCP bridge".

- The **server** is the editor's. It is shared, it is on the machine, and it is up whenever
  the editor is.
- The **client entry** is one agent's configuration. "User scope" is a Claude Code concept
  and it means "every Claude Code session" — not "every agent". Nothing propagates. Verified
  2026-11-15: `~/.claude/.claude.json` holds the only `unreal-mcp` entry; OpenCode's global
  config has no MCP server at all; Codex's `config.toml` registers only `node_repl`; DSH has
  no MCP client, so no `mcp__*` tools can appear in its surface.

**Fix:** Decide from the agent's own config, not from a document claiming the registration
exists — and prove the server is reachable before touching any client config:

```powershell
python V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py list_toolsets
```

A list of toolsets back means the bridge is healthy and **this agent needs no registration**;
`mcp_call.py` is the route, and it is not a degraded one. Register only if this agent's own
config takes an HTTP MCP server — `ue-op-mcp-diagnose` step 5 — and register it in *that*
agent's config, at a scope that means "every directory". Never "solve" a missing entry with a
project-scope one.

**Applies when:** a toolkit has no `mcp__*` Unreal tools while the editor is running; a
document (including this workshop's own README) says the server is "registered"; or an agent
is about to re-register a bridge it has never had.
