# The tool layer is specified, not built — and it belongs to the DSH side

**Date:** 2026-11-15
**Status:** active
**Decision:** `tools/` holds a **specification** of the Blender tool layer, not an
implementation. The scripts it describes have not been written. The user decided that the
**DSH (DeepSeek harness) side writes the necessary tools**: *"your job is to actually just
write the infrastructure of the workshop, so you can leave the tools to dsh"* and *"i think
its better for dsh to write the necessary tools."*

What this workspace owns:

- `AGENTS.md` — the onboarding, the rules, the traps.
- `.skills/` — the procedure format and the rules for writing one.
- `.vault/` — the memory bank.
- `tools/README.md` — **the contract** the tool layer has to satisfy: what each tool does,
  what it takes, what it returns, and what it must not do.

What the tool layer owns (not written here):

- The version resolver.
- The bridge client for `127.0.0.1:9876`.
- The headless runner.
- The MCP bridge that fills `.mcp.json`.

**Reason:** the tools are the part that has to change when Blender changes, and the DSH
side is the one that will be exercising them against a live Blender on every task. Writing
the spec here — rather than a half-implementation — keeps one owner for the moving part
and stops this workspace from shipping a second, conflicting version of the same client.

**Consequence for this repo:** `tools/` contains no scripts yet, and `AGENTS.md` points at
§4 (the three ways to talk to Blender) as the working path until they exist.

**Applies when:** anyone is tempted to add a script under `tools/`. Check with the DSH side
first; if the tool is not theirs, the answer goes in the spec, not in the tree.

**Related:** `2026-11-15-port-9876-is-not-an-mcp-endpoint.md`.
