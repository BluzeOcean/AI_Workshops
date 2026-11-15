# `.skills/` — procedures

A skill is a **repeatable task** you want any agent to be able to execute well, without
rediscovering it. "How to import a glTF and clean it up", "How to render a turntable set",
"How to export for Unreal" — those are skills. "What went wrong last time" is not; that is a
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

- ✅ `description: Import a glTF into Blender 5.3, apply transforms, rename the root and save it to a confirmed destination. Use when a task brings in a 3D file to clean up or re-export.`
- ❌ `description: Blender helper.` — tells an agent nothing about when to use it.

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
7. **Never hardcode the Blender version or path.** Resolve it (§3 of `AGENTS.md`). A skill
   that names `Blender 5.3\blender.exe` will be wrong the day 5.4 lands — and the skill
   should say so out loud when it re-resolves to a newer install.

## Forging new skills

The point of `.skills/` is that it **grows as the workspace is used**. Nothing here ships
with the workshop; the skills are forged out of tasks that actually happened.

When a task succeeds, do not just log it — **decompose it**. Break the operation into its
modular pieces and ask which one is worth keeping as a procedure: the part that was
fiddly, the part that will come up again, the part that took three attempts to get right.
That piece becomes a skill — written with the **optimized steps**, not the steps you
happened to take. The skill records the fastest correct path, so the next agent starts
there instead of rediscovering the slow one.

To forge one:

1. Do it once, for real.
2. Write the `SKILL.md` that would have let you do it correctly the first time.
3. Save any helper script next to the skill, in `scripts/`.
4. If the task produced a lesson, write the lesson too — in `.vault/lessons/`.
5. **Add it to the table below.** An agent decides what to open by reading that table; a
   skill that is not listed is a skill nobody will find.

Do **not** write a skill for something you have only done once, speculatively. A skill that
is wrong is worse than no skill, because agents trust it.

## Skills available now

None yet. The tool layer (`tools/README.md`) has to exist before a skill can promise a
command, and this workspace has not run a Blender task yet.

Keep this table current as skills are forged:

| Skill | What it covers |
|---|---|
| _(none yet)_ | |
