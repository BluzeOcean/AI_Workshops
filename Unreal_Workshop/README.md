# Unreal_Workshop

A workspace that gives any agent the ability to drive Unreal Engine.

**Tell the agent to read this file. That is the entire entry point.** From here the agent
reads `AGENTS.md`, picks up the tools and skills that exist, and does the work — with no
tutorial, no prior context, and no hand-holding.

It contains no media. It contains the **instructions**, the **skills**, the **tools**, and the
**memory**.

```
AGENTS.md        <- start here. the whole onboarding.
.skills/         <- procedures: one folder per skill, each with a SKILL.md
.vault/          <- the memory bank: lessons, decisions, notes, recipes, workflows
tools/           <- the scripts (spec only for now — see tools/README.md)
```

## Quick start for an agent

1. Read `AGENTS.md`. It covers the destination rule, the Unreal installs and how to resolve
   the version, the six ways to talk to Unreal, and the mistakes that cost the most time.
2. Confirm the **destination** for the task — which project, and which folder inside it. If
   the user has not said, ask. Unreal projects live under `D:\UE\<Project>\`.
3. Check what already exists: `.skills/README.md` lists the skills; `tools/README.md`
   describes the tool layer; `.vault/` holds what past tasks learned.
4. Talk to Unreal — see §4 of `AGENTS.md`:
   - the live editor process (find it with WMI, and read its command line for the project),
   - Epic's built-in MCP plugin on `127.0.0.1:8000/mcp` (UE 5.8+ only),
   - the Unreal Canvas bridge — a *different* MCP server that looks the same,
   - headless: `UnrealEditor-Cmd.exe -run=<Commandlet>` or `-ExecutePythonScript=`,
   - the external `ue-op-*` skillset in `D:\UE\.ue-op-skillset\`,
   - or the tools in `tools/`, once they do.
5. Build the script in `work/` (git-ignored) or the project's `Saved/` folder. Save into the
   destination.
6. **Log the memory** in `.vault/` when the task is done — and turn what worked into a
   skill. See `.vault/README.md` and §6 of `AGENTS.md`.

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

The index of what the workshop can currently do is `.skills/README.md`. It is kept current
as skills are forged, because an agent decides what to open by reading it.

## The three ideas

**The destination is confirmed, never assumed.** Unreal will create assets in any project
you point it at, so a guessed project means the work is in the wrong place and nothing tells
you. Ask — and never save over an asset the user has open.

**The Unreal version is resolved, not pinned.** 5.9.0, 5.8.4 and 5.5.4 are installed side
by side. The newest wins, and the launcher registry cannot be trusted — UE 5.9 is installed
and running but is *not* in the registry. Scan `Engine/Build/Build.version` instead.

**The vault is a memory bank.** Written after each task, searched when something breaks. It
is what stops the workspace from making the same mistake twice.

## State of the tool layer

`tools/` is a **specification, not an implementation**. The scripts it describes — a version
resolver, an MCP client, a headless runner — have not been written yet. Read `tools/README.md`
for what they have to do and what they must not do.

## About the MCP bridge

Unlike the Blender workshop, a working Unreal MCP bridge **already exists on this machine**:
UE 5.8+ ships Epic's own `ModelContextProtocol` plugin, and it is registered with Claude Code
at **user scope** — check it with:

```bash
claude mcp list          # shows the server, its URL and whether it is connected
```

Because it is user scope, every Claude Code session in every directory sees it and connects
automatically when an editor is up. **Do not add a project-scoped `.mcp.json`** — a duplicate
in this folder would show as "⏸ Pending approval" and break that.

`.mcp.json.example` is therefore the **reserved slot**: it holds the server definition, for
the case where the user-scope entry is missing or you need to point at a second editor on a
different port. Read §4b and §4c of `AGENTS.md` before touching it — there are **two**
Unreal MCP surfaces on this box and they are not interchangeable.

## Sister workshops

`../Blender_Workshop/` (DCC), `../Unity_Workshop/`, `../ComfyUI_Workshop/` (image generation).
They follow the same shape — `AGENTS.md`, `.skills/`, `.vault/`, `tools/` — and a task that
hands work between them (a render in, a model out) keeps the destination rule and the
version rule in each.

Note the unit boundary when handing off: **Blender and Unity are metres, Unreal is
centimetres.** The ×100 scale is decided at export time.
