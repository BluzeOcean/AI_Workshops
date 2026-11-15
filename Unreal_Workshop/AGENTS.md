# AGENTS.md — Unreal_Workshop

**This workspace drives Unreal Engine. Any agent can open this folder, read this file, and be
productive — no tutorial, no prior context, no hand-holding needed.**

Read this file completely before touching anything. It is the entire onboarding.

You do not need to know Unreal. You need to know **which Unreal is installed**, **how to
reach it**, **where the files go**, and **how not to destroy somebody's work**. Those four
things are below.

---

## 1. The map

| Path | What it is |
|---|---|
| `.skills/` | **Procedures.** One folder per skill, each with a `SKILL.md`, always named `ue-op-<verb-noun>`. 31 skills covering blueprint authoring, input, PIE, asset search and migration, capture, the web build pipeline, skeletal import and more. `.skills/skill_catalog.md` is the index — read it to find the one you need; `.skills/README.md` has the format and the naming rule. |
| `.vault/` | **The memory bank.** Unreal-specific facts worth carrying forward — lessons, decisions, model notes, recipes, workflows. It is **written after a task, not read before one** (see §6). Every entry must make a future agent **faster or safer**; generic house rules live in this file, not in the vault. The **map** of it is `.vault/vault_index.md` — read that when you want to fetch wisdom, never the folders. |
| `tools/` | The scripts. Currently a **specification, not an implementation** — see `tools/README.md`. Whoever builds them owns this layer. |

### The workshop is agent-agnostic

**Nothing in this tree is specific to one agent tool.** No `.claude/`, no `.cursor/`, no
editor config, no framework manifest, no agent-plugin directory. It is markdown, plain
JSON and small scripts — an agent reads `AGENTS.md`, opens the skills it needs, and works.

A skill is a folder with a `SKILL.md` (frontmatter + body). Any agent that can read a
markdown file can use one.

Where an agent needs a **pointer** into this workshop — a junction into its own skills
directory, an MCP registration, a settings file — that pointer belongs **outside** this
tree, in the agent's own configuration, or beside the skill that needs it (as
`.skills/<name>/references/`). The workshop carries the content; the agent carries the
wiring.

**`.vault/` is a memory bank, not a checklist.** You do not read it at the start of a task —
that would waste context on a log that is mostly irrelevant to what you are doing right now.
You *write* to it when a task ends, and you *search* it when something breaks or the user asks
whether it has happened before.

### This workshop holds text only

**This workshop holds skills, the vault (memory) and the tool layer. It holds no Unreal media
assets and no media files of any kind — no `.uasset`, no `.umap`, no pictures, no renders, no
textures, no audio, no video, no cooked builds, no archives, and no other large or binary
file.**

Everything in this tree is text an agent can read: markdown, JSON, and small scripts. That is
the point — the workshop travels between machines in git, and a repository of text is
reviewable, diffable and cheap to clone. A binary in the tree breaks all three.

Concretely:

- Never write a `.uasset`, a `.umap`, a `.png`/`.jpg`/`.exr` image, a `.fbx`/`.glb` import, a
  `.wav`, a `.pak`, a cooked `Saved/Cooked` tree or a `.zip` into this tree — **not in a
  subfolder, not as a "temporary" one, not as an example**.
- **There is no `.gitignore` here, on purpose.** Nothing needs excluding, because nothing
  that belongs here is media. Do not add one. If a file you are about to write would need a
  `.gitignore` rule to keep it out of the tree, that file does not belong here.
- A recipe in `.vault/recipes/` is **text**: the command, the import settings, the sequence.
  Not the asset it produced.
- Scratch scripts and intermediate JSON do not belong here either. They go in the
  **project's `Saved/` folder** (engine-owned and disposable, and where the UE skills already
  put their scripts), or next to the skill they serve, in `.skills/<name>/scripts/`.
- A `.uasset` is especially tempting to keep here because it is "the work". It is not. It is a
  binary package with absolute paths and a source-control revision; it belongs next to the
  project it is for, inside `Content/`.

---

## 2. The destination — read this twice

**The destination is the Unreal project the work belongs to. You must know WHICH project, and
WHICH folder inside it, BEFORE you produce anything.**

