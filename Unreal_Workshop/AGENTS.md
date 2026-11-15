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
| `.skills/` | **Procedures.** One folder per skill, each with a `SKILL.md`. A skill is a repeatable task — "import a skeletal mesh and bind a skeleton", "render a level sequence to PNG", "cook a web build", "reach the editor over MCP". Read `.skills/README.md` before writing one. |
| `.vault/` | **The memory bank.** Unreal-specific facts worth carrying forward — lessons, decisions, model notes, recipes, workflows. It is **written after a task, not read before one** (see §6). Every entry must make a future agent **faster or safer**; generic house rules live in this file, not in the vault. The entries that will save you the most time are listed in §8. |
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

> **The procedure for this is the skill `.skills/ue-mcp-bridge/SKILL.md`** — it covers
> resolving the engine, finding the editor, proving which server answered, and registering
> a client. This section is the reference behind it.

UE **5.8 and newer** ship Epic's own MCP server as an engine plugin:

```
C:\Program Files\Epic Games\UE_5.9\Engine\Plugins\Experimental\ModelContextProtocol\
```

`ModelContextProtocol.uplugin` — FriendlyName "Unreal MCP", CreatedBy "Epic Games, Inc.",
**It does not exist in 5.5.** Verified: `UE_5.5\Engine\Plugins\Experimental\` has no
`ModelContextProtocol` entry. Do not point a 5.5 project at this surface.

It serves the Model Context Protocol over **HTTP (JSON-RPC 2.0)** at
`http://127.0.0.1:8000/mcp` — there is no stdio bridge and nothing to install.

**Verified handshake** (probed against the running 5.9 editor on 2026-11-15):

```bash
curl -s -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}'
```

The literal response, trimmed:

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": { "resources": {}, "tools": { "listChanged": true } },
    "serverInfo": { "name": "unreal-mcp", "version": "5.9.0-60351404" },
    "_meta": {
      "com.epicgames.unrealengine/instance": {
        "instanceId": "2196bb3e-46a4-6c10-ed40-828a7d2f3ed9",
        "processId": 38212,
        "engineVersion": "5.9.0-60351404",
        "engineBranch": "//UE5/Release-5.9",
        "engineChangelist": 60351404,
        "projectName": "EpicJam2026",
        "engineDirectory": "C:/Program Files/Epic Games/UE_5.9/Engine/",
        "projectDirectory": "D:/UE/EpicJam2026/",
        "projectFile": "D:/UE/EpicJam2026/EpicJam2026.uproject"
      }
    }
  }
}
```

That `_meta` block is the single most useful thing about the protocol: **it tells you which
editor and which project answered.** Read it before you act on anything.

Three details this protocol will bite on:

- The `Accept` header must include **both** `application/json` and `text/event-stream`.
- The `Mcp-Session-Id` header returned by `initialize` is **required** on every subsequent
  call.
- `notifications/initialized` must be sent before `tools/list`, or the session is not fully
  established.

**Auto-start** is configured per project, per user, in a file that is *not* `Default*.ini`:

```
<project>\Saved\Config\WindowsEditor\EditorPerProjectUserSettings.ini
```

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
ServerUrlPath=/mcp
ServerPortNumber=8000
bAutoStartServer=True
bEnableToolSearch=True
```

`bEnableToolSearch=True` (the default) registers **three meta-tools** instead of every
toolset tool natively: `list_toolsets`, `describe_toolset`, `call_tool`. The individual
toolset tools are **not** directly callable — `tools/call` with a name like
`EditorToolset.EditorAppToolset.GetOpenAssets` returns **HTTP 400**. Go through the
meta-tool instead:

```json
{ "method": "tools/call",
  "params": { "name": "call_tool",
              "arguments": { "toolset_name": "EditorToolset.EditorAppToolset",
                             "tool_name": "GetOpenAssets",
                             "arguments": {} } } }
```

`tool_name` is the bare name **without** the toolset prefix. Use `describe_toolset` first to
get the exact names and input schemas.

