# `.vault/` — the workspace memory

This folder is **not** a cache and **not** an output directory. It is the durable
memory of this workspace: everything an agent needs to work *better than the last
agent did*.

> **The rule:** if a lesson cost time, money, or a wrong delivery, it belongs in
> `.vault/`. If it is a repeatable *procedure*, it belongs in `.skills/`. If it is
> a *rule for how to behave here*, it belongs in `AGENTS.md`.

## Layout

| Folder | Holds |
|---|---|
| `lessons/` | One file per hard-won lesson — what went wrong, why, and the fix. Append-only. |
| `decisions/` | Decisions taken for this workspace (scope, conventions, ownership). Each records the date and the reason, so a later agent can see *why* and can challenge it. |
| `model-notes/` | Notes about add-ons, render engines and settings: what works well on this machine, and the settings that did it. Text only. |
| `recipes/` | A script + settings + export options that produced something good. **Text only** — never the `.blend` or the render. |
| `workflows/` | Known-good command sequences (a boot sequence, a bridge handshake, an export chain) plus the notes on when to use them. |

> **No media in this folder.** No `.blend`, no renders, no textures, no exports.
> The vault records *how* the work was done — the script, the settings, the
> version — and the artifact itself lives in the destination the user confirmed.

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

## Rules for agents

1. **Check `lessons/` before running something expensive.** It is cheaper than repeating a
   failure.
2. **Write the lesson, not the diary.** One file, one lesson. No session logs.
3. **Never overwrite a lesson.** Add a new one and mark the old decision `superseded`.
4. **A lesson that contradicts `AGENTS.md` does not silently win.** Fix `AGENTS.md`
   too, or say clearly in the lesson that it is an open question.
5. **If a lesson is no longer true, say so in the file.** Mark it `Status: stale` with the
   date it stopped applying and why.
6. **Record the Blender version** in any entry that depends on the API. A trick that works
   on 5.3 and fails on 5.4 is a versioned fact, not a universal one.
7. **A success is not just a log entry — it is material for a skill.** After a task that
   went well, decompose the operation and write the modular piece worth repeating into
   `.skills/`, with the optimized steps. See §6 of `AGENTS.md`.
8. **Keep the indexes current.** `.skills/README.md` lists the skills; an agent decides
   what to open by reading it. A skill that exists but is not listed is a skill nobody
   finds.
