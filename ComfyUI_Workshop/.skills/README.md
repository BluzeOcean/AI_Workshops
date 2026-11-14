# `.skills/` — procedures

A skill is a **repeatable task** you want any agent to be able to execute well, without
rediscovering it. "How to bring ComfyUI up", "how to generate a concept sheet", "how to
batch a turnaround" — those are skills. "What went wrong last time" is not; that is a
**lesson**, and it belongs in `.vault/lessons/`.

## Layout

```
.skills/
  README.md
  <skill-name>/
    SKILL.md          <- required: frontmatter + the instructions
    scripts/          <- optional: executable helpers for this skill
    references/       <- optional: long docs, loaded only when needed
```

## Writing a `SKILL.md`

YAML frontmatter, then the body:

```markdown
---
name: skill-name
description: One sentence saying what it does AND when to use it.
---

# Skill title

<the instructions>
```

**The `description` is the whole discovery mechanism.** An agent decides whether to open a
skill by reading that one line, alongside every other skill it can see. It must contain both
the *what* and the *when*:

- ✅ `description: Generate a MOSS-Image concept sheet and save it to a confirmed destination. Use when asked for mech or prop concept art.`
- ❌ `description: ComfyUI helper.` — tells an agent nothing about when to use it.

Body rules:

1. **Write for a competent agent, not a beginner.** No "let's think step by step". State the
   command, the expected output, and the failure mode.
2. **Every command must be copy-pasteable and runnable as written.** No placeholders the
   agent has to guess how to fill — use `<ANGLE_BRACKETS>` for the one value that must vary,
   and say what it is.
3. **Include the failure modes.** The most valuable line in a skill is usually the one that
   says what a wrong result looks like and what to do about it.
4. **Keep it short.** If it runs long, move detail into `references/` and link to it.
5. **Say where the outputs land.** Always name the destination explicitly.
6. **Link the lessons.** If a step is there because something went wrong, link the lesson file
   so the reason survives.

## Forging new skills

The point of `.skills/` is that it grows as the workspace is used. When you do something
worth repeating:

1. Do it once, for real.
2. Write the `SKILL.md` that would have let you do it correctly the first time.
3. Save any helper script next to the skill, in `scripts/`.
4. If the task produced a lesson, write the lesson too — in `.vault/lessons/`.

Do **not** write a skill for something you have only done once, speculatively. A skill that
is wrong is worse than no skill, because agents trust it.

## Skills available now

| Skill | What it covers |
|---|---|
| [`comfyui-boot`](comfyui-boot/SKILL.md) | Bring the headless ComfyUI + MCP stack up against a confirmed destination, and diagnose it when it will not come up. |
| [`comfyui-generate`](comfyui-generate/SKILL.md) | Turn a request into a confirmed destination, a valid graph, and a rendered asset — including MOSS-Image layout control. |
| [`moss-reference-variation`](moss-reference-variation/SKILL.md) | Generate variations of an **existing model or picture** by feeding the reference PNG into MOSS-Image with the edit LoRA, so the design is inherited instead of re-described. |