Unreal projects on this machine live under `D:\UE\<Project>\`, each with its own
`<Project>.uproject`, `Content/`, `Config/`, `Source/`, `Plugins/`.

- If the user named a project → use **exactly** that path. Character for character.
- If the user did **not** → **ASK.** Do not guess. Do not fall back to "the last project I
  saw". Do not pick the one that happens to have an editor running.

This is not politeness. Unreal will happily create assets in *any* project you point it at,
which means a guessed project produces work in the wrong place with no error to tell you.
And the user's project is often open in a running editor — writing over it destroys their work
silently.

The order is always: **confirm destination → work → save there.**

```
DESTINATION = D:\UE\<Project>\Content\<Folder>\     (or wherever the user said)
```

There are two hard rules on top of that, and they are the ones that actually cost data:

> **Never save over the asset the user has open.** Unreal's "save" writes the in-memory state
> back onto the same package. If the user has `BP_Hero` open and a script calls
> `unreal.EditorAssetLibrary.save_asset(asset, only_if_is_dirty=False)`, you have just
> overwritten their work. Save into the destination as a **new** path, or use an explicit
> save-as. Never call a plain "save" on an asset the user did not hand you.

> **Never write into `Content/` by hand.** Assets are created *through the editor* (or the
> asset tools), not by copying files into `Content/`. A `.uasset` copied in from outside
> loses its package metadata, its source-control state, and often its references. The
> destination inside a project is a **content folder**, but the *means* of getting an asset
> there is the editor.

### Two Unreal destinations that are not the same thing

| Destination | What it is | Where |
|---|---|---|
| **The project** | `<Project>.uproject` + `Content/` + `Config/` — the deliverable | `D:\UE\<Project>\` |
| **The scratch area** | `Saved/`, `Intermediate/`, `DerivedDataCache/` — engine-owned, disposable | inside the project |

Scripts, intermediate JSON, captured results and editor logs belong in the project's
`Saved/` folder, **not** in `Content/` and **not** in this workshop. `Saved/` is engine-owned:
the project ignores it and the engine prunes it freely. Never put a deliverable in `Saved/`.

---

## 3. The Unreal Engine installs on this machine

Three engine versions are installed:

| Version | Path | Note |
|---|---|---|
| **5.9.0** (CL 60351404) | `C:\Program Files\Epic Games\UE_5.9\` | **Current, and the one in use.** Not in the launcher registry — see the warning below. |
| 5.8.4 (CL 58902052) | `C:\Program Files\Epic Games\UE_5.8\` | Previous release. Registered with the launcher. Has the MCP plugin. |
| 5.5.4 (CL 40574608) | `C:\Program Files\Epic Games\UE_5.5\` | Oldest. **Has no MCP plugin** (see §4b). |

Each install's exact version is in `Engine/Build/Build.version`:

```powershell
Get-Content "C:\Program Files\Epic Games\UE_5.9\Engine\Build\Build.version"
```

### The version is RESOLVED, never pinned

**Always use the newest Unreal installed.** Do not hardcode `5.9` into a script, a skill, or
a tool. When UE 5.10 lands, the workspace must use 5.10 without a human editing paths.

Resolution rule, in order of authority:

1. **Inside a running editor** — `unreal.SystemLibrary.get_engine_version()` is the version
   in use, and the editor's own executable path is the truth. This is the authority.
2. **From the shell** — scan `C:\Program Files\Epic Games\UE_*/Engine/Build/Build.version`,
   parse `MajorVersion`/`MinorVersion`/`PatchVersion`, and take the highest. Compare on the
   **version tuple**, not the folder name: `5.9` > `5.8`, and a `5.9.1` beats a `5.9`.

### The registry is NOT the resolver — verified

`HKLM\SOFTWARE\EpicGames\Unreal Engine\` lists `5.2, 5.4, 5.5, 5.6, 5.7, 5.8` with their
`InstalledDirectory` values — but **5.9 is installed and running, and it is not in the
registry.** It is not on disk via the launcher, or its registry entry was removed. Either
way the registry is not a list of what is installed.

```powershell
reg query "HKLM\SOFTWARE\EpicGames\Unreal Engine" //s
```

A resolver that reads the registry will pick **5.8** on a machine whose current editor is
5.9 — and then produce a `.uasset` that the 5.9 editor refuses to load. **Scan the install
directory; use the registry only as a hint.**

A skill or tool that hardcodes a version must **update its own path** when it finds a newer
install, and say that it did so in its output. A skill that silently keeps using 5.8 after
5.10 is installed is a bug, and it is the kind of bug that produces "why does the API
differ?" answers three weeks later.

### Why the version matters at all

Unreal's API and content format are versioned, and the differences are not additive:

- **Asset format.** A `.uasset`/`.umap` saved by 5.9 does not open in 5.8, and cannot be
  cooked by 5.8. Content is forward-locked to the engine that wrote it.
- **Enhanced Input** replaced the legacy Axis/Action mappings. A project on the new system
  does not respond to a project on the old one.
- **Blueprint node ids change.** `ue-op-wire-graph` and friends fail on nodes that moved
  between releases; `ue-op-fix-compile-error` exists because a blueprint will not compile
  against the engine in front of it.
- **Python API renames.** `get_editor_property` field names are not stable across releases
  (see §5, rule 4).

**Check the engine version before you rely on an API detail.**

---

## 4. Talking to Unreal — six ways, and they are not equivalent

Unreal is a desktop application with a heavy editor process, so unlike the ComfyUI workshop
there is no single server that is "already up". There are six distinct surfaces. **They
look alike and behave differently** — that is the single most expensive confusion on this
machine, so §4b and §4c are worth reading carefully.

### 4a. The live editor process

As of 2026-11-15, one editor is running:

| | |
|---|---|
| Process | `UnrealEditor.exe`, PID **38212** |
| Engine | UE **5.9.0** (`C:\Program Files\Epic Games\UE_5.9\Engine\`) |
| Project | `D:\UE\EpicJam2026\EpicJam2026.uproject` |

Check for yourself — never trust a stale PID:

```powershell
Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" |
  Select-Object ProcessId, CommandLine
