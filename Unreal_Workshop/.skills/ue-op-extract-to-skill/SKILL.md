---
name: ue-op-extract-to-skill
description: Use when an operation has just been completed and should be captured as a reusable skill — distils the session's dead ends into a verified, named procedure under V:\04_Projects\Workshops\Unreal_Workshop\.skills\<name>\SKILL.md, checks for duplicates first, and wires the new skill into Claude Code's discovery. Skip when the work was a one-off with no reusable shape (record that in memory instead), or when an existing skill already covers the operation (update that one instead).
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# ue-op-extract-to-skill — turn a finished operation into a reusable skill

A skill is only worth writing if it saves a **dead end**. An operation that
went smoothly because the API was obvious does not need a skill. Rank candidate
operations by how much reasoning the dead ends cost.

## When to apply

- The user says "save this as a skill", "capture this workflow", "write a
  skill for this", "modularise what you just did"
- You have just finished a multi-step operation whose steps were non-obvious
  (wrong tool names, wrong type ids, a modal dialog that wedged the editor,
  a config that only takes effect after a restart)
- A recurring operation has emerged across sessions

## When NOT to apply

- The work was a genuine one-off with no reusable shape — record the *fact* in
  memory instead (`memory/<name>.md` + a line in `MEMORY.md`)
- An existing skill already covers the operation — **update that skill**
  rather than adding a near-duplicate. Duplicates drift, and a stale
  duplicate is worse than no skill
- The knowledge is a single fact or a path — that is memory, not a skill

---

## Procedure

### 1. Mine the session for dead ends

Re-read what actually happened and list the moments where you were **wrong**:
wrong tool name, wrong argument shape, wrong property name, an operation that
silently did nothing, an error that had to be diagnosed from a log.

These are the payload. A skill that only restates the happy path is a
tutorial, not a skill — and the happy path is what the model can already infer.

For each dead end capture:
- the **symptom** (what you saw: error text, empty result, timeout)
- the **cause** (which file/line/argument was wrong)
- the **fix** (the exact corrected call)

### 2. Check for duplicates — deeply

Name matching is not enough. Two skills can do "the same thing" under
different names, and a new skill is often an **upgrade** or a **variant** of
an existing one rather than a new topic.

**Step 2a — inventory every skill**

```bash
for d in "V:/04_Projects/Workshops/Unreal_Workshop/.skills" "D:/UE/.ue-op-skillset" "D:/Godot/skills" "C:/Users/Bluze/.claude/skills"; do
  find "$d" -name "SKILL.md" 2>/dev/null | while read f; do
    echo "== $(grep -m1 '^name:' "$f" | sed 's/name: *//')  <- $f"
    grep -m1 '^description:' "$f" | cut -c14-160
  done
done
```

**Step 2b — read the bodies of every candidate, not just their descriptions**

A skill only duplicates another if it operates on **the same things for the
same intent**. Compare each candidate against the operation you just
performed:

| Dimension | Question |
|---|---|
| Target | Same asset/objects? (blueprint vs data asset vs level vs config) |
| Intent | Same outcome the caller wants? |
| Trigger | Would the same user request fire both? |
| Tooling | Same tool family? (MCP dispatcher vs filesystem vs CLI) |
| Preconditions | Same engine version / project type / plugin set? |

If any two differ in **target, intent, or trigger**, they are different
skills even if the wording is similar.

**Step 2c — classify the relationship**

| Relationship | Test | Action |
|---|---|---|
| **Same operation** | same target + same intent + same trigger | **Upgrade the existing skill.** Merge the new dead ends into it; do not create a second skill |
| **Variant** | same intent + same target, but a different *situation / config / settings / mode* | Create the new variant **and rename the existing one** so the pair reads as siblings (see below) |
| **Partial overlap** | shares machinery but a different target | Put the shared machinery in one skill and cross-reference the other |
| **Disjoint** | nothing in common | Create a new skill |

"Upgrade" is the common case: the operation you just did is the *same*
operation as an existing skill but you learned more. Fold the new knowledge
into that skill — richer gotchas, corrected calls, extra examples — and leave
one skill for that operation.

### 2d — Naming variants so siblings are obvious

**The `ue-op-` prefix is mandatory.** Every skill folder in this workshop is
`ue-op-<verb-noun>` — no exceptions. The prefix says which application the
skill belongs to and keeps Unreal skills from colliding with skills from other
workshops in a shared skills directory. The frontmatter `name:` must match the
folder name exactly.

When the operation is a **variant** of an existing skill, name the pair so the
relationship is self-evident:

```
ue-op-<verb-noun>-<situation>
```

Examples of the situation suffix: `-legacy`, `-enhanced`, `-node`,
`-multi-project`, `-new-project`, `-existing-project`.

**Rename the existing skill too**, so both carry the same suffix dimension:

```
ue-op-setup-input          (legacy axis bindings)   → ue-op-setup-input-legacy
ue-op-setup-input-enhanced (Enhanced Input)          ← the new one
```

The family then reads as siblings rather than as one generic skill plus an
unrelated extra.

Renaming mechanics — the directory name, the frontmatter `name:`, and every
cross-reference must move together:

