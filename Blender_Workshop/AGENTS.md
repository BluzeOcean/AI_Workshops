# AGENTS.md — Blender_Workshop

**This workspace drives Blender. Any agent can open this folder, read this file, and be
productive — no tutorial, no prior context, no hand-holding needed.**

Read this file completely before touching anything. It is the entire onboarding.

You do not need to know Blender. You need to know **which Blender is installed**, **how to
reach it**, **where the files go**, and **how not to destroy somebody's work**. Those four
things are below.

---

## 1. The map

| Path | What it is |
|---|---|
| `.skills/` | **Procedures.** One folder per skill, each with a `SKILL.md`. A skill is a repeatable task — "import a glTF and clean it up", "render a turntable", "export for Unreal". Read `.skills/README.md` before writing one. |
| `.vault/` | **The memory bank.** A log of what worked and what did not — lessons, decisions, model notes, recipes. It is **written after a task, not read before one** (see §6). |
| `tools/` | The scripts. Currently a **specification, not an implementation** — see `tools/README.md`. Whoever builds them owns this layer. |
| `.mcp.json.example` | The reserved slot for an MCP bridge. The bridge itself is not built yet; see §4c. |
| `.claude/settings.local.json` | Registers the project's MCP servers for agents that read it. |

**`.vault/` is a memory bank, not a checklist.** You do not read it at the start of a task —
that would waste context on a log that is mostly irrelevant to what you are doing right now.
You *write* to it when a task ends, and you *search* it when something breaks or the user asks
whether it has happened before.

### This workspace holds no media

**No `.blend` files, no renders, no textures, no exports, no caches — ever.** This workspace
is instructions, skills and a memory bank. Blender output goes to the **destination outside
this folder**, and the workspace only ever keeps the *text* that describes how it was made.

Concretely:

- Never write a `.blend`, a `.png` render, a `.fbx`/`.glb` export or an `.obj` into this tree.
- A recipe in `.vault/recipes/` is **text**: the script, the settings, the export options. Not
  the mesh it produced.
- Intermediate scripts and JSON are scratch. Build them in `work/` (git-ignored), not in
  `.vault/`.
- `.blend` files are especially tempting to keep here because they are "the work". They are
  not. A `.blend` is a build artifact with absolute paths and a binary payload; it belongs
  next to the project it is for.

---

## 2. The destination — read this twice

**The destination is the folder Blender output lands in. You must know it BEFORE you
produce anything.**

- If the user gave you a destination → use **exactly** that path. Character for character.
- If the user did **not** → **ASK.** Do not guess. Do not fall back to a default. Do not reuse
  the destination from an earlier task in this session.

This is not politeness. Blender will happily write a `.blend` to *any* path you name, which
means a guessed path produces work in the wrong place with no error to tell you. And the
user's own scene is often already open in the running Blender — writing over it destroys
their work silently.

The order is always: **confirm destination → work → save there.**

```
DESTINATION = <the folder the user named>
```

There is one hard rule on top of that, and it is the one that actually costs data:

> **Never save over the file the user has open.** Use *Save As* into the destination. If the
> user has `scene.blend` open in the running Blender and you call `bpy.ops.wm.save_mainfile()`,
> you have just overwritten their scene with whatever was in memory. `save_as_mainfile()` with
> an explicit path is the safe call.

---

## 3. The Blender install on this machine

Two versions are installed:

| Version | Path | Note |
|---|---|---|
| **5.3.0** (build 2026-11-10) | `C:\Program Files\Blender Foundation\Blender 5.3\blender.exe` | The current release. **This is the one in use.** |
| 5.2.1 LTS | `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` | Older LTS, kept as a fallback. |

### The version is RESOLVED, never pinned

**Always use the newest Blender installed.** Do not hardcode `5.3` into a script, a skill, or
a tool. When Blender 5.4 lands, the workspace must use 5.4 without a human editing paths.

Resolution rule, in order of authority:

1. **Inside a running Blender** — `bpy.app.binary_path` is the exact executable in use, and
   `bpy.app.version` / `bpy.app.version_string` are its version. This is the authority.