```

**The command line is the truth about which project is open.** Two editors can run at once,
each with its own project, and a tool that talks to "the editor" without reading the command
line will write into whichever one it reached.

**The running instance holds the user's actual work.** Treat every write to it as a write to
their work. It is also a **shared resource**: as of this writing another agent is actively
using it. Assume the scene may change under you — read what you need immediately before you
act, and re-read after anything slow.

### 4b. MCP — Epic's built-in ModelContextProtocol plugin

> **The procedure is the skill `.skills/ue-op-mcp-diagnose/SKILL.md`** — resolving the
> engine, finding the editor, proving which server answered, registering a client. The raw
> facts (the handshake payload, the `_meta` shape, the ini keys, the console commands) are
> in `.vault/model-notes/2026-11-15-unreal-mcp-surfaces-on-this-machine.md`. Neither is
> loaded unless you actually need it.

UE **5.8 and newer** ship Epic's own MCP server as an engine plugin
(`Engine/Plugins/Experimental/ModelContextProtocol/`). **It does not exist in 5.5** — a 5.5
project has no MCP surface at all; use §4d.

It serves MCP over **HTTP (JSON-RPC 2.0)** at `http://127.0.0.1:8000/mcp` — no stdio bridge,
nothing to install. Bound to `127.0.0.1` only.

Four things about it bite, and all four are handled by the skill:

- The `Accept` header must carry **both** `application/json` and `text/event-stream`; the
  `Mcp-Session-Id` from `initialize` is **required** on every later call; and
  `notifications/initialized` must precede `tools/list`.
- **Every editor defaults to port 8000.** A second editor cannot bind it; its `StartServer`
  hits `ensure(HttpRouter.IsValid())` and serves nothing while your client stays happily
  connected to the **first** editor — healthy, answering promptly, about entirely different
  content. Give each editor its own port:
  `-ModelContextProtocolPort=8010 -ModelContextProtocolStartServer`.
- The `initialize` reply's `_meta` block says **which editor and which project answered.**
  Read it before you act on anything, and compare it against the `.uproject` in the running
  editor's command line (§4a).
- **`editor_toolset` is not registered in this build.** `editor_toolset.*` fails with
  `Toolset 'editor_toolset.BlueprintTools' not found`, and retrying does not help. The
  editor's own Python through the console-command bridge covers everything except Blueprint
  **graph** authoring — which has no fallback here, so **say so** rather than silently
  skipping the graph.

Auto-start is configured per project, per user, in
`<project>\Saved\Config\WindowsEditor\EditorPerProjectUserSettings.ini` (not
`Default*.ini`). It is **skipped in commandlets** — a cook or a build would race the editor
for the port; pass `-ModelContextProtocolStartServer` to force it on (§5 rule 11).

### 4c. MCP — the Unreal Canvas bridge (a *different* server)

**Not the same thing as §4b, and confusing the two is expensive.** Epic's plugin runs inside
the editor; the Canvas bridge is a separate `unrealcanvas-server.exe` the editor spawns.
Both speak MCP, and on this machine both were live at once.

| | Epic's plugin (§4b) | Canvas / "merlin" |
|---|---|---|
| Process | `UnrealEditor.exe` | `unrealcanvas-server.exe` |
| `serverInfo.name` | `unreal-mcp` | `merlin` |
| Tool style | toolsets behind `list_toolsets` / `call_tool` | flat, task-shaped tools |

Canvas-shaped tools — `TriggerMRGRender`, `SpawnMeshAt`, `RunMeshOps`, `SetSkybox`,
`SpawnGsplatFromPLY`, `ListCutouts`, `StartViewportStream`, the annotation tools — belong to
**this** surface. If a canvas tool reports that no frontend is connected, or a render never
starts, that is the bridge — not the editor, and not §4b. Its `/mcp` reply carries a
`frontendBuild` note saying whether a frontend is attached; read it before calling.

