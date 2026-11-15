# Vault index — every entry, one row

**The map of `.vault/`.** An agent that wants to fetch wisdom reads **this file**, picks the
row, and opens only that entry. **Never read the vault end to end** — grep it (see
`../AGENTS.md` §6) or read this index.

**`Status` is the first column to read.** Only `active` rows are worth opening. A
`superseded` row names its replacement. A `stale` row was once true and no longer is.

| Status | Entry | What it saves you |
|---|---|---|
| active | [`decisions/2026-11-15-where-unreal-artifacts-belong.md`](decisions/2026-11-15-where-unreal-artifacts-belong.md) | Content vs Saved vs export — where an artifact goes, and what must be created *through the editor* |
| active | [`decisions/2026-11-15-the-unit-scale-is-decided-at-export-time.md`](decisions/2026-11-15-the-unit-scale-is-decided-at-export-time.md) | The ×100 Blender/Unity → Unreal scale, decided at export, not at import |
| active | [`decisions/2026-11-15-the-unreal-version-is-resolved-not-pinned.md`](decisions/2026-11-15-the-unreal-version-is-resolved-not-pinned.md) | Why the launcher registry cannot be trusted here |
| active | [`decisions/2026-11-15-the-two-unreal-mcp-surfaces-are-not-interchangeable.md`](decisions/2026-11-15-the-two-unreal-mcp-surfaces-are-not-interchangeable.md) | Telling Epic's plugin from the canvas bridge |
| active | [`decisions/2026-11-15-this-workshop-carries-no-mcp-configuration.md`](decisions/2026-11-15-this-workshop-carries-no-mcp-configuration.md) | Why the workshop ships no MCP config, and where the client definition lives instead |
| active | [`decisions/2026-11-15-the-workshop-is-loaded-lazily-and-pruned.md`](decisions/2026-11-15-the-workshop-is-loaded-lazily-and-pruned.md) | Why there are two indexes, why `AGENTS.md` never duplicates a fetched layer, and why the vault is pruned |
| active | [`lessons/2026-11-15-the-launcher-registry-does-not-list-ue-5-9.md`](lessons/2026-11-15-the-launcher-registry-does-not-list-ue-5-9.md) | The resolver trap, with the scan command |
| active | [`lessons/2026-11-15-verify-the-port-and-its-owner-before-trusting-an-mcp-connection.md`](lessons/2026-11-15-verify-the-port-and-its-owner-before-trusting-an-mcp-connection.md) | "Connected but about the wrong project" |
| active | [`lessons/2026-11-15-ue-5-5-has-no-mcp-plugin.md`](lessons/2026-11-15-ue-5-5-has-no-mcp-plugin.md) | Why an old engine has no MCP at all |
| active | [`lessons/2026-11-15-a-copied-index-goes-stale-without-an-owner.md`](lessons/2026-11-15-a-copied-index-goes-stale-without-an-owner.md) | A hand-copied table of contents has no owner, so a revoked decision stays listed as live forever |
| active | [`model-notes/2026-11-15-mcp-tool-surface-reality-in-this-build.md`](model-notes/2026-11-15-mcp-tool-surface-reality-in-this-build.md) | `editor_toolset` absent; base64-wrapped images; the sandbox limits; `mcp_call.py` |
| active | [`model-notes/2026-11-15-ue-installs-and-mcp-capability.md`](model-notes/2026-11-15-ue-installs-and-mcp-capability.md) | Which engine can do what; verified commandlets; reusable engine assets |
| active | [`model-notes/2026-11-15-unreal-mcp-surfaces-on-this-machine.md`](model-notes/2026-11-15-unreal-mcp-surfaces-on-this-machine.md) | Ports, protocol versions, config keys, console commands |
| active | [`workflows/2026-11-15-identify-which-unreal-mcp-answered.md`](workflows/2026-11-15-identify-which-unreal-mcp-answered.md) | The copy-pasteable "which server answered" sequence |

**14 entries.** Folder charters (`decisions/README.md`, `lessons/README.md`, and the rest)
are **not** entries — they say how a folder is written, not what is known.

The `skills` have their own index: `.skills/skill_catalog.md`. The two indexes together are
the whole workshop: **one map of procedures, one map of memory.**

---

## Rules for this index

1. **Every entry has a row here, added in the same commit that created the file.** A vault
   file that is not in this index **does not exist** — no agent will find it, and the prune
   will delete it. If you wrote an entry and it is not in the index, the entry is unfinished.
2. **A row says enough to decide whether to open the file.** If the row is longer than the
   entry behind it, the entry is unnecessary — fold the row's content back and shorten it.
3. **The status changes when the fact changes.** Revoking a decision is a four-step
   write-back — `../AGENTS.md` §6, *Revoking a decision*.
4. **The index is pruned with the vault, never after it.** A prune pass that ends with an
   index that still lists a deleted file is a failed prune.

---

## Maintenance

The index is also the **pruning surface**: one row per entry means the vault's size is
visible at a glance, and a stale row is a stale fact that gets pointed at.

The prune procedure — when to run it, what to delete, what to keep marked stale — is in
[`README.md`](README.md) → *Maintenance*.
