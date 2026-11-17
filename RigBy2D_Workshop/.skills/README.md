# `.skills/` — procedures

A skill is a **repeatable task** you want any agent to be able to execute well, without
rediscovering it. "What went wrong last time" is not; that is a **lesson**, and it belongs
in `.vault/lessons/`.

**The catalog of what exists is [`skill_catalog.md`](skill_catalog.md).** Read it to find the
skill you need; this file is about the format and the naming rule.

The workshop has **two maps** and they are the only things an agent needs before it starts
working: this catalog (procedures) and `.vault/vault_index.md` (memory). The folders they
point at are fetched on demand — never read them end to end.

## Layout

```
.skills/
  README.md          <- this file: the format and the naming convention
  skill_catalog.md   <- the index: every skill, what it does, when to use it
  <skill-name>/
    SKILL.md         <- required: frontmatter + the instructions
    scripts/         <- optional: executable helpers for this skill
    references/      <- optional: long docs, loaded only when needed
```

---

## Naming convention

**Every skill folder is named `rb2d-op-<verb-noun>`. The `rb2d-op-` prefix is mandatory.**

```
rb2d-op-build-rig        <- verb-noun
rb2d-op-export-animation <- verb-noun
rb2d-op-import-sprites   <- verb-noun
```

The rules:

1. **The folder name starts with `rb2d-op-`.** No exceptions. The prefix says which
   application the skill belongs to, and it keeps RigBy2D skills from colliding with skills
   from other workshops in a shared skills directory.
2. **`<verb-noun>` describes the operation**, in lowercase with hyphens:
   `build-rig`, `export-animation`, `import-sprites`. Not `rig-building` or `sprites`.
3. **The frontmatter `name:` must match the folder name exactly.** A mismatch is the usual
   cause of a skill not registering.
4. **A skill is one operation.** If the description needs the word "and", it is two skills.
5. **Variants carry a situation suffix**, and the existing sibling is renamed to match, so
   the family reads as siblings: `rb2d-op-import-sprites` → `rb2d-op-import-sprites-batch`.

---

## Writing a `SKILL.md`

YAML frontmatter, then the body:

```markdown
---
name: rb2d-op-<verb-noun>
description: One sentence saying what it does AND when to use it.
---

# Skill title

<the instructions>
```

**The `description` is the whole discovery mechanism.** An agent decides whether to open a
skill by reading that one line, alongside every other skill it can see. It must contain both
the *what* and the *when*:

- ✅ `description: One sentence saying what it does AND when to use it.`
- ❌ `description: RigBy2D helper.` — tells an agent nothing about when to use it.

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
6. **Link the lessons.** If a step is there because something went wrong, link the lesson
   file so the reason survives.
7. **Never hardcode a version or an install path.** Resolve it at run time, so the skill
   still works after the app updates.

---

## Forging new skills

The point of `.skills/` is that it **grows as the workspace is used**. Skills are forged out
of tasks that actually happened.

When a task succeeds, do not just log it — **decompose it**. Break the operation into its
modular pieces and ask which one is worth keeping as a procedure: the part that was
fiddly, the part that will come up again, the part that took three attempts to get right.
That piece becomes `SKILL.md` — written with the **optimized steps**, not the steps you
happened to take. The skill records the fastest correct path, so the next agent starts
there instead of rediscovering the slow one.

To forge one:

1. Do it once, for real.
2. Write the `SKILL.md` that would have let you do it correctly the first time.
3. Name the folder `rb2d-op-<verb-noun>` — **the prefix is not optional** — and make the
   frontmatter `name:` match it exactly.
4. Save any helper script next to the skill, in `scripts/`.
5. If the task produced a lesson, write the lesson too, in `.vault/lessons/` — **and add
   its row to `.vault/vault_index.md`**. A vault file with no row does not exist: no agent
   will find it, and the next prune deletes it.
6. **Add it to `skill_catalog.md`.** An agent decides what to open by reading that file; a
   skill that is not listed is a skill nobody will find.

**Do not write a skill speculatively.** A skill for something you have only done once, or
for a task that has not happened yet, is a guess with a confident tone — and an agent
trusts it. Skills here are forged from real work, not predicted work.