`--mcp-port 8000` is a **request, not a reservation** — the canvas server landed on
58784/58785 because the editor already held 8000. Always confirm with `netstat`.

**Which one is the client pointed at?** The client is registered at **user scope**, so it is
visible from every directory: `claude mcp list`. The endpoint it points at is the editor's
own route, `http://127.0.0.1:8000/mcp`. The definition to register is in
`.skills/ue-op-mcp-diagnose/references/client-config.json`.

**Verify the port before you trust a tool** — §5 rule 10; the port-owner check is step 3 of
the skill.

An MCP client loads servers **at session start**: a server registered after the session began
is not in the toolkit until `/mcp` reconnects it or Claude Code restarts.

### 4d. Headless — commandlets and the editor's Python

The escape hatch that always works, needs no running GUI and no MCP:

```powershell
& "C:\Program Files\Epic Games\UE_5.9\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "D:\UE\<Project>\<Project>.uproject" -run=<Commandlet> -unattended -nosplash
```

Common commandlets (names verified against
`Engine/Source/Editor/UnrealEd/Classes/Commandlets/` in 5.9):

| Commandlet | What it does |
|---|---|
| `-run=ResavePackages` | resave assets, optionally with `-PackageFilter=` |
| `-run=Cook` | cook content for a target platform |
| `-run=DerivedDataCache -fill` | pre-fill the DDC |
| `-run=DumpAssetRegistry` | dump the asset registry |

**Automation tests are not a `-run=` commandlet in 5.9** — there is no `AutomationCommandlet`
and no `RunUnreal` AutomationTool script. Run them from the editor console instead:

```
Automation RunTests <TestName>
```

or headless:

```powershell
UnrealEditor-Cmd.exe "D:\UE\<Project>\<Project>.uproject" `
  -ExecCmds="Automation RunTests <TestName>;Quit" -unattended -nosplash -NullRHI
```

**Python inside the editor** needs the `PythonScriptPlugin` (present in 5.9 at
`Engine/Plugins/Experimental/PythonScriptPlugin`):

```powershell
UnrealEditor-Cmd.exe "D:\UE\<Project>\<Project>.uproject" `
  -ExecutePythonScript="D:\UE\<Project>\Saved\script.py" -unattended
```

- Unreal's Python is **3.11.8**, at
  `Engine/Binaries/ThirdParty/Python3/Win64\python.exe`. `import unreal` is available
  **only** inside the editor or a commandlet — a bare system Python cannot import it.
- The script's working directory is the launch directory, not the script's folder.
  **Use absolute paths inside scripts.**
- Nothing persists between runs except what you save.

### 4e. The `ue-op-*` skills — vendored into this workshop

`.skills/` holds **31 skills**: the 30 that were forged on this machine at
`D:\UE\.ue-op-skillset\` (29 `ue-op-*` plus `ue-op-mcp-connect`), now vendored in, plus
`ue-op-mcp-diagnose` (§4b).

```
Unreal_Workshop\.skills\<skill-name>\SKILL.md
```

They cover blueprint authoring and repair, components, input, game modes, PIE, asset
search and dependency walks, asset migration, capture, offscreen verification, the editor's
Python, the web build pipeline, skeletal import, the Tripo/AI-character pipeline, and
skill extraction. **`.skills/skill_catalog.md` is the index — read the `When to use it`
column and open the one that matches.** Do not read them all.

**Helper scripts live next to the skill that owns them**, and the paths inside the skills
point at this copy — `ue-op-mcp-connect/mcp_call.py`, `ue-op-bake-mesh-partition/scripts/`,
`ue-op-build-web/scripts/`, and so on.

**Two copies exist.** The original at `D:\UE\.ue-op-skillset\` is still the one wired
into the UE projects — `D:\UE\EpicJam2026\.claude\skills\` junctions point there. When
you change a skill **here**, change it there too, or move the junction:

```powershell
New-Item -ItemType Junction -Path "D:\UE\<Project>\.claude\skills\<name>" `
  -Target "V:\04_Projects\Workshops\Unreal_Workshop\.skills\<name>"
```

**New skills are forged here**, into `.skills/<name>/SKILL.md`. `ue-op-extract-to-skill`
does exactly that, and its duplicate scan covers both this folder and the original set.

### 4f. The tools in `tools/`

Written by whoever owns the tool layer. See `tools/README.md` for the spec. When they exist,
they will wrap 4a–4d — they do not replace them.

---

## 5. Rules that will save you the time

These are not style preferences. Each one cost somebody real time to learn.

1. **Never kill an editor the user started.** Check the PID *and* the command line first
   (§4a). Restarting the editor is the user's call. If an instance is wedged, ask.

