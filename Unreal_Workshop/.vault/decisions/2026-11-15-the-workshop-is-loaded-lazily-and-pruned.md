# The workshop is loaded lazily, and the vault is pruned

**Date:** 2026-11-15
**Status:** superseded
**Superseded by:** `../decisions/2026-11-15-agents-md-is-a-router-not-a-manual.md`

> **Superseded.** The rule this file recorded is now carried by
> `../decisions/2026-11-15-agents-md-is-a-router-not-a-manual.md`, which merges it
> with the rule about what `AGENTS.md` may contain. Read that one instead.

**Decision:** The workshop is built so that **reading its entry points costs a page, not a
library**. Three rules, and they hold together:

1. **Two indexes, and only two.** `.skills/skill_catalog.md` maps the procedures;
   `.vault/vault_index.md` maps the memory. An agent reads the index, picks the one entry it
   needs, and opens that. It never reads a folder end to end, and never reads every skill
   to decide which one applies.
2. **The always-loaded file never duplicates a fetched layer.** `AGENTS.md` carries the
   *rules* — the destination rule, the version rule, the traps. It does **not** carry the
   handshake payload, the `_meta` shape, the ini keys or the vault contents, because those
   already live in a skill and a model-note and a copy in `AGENTS.md` is a copy nobody owns.
3. **The vault is pruned, not just grown.** Every task adds to it, so something has to take
   away. A prune pass runs over the index after any task that touched the vault.

**Reason:** An agent's context window is the budget, and the whole point of this workspace
is to be *loaded* by an agent that knows nothing. A workshop that carries its own library
into every session is a liability, not an asset — the always-loaded file is the part that
can never be lazily fetched, so every byte in it is paid for by every task forever. The
slimming of `AGENTS.md`'s MCP sections from 137 lines to 47 was not tidiness: it was the removal
of content that a skill already carried and a vault note already carried, so the fetch
returned to being an actual fetch instead of a formality.

The pruning rule exists for a second reason: **memory that only grows stops being memory.**
The vault's own test is "would a future agent act faster or avoid a failure because this
file exists" — an entry that fails that test is not a safety net, it is a place where the
signal drowns. The index makes the vault's size visible at a glance, so rot is visible
before it is expensive.

**Supersedes:** —

**Reuse when:** deciding whether something belongs in `AGENTS.md` (always-loaded, a rule)
or in the vault (fetched, a fact); deciding whether to add a third index; deciding what to
delete when the vault gets long.