2. **From the shell** — scan `C:\Program Files\Blender Foundation\Blender */blender.exe`,
   ask each candidate for its version (`blender.exe --version`), and take the highest.
   Compare on the **version tuple**, not the folder name: `5.3` > `5.2`, and a `5.3.1` beats a
   `5.3`.

A skill or tool that hardcodes a version must **update its own path** when it finds a newer
install, and say that it did so in its output. A skill that silently keeps using 5.2 after 5.4
is installed is a bug, and it is the kind of bug that produces "why does the API differ?"
answers three weeks later.

### Why the version matters at all

Blender's Python API changes between versions, and the changes are not additive. Things that
have already moved between 4.x and 5.x: the EEVEE engine identifier, `bpy.ops.mesh.*`
operator names, node group internals, the extension system replacing legacy add-ons, and
parts of the compositor API. **Check `bpy.app.version` before you rely on an API detail, and
when a snippet fails, check the version before you assume the code is wrong.**

---

## 4. Talking to Blender — four ways

Blender is a desktop application, so unlike the ComfyUI workshop there is no server that is
"already up". There are four surfaces, and they are not equivalent.

### 4a. The live instance — the DSH bridge on 127.0.0.1:9876

A Blender 5.3 instance is running on this machine with the **DSH Blender Bridge** add-on
enabled. It listens on `127.0.0.1:9876` and speaks a small JSON request/response protocol
over a TCP socket.

**Verified protocol** (probed against the running instance on 2026-11-15):

Request — one JSON object per request, newline-terminated:

```json
{"type": "<command>", "params": { ... }}
```

Response — one JSON object per response:

```json
{"status": "success", "result": { ... }}
{"status": "error",   "message": "..."}
```

Verified commands:

| Command | Params | Returns |
|---|---|---|
| `ping` | — | `{"pong": true}` — liveness check, no side effects |
| `get_scene_info` | — | scene name, `object_count`, a list of objects (name, type, location), `materials_count` |
| `get_object_info` | `{"name": "<object name>"}` | that object's type, location, rotation, scale, visibility, materials |
| `execute_code` | `{"code": "<python>"}` | `{"executed": true, "result": "<captured stdout>"}` — runs Python inside the running Blender |

Unknown commands come back as `{"status": "error", "message": "Unknown command type: ..."}`
rather than a dropped connection.