2. **Never write into a live level or session by accident.** No "reset the level", no
   "clear the world", no "new blank map" — not even "to start clean". Start from what is
   there, or work in a headless commandlet against a project you were given.

3. **Unreal Python discards struct writes taken from a getter.** This one fails *silently* —
   no exception, no log line, and the change is simply gone:

   ```python
   mats = mesh.get_editor_property("materials")
   mats[i].set_editor_property("material_interface", mi)   # lost
   mesh.set_editor_property("materials", mats)             # still lost
   ```

   Build fresh structs and assign the whole array:

   ```python
   new = []
   for sm in mats:
       n = unreal.SkeletalMaterial()
       n.set_editor_property("material_slot_name", sm.get_editor_property("material_slot_name"))
       n.set_editor_property("material_interface", mi)
       new.append(n)
   mesh.set_editor_property("materials", new)
   ```

   The same pattern applies to any struct array — `SingleAnimationPlayData`,
   `PostProcessSettings`, retarget chain settings. **When an Unreal Python snippet appears
   to do nothing, suspect this before rewriting the logic.**

4. **Some Unreal Python fields are renamed, and the old names are silently ignored.**
   For `SingleAnimationPlayData` the correct names are `anim_to_play`, `saved_looping`,
   `saved_playing`, `saved_position`, `saved_play_rate`. These are silently ignored:
   `loop_animation`, `playing`, `play_rate`.

5. **A skeletal mesh component *is* the actor's root component.** Setting
   `relative_location` on it moves the whole actor. Use `set_actor_location` on the actor.

