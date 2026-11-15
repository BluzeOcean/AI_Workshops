# Unreal_Workshop

A workspace that gives any agent the ability to drive Unreal Engine.

**Tell the agent to read this file, then `AGENTS.md`.** That is the entire entry point.
`AGENTS.md` is the **gateway and the rules** — where everything is, how to look it up, and
how to maintain the workshop. Everything else is fetched on demand.

It contains **no media**. It holds only the **rules**, the **skills**, the **vault
(memory)** and the **tools** — text an agent can read. No Unreal assets, no pictures, no
renders, no large or binary files of any kind, and deliberately **no `.gitignore`**:
nothing that belongs here needs excluding, because media does not come here at all.

```
AGENTS.md        <- start here. the gateway and the rules.
.skills/         <- procedures: one folder per skill, each with a SKILL.md
.vault/          <- the memory bank: lessons, decisions, notes, recipes, workflows
tools/           <- the scripts (spec only for now — see tools/README.md)
```

Two files are **maps**, and they are the only ones an agent needs before it starts working:
`.skills/skill_catalog.md` (every skill, what it does, when to use it) and
`.vault/vault_index.md` (every memory, its status, what it saves you). The folders they
point at are fetched on demand.

The workshop is **agent-agnostic**: markdown, plain JSON and small scripts. There is no
`.claude/`, no `.cursor/`, no agent-tool config in the tree. A skill is a folder with a
`SKILL.md` — any agent that can read a markdown file can use one. Where an agent needs a
pointer into this workshop (a junction into its own skills directory, an MCP registration),
that pointer lives in the **agent's own configuration**, not here.

## Quick start for an agent

1. Read `AGENTS.md`. It is the gateway: the map, the lookup discipline, and the rules for
   working inside the workshop.
2. Confirm the **destination** for the task — which project, and which folder inside it. If
   the user has not said, ask. The rule is in
   `.vault/decisions/2026-11-15-working-in-a-live-unreal-project.md`.
3. Check what already exists: `.skills/skill_catalog.md` is the **index of the skills** —
   read the `When to use it` column and open the one that matches; `tools/README.md`
   describes the tool layer; `.vault/vault_index.md` is the **map of what past tasks
   learned** — read the index, never the vault end to end.
4. Reach Unreal through the skill that fits — the live editor over MCP
   (`ue-op-mcp-diagnose`), headless (`ue-op-run-headless`), the live editor's Python
   (`ue-op-editor-script`), or a task-specific skill. The catalog says which.
5. Build the script in the **project's `Saved/` folder** (or next to the skill it serves, in
   `.skills/<name>/scripts/`). Save the result into the destination.
6. **Log the memory** in `.vault/` when the task is done — add its row to
   `.vault/vault_index.md`, turn what worked into a skill, and prune what you touched.
   See `.vault/README.md` and §5 of `AGENTS.md`.

## The workshop is not finished when it is created

**The tools, the skills and the memory accumulate as the workshop is used.** They are not
installed at creation time — they are *grown*, by the agent, out of real tasks.

That is what the `.vault/` is for. It is the self-learning mechanism:

- **Failures** become **lessons** — the symptom, the cause, the fix, and the trigger. This
  is what stops the workshop from falling into the same mistake twice.
- **Successes** are **decomposed**. After a task that went well, the agent works out which
  modular piece of that operation is worth keeping as a skill with optimized steps, and
  writes it into `.skills/`. A skill records the fastest correct path, so the next agent
  starts there instead of rediscovering the slow one.
- **Known-good instances** become **recipes** — the exact settings that worked, so the
  result can be reproduced.

The index of what the workshop can currently do is `.skills/skill_catalog.md`. It is kept
current as skills are forged, because an agent decides what to open by reading it. The
memory has its own index, `.vault/vault_index.md`, kept current the same way.

**The vault is pruned, not just grown.** Every task adds to it, so something has to take
away. After a task that touched the vault, the agent runs one prune pass over the index:
an entry no future task would ever read is a diary entry and is deleted; an entry about
machine state that has stopped being true is marked `stale`; two entries answering the same
question are merged; a procedure that keeps being repeated moves into `.skills/`. The
procedure is `.vault/README.md` → *Maintenance*.

Every skill folder is named `ue-op-<verb-noun>`, and the frontmatter `name:` matches the
folder exactly — the convention is in `.skills/README.md`.

## The ideas

**Nothing is loaded until it is needed.** The catalog is the map of the skills; the index is
the map of the memory. Reading either costs a page, not a library. `AGENTS.md` and this
file tell an agent *where* everything is and *when* to open it — they do not carry the
skill bodies or the vault entries with them. Fetch the one you need, when you need it.

**`AGENTS.md` is a router, not a manual.** It holds the rules for working in the workshop
and points at the catalogs for everything else. The Unreal rules — where work goes, which
engine to use, how to reach the editor — live in the vault and the skills, where they are
read when a task needs them and kept current in one place.

**The vault is a memory bank.** Written after each task, searched when something breaks. It
is what stops the workspace from making the same mistake twice.

**A decision that is revoked is superseded, in four places.** The replacement file, the old
file's status, its `Superseded by:` back-link, and the index row — plus `AGENTS.md` if it
quoted the old decision, because `AGENTS.md` is loaded at every session start. A decision
revoked in the vault but still quoted in `AGENTS.md` has not actually been revoked. The
procedure is `AGENTS.md` §5.

## State of the tool layer

`tools/` is a **specification, not an implementation**. The scripts it describes — a version
resolver, an MCP client, a headless runner — have not been written yet. Read `tools/README.md`
for what they have to do and what they must not do.

## About the MCP bridge

A working Unreal MCP bridge **already exists on this machine**: UE 5.8+ ships Epic's own
`ModelContextProtocol` plugin, and it is registered with the agent at **user scope** — so
every session in every directory connects automatically when an editor is up.

**The workshop carries no MCP configuration.** No `.mcp.json`, no `.mcp.json.example`. The
client definition and the procedure for registering it live together in the skill that
needs them:

- `.skills/ue-op-mcp-diagnose/SKILL.md` — the procedure
- `.skills/ue-op-mcp-diagnose/references/client-config.json` — the server definition to register

Two things to know before you use it: **do not register the server at project scope** in a
project that already has the user-scope entry — a duplicate shows as "⏸ Pending approval"
and shadows the working one. And there are **two** Unreal MCP surfaces on this box which
are not interchangeable; read the `ue-op-mcp-diagnose` skill, or the vault decision *the
two Unreal MCP surfaces are not interchangeable*, before assuming which one answered.

## Sister workshops

`../Blender_Workshop/` (DCC), `../Unity_Workshop/`, `../ComfyUI_Workshop/` (image generation).
They follow the same shape — `AGENTS.md`, `.skills/`, `.vault/`, `tools/` — and a task that
hands work between them (a render in, a model out) keeps the destination rule and the
version rule in each.

Note the unit boundary when handing off: **Blender and Unity are metres, Unreal is
centimetres.** The ×100 scale is decided at export time.
