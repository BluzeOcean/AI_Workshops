# A copied index goes stale without an owner

**Status:** active

**Date:** 2026-11-15
**Symptom:** `AGENTS.md`'s reference section carried a hand-maintained table of the vault's
twelve entries,
duplicating what `.vault/` already knew. The table had **no status column**, so it could
not express the one fact that matters about a memory — whether it is still true. The
decisions it listed each carried `Status: active | superseded` in their own file, and the
mechanism for revoking one existed (`Supersedes:`), but **nothing recorded the revocation
back into the table.** A decision revoked tomorrow would still be listed in `AGENTS.md` as
live, and `AGENTS.md` is loaded at every session start.

The same shape turned up twice more in the same tree: the bootstrap skill
`ue-op-mcp-connect` carried its own table of the `ue-op-*` skills, which had drifted to
listing 20 of the workshop's 32, and the deprecated skillset folder held an older copy of
every skill — so a duplicate scan found a match for almost anything it was asked to
forge.

**Cause:** A copy with no owner. The table was written once, as a convenience, and then
every future update to the vault had to be applied in two places — and the second place
had no rule attached to it, so it silently did not happen. The supersession mechanism also
pointed in one direction only: the new decision linked to the old one, but the old one
never linked forward, so an agent that opened a revoked decision hit a dead end instead of
being handed the replacement.

**Fix:**

- **Never copy an index into the always-loaded file.** Put the index in one place with a
  status column, and point at it. `AGENTS.md` now references `.vault/vault_index.md`
  instead of duplicating it.
- **A supersession is recorded in four places, in one commit:** the replacement file
  (`Supersedes:`), the old file (`Status: superseded` **and** a `Superseded by:`
  back-link), the index row, and `AGENTS.md` if it quoted the old decision.
- **The back-link is not optional.** `Supersedes` points forward from the replacement;
  `Superseded by` points back from the revoked entry. Without the back-link, an agent
  reading the old file learns that it is dead and nothing else.
- **A skill that has to carry a catalogue should point at the catalogue.** The bootstrap
  skill now names the path of `skill_catalog.md` instead of listing skills, and the
  duplicate scan no longer walks the deprecated folder — a scan that finds this
  workshop's own past is not finding a duplicate.

**Applies when:** anything in the workshop is duplicated in more than one place, whenever
an entry's truth can change, and whenever a table of contents is maintained by hand in a
file that is loaded on every session.
