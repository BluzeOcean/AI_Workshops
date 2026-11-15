# `decisions/` — how this workspace works

Decisions taken for this workspace: scope, conventions, ownership. Each one records the
date and the reason, so a later agent can see *why* and can challenge it.

```
decisions/YYYY-MM-DD-short-slug.md
```

```markdown
# <decision>

**Date:** YYYY-MM-DD
**Status:** active | superseded | stale
**Decision:** ...
**Reason:** ...
**Supersedes:** <link, if any>
**Superseded by:** <link, if any>
```

Mark a decision `superseded` rather than deleting or rewriting it — a later agent has to be
able to see what was true then, and why it stopped being true.

`Superseded by` is the **back-link**: a revoked decision names its replacement, so an agent
who opens it is handed the new one instead of a dead end. `Supersedes` points the other
way, from the replacement to what it replaced. Both directions, always.

A decision is not revoked until the revocation is recorded in **four** places — the new
file, the old file's status, its `Superseded by:` back-link, and the `vault_index.md` row.
The procedure is in `../../AGENTS.md` §6, *Revoking a decision*.
