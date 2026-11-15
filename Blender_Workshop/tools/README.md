# `tools/` — the tool layer

**This folder is a specification. There are no scripts here yet.**

The tools are written by the **DSH side** — see
`../.vault/decisions/2026-11-15-the-tool-layer-is-specified-not-built.md`. This file is the
contract they have to satisfy, so that an agent can rely on them the way it relies on
`tools/` in the ComfyUI workshop.

Until they exist, the working path is the one in `AGENTS.md` §4: the live instance on
`127.0.0.1:9876`, or a headless `blender.exe --background --python` run.

---

## What the tools have to do

| Tool | Purpose | Contract |
|---|---|---|
| **version resolver** | Find the newest Blender installed. | Scan `C:\Program Files\Blender Foundation\Blender */blender.exe`. Compare on the **version tuple**, not the folder name (`5.3` > `5.2`; `5.3.1` > `5.3`). Output: the executable path and the version. **Every other tool calls it** — none of them hardcode a version. When it finds a newer install than the one it used last, it **updates its own path** and says so in its output. |
| **headless runner** | Run a Python script inside Blender, no GUI. | `blender.exe --background --python <script>`. Options it needs: the script path, an optional `.blend` to open first, an optional timeout, and a way to surface the script's stdout/stderr and its exit status. **Absolute paths only** — the script's working directory is where Blender was launched, not where the script lives. |
| **bridge client** | Talk to the live instance. | Connect to `127.0.0.1:9876` and issue the add-on's commands: `ping`, `get_scene_info`, `get_object_info`, `execute_code`. Verify the protocol against `../.vault/decisions/2026-11-15-port-9876-is-not-an-mcp-endpoint.md` — the request/response shapes are recorded there, with real probe output. |
| **MCP bridge** | Expose Blender to an MCP client. | Serves a streamable-HTTP MCP endpoint that fronts the official Blender MCP extension (`blender.exe --background <file.blend> --command blender_mcp --port <PORT>`). **9876 is taken** — use a free port such as 9877, and fill in `.mcp.json` from `.mcp.json.example`. |

Anything else the DSH side adds is welcome; this table is the floor, not the ceiling.

---

## Constraints every tool obeys

These are not preferences. They are the rules that keep the tool layer from destroying work.

1. **Never kill a Blender the user started.** If a tool starts Blender, it records the PID
   and only ever stops *that* PID. A Blender the user launched themselves is never touched.
   Restarting Blender is the user's call.

2. **Never write into the live scene by accident.** The running instance holds the user's
   real scene (50 objects, 25 materials, as of 2026-11-15). No tool resets it, clears it, or
   saves over it.

3. **Save As, never Save.** `save_as_mainfile(filepath=...)` with an explicit path.
   `save_mainfile()` overwrites whatever is open.

4. **The destination is required, not defaulted.** A tool that writes output takes the
   destination as an argument and refuses to guess one.

5. **Resolve the version, never pin it.** See the resolver row above.

6. **No media in the workspace.** Tools write into the destination. Scratch goes to
   `work/` (git-ignored). Nothing binary lands in this tree.

7. **Fail loudly.** A tool that cannot reach Blender says so and says what it tried. A tool
   that half-succeeded is worse than one that failed.

---

## A note on the two Blender surfaces

They are not interchangeable, and the tools should not pretend otherwise:

- The **live instance** (DSH bridge, 9876) has the user's scene, the user's UI state and
  the user's add-ons. Writes go straight into their work.
- A **headless run** (`--background`) is a clean process. It has no UI state, and it does
  not touch the running instance — but it also cannot see anything the user has not saved
  to a file.

Pick the surface by the task, and say which one was used.