6. **Live Coding cannot add a class.** It patches existing code; it cannot add a new
   `UCLASS`, a new file, or a new reflected `UPROPERTY`. Those need the header tool and a
   full build:

   ```powershell
   & "C:\Program Files\Epic Games\UE_5.9\Engine\Build\BatchFiles\Build.bat" `
     <Target> Win64 Development -Project="D:\UE\<Project>\<Project>.uproject"
   ```

   With the editor left open, UBT writes `UnrealEditor-<Module>-0002.dll`, which the editor
   never loads — so the change appears to vanish. Live Coding also leaves `*.patch_N.exe`
   artefacts behind; delete them.

7. **Unreal works in centimetres; Blender and Unity do not.** Unreal's default unit is
   **1 uu = 1 cm**. Blender is metres, Unity is metres. The Blender→Unreal handoff is
   therefore a **×100 scale**, decided at export time, not left to the importer. Getting
   this wrong produces a character one hundredth of its intended size (or a giant) with no
   error.

8. **The engine version is resolved by scanning the install directory, never by reading the
   registry** (§3). The registry does not list 5.9, and it will silently hand you 5.8.

9. **Not every engine version has the MCP plugin.** It exists in 5.8 and 5.9 and is
   **absent from 5.5**. A 5.5 project gets no MCP surface — use commandlets (§4d).

10. **Every editor defaults to MCP port 8000.** A second editor cannot bind it, and the
    client silently stays connected to the first one — a healthy-looking session pointed at
    the wrong project. Give each editor its own port, and **check the `_meta` block** (§4b)
    to confirm which project answered.

11. **MCP auto-start is skipped in commandlets.** A cook or build racing the editor for
    port 8000 is the usual symptom. Pass `-ModelContextProtocolStartServer` to force it on,
    or run the cook with the editor closed.

12. **The MCP tool list freezes when your session starts.** If the bridge is not running
    when the session opens, its tools never appear for that session, and restarting the
    server will not fix it. Fall back to 4d or 4e.

13. **The running editor is a shared resource.** Two agents (or an agent and a human) can
    hit the same editor. Assume the level may change under you: read what you need
    immediately before you act, and re-read after anything slow. **Never restart it to
    "get a clean slate."**

14. **A deleted asset in the editor is not a deleted file.** Deleting a referenced asset
    leaves a **redirector** behind, and the file may survive in source control. Cleaning up
    properly is a separate operation. Check `git status` in the project before assuming
    anything was removed.

15. **Autosaves are not the destination.** `Saved/Autosaves` and `Saved/Backup` hold
    recovery copies of the user's level. They are disposable and the engine prunes them.
    Never treat them as a deliverable, and never restore one over the user's work without
    asking.

16. **Check the engine version before you trust an API detail.** Unreal's Python API is
    versioned and the community answers are heavily mixed across releases — a snippet from
    5.3 may name a field that 5.9 renamed, and §5 rule 4 shows what that looks like.

17. **A tool that is listed but does nothing may not be broken.** Check which MCP surface
    it belongs to (§4b vs §4c) and whether that surface is even connected — the canvas
    server reports this itself in its `frontendBuild` note. And in this build
    `editor_toolset.*` is **absent**, so Blueprint graph tools fail with
    `Toolset 'editor_toolset.BlueprintTools' not found` while everything else works
    (§4b).

---

## 6. Write back — always log the memory after a task

**When a task is complete, log the memory. This is not optional.** The vault is how this
workspace gets better instead of repeating itself.

The vault is a **memory bank**: a running record of what worked and what did not, so a future
agent can trace the history and solve a problem that has already been solved. It is
**appended to after each task**, not consulted at the start of each task.

| You learned | Put it in |
|---|---|
| A mistake that cost time, money or a wrong delivery | `.vault/lessons/YYYY-MM-DD-slug.md` |
| A decision about how this workspace works | `.vault/decisions/YYYY-MM-DD-slug.md` |
| An engine version, plugin or setting that works well | `.vault/model-notes/` |
| A script + settings that produced something good | `.vault/recipes/` |
| A known-good command sequence | `.vault/workflows/` |
| A repeatable procedure worth repeating | `.skills/<name>/SKILL.md` |
| A rule about how to behave here | **this file** |

### The growth loop — how this workshop accumulates capability

**This workspace is not finished when it is created. It gets its tools, its skills and its
memory from being used.** Nothing here is complete on day one, and that is by design.

After every task, ask two questions:

**1. What went wrong?** → a **lesson**. A mistake that cost time, money or a wrong delivery
becomes `.vault/lessons/YYYY-MM-DD-slug.md`: the symptom as observed, the cause, the fix as
an instruction, and the trigger that makes it relevant again. This is the mechanism that
stops the workshop from making the same mistake twice.

**2. What worked?** → decompose it. A success is not just a log entry — it is **material to
turn into a skill**. Break the operation into its modular pieces and ask which one is worth
writing down as a procedure with optimized steps: the part that was fiddly, the part that
will come up again, the part that took three attempts to get right. That piece becomes
`.skills/<name>/SKILL.md` — with the *improved* sequence, not the sequence you happened to
perform. A skill written from a success records the fastest correct path, so the next
agent starts there instead of rediscovering the slow one.

The distinction that matters:

- A **skill** is a procedure — how to do the thing, in the order that works.
- A **lesson** is memory — what went wrong, so it is not repeated.
- A **recipe** is a known-good instance — the exact settings that produced a good result.
- A **workflow** is a known-good command sequence — the order of the commands.
- A **tool** is a script — something that can be run rather than read.

All five grow by use. The workshop has **two indexes**, and both must be kept current,
because an agent decides what to open by reading them: `.skills/skill_catalog.md` for the
procedures, and `.vault/vault_index.md` for the memory. A skill or an entry that exists but
is not in its index is one nobody will find.

**Every skill folder is named `ue-op-<verb-noun>`, and the frontmatter `name:` matches the
folder exactly.** The prefix says which application the skill belongs to and keeps Unreal
skills from colliding with skills from other workshops. A skill without it is a
convention break.

**A new skill is forged from a task that actually happened in this app, for this
workspace.** The `ue-op-*` set (§4e) was vendored in as a body of proven work — that is a
deliberate exception, not a licence to import anything. A skill you add yourself is
written from your own run, with the optimized steps. Do not import from a sibling
workshop, and do not clone a skill you have not verified.

If a task needs a tool that does not exist yet, that is a finding too: add it to the
specification in `tools/README.md` rather than working around it silently.

### What does NOT belong in the vault

**The vault is a shortcut for a future agent working on Unreal. It is not a record of what
you did today.**

An entry earns its place only if it passes this test:

> **Would a future agent, facing the same situation, act faster or avoid a failure because
> this file exists?** If the entry would not change what they do, it does not go in the vault.

Concretely, do **not** write:

- **Anything that would be true of any application.** "The destination is confirmed, never
  assumed", "the vault is a memory bank", "the tool layer is a spec not an implementation" —
  those are house rules, they belong in **this file, once**, and a vault copy of them is
  duplication that costs a future agent a read and teaches them nothing about Unreal.
- **A narrative of the session.** "Today I did X, then Y, then fixed Z." One file, one
  fact. No diaries, no status reports, no "what I did today" entries.
- **A restatement of something already in `AGENTS.md`.** If this file says it, the vault
  does not need to — link to the section instead.
- **Unverified guesses.** A lesson that was never observed is a guess with a confident tone.
  If you did not see it happen, it is not a lesson.
- **Anything with no operational consequence.** If it changes no command, no path, no
  setting and no decision, it is chatter.

The vault stays **Unreal-specific**. A generic software-engineering insight belongs in a
general skills library, not in this workshop — and if it would apply to Blender and Unity
too, it is a house rule, not a lesson from working on Unreal.

### When to write

**After every completed task.** Even a task that went fine — especially one that went fine.
"What worked" is as valuable to record as "what did not": the next agent needs to know that
*this* approach with *that* engine version and *those* settings produced a good result.

Write at least one entry per task that produced a durable fact. If genuinely nothing durable
came out of a task, say so in the task summary instead of writing a filler file.

**Every new entry gets a row in `.vault/vault_index.md`, in the same commit.** A vault file
with no row does not exist — no agent will find it, and the next prune deletes it.

**Then prune what you touched.** The vault grows on every task, and growth is not the goal —
a memory bank that only ever grows becomes a landfill. After any task that added or changed
an entry, run one prune pass over `.vault/vault_index.md`: an entry no future task would
ever read is a diary entry and gets deleted; an entry about machine state (an installed
engine, a port, a PID, a plugin inventory) that has stopped being true gets marked
`Status: stale`; two entries answering the same question get merged; a procedure that keeps
being repeated moves to `.skills/`. The full procedure is in `.vault/README.md` →
*Maintenance*. The trigger lives here; the procedure is fetched only when it runs.

**Then commit it** — see §7. One task, one commit, and only when something substantial
landed.

### When to read

**Only when it will pay for itself:**

- **Something went wrong** and you suspect it has happened before — search the vault before
  guessing at a fix.
- **The user asks** what has worked before, what to avoid, or for a specific recipe.
- **You are about to repeat an expensive operation** (a cook, a big asset import, a render)
  and want to reuse a known-good setup.

**Read `.vault/vault_index.md` first — it is the map.** It lists every entry with its status,
one row each, and a row says enough to decide whether to open the file behind it. Then open
the one entry you need.

Search it with `grep`, not by reading it end to end:

```powershell
Select-String -Path .vault\lessons\*.md -Pattern 'port' -SimpleMatch
```

### Never overwrite a lesson

Add a new one and link it. A later agent has to be able to see what was true *then*, and
why it stopped being true. A **lesson** is never edited in place; a **decision** is revoked
by supersession — see below.

Format for a lesson:

```markdown
# <one-line title>