**Framing: one JSON object per line.** LF and CRLF both work; a bare null byte does
**not** (that is the *other* add-on's framing — see §4c).

```powershell
# liveness, from PowerShell. Write raw bytes: a StreamWriter and a StreamReader
# over the same socket buffer against each other and the read times out.
$c = [System.Net.Sockets.TcpClient]::new('127.0.0.1', 9876)
$c.ReceiveTimeout = 5000
$s = $c.GetStream()
$s.ReadTimeout = 5000
$req = [System.Text.Encoding]::UTF8.GetBytes('{"type":"ping"}' + "`n")
$s.Write($req, 0, $req.Length)
$s.Flush()
$buf = New-Object byte[] 65536
$n = $s.Read($buf, 0, $buf.Length)
[System.Text.Encoding]::UTF8.GetString($buf, 0, $n).Trim()
$c.Close()
```

```python
# the same thing in Python
import json, socket
s = socket.create_connection(("127.0.0.1", 9876), timeout=5)
s.sendall(json.dumps({"type": "ping"}).encode() + b"\n")
print(s.recv(65536).decode())
s.close()
```


**This port is NOT an MCP endpoint.** It speaks the add-on's own command protocol, not
MCP/JSON-RPC. An MCP client cannot point at `9876` and expect to connect. Getting a real MCP
surface is §4c.

**The live instance holds the user's actual scene.** As of 2026-11-15 it had a scene open with
50 objects and 25 materials. Treat every write to it as a write to their work.

### 4b. Headless one-shot — `blender --background --python`

The escape hatch that always works, needs no add-on, no port and no running GUI:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe" `
  --background --factory-startup --python "V:\...\work\script.py"
```

- `--factory-startup` loads no add-ons and no user preferences — deterministic, and it keeps
  a heavy add-on from stalling the startup. Drop it when you *need* an add-on.
- `--python` runs the file in Blender's embedded interpreter. `bpy` is importable **only**
  there; a system Python cannot `import bpy`.
- The script's working directory is where Blender was launched from, not where the script
  lives. **Use absolute paths inside scripts.**
- Nothing persists between runs except what you save. A headless run has no viewport and no
  UI state.

### 4c. MCP — the official Blender MCP extension

Blender 5.3 ships an **official MCP bridge extension** (`lab_blender_org/mcp`), installed at:

```
C:\Users\Bluze\AppData\Roaming\Blender Foundation\Blender\5.3\extensions\lab_blender_org\mcp\
```

It provides a real MCP server, runnable in background mode:

```powershell
blender.exe --background <file.blend> --command blender_mcp --port <PORT>
```

**It speaks MCP**, with the official protocol: requests are null-byte-terminated JSON
`{"type": "execute", "code": "<python>", "strict_json": true}`; the executed Python sets a
`result` dict and the server returns `{"status": "ok", "result": {...}}` plus captured
`stdout`/`stderr`.

Two things to know:

- **Port 9876 is taken** by the DSH bridge (§4a). A second MCP server needs a different port
  — 9877 is free.
- The add-on refuses to run unless **Online Access is enabled** in Blender's Preferences →
  System → Network. If it will not start, that is why.

**The bridge that exposes this to an MCP client is not built yet.** `.mcp.json.example` is
the reserved slot; `tools/README.md` says what it has to do. Until it exists, an
MCP-capable agent uses 4a or 4b and an MCP-less agent uses 4b alone.

### 4d. The tools in `tools/`

Written by whoever owns the tool layer. See `tools/README.md` for the spec. When they exist,
they will wrap 4a/4b/4c — they do not replace them.

---

## 5. Rules that will save you the time

These are not style preferences. Each one cost somebody real time to learn.

1. **Never kill a Blender the user started.** Two `blender.exe` processes are running as of
   2026-11-15 — the GUI instance with the user's scene, and a child of it. Restarting
   Blender is the user's call. If an instance is wedged, ask.

2. **Never reset the user's scene.** No `bpy.ops.wm.read_homefile()`, no
   `read_factory_settings()`, no "clear the scene" — not even "to start clean". Start from
   what is there, or work in a headless process against a file you were given.

3. **`bpy.ops` needs a context; `bpy.data` does not.** In background mode `bpy.context.area`
   is `None` and `bpy.context.screen` may be a stub, so any operator that wants a 3D view
   fails with a context error that reads like a Blender bug. Prefer the data API
   (`bpy.data.objects.new`, `bpy.data.objects.remove(obj, do_unlink=True)`) over the
   operator API (`bpy.ops.object.delete()`), and when you must use an operator, pass a
   `context_override`.

4. **Deleting objects: use the data API.** `bpy.ops.object.delete()` depends on selection and
   the active object, and silently does nothing when there is no active object.
   `bpy.data.objects.remove(obj, do_unlink=True)` is unconditional.

5. **Name collisions auto-suffix, and nobody notices.** `bpy.data.objects.new("Crate", ...)`
   in a scene that already has a `Crate` creates `Crate.001`. After a scripted build, check
   for `.001` suffixes before you save — they mean a duplicate got in, and they propagate
   into exports and into downstream game-engine scenes.

6. **Modifiers are not geometry until they are evaluated.** A bevel, a subsurf or a mirror
   modifier changes the *evaluated* mesh, not the stored one. Exporters differ in whether
   they apply modifiers (glTF does by default; FBX has its own option). Decide
   deliberately, and do not apply modifiers destructively just to "make it look right" —
   that destroys the non-destructive setup the user may be relying on.

7. **Renders need an explicit output path.** `bpy.ops.render.render(write_still=True)` writes
   to `scene.render.filepath`. Set it every time, with the extension you want, and leave
   `scene.render.use_file_extension` alone unless you have a reason. Otherwise the frame
   lands in a temp path with a name you did not choose.

8. **The engine identifier changed.** In Blender 5.x the EEVEE engine id is
   `BLENDER_EEVEE`. In 4.2–4.5 it was `BLENDER_EEVEE_NEXT`. A script written for 4.x will
   raise on 5.x. Cycles (`CYCLES`) is available and is the right choice for a still that has
   to be correct; EEVEE is the right choice for speed and previews. The `enum_items` listing
   for `scene.render.engine` is unreliable in background mode — it reported only `BLENDER_EEVEE`
   while `CYCLES` still worked, so **set the engine and catch the failure**, rather than
   trusting the enum.

9. **Units: Blender is metres, and the sister workshops are not.** Blender's default unit
   system is METRIC with `scale_length` 1.0 — 1 Blender unit = 1 metre. Unreal works in
   centimetres and Unity in metres. When a task hands off to `../Unreal_Workshop` or
   `../Unity_Workshop`, the scale is part of the export decision, and it is decided at
   export time, not left to the importer.

10. **The scene is a deliverable, not a scratchpad.** Object names, collection structure and
    material names survive into the export and into the game engine. Name things the way the
    project would name them; do not leave `Cube.003` and `Material.007` in a delivery.

11. **A save is not a render, and a render is not a save.** They are separate steps with
    separate failure modes. Saving a `.blend` that references a missing texture produces a
    file that opens with holes in it.

12. **The MCP tool list freezes when your session starts.** If the bridge is not running when
    the session opens, its tools never appear for that session, and restarting the server
    will not fix it. Fall back to 4a/4b.

13. **The running instance is a shared resource.** Two agents (or an agent and a human) can
    hit the same Blender. Assume the scene may change under you: read what you need
    immediately before you act, and re-read after anything slow.

14. **Check the version before you trust an API detail.** `bpy.app.version` first, then the
    docs for that version. Blender's API is versioned by release and the community answers
    are heavily mixed across versions.

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
| An add-on, model or render setting that works well | `.vault/model-notes/` |
| A script + settings that produced something good | `.vault/recipes/` |
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
- A **tool** is a script — something that can be run rather than read.

All four grow by use. The index of what exists is `.skills/README.md` (§ "Skills available
now"); **keep it current**, because an agent decides what to open by reading it. A skill
that exists but is not in the table is a skill nobody will find.

If a task needs a tool that does not exist yet, that is a finding too: add it to the
specification in `tools/README.md` rather than working around it silently.

### When to write

**After every completed task.** Even a task that went fine — especially one that went fine.
"What worked" is as valuable to record as "what did not": the next agent needs to know that
*this* approach with *that* version and *those* settings produced a good result.

Write at least one entry per task that produced a durable fact. If genuinely nothing durable
came out of a task, say so in the task summary instead of writing a filler file.

### When to read

**Only when it will pay for itself:**

- **Something went wrong** and you suspect it has happened before — search the vault before
  guessing at a fix.
- **The user asks** what has worked before, what to avoid, or for a specific recipe.
- **You are about to repeat an expensive operation** (a long render, a big scene build) and
  want to reuse a known-good setup.

Search it with `grep`, not by reading it end to end:

```powershell
Select-String -Path .vault\lessons\*.md -Pattern 'modifier' -SimpleMatch
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

## 7. Reference

| What | Where |
|---|---|
| Blender 5.3 (current) | `C:\Program Files\Blender Foundation\Blender 5.3\blender.exe` |
| Blender 5.2.1 LTS (older) | `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` |
| Blender install root | `C:\Program Files\Blender Foundation\` |
| DSH bridge (live instance) | `127.0.0.1:9876` — JSON command socket, **not** MCP |
| Official MCP extension | `…\Blender\5.3\extensions\lab_blender_org\mcp\` |
| Official MCP command | `blender.exe --background <file.blend> --command blender_mcp --port <PORT>` |
| Blender's own Python | `C:\Program Files\Blender Foundation\Blender 5.3\5.3\python\bin\python.exe` (no `bpy` — that is only inside Blender) |
| Blender temp dir | `bpy.app.tempdir` — autosave lives here, not in the destination |
| Sister workshops | `../Unreal_Workshop/`, `../Unity_Workshop/` |
| ComfyUI workshop (image generation) | `../ComfyUI_Workshop/` |
| The tool spec | `tools/README.md` |
| Memory bank | `.vault/README.md` |

> **The path to Blender is not a constant.** It moves when Blender is updated. Resolve it
> (§3) instead of assuming the path above is still correct.