#### `editor_toolset` is not registered in this build

The toolset registry on the live 5.9 editor carries the canvas toolset, **not** the
editor's own Blueprint/Asset/Actor toolsets. Calls to `editor_toolset.*` fail with:

```
Toolset 'editor_toolset.BlueprintTools' not found
```

and retrying does not help — the toolset is simply absent.

**What works instead:** the editor's own Python, driven through the MCP bridge's
console-command bridge. That covers most editor work that is *not* Blueprint graph
authoring. Blueprint graph authoring specifically still needs `editor_toolset` — if it is
unavailable, **say so** rather than silently skipping the graph.

Details and the ready-made fallback client:
`.vault/model-notes/2026-11-15-mcp-tool-surface-reality-in-this-build.md`.

Useful console commands (editor Output Log, `~` key):

| Command | Effect |
|---|---|
| `ModelContextProtocol.StartServer [port]` | start the HTTP server (optional port override) |
| `ModelContextProtocol.StopServer` | stop it |
| `ModelContextProtocol.RefreshTools` | rebuild the tool list, drop cached schemas |
| `ModelContextProtocol.GenerateClientConfig <ClaudeCode\|Cursor\|VSCode\|Gemini\|Codex\|All>` | write client config files |

CLI flags: `-ModelContextProtocolStartServer`, `-ModelContextProtocolPort=<N>`.

**Auto-start is skipped in commandlets** — a cook or a build would race the editor for the
port. Pass `-ModelContextProtocolStartServer` to force it on.

**Every editor defaults to port 8000.** A second editor cannot bind it; its `StartServer`
hits `ensure(HttpRouter.IsValid())` and serves nothing, while the client stays happily
connected to the *first* editor. Give each editor its own port:

```powershell
UnrealEditor.exe "D:\UE\<Project>\<Project>.uproject" `
  -ModelContextProtocolPort=8010 -ModelContextProtocolStartServer
```

The server binds `127.0.0.1` only — it is not reachable from the network.

### 4c. MCP — the Unreal Canvas bridge (a *different* server)

**This is not the same thing as §4b, and confusing the two is expensive.** Epic's plugin and
the Unreal Canvas bridge both expose tools over MCP, and on this machine both were live at
once.

| | Epic's plugin (§4b) | Unreal Canvas / "merlin" |
|---|---|---|
| Process | `UnrealEditor.exe` (PID 38212) | `unrealcanvas-server.exe` (PID 32220) |
| Build | part of the engine | `C:\Users\Bluze\AppData\Local\UnrealCanvas\Builds\v0.21.0\` |
| Version string | `5.9.0-60351404` (the engine version) | `0.21.0` (`merlin-version.txt`) |
| `serverInfo.name` | `unreal-mcp` | `merlin` |
| Protocol version | negotiated: `2025-11-25`, `2025-06-18`, `2024-11-05` | `2025-03-26` |
| Observed ports | `127.0.0.1:8000` | `127.0.0.1:58784`, `58785` |
| Tool style | toolsets behind `list_toolsets` / `call_tool` | flat, task-shaped tools |

The canvas server is spawned by the editor, and its command line shows what it was asked
for and what it actually got:

```
unrealcanvas-server.exe --port 0 --parent-pid 38212
  --python "<engine>\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
  --mcp-port 8000 --viewport-port 58782
  --pythonpath "<project>\Intermediate\PipInstall\Lib\site-packages"
```

Note `--mcp-port 8000` was **requested** but the editor already held 8000 — the canvas
server ended up on 58784/58785 instead. **`--mcp-port` is a request, not a guarantee; always
confirm with `netstat`.**

Probing the canvas server's `/mcp` returns a `frontendBuild` note that tells you its state:

```json
"frontendBuild": { "known": false,
  "why": "No Unreal Canvas frontend is connected, so nothing is executing tool calls. Open the Unreal Canvas panel." }
