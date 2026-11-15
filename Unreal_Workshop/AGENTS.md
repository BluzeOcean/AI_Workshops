# AGENTS.md — Unreal_Workshop

**This file is the gateway to the workshop, and the rules for working inside it.** It says
where things are and how the workshop behaves. **It does not teach you Unreal.**

Everything else lives in a catalog and is fetched when a task points at it:

| If you need | Read |
|---|---|
| a procedure | `.skills/skill_catalog.md` → then the one skill that matches |
| a fact, a lesson, a decision | `.vault/vault_index.md` → then the one entry that matches |
| a script | `tools/README.md` → the tool's spec |
| how to write a skill | `.skills/README.md` |
| how to write memory, and the prune procedure | `.vault/README.md` |

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
   Select-String -Path .vault\lessons\*.md -Pattern 'port' -SimpleMatch
   ```
4. **Need a tool?** Run it. A tool is something to be **run, not read**. Read its source
   only when you are fixing it or writing the next one.
5. **Not sure something exists?** Check the catalog and the index. Both are kept current on
   purpose — an entry that is not listed is one nobody finds.

---

## 3. The rules of this workshop

### Text only

**This tree holds no Unreal media assets and no media files of any kind** — no `.uasset`,
no `.umap`, no pictures, no renders, no textures, no audio, no video, no cooked builds, no
archives, and no other large or binary file.

- **Never write one in** — not in a subfolder, not as a "temporary" one, not as an example.
- **There is no `.gitignore` here, on purpose. Do not add one.** If a file would need a
  `.gitignore` rule to stay out of the tree, it does not belong here, and the answer is not
  to add the rule.
- A recipe in `.vault/recipes/` is **text**: the command, the import settings, the
  sequence — not the asset it produced.
- Scratch scripts and intermediate JSON go in the **project's `Saved/` folder** (engine
  owned and disposable), or next to the skill they serve, in `.skills/<name>/scripts/`.
- A `.uasset` belongs next to the project it is for, inside `Content/`.

### Agent-agnostic

**Nothing in this tree is specific to one agent tool.** No `.claude/`, no `.cursor/`, no
editor config, no framework manifest, no agent-plugin directory.

Where an agent needs a pointer into this workshop — a junction into its own skills
directory, an MCP registration, a settings file — that pointer belongs **outside** this
tree, in the agent's own configuration, or beside the skill that needs it, as
`.skills/<name>/references/`. **The workshop carries the content; the agent carries the
wiring.**

### Naming

- Every skill folder is `ue-op-<verb-noun>`, and the frontmatter `name:` matches the
  folder exactly. The prefix says which application the skill belongs to and keeps Unreal
  skills from colliding with skills from other workshops.
- Vault files are `<kind>/YYYY-MM-DD-short-slug.md`.
- A skill that exists but is not in the catalog is a skill nobody will find. A vault
  entry with no index row is an entry nobody will find — and the next prune deletes it.

### Two copies of the skillset

The original set lives at `D:\UE\.ue-op-skillset\`, and the UE projects still junction
from there. **This copy is the canonical one.** When you change a skill here, change it
there too, or move the junction:

```powershell
New-Item -ItemType Junction -Path "D:\UE\<Project>\.claude\skills\<name>" `
  -Target "V:\04_Projects\Workshops\Unreal_Workshop\.skills\<name>"
```

---

## 4. Working in Unreal — those rules live in the vault

**This workshop does not hold the Unreal rules; the vault and the skills do.** They are
fetched when a task touches Unreal, and they are not repeated here.

| Before you | Read |
|---|---|
| write anything into a project | `.vault/decisions/2026-11-15-working-in-a-live-unreal-project.md` — confirm the destination, and the rules that stop an agent destroying the user's work |
| decide where an artifact goes | `.vault/decisions/2026-11-15-where-unreal-artifacts-belong.md` — Content vs Saved vs export |
| pick an engine version | `.vault/decisions/2026-11-15-the-unreal-version-is-resolved-not-pinned.md` — resolve it, never pin it |
| cross a tool boundary | `.vault/decisions/2026-11-15-the-unit-scale-is-decided-at-export-time.md` — the ×100 scale, decided at export |
| reach an editor over MCP | `.skills/ue-op-mcp-diagnose/SKILL.md` — which editor, which MCP server, which port |
| run Unreal with no GUI | `.skills/ue-op-run-headless/SKILL.md` — commandlets and editor Python |
| write Unreal Python | `.skills/ue-op-python-gotchas/SKILL.md` — the calls that fail silently |
| drive the live editor | `.skills/ue-op-editor-script/SKILL.md` — batch edits, scene reads, captures |

For anything not in that table, read the catalogs — the index row tells you which entry
holds it.

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
| an engine version, plugin or setting that works well | `.vault/model-notes/` |
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
- **You are about to repeat an expensive operation** (a cook, a big asset import, a
  render) and want to reuse a known-good setup.

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
installed engine, a port or a PID expires on its own; mark it `Status: stale` with the date
it stopped applying, rather than rewriting it.

---

## 6. Commit policy

**One commit per substantial change, committed and pushed at the end of a task.** A commit
should mean *something meaningful changed*, not *the agent saved a file*.

**Commit when something substantial lands:** a skill is added or materially revised · a
lesson is written · a decision is added or superseded · a recipe or workflow is added · a
tool is added or its behaviour changes · a rule in this file changes.

**Do not commit:** a typo, a reformat, a whitespace change · scratch files (they belong in
the project's `Saved/` folder) · a file that is still being edited · the same entry
rewritten three times while the agent is still figuring it out.

**Cadence: one task, one commit.** If a task produced three lessons, a new skill and a
recipe, that is **one** commit. If a task produced nothing substantial, do not commit at
all — an empty commit is noise.

```powershell
cd V:\04_Projects\Workshops
git status --short              # look before staging
git add Unreal_Workshop         # ONLY the folder you worked in
git commit -m "<type>(workshop): <what changed>"
git push origin master          # then push it
```

- **Stage only your own workshop.** Other workshops have untracked files of their own;
  `git add -A` would sweep them into your commit.
- **Push after every commit.** The remote is `origin`. If the push fails, report it —
  **never force-push**.
- Commit on the branch you are on (`master`). It is a personal working repo — do not
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
| the machine's engine installs, paths and capability matrix | `.vault/model-notes/2026-11-15-ue-installs-and-mcp-capability.md` |
| the MCP surfaces, ports and config keys | `.vault/model-notes/2026-11-15-unreal-mcp-surfaces-on-this-machine.md` |
| what the MCP tools can actually do in this build | `.vault/model-notes/2026-11-15-mcp-tool-surface-reality-in-this-build.md` |
| the workshop's own decisions | `.vault/decisions/` — indexed in `.vault/vault_index.md` |
| the sister workshops | `../Blender_Workshop/`, `../Unity_Workshop/`, `../ComfyUI_Workshop/` |

> **The path to Unreal is not a constant.** It moves when the engine is updated, and the
> launcher registry does not list every install. Resolve it — never assume it.
