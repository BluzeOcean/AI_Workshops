# `.vault/` — the RigBy2D memory bank

This folder is **not** a cache, **not** an output directory, and **not** a diary of what
agents did. It is the durable, **RigBy2D-specific** memory of this workspace: the facts
that would make the next agent working on RigBy2D faster, or stop it repeating a failure.

> **The rule:** if a lesson cost time, money, or a wrong delivery, it belongs in
> `.vault/`. If it is a repeatable *procedure*, it belongs in `.skills/`. If it is a
> *rule for how to behave here*, it belongs in `AGENTS.md`.

## The test every entry must pass

> **Would a future agent, facing the same situation, act faster or avoid a failure because
> this file exists?** If the entry would not change what they do, it does not go in the
> vault.

That test rules out, in one stroke:

- **House rules that would hold for any application** — they belong in `AGENTS.md`, once.
- **Session narratives** — one file, one fact. No diaries.
- **Restatements of `AGENTS.md`** — link to the section instead.
- **Unverified guesses** — a lesson nobody observed is a guess with a confident tone.
- **Anything with no operational consequence** — if it changes no command, path, setting or
  decision, it is chatter.

## Layout

| Folder | Holds |
|---|---|
| `decisions/` | Decisions taken for this workspace (scope, conventions, ownership). Each records the date and the reason, so a later agent can see *why* and can challenge it. |
| `lessons/` | One file per hard-won lesson — what went wrong, why, and the fix. Append-only. |
| `model-notes/` | Notes about RigBy2D itself — what it is good for, what this machine's install can do, and the settings that worked. Text only. |
| `recipes/` | A script + settings that produced something good. **Text only** — never the artifact. |
| `workflows/` | Known-good command sequences plus the notes on when to use them. |
| `vault_index.md` | **The map.** One row per entry, with its status. This is what an agent reads to fetch wisdom — never the folders themselves. |

> **No media in this folder.** The vault records *how* the work was done — the command,
> the settings, the version — and the artifact itself lives in the destination the user
> confirmed.

## Writing a lesson

Use this shape — short, concrete, and written for a stranger with no context:

```markdown
# <one-line title>

**Status:** active

**Date:** YYYY-MM-DD
**Symptom:** what was observed, literally (the error text, the wrong output).
**Cause:** why it happened.
**Fix:** what to do instead — as an instruction, not a story.
**Applies when:** the trigger that means this lesson is relevant again.
```

Filename: `lessons/YYYY-MM-DD-short-slug.md`.

**Every entry carries a `Status:` field**, whatever its folder: `active`, `superseded`,
`stale`, or `draft`. The index row and the file must agree — a file that says one thing
and an index that says another is the exact failure the index exists to prevent. Model
notes and workflows also carry `**Recorded:** YYYY-MM-DD` — the date the fact was
**verified**, because a fact about this machine expires on its own.

## Writing a decision

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

`Superseded by` is the **back-link**. A decision that is revoked points at its replacement,
so an agent who opens the old file is handed the new one instead of a dead end. `Supersedes`
points forward from the replacement to what it replaced. Both directions, always.

The full revocation procedure — the four places a supersession must be recorded, and in what
order — is in `../AGENTS.md` §5, *Revoking a decision*.

## Rules for agents

1. **Check `lessons/` before running something expensive.** It is cheaper than repeating a
   failure.
2. **Write the lesson, not the diary.** One file, one lesson. No session logs.
3. **Never overwrite a lesson.** Add a new one and link it. A **decision** is revoked with
   `Status: superseded` plus a `Superseded by:` back-link — the four-step procedure is in
   `../AGENTS.md` §5, *Revoking a decision*.
4. **A lesson that contradicts `AGENTS.md` does not silently win.** Fix `AGENTS.md`
   too, or say clearly in the lesson that it is an open question.
5. **If a lesson is no longer true, say so in the file.** Mark it `Status: stale` with the
   date it stopped applying and why.
6. **Record the version** in any entry that depends on the API. A trick that works on one
   version and fails on the next is a versioned fact, not a universal one.