**Status:** active

**Date:** YYYY-MM-DD
**Symptom:** what was observed, literally.
**Cause:** why it happened.
**Fix:** what to do instead — an instruction, not a story.
**Applies when:** the trigger that means this is relevant again.
```

Format for a "what worked" entry — same shape, different headings:

```markdown
# <one-line title>

**Status:** active

**Date:** YYYY-MM-DD
**What was run:** the exact command / script / settings.
**Result:** what came out, and where it landed.
**Reuse when:** the situation where this is the right starting point.
```

### Revoking a decision — the four-step write-back

**A decision is not deleted when it stops being true. It is superseded**, and the
supersession is recorded in **four places, in one commit**. A decision that is revoked in
the vault but still quoted in `AGENTS.md` has not actually been revoked — `AGENTS.md` is
loaded at every session start, so a stale quote there is stale guidance handed to every
future agent.

1. **Write the replacement.** A new decision file, `Status: active`, with
   `**Supersedes:** <the old file>`. Never edit the old one's content.
2. **Mark the old one.** `Status: superseded` **and** `**Superseded by:** <the new file>`.
   The back-link is what hands an agent who opens the old file the replacement instead of a
   dead end. `Supersedes` points forward, `Superseded by` points back — both, always.
3. **Update the index row.** `.vault/vault_index.md`: the old row becomes
   `superseded → <new file>`, the new row becomes `active`. A row still reading `active` on
   a revoked decision is worse than no index at all — the index is what an agent trusts.
4. **Fix `AGENTS.md` in the same commit** if the old decision was quoted there.

Steps 3 and 4 are the ones that get forgotten. Do them in the same commit as steps 1 and 2,
not later.

**A fact that quietly stops being true is different from a decision being revoked.** A
model-note about an installed engine, a port, a PID or a plugin inventory expires on its
own; mark it `Status: stale` with the date it stopped applying and why, rather than
rewriting it. See `.vault/README.md` → *Maintenance*.

---

## 7. Commit policy

**One commit per substantial change, committed and pushed at the end of a task.** This repository is a
working record, not a commit stream — a commit should mean *something meaningful changed*,
not *the agent saved a file*.

**Commit when something substantial lands:**

- a new skill is added, or an existing skill is materially revised
- a lesson is written — something cost time, money, or a wrong delivery
- a decision is added, or an existing one is superseded
- a recipe or a workflow is added
- a tool is added, or a tool's behaviour changes
- a rule in this file changes

**Do not commit:**

- a typo, a reformat, a whitespace change
- scratch files (they belong in the project's `Saved/` folder, not in this tree)
- a file that is still being edited in this task
- the same entry rewritten three times while the agent is still figuring it out

**Cadence: one task, one commit.** If a task produced three lessons, a new skill and a
recipe, that is **one** commit, not five. If a task produced nothing substantial, do not
commit at all — an empty commit is noise.

**How:**

```powershell
cd V:\04_Projects\Workshops
git status --short              # look before staging
git add Unreal_Workshop         # ONLY the folder you worked in
git commit -m "<type>(workshop): <what changed>"
git push origin master          # then push it
```

- **Stage only your own workshop.** Other workshops usually have untracked files of their
  own; `git add -A` would sweep them into your commit.
- **Push after every commit.** The remote is `origin`
  (`https://github.com/BluzeOcean/AI_Workshops.git`) and `master` tracks `origin/master`.
  A commit that stays local is work the next machine does not have. If the push fails,
  report it — **never force-push**.
