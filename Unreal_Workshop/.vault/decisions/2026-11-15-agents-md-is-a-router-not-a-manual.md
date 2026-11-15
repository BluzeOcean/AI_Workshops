# The workshop is routed through catalogs, and AGENTS.md is a router, not a manual

**Date:** 2026-11-15
**Status:** active
**Decision:** The workshop is organised so that **reading its entry points costs a page,
not a library**, and **`AGENTS.md` is the router that gets you there**. Four rules, and
they hold together:

1. **Two indexes, and only two.** `.skills/skill_catalog.md` maps the procedures;
   `.vault/vault_index.md` maps the memory. An agent reads the index, picks the one entry
   it needs, and opens that. It never reads a folder end to end, and never reads every
   skill to decide which one applies.

2. **`AGENTS.md` holds exactly three things** — the **map** (the three layers and the
   catalog that indexes each), the **lookup discipline** (read a catalog, open one entry,
   grep rather than read end to end, run a tool rather than read it), and the **rules for
   working in and maintaining this workshop** (text only, agent-agnostic, the naming
   convention, the write-back loop, the index row, the prune, the revocation procedure,
   the commit policy). Everything else lives behind a catalog and is **routed to**, not
   restated.

3. **The always-loaded file never duplicates a fetched layer.** It does not carry the
   handshake payload, the `_meta` shape, the ini keys, the commandlet table, the Python
   gotchas, the install matrices or a path reference table — because each of those already
   lives in a skill or a vault note, and a copy in `AGENTS.md` is a copy nobody owns.

4. **The vault is pruned, not just grown.** Every task adds to it, so something has to
   take away. A prune pass runs over the index after any task that touched the vault.

**The boundary rule, for deciding where a new fact goes:**

| It is | It goes |
|---|---|
| a rule about how to work **in this workshop** | `AGENTS.md` |
| a rule about working **in Unreal**, on this machine | `.vault/decisions/` |
| a fact about Unreal, the engine, or this box | `.vault/model-notes/` |
| something that went wrong | `.vault/lessons/` |
| a procedure, in the order that works | `.skills/<name>/SKILL.md` |
| a script to be run | `tools/` |

**Reason:** `AGENTS.md` is the only file in the tree that is loaded at every session start,
so it is the only file whose every byte is paid for by every task forever. It grew into a
manual — the MCP protocol, the handshake payload, the commandlet table, the Python
gotchas, the install matrices, a path reference table — and the cost was not just tokens.
It was **drift**: the Python gotchas existed in `ue-op-python-gotchas` *and* in
`AGENTS.md`; the MCP facts existed in a vault note *and* in `AGENTS.md`; and two copies of
a fact with no owner between them do not stay equal. The old `AGENTS.md` §4b/§4c were a
copy of `ue-op-mcp-diagnose/SKILL.md` and `unreal-mcp-surfaces-on-this-machine.md` — and
the copy was the one that went stale.

A router has one advantage a manual cannot have: **it does not go stale**, because it
holds no facts to go stale. It holds pointers, and pointers point at the layer that owns
the fact.

The pruning rule exists for a second reason: **memory that only ever grows stops being
memory.** The vault's own test is "would a future agent act faster or avoid a failure
because this file exists" — an entry that fails that test is not a safety net, it is a
place where the signal drowns. The index makes the vault's size visible at a glance, so
rot is visible before it is expensive.

**Supersedes:** `../decisions/2026-11-15-the-workshop-is-loaded-lazily-and-pruned.md`
**Superseded by:** —

**Reuse when:** deciding where something belongs (`AGENTS.md` or the vault or a skill);
when `AGENTS.md` grows past what a session start should cost; when a fact is about to be
written in two places at once; when a new layer is added to the workshop and needs a
catalog.