```

**Read that before calling it.** A canvas tool that is listed but not executing is a
misconfigured frontend, not a broken tool.

Canvas-style tools in a session (`TriggerMRGRender`, `SpawnMeshAt`, `RunMeshOps`,
`SetSkybox`, `SpawnGsplatFromPLY`, `ListCutouts`, `StartViewportStream`, the annotation
tools) are the canvas surface's vocabulary. If a canvas tool reports that no frontend is
connected, or a render never starts, that is the canvas bridge — not the editor, and not
§4b.

**Which one is the Claude Code client pointed at?** The client is registered at **user
scope**, so it is visible from every directory on the machine:

```bash
claude mcp list          # shows the server, its URL and whether it is connected
```

The endpoint it points at is the editor's own MCP route, `http://127.0.0.1:8000/mcp`. The
definition to register is in `.skills/ue-mcp-bridge/references/client-config.json`, and
`.skills/ue-mcp-bridge/SKILL.md` is the procedure for registering it.

**Verify the port before you trust a tool.** One command:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen |
  ForEach-Object { Get-CimInstance Win32_Process -Filter "ProcessId=$($_.OwningProcess)" } |
  Select-Object Name, ProcessId, CommandLine
```

An MCP client loads servers **at session start**. A server registered after the session began
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

### 4e. The `ue-op-*` skillset — external, and already good

A large, working skillset for Unreal operations lives **outside this workshop**:

```
D:\UE\.ue-op-skillset\<skill-name>\SKILL.md
```

It has 30 skill folders (29 `ue-op-*` plus `ue-mcp-connect`):
`ue-op-inspect-blueprint`, `ue-op-create-blueprint`, `ue-op-add-component`,
`ue-op-wire-graph`, `ue-op-fix-compile-error`, `ue-op-fix-large-ue-sample-project`,
`ue-op-setup-game-mode`, `ue-op-setup-input`, `ue-op-setup-playable-character`,
`ue-op-test-pie`, `ue-op-find-assets`, `ue-op-find-dependencies`,
`ue-op-clone-assets`, `ue-op-relocate-assets`, `ue-op-capture-editor`,
`ue-op-offscreen-verify`, `ue-op-editor-script`, `ue-op-python-gotchas`,
`ue-op-build-web`, `ue-op-verify-web`, `ue-op-ship-web`, `ue-op-bake-mesh-partition`,
`ue-op-browser-look-budget`, `ue-op-blender-rig-for-ue`, `ue-op-animate-foreign-rig`,
`ue-op-skeletal-import-and-skeleton`, `ue-op-tripo-pipeline`,
`ue-op-tripo-triage-asset`, `ue-op-extract-to-skill`.

**Read the matching `SKILL.md` directly from disk** — that is the intended access path. It is
deliberately kept outside any agent's skills directory and registered per project, so
agents working in non-UE projects never load it.

To make them callable inside a UE project, junction them into that project's skills
directory (the convention most agents use is `.claude/skills`; others differ):

```powershell
New-Item -ItemType Junction -Path "D:\UE\<Project>\.claude\skills\<name>" `
  -Target "D:\UE\.ue-op-skillset\<name>"
```

**These are not this workshop's skills.** They are a sibling asset. When one of them proves
itself in a real task, the *generalized* version — the part that is not specific to one
project — belongs in `.skills/` here, written with the optimized steps. Copying a skill
across verbatim teaches this workshop nothing.

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

