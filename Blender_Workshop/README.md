# Blender_Workshop

A workspace that gives any agent the ability to drive Blender.

**Tell the agent to read this file. That is the entire entry point.** From here the agent
reads `AGENTS.md`, picks up the tools and skills that exist, and does the work — with no
tutorial, no prior context, and no hand-holding.

It contains no media. It contains the **instructions**, the **skills**, the **tools**, and
the **memory**.

```
AGENTS.md        <- start here. the whole onboarding.
.skills/         <- procedures: one folder per skill, each with a SKILL.md
.vault/          <- the memory bank: lessons, decisions, notes, recipes, workflows
tools/           <- the scripts (spec only for now — see tools/README.md)
```

## Quick start for an agent

1. Read `AGENTS.md`. It covers the destination rule, the Blender install and how to resolve
   it, the three ways to talk to Blender, and the mistakes that cost the most time.
2. Confirm the **destination** for the task. If the user has not said, ask.
3. Check what already exists: `.skills/README.md` lists the skills; `tools/README.md`
   describes the tool layer; `.vault/` holds what past tasks learned.
4. Talk to Blender — see §4 of `AGENTS.md`:
   - the live instance on `127.0.0.1:9876` (DSH bridge, JSON command socket),
   - headless: `blender.exe --background --factory-startup --python <script.py>`,
   - the official Blender MCP extension (once the bridge exists),
   - or the tools in `tools/`, once they do.
5. Build the script in `work/` (git-ignored). Save and render into the destination.
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

**The destination is confirmed, never assumed.** Blender will write anywhere you point it,
so a guessed path means the work is in the wrong place and nothing tells you. Ask.

**The Blender version is resolved, not pinned.** 5.3.0 and 5.2.1 LTS are installed side by
side. The newest wins, and a tool that hardcodes a version updates its own path when it
finds a newer install. Inside Blender, `bpy.app.binary_path` is the authority.

**The vault is a memory bank.** Written after each task, searched when something breaks. It
is what stops the workspace from making the same mistake twice.

## State of the tool layer

`tools/` is a **specification, not an implementation**. The scripts it describes — a version
resolver, a bridge client, a headless runner — have not been written yet; the DSH side owns
that layer. Read `tools/README.md` for what they have to do and what they must not do.

`.mcp.json.example` is the reserved slot for an MCP bridge. The official Blender MCP
extension is installed and can serve real MCP on a free port (9876 is taken by the DSH
bridge, which speaks its own JSON protocol), but the bridge that exposes it to an MCP
client does not exist yet.

## Sister workshops

`../ComfyUI_Workshop/` (image generation), `../Unreal_Workshop/`, `../Unity_Workshop/`.
They follow the same shape — `AGENTS.md`, `.skills/`, `.vault/`, `tools/` — and a task that
hands work between them (a render in, a model out) keeps the destination rule and the
version rule in each.