```bash
mv "V:/04_Projects/Workshops/Unreal_Workshop/.skills/<old>" "V:/04_Projects/Workshops/Unreal_Workshop/.skills/<new>"
# then update frontmatter name:, and any "ue-op-<old>" mentions in other skills
grep -rl "ue-op-<old>" "V:/04_Projects/Workshops/Unreal_Workshop/.skills" | xargs sed -i 's/ue-op-<old>/ue-op-<new>/g'
```

Then re-junction the renamed skill (see step 5) — a junction still points at
the old path otherwise.

### 3. Name it

- `ue-op-<verb-noun>` for a single editor/content operation
  (`ue-op-setup-input`, `ue-op-wire-graph`, `ue-op-capture-editor`)
- `ue-op-<noun>` for a composite recipe
  (`ue-op-setup-playable-character`)
- `ue-op-<verb-noun>-<situation>` when it is a variant of an existing skill —
  and rename the existing one to match (step 2d)
- Check the name is not already taken (step 2)
- The folder name starts with `ue-op-` — the prefix is not optional

### 4. Write it

Location: `V:\04_Projects\Workshops\Unreal_Workshop\.skills\<name>\SKILL.md`,
where `<name>` **always starts with `ue-op-`**.

Frontmatter — every field matters:

```yaml
---
name: ue-op-setup-input          # must match the directory name, ue-op- prefix included
description: Use when <trigger>. <what it does>. Skip for <conditions>.
user-invocable: true             # so it can be called as /ue-op-<name>
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - mcp__unreal-mcp__call_tool   # the MCP dispatcher, when the skill uses the editor
---
```

The `description` is the *only* thing loaded into every session, so it must
carry the trigger and the skip conditions — that is what stops the skill
firing on the wrong task.

Body structure that works:

| Section | Purpose |
|---|---|
| `When to apply` / `When not to apply` | stop it firing on the wrong task |
| `Procedure` | numbered, concrete, each step a real call |
| `Verified facts & gotchas` | the dead ends, written as symptom → cause → fix |
| `Output contract` | what the caller should end up with |

Rules:
- **Every command must be one that was actually run.** If a form was guessed,
  say so or drop it.
- Prefer exact strings: tool names, type ids, property names, file paths,
  error messages. That is what makes the skill worth loading.
- Show the call shape, not just the prose. A parameter the model would get
  wrong should appear verbatim.
- Keep it under ~150 lines. A skill nobody reads is not a skill.

### 5. Wire it into discovery — scoped, never global

`V:\04_Projects\Workshops\Unreal_Workshop\.skills` is deliberately **outside** `~/.claude/skills` so that
non-UE agents never load these skills. Keep it that way.

**Do not flat-junction into `~/.claude/skills` unless the skill is the single
UE entry point.** Nested skills are not discovered — a junction
`~/.claude/skills/ue -> V:\04_Projects\Workshops\Unreal_Workshop\.skills` does *not* expose the skills inside it
(verified: a skill written there stays invisible).

Register UE-operation skills **project-scoped**, so only sessions in a UE
project see them:

```bash
cmd //c "mklink /J D:\UE\<Project>\.claude\skills\<name> V:\04_Projects\Workshops\Unreal_Workshop\.skills\<name>"
```

For each UE project the user works in, that one command makes the skill
callable as `/<name>`. A plain directory copy must be deleted before
junctioning, or the copy silently shadows the source and drifts.

The single global UE entry point (`ue-op-mcp-connect`) stays flat-junctioned in
`~/.claude/skills` — it is the bootstrap, and its body carries the catalogue
of the `ue-op-*` skills so they can be found on demand even in a project that
has not been wired yet.

### 6. Add it to the catalog

The catalog is `.skills/skill_catalog.md` — the file an agent reads to decide what to
open. **A skill that is not listed there is a skill nobody will find.**

Add a row for the new skill, in the group it belongs to, with the same shape as the
others: the name as a link, what it does, and when to use it.

### 7. Verify

```bash
cmd //c "dir /AL D:\UE\<Project>\.claude\skills" | findstr /I "<name>"
```

Then confirm the skill appears in the available-skills list (it is announced
at the start of the next turn). Fix the frontmatter `name:` if it did not
register — a name/directory mismatch is the usual cause.

### 8. Report

Tell the user: the skill name, what dead end it now prevents, and which
existing skill it cross-references. Offer the next candidate operation if the
session had one.

---

## Anti-patterns

| Don't | Why |
|---|---|
| Write a skill that restates the API docs | the model can read the source; a skill should carry what the docs don't |
| One giant skill for a whole project | uncallable; split at the seams |
| Duplicate a skill under a second name | they drift, and the stale one misleads |
| Put a one-off fact in a skill | use memory — it loads as one line |
| Leave a skill unwired | undiscoverable = nonexistent |
| Leave a skill out of `skill_catalog.md` | undiscoverable = nonexistent |
| Name a skill without the `ue-op-` prefix | breaks the convention every other skill follows |

## Related

- `ue-op-mcp-connect` — establishing the MCP bridge itself (the operation that
  *precedes* every other one)
- `ue-op-setup-playable-character` — the composite recipe; references the
  primitives rather than repeating them