7. **A success is not just a log entry — it is material for a skill.** After a task that
   went well, decompose the operation and write the modular piece worth repeating into
   `.skills/`, with the optimized steps.
8. **Keep the indexes current.** `.skills/skill_catalog.md` lists the skills and
   `vault_index.md` lists the vault entries; an agent decides what to open by reading
   them. A skill or an entry that exists but is not listed is one nobody finds.
9. **A vault file with no index row does not exist.** If you wrote one, add its row in the
   same commit — otherwise the next prune deletes a file nobody can find.

---

## Maintenance — the vault is pruned, not just grown

**The vault grows on every task. Growth is the point; accumulation is not.** An entry no
future task would ever read is a pure cost: it lengthens every index, it competes for
attention in a grep, and it slowly contradicts the entries that matter. Six weeks from now
the vault is either a memory bank or a landfill, and the difference is decided by whether
somebody prunes it.

**The procedure lives here and the trigger lives in `../AGENTS.md` §5** — the trigger is
always loaded, this is fetched only when a prune actually runs.

### When a prune runs

- **After any task that added or changed a vault entry.** You are already in the file; the
  cost is one read of `vault_index.md`.
- **Whenever `vault_index.md` passes 40 rows.** Past that, the index stops being a map.
- **Whenever two entries answer the same question.** Merge them, then prune.

### The three questions, per entry, in this order

1. **Would a future agent ever read this?** If no plausible future task would grep for it,
   it is a diary entry — **delete it**. This is the question that keeps the vault small.
2. **Is it still true?** Facts about *this machine* expire — an installed app, a port, a
   PID, a plugin inventory, a registry quirk. Mark it `Status: stale` with the date it
   stopped applying and why, or refresh it in place. **An entry about machine state must
   carry the date it was verified.**
3. **Is it in the right place?** A rule → `AGENTS.md`. A procedure → `.skills/`. A fact →
   the vault. Two facts in one file → split it, because one of them will be updated and
   the other will rot.

### The size rule

- **One file, one fact.**
- **Past ~40 lines it is not a vault entry.** It is a skill (a procedure), a recipe
  (settings that worked), or it belongs in `AGENTS.md` (a rule). Split it or move it.
- **The index row is the entry's body for most purposes.** If the row in `vault_index.md`
  already says what a future agent needs, the file behind it may be three lines long.

### Keep, merge, delete

| | What |
|---|---|
| **Keep, marked `stale`** | a lesson that cost real time — losing it means paying again |
| **Delete** | a diary entry, a restatement of `AGENTS.md`, an unverified guess, anything with no operational consequence |
| **Merge** | two entries about the same symptom — keep the sharper one, fold the other's specifics into it, delete the other, update the index |
| **Move** | a procedure that keeps being repeated → `.skills/`; a rule → `AGENTS.md` |

### The index is the pruning surface

`vault_index.md` holds one row per entry with its status, so the vault's size is visible at
a glance, and a stale row is a stale fact that keeps being pointed at.

**A prune is finished when every file in `.vault/` has a row and every row's status is
true.** A file with no row is deleted; a row pointing at a deleted file is deleted. Do not
leave the index describing a vault that no longer exists.

### The skills get the same treatment

The vault is not the only thing that rots. A skill whose procedure no longer works — a
command that changed, a path that moved, a step that the app renamed — is worse than
no skill, because an agent trusts it. When a prune finds a stale skill, **fix it or mark
it**, and update `.skills/skill_catalog.md` in the same commit. A skill that exists but is
not in the catalog is a skill nobody finds; a skill in the catalog that no longer works is
a trap.

---

## What is in here right now

**Nothing yet.** This workshop was scaffolded on 2026-11-17 and the vault is empty on
purpose — no fact about RigBy2D has been verified yet, and an unverified guess is worse
than an empty folder.

The research contract in `../AGENTS.md` §4 is what fills it. Every entry, with its status,
goes in [`vault_index.md`](vault_index.md). That file is the map; these folders are the
territory. Read the index, not the folders.

_Scaffolded 2026-11-17 for RigBy2D_Workshop._