All five grow by use. The index of what exists is `.skills/README.md` (§ "Skills available
now"); **keep it current**, because an agent decides what to open by reading it. A skill
that exists but is not in the table is a skill nobody will find.

**Do not import skills from a sibling workshop or from the `ue-op` skillset verbatim.** A
skill is forged from a task that actually happened *in this app, for this workspace*.
`D:\UE\.ue-op-skillset\` is a sibling asset (§4e) — generalize from it, don't clone it.

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

**Then commit it** — see §7. One task, one commit, and only when something substantial
landed.

### When to read

**Only when it will pay for itself:**

- **Something went wrong** and you suspect it has happened before — search the vault before
  guessing at a fix.
- **The user asks** what has worked before, what to avoid, or for a specific recipe.
- **You are about to repeat an expensive operation** (a cook, a big asset import, a render)
  and want to reuse a known-good setup.

Search it with `grep`, not by reading it end to end:

```powershell
Select-String -Path .vault\lessons\*.md -Pattern 'port' -SimpleMatch
```

### Never overwrite a lesson

Add a new one and mark the old decision `superseded`. A later agent has to be able to see
what was true *then*, and why it stopped being true.

Format for a lesson:

```markdown
# <one-line title>

**Date:** YYYY-MM-DD
**Symptom:** what was observed, literally.
**Cause:** why it happened.
**Fix:** what to do instead — an instruction, not a story.
**Applies when:** the trigger that means this is relevant again.
```

Format for a "what worked" entry — same shape, different headings:

```markdown
# <one-line title>

**Date:** YYYY-MM-DD
**What was run:** the exact command / script / settings.
**Result:** what came out, and where it landed.
**Reuse when:** the situation where this is the right starting point.
```

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
| `ue-op-*` skillset (external) | `D:\UE\.ue-op-skillset\<name>\SKILL.md` |
| Unreal projects | `D:\UE\<Project>\<Project>.uproject` |
| Engine templates | `<engine>\Templates\` (`TP_ThirdPerson\`, `TP_FirstPerson\`, `TP_Blank\`, …) |
| Claude Code MCP entry | user scope — check with `claude mcp list` |
| Dependency-free MCP client | `D:\UE\.ue-op-skillset\ue-mcp-connect\mcp_call.py` |
| Sister workshops | `../Blender_Workshop/`, `../Unity_Workshop/`, `../ComfyUI_Workshop/` |
| The tool spec | `tools/README.md` |
| Memory bank | `.vault/README.md` |

### The vault entries that will save you the most time

| File | What it saves you |
|---|---|
| `.vault/decisions/2026-11-15-where-unreal-artifacts-belong.md` | Content vs Saved vs export — where an artifact goes, and what must be created *through the editor* |
| `.vault/decisions/2026-11-15-the-unit-scale-is-decided-at-export-time.md` | The ×100 Blender/Unity → Unreal scale, decided at export, not at import |
| `.vault/decisions/2026-11-15-the-unreal-version-is-resolved-not-pinned.md` | Why the launcher registry cannot be trusted here |
| `.vault/decisions/2026-11-15-the-two-unreal-mcp-surfaces-are-not-interchangeable.md` | Telling Epic's plugin from the canvas bridge |
| `.vault/decisions/2026-11-15-this-workshop-carries-no-mcp-configuration.md` | Why the workshop ships no MCP config, and where the client definition lives instead |
| `.vault/lessons/2026-11-15-the-launcher-registry-does-not-list-ue-5-9.md` | The resolver trap, with the scan command |
| `.vault/lessons/2026-11-15-verify-the-port-and-its-owner-before-trusting-an-mcp-connection.md` | "Connected but about the wrong project" |
| `.vault/lessons/2026-11-15-ue-5-5-has-no-mcp-plugin.md` | Why an old engine has no MCP at all |
| `.vault/model-notes/2026-11-15-mcp-tool-surface-reality-in-this-build.md` | `editor_toolset` absent; base64-wrapped images; the sandbox limits; `mcp_call.py` |
| `.vault/model-notes/2026-11-15-ue-installs-and-mcp-capability.md` | Which engine can do what; verified commandlets; reusable engine assets |
| `.vault/model-notes/2026-11-15-unreal-mcp-surfaces-on-this-machine.md` | Ports, protocol versions, config keys, console commands |
| `.vault/workflows/2026-11-15-identify-which-unreal-mcp-answered.md` | The copy-pasteable "which server answered" sequence |

> **The path to Unreal is not a constant.** It moves when the engine is updated, and the
> launcher registry does not list every install. Resolve it (§3) instead of assuming the
> paths above are still correct.
