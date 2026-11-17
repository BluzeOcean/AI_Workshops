# AGENTS.md — RigBy2D_Workshop

**This file is the gateway to the workshop, and the rules for working inside it.** It says
where things are and how the workshop behaves. **It does not teach you RigBy2D.**

| If you need | Read |
|---|---|
| a procedure | `.skills/skill_catalog.md` → then the one skill that matches |
| a fact, a lesson, a decision | `.vault/vault_index.md` → then the one entry that matches |
| a script | `tools/README.md` → the tool's spec |
| how to write a skill | `.skills/README.md` |
| how to write memory, and the prune procedure | `.vault/README.md` |
| **how to drive RigBy2D itself** | **§4 — open, and it is the first thing to fill in** |

**Do not read a folder end to end.** Every layer here is indexed for exactly that reason.

Read this file completely before touching anything. It is short, and it is the whole
onboarding.

---

## 1. The workshop in one table

| Path | Layer | Holds | Its catalog |
|---|---|---|---|
| `.skills/` | **procedures** | one folder per skill, each with a `SKILL.md` | `.skills/skill_catalog.md` |
| `.vault/` | **memory** | lessons, decisions, model notes, recipes, workflows | `.vault/vault_index.md` |
| `tools/` | **scripts** | repeatable mechanical actions | `tools/README.md` |

Everything in the tree is **text** — markdown, plain JSON, small scripts. The workshop
travels between machines in git, and a repository of text stays reviewable, diffable and
cheap to clone.

The two catalogs are the whole workshop. The folders are the territory.

### Its current state — empty on purpose

**This workshop was scaffolded on 2026-11-17 and holds no capabilities yet.** There are no
skills, no vault entries, no tools, and — importantly — **no verified facts about
RigBy2D**. §4 is the research contract that turns it into a working workshop.

That emptiness is the design, not a gap to paper over. A workshop that ships a plausible
but unverified description of an application teaches the next agent to trust a guess. An
empty workshop teaches it to go and find out.

---

## 2. How to look things up

**The workshop is lazy-loaded by design.** Only this file is loaded at session start;
everything else is fetched when a task needs it.

1. **Need a procedure?** Read `.skills/skill_catalog.md` — read the `When to use it`
   column and open the one skill that matches. Do not open the others.
2. **Need a fact or a memory?** Read `.vault/vault_index.md` — one row per entry, with its
   status and one line saying what it saves you. Open the one entry you need.
3. **Think something has gone wrong before?** Grep the vault; do not read it:
   ```powershell
   Select-String -Path .vault\lessons\*.md -Pattern 'rig' -SimpleMatch
   ```
4. **Need a tool?** Run it. A tool is something to be **run, not read**. Read its source
   only when you are fixing it or writing the next one.
5. **Not sure something exists?** Check the catalog and the index. Both are kept current on
   purpose — an entry that is not listed is one nobody finds.

---

## 3. The rules of this workshop

### Text only

**This tree holds no RigBy2D media files of any kind** — no spritesheets, no rigs, no
skeletons, no exported animations, no pictures, no renders, no audio, no video, no
archives, and no other large or binary file.

- **Never write one in** — not in a subfolder, not as a "temporary" one, not as an example.
- **There is no `.gitignore` here, on purpose. Do not add one.** If a file would need a
  `.gitignore` rule to stay out of the tree, it does not belong here, and the answer is not
  to add the rule.
- A recipe in `.vault/recipes/` is **text**: the command, the settings, the sequence — not
  the artwork it produced.
- Scratch scripts and intermediate JSON go **outside this tree** — in the folder the app
  itself uses for scratch, or next to the skill they serve, in `.skills/<name>/scripts/`.
- A produced asset belongs **next to the project it is for**, in the destination the user
  confirmed.

### Agent-agnostic

**Nothing in this tree is specific to one agent tool.** No `.claude/`, no `.cursor/`, no
editor config, no framework manifest, no agent-plugin directory.

Where an agent needs a pointer into this workshop — a junction into its own skills
directory, an MCP registration, a settings file — that pointer belongs **outside** this
tree, in the agent's own configuration, or beside the skill that needs it, as
`.skills/<name>/references/`. **The workshop carries the content; the agent carries the
wiring.**

### Naming

- Every skill folder is `rb2d-op-<verb-noun>`, and the frontmatter `name:` matches the
  folder exactly. The prefix says which application the skill belongs to and keeps
  RigBy2D skills from colliding with skills from other workshops in a shared skills
  directory.
- Vault files are `<kind>/YYYY-MM-DD-short-slug.md`.
- A skill that exists but is not in the catalog is a skill nobody will find. A vault
  entry with no index row is an entry nobody will find — and the next prune deletes it.