- Commit on the branch you are on (`master`). This is a personal working repo — do not
  create side branches unless the user asks.
- Never commit media. It does not belong in this workshop in the first place — check
  `git status` after staging, and if something binary shows up, move it to the destination.

**Message:** `<type>(workshop): <what changed in one line>`, where the type is `feat`,
`docs`, `fix` or `chore`. Say *what* changed, not that something changed.

---

## 8. Reference

| What | Where |
|---|---|
| UE 5.9.0 (current) | `C:\Program Files\Epic Games\UE_5.9\` |
| UE 5.8.4 | `C:\Program Files\Epic Games\UE_5.8\` |
| UE 5.5.4 (no MCP plugin) | `C:\Program Files\Epic Games\UE_5.5\` |
| Engine install root | `C:\Program Files\Epic Games\` |
| Engine version file | `<engine>\Engine\Build\Build.version` |
| Launcher registry (incomplete — no 5.9) | `HKLM\SOFTWARE\EpicGames\Unreal Engine\` |
| Editor executable | `<engine>\Engine\Binaries\Win64\UnrealEditor.exe` |
| Commandlet executable | `<engine>\Engine\Binaries\Win64\UnrealEditor-Cmd.exe` |
| Build / UAT | `<engine>\Engine\Build\BatchFiles\Build.bat`, `RunUAT.bat` |
| Unreal's Python 3.11.8 | `<engine>\Engine\Binaries\ThirdParty\Python3\Win64\python.exe` (no `unreal` module outside the editor) |
| Epic MCP plugin (5.8+) | `<engine>\Engine\Plugins\Experimental\ModelContextProtocol\` |
| Epic MCP endpoint | `http://127.0.0.1:8000/mcp` — HTTP JSON-RPC, session-id required |
| Editor Python plugin | `<engine>\Engine\Plugins\Experimental\PythonScriptPlugin\` |
| Unreal Canvas / merlin build | `C:\Users\Bluze\AppData\Local\UnrealCanvas\Builds\v0.21.0\` |
| Unreal Canvas version | `…\v0.21.0\merlin-version.txt` |
| `ue-op-*` skills (31 in `.skills/`) | `Unreal_Workshop\.skills\<name>\SKILL.md` — index in `.skills/skill_catalog.md` |
| Original skillset (still wired into UE projects) | `D:\UE\.ue-op-skillset\<name>\SKILL.md` |
| Unreal projects | `D:\UE\<Project>\<Project>.uproject` |
| Engine templates | `<engine>\Templates\` (`TP_ThirdPerson\`, `TP_FirstPerson\`, `TP_Blank\`, …) |
| Claude Code MCP entry | user scope — check with `claude mcp list` |
| Dependency-free MCP client | `.skills/ue-op-mcp-connect/mcp_call.py` |
| Sister workshops | `../Blender_Workshop/`, `../Unity_Workshop/`, `../ComfyUI_Workshop/` |
| The tool spec | `tools/README.md` |
| Memory bank | `.vault/README.md` |
| **The vault index — every entry, with its status** | **`.vault/vault_index.md`** |

### The vault index

Every entry in `.vault/` is listed in **`.vault/vault_index.md`** — one row each, with its
status (`active` / `superseded` / `stale`) and one line saying what it saves you. That file
is the **map**; the folders are the territory. Read the index when you want to fetch wisdom,
never the folders end to end.

This file deliberately does **not** duplicate the index. A table copied here goes stale the
moment a decision is revoked, and `AGENTS.md` is loaded at every session start — a stale
copy is stale guidance handed to every future agent. §8 stays a reference to *places*; the
index stays the reference to *entries*. The rule that keeps them in step is §6,
*Revoking a decision*.

> **The path to Unreal is not a constant.** It moves when the engine is updated, and the
> launcher registry does not list every install. Resolve it (§3) instead of assuming the
> paths above are still correct.
