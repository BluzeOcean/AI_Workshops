# `.vault/` — the Unreal memory bank

This folder is **not** a cache, **not** an output directory, and **not** a diary of what
agents did. It is the durable, **Unreal-specific** memory of this workspace: the facts that
would make the next agent working on Unreal faster, or stop it repeating a failure.

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
| `model-notes/` | Notes about Unreal itself — what it is good for, what this machine's engine builds can do, and the settings that worked. Text only. |
| `recipes/` | A script + settings that produced something good. **Text only** — never the artifact. |
| `workflows/` | Known-good command sequences plus the notes on when to use them. |

> **No media in this folder.** The vault records *how* the work was done — the command,
> the settings, the version — and the artifact itself lives in the destination the user
> confirmed. See `../decisions/2026-11-15-where-unreal-artifacts-belong.md`.

## Writing a lesson

Use this shape — short, concrete, and written for a stranger with no context:

```markdown
# <one-line title>

**Date:** YYYY-MM-DD
**Symptom:** what was observed, literally (the error text, the wrong output).
**Cause:** why it happened.
**Fix:** what to do instead — as an instruction, not a story.
**Applies when:** the trigger that means this lesson is relevant again.
```

Filename: `lessons/YYYY-MM-DD-short-slug.md`.

## Writing a decision

```markdown
# <decision>

**Date:** YYYY-MM-DD
**Status:** active | superseded
**Decision:** ...
**Reason:** ...
**Supersedes:** <link, if any>
```

Mark a decision `superseded` rather than deleting or rewriting it — a later agent has to be
able to see what was true then, and why it stopped being true.

## Rules for agents

1. **Check `lessons/` before running something expensive.** It is cheaper than repeating a
   failure.
2. **Write the lesson, not the diary.** One file, one lesson. No session logs.
3. **Never overwrite a lesson.** Add a new one and mark the old decision `superseded`.
4. **A lesson that contradicts `AGENTS.md` does not silently win.** Fix `AGENTS.md`
   too, or say clearly in the lesson that it is an open question.
5. **If a lesson is no longer true, say so in the file.** Mark it `Status: stale` with the
   date it stopped applying and why.
6. **Record the version** in any entry that depends on the API. A trick that works on one
   version and fails on the next is a versioned fact, not a universal one.
7. **A success is not just a log entry — it is material for a skill.** After a task that
   went well, decompose the operation and write the modular piece worth repeating into
   `.skills/`, with the optimized steps.
8. **Keep the indexes current.** `.skills/README.md` lists the skills; an agent decides
   what to open by reading it. A skill that exists but is not listed is a skill nobody
   finds.

## What is in here right now

The entries that will save a future agent the most time are indexed in `../AGENTS.md` §8.

_Scaffolded 2026-11-15 for Unreal_Workshop._
