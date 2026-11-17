# Vault index — every entry, one row

**The map of `.vault/`.** An agent that wants to fetch wisdom reads **this file**, picks the
row, and opens only that entry. **Never read the vault end to end** — grep it (see
`../AGENTS.md` §5) or read this index.

**`Status` is the first column to read.** Only `active` rows are worth opening. A
`superseded` row names its replacement. A `stale` row was once true and no longer is.

| Status | Entry | What it saves you |
|---|---|---|
| — | _(none yet)_ | |

**No entries yet.** This workshop was scaffolded on 2026-11-17 and the vault is empty on
purpose. No fact about RigBy2D has been verified yet, and **an unverified guess is worse
than an empty vault** — it reads like knowledge and gets trusted.

The research contract in `../AGENTS.md` §4 is what fills this table: find the install, find
the control surface, probe the API, find where output goes, verify one real trap. Each
answer goes in a file under the matching folder, and each file gets a row here **in the
same commit**.

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
   write-back — `../AGENTS.md` §5, *Revoking a decision*.
4. **The index is pruned with the vault, never after it.** A prune pass that ends with an
   index that still lists a deleted file is a failed prune.