### The destination is confirmed, never assumed

**The destination is the folder RigBy2D output lands in. You must know it BEFORE you
produce anything.**

- If the user gave you a destination → use **exactly** that path. Character for character.
- If the user did **not** → **ASK.** Do not guess. Do not fall back to a default. Do not
  reuse the destination from an earlier task in this session.

The order is always: **confirm destination → work → save there.**

What that means concretely for RigBy2D — whether the app pins its output path at launch,
whether it writes anywhere at all, and whether it will overwrite what is already there —
is one of the open questions in §4. Until it is answered, ask.

---

## 4. RigBy2D — the part that is not written yet

**This section is the workshop's first task.** Everything in §1–§3 is the house shape that
every workshop in this repo follows and that does not depend on the application. §4 is
where the application enters, and it is **empty** — deliberately.

### The rule

> **Never write a fact about RigBy2D that was not verified by running it.** A protocol
> described from memory is a guess with a confident tone, and the next agent will trust it.

Verify by **running** the thing and recording what literally happened — the command, the
exit code, the literal response shape.

### The research contract

These are the questions that have to be answered, and where each answer belongs. Answer
them by probing the machine, not by reading documentation alone.

| # | Question | How to answer it | Where the answer goes |
|---|---|---|---|
| 1 | **Where is it installed? Which versions?** | Scan the usual roots (`C:\Program Files\…`, `D:\…`, the user's AppData, and any store/launcher install). Run `<exe> --version` on each candidate. **Two versions side by side is common** — note both, and note which is current. | `.vault/model-notes/` + §4 of this file |
| 2 | **What is the control surface?** | CLI? local HTTP API? a socket? a Python/JS SDK? a plugin/add-on? a headless mode? List the **real** entry points. | `.vault/model-notes/` |
| 3 | **Is anything running right now?** | Check processes and listening ports. A live instance holding the user's work is a fact that must be warned about. | `.vault/model-notes/` |
| 4 | **What does its API actually speak?** | **Probe it.** Send a harmless request and record the literal response shape. Do not describe a protocol from memory. | `.vault/model-notes/` |
| 5 | **Where does output go, and what is "the destination"?** | Some apps pin the output path at launch; others write anywhere. The destination rule is written differently depending on the answer. | `.vault/decisions/` |
| 6 | **What file types does it produce?** | These are the files that must never land in this tree. | `.vault/model-notes/` + §3, *Text only* |
| 7 | **What are the expensive traps?** | Context failures, silent defaults, version-changed APIs, ops that do nothing without a selection. **Verify one of them; do not invent it.** | `.vault/lessons/` |

**If the app has a companion MCP bridge or an official plugin, read its source.** That is
the fastest way to get the protocol exactly right, and it prevents documenting a protocol
that does not exist. **A protocol that looks like another one is a trap** — two surfaces of
the same app can look alike and behave differently. Record the literal probe output, and
say which is which.

### Filling it in

1. Research the seven questions above, on this machine, by running things.
2. Write the answers into `.vault/` — model notes for facts, decisions for choices,
   lessons for traps — and **add a row for each** in `.vault/vault_index.md`, in the same
   commit.
3. Replace this section with the result: the install and **the rule for resolving the
   version**, **how to talk to the app** (every surface, with the verified protocol), the
   rules that cost time, and a reference table.
4. If a task produced a repeatable procedure, forge it into `.skills/rb2d-op-<verb-noun>/`
   and add its row to `.skills/skill_catalog.md`.

**The version is resolved, never pinned.** That rule holds whatever the answers turn out
to be: a skill or tool that hardcodes a version or an install path must **update its own
path** when it finds a newer install, and say that it did so in its output. A skill that
silently keeps using an old version after a new one is installed is a bug, and it is the
kind of bug that produces "why does the API differ?" answers three weeks later.

### Until then

If a task arrives that needs RigBy2D and §4 is still empty, **research first, then do the
task.** Do not improvise an API from memory, and do not quietly build the whole thing on
an unverified guess — that is how a workshop starts lying to the next agent.

---

## 5. Maintain the workshop

### After every task

**Log the memory. This is not optional.** The vault is how this workspace gets better
instead of repeating itself. It is **written after a task, not read before one** — the
vault is a shortcut for a future agent, not a checklist to work through.

1. **Write it.** At least one entry per task that produced a durable fact. If genuinely
   nothing durable came out, say so in the task summary instead of writing a filler file.
2. **Index it.** Every new entry gets a row in `.vault/vault_index.md`, in the same
   commit. A vault file with no row does not exist — no agent will find it, and the next
   prune deletes it.
3. **Prune what you touched.** The vault grows on every task, and growth is not the goal —
   a memory bank that only ever grows becomes a landfill. After any task that added or
   changed an entry, run one prune pass over the index: an entry no future task would ever
   read is a diary entry and is deleted; an entry about machine state that has stopped being
   true is marked `stale`; two entries answering the same question are merged; a procedure
   that keeps being repeated moves to `.skills/`. The full procedure is in
   `.vault/README.md` → *Maintenance*.
4. **Commit it** — see §6.

### Where a lesson goes

| You learned | Put it in |
|---|---|
| a mistake that cost time, money or a wrong delivery | `.vault/lessons/` |
| a decision about how this workspace works | `.vault/decisions/` |
| a version, plugin or setting that works well | `.vault/model-notes/` |
| a script + settings that produced something good | `.vault/recipes/` |
| a known-good command sequence | `.vault/workflows/` |
| a repeatable procedure worth repeating | `.skills/<name>/SKILL.md` |
| a rule about how to behave here | **this file** |

**A success is not just a log entry — it is material to turn into a skill.** After a task
that went well, decompose the operation and write the modular piece worth repeating into
`.skills/`, with the optimized steps. The procedure is `.skills/README.md`.

**What does not belong in the vault** — diary entries, restatements of this file,
unverified guesses, anything with no operational consequence — is listed in
`.vault/README.md`.

### When to read the vault

- **Something went wrong** and you suspect it has happened before — search before guessing
  at a fix.
- **The user asks** what has worked before, what to avoid, or for a specific recipe.
- **You are about to repeat an expensive operation** and want to reuse a known-good setup.

**Read `.vault/vault_index.md` first — it is the map.** Then open the one entry you need.

### Revoking a decision

**A decision is not deleted when it stops being true. It is superseded**, and the
supersession is recorded in **four places, in one commit**:

1. the replacement file — `Status: active`, with `**Supersedes:** <the old file>`;
2. the old file — `Status: superseded` **and** `**Superseded by:** <the new file>`. The
   back-link hands an agent who opens the old file its replacement instead of a dead end;
3. the row in `.vault/vault_index.md` — the old row becomes `superseded → <new file>`, the
   new row becomes `active`;
4. **this file**, if it quoted the old decision. This file is loaded at every session
   start, so a stale quote here is stale guidance handed to every future agent.

Steps 3 and 4 are the ones that get forgotten.

**A fact that quietly stops being true is not a revoked decision.** A model-note about an
installed app, a port or a PID expires on its own; mark it `Status: stale` with the date
it stopped applying, rather than rewriting it.

---

## 6. Commit policy

**One commit per substantial change, committed and pushed at the end of a task.** A commit
should mean *something meaningful changed*, not *the agent saved a file*.

**Commit when something substantial lands:** a skill is added or materially revised · a
lesson is written · a decision is added or superseded · a recipe or workflow is added · a
tool is added or its behaviour changes · a rule in this file changes.

**Do not commit:** a typo, a reformat, a whitespace change · scratch files (they belong
outside this tree) · a file that is still being edited · the same entry rewritten three
times while the agent is still figuring it out.

**Cadence: one task, one commit.** If a task produced three lessons, a new skill and a
recipe, that is **one** commit. If a task produced nothing substantial, do not commit at
all — an empty commit is noise.

```powershell
cd V:\04_Projects\Workshops
git status --short              # look before staging
git add RigBy2D_Workshop        # ONLY the folder you worked in
git commit -m "<type>(workshop): <what changed>"
git push origin master          # then push it
```

- **Stage only your own workshop.** Other workshops usually have untracked files of their
  own; `git add -A` would sweep them into your commit.
- **Push after every commit.** The remote is `origin`. If the push fails, report it —
  **never force-push**.
- Commit on the branch you are on (`master`). This is a personal working repo — do not
  create side branches unless the user asks.
- **Never commit media.** It does not belong here in the first place — check
  `git status` after staging, and if something binary shows up, move it to the destination.

**Message:** `<type>(workshop): <what changed in one line>`, where the type is `feat`,
`docs`, `fix` or `chore`. Say *what* changed, not that something changed.

---

## 7. Reference

| What | Where |
|---|---|
| the skills | `.skills/skill_catalog.md` |
| the memory | `.vault/vault_index.md` |
| the tools | `tools/README.md` |
| how to write a skill | `.skills/README.md` |
| how to write memory, and the prune procedure | `.vault/README.md` |
| **how to drive RigBy2D** | **§4 — open; the research contract lives there** |
| the sister workshops | `../Blender_Workshop/`, `../Unreal_Workshop/`, `../Unity_Workshop/`, `../ComfyUI_Workshop/` |

> **The path to RigBy2D is not a constant.** It moves when the app is updated. Resolve it —
> never assume a path you were told about once is still correct.
