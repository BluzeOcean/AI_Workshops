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
| `decisions/` | Decisions taken for this workspace (output conventions, model choices, scope). Each records the date and the reason, so a later agent can see *why* and can challenge it. |
| `model-notes/` | **Notes about** models: what each one in `D:\.models` is good for, and the settings that worked. Text only — the model files live in `D:\.models`, never here. |
| `workflows/` | Known-good ComfyUI graphs (API format) plus the notes on when to use them. |
| `recipes/` | Reusable prompt + layout + settings that produced something good. |

> **No media in this folder.** No images, no video, no audio, no meshes, no model files.
> The vault records *how* an asset was made — the prompt, the boxes, the seed, the settings —
> and the asset itself lives in the destination the user confirmed.

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

1. **Check `lessons/` before running a generation.** It is cheaper than repeating a failure.
2. **Write the lesson, not the diary.** One file, one lesson. No session logs.
3. **Never overwrite a lesson.** Add a new one and mark the old decision `superseded`.
4. **A lesson that contradicts `AGENTS.md` does not silently win.** Fix `AGENTS.md`
   too, or say clearly in the lesson that it is an open question.
5. **If a lesson is no longer true, say so in the file.** Mark it `Status: stale` with the
   date it stopped applying and why.
