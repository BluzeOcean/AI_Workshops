# `tools/` — the tool layer

The scripts that drive Unreal. Each one is a repeatable mechanical action that a skill
can call: start something, stop something, run a command, read a state.

## What belongs here

A tool is something that can be **run**, not read. If the answer to "how do I do X?" is a
paragraph, it is a skill. If it is a script with arguments, it is a tool.

| Tool | Purpose |
|---|---|
| _(none yet)_ | |

## What Unreal specifically needs

The generic rules above are inherited from the house shape. These are the tools this
workshop is missing, in the order an agent is most likely to want them. They are
**specifications** — none are written yet.

| Tool | Purpose | Notes |
|---|---|---|
| `resolve_engine` | Print the newest Unreal install: engine root, version, changelist, and whether it has the MCP plugin. | Must scan `C:\Program Files\Epic Games\UE_*/Engine/Build/Build.version` and compare version tuples. **Must not consult the launcher registry** — it omits UE 5.9. See `.vault/lessons/2026-11-15-the-launcher-registry-does-not-list-ue-5-9.md`. |
| `find_editors` | List running `UnrealEditor.exe` processes with PID, engine path and the `.uproject` each has open. | Read via WMI `Win32_Process`. The `.uproject` in the command line is the authority — never infer the project from memory. |
| `mcp_identify` | Report which MCP server a URL belongs to: owning process, `serverInfo.name`, engine version, project file, and whether a canvas frontend is connected. | Wraps `.vault/workflows/2026-11-15-identify-which-unreal-mcp-answered.md`. Read-only. |
| `mcp_call` | A dependency-free MCP client for the endpoint — initialize, track `Mcp-Session-Id`, send `notifications/initialized`, then `tools/list` / `tools/call`. | Mirrors `V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py`, which already works. Prefer reusing that over writing a new one. |
| `run_commandlet` | Run `UnrealEditor-Cmd.exe -run=<Commandlet>` against a named project, with the engine resolved at run time. | Must refuse to start while the target port is held by another editor — commandlets skip MCP auto-start and would race it. |
| `run_editor_python` | Run a Python script inside the editor (`-ExecutePythonScript=`) with the engine and project resolved. | `import unreal` is only available inside the editor; the standalone `python.exe` cannot import it. |
| `sync_skills` | Copy the workshop's skills into a UE project's `.claude\skills\`, replacing older copies. Reports what changed, what was added, and what is stale. | The workshop is the only copy of the skillset; a project consumes a skill by **copying** it, so a copy is a snapshot that must be refreshed. Never junctions — a junction lets a project silently edit the workshop. See `.vault/decisions/2026-11-15-the-workshop-is-the-only-copy-of-the-skillset.md`. |

## Rules every tool obeys

1. **Never kill something the user started.** If a tool starts Unreal, it records the
   PID and only ever stops *that* PID. An instance the user launched themselves is never
   touched. Restarting the app is the user's call.
2. **Never write into a live scene or session by accident.** A running instance may hold
   the user's real work. No tool resets it, clears it, or saves over it.
3. **The destination is required, not defaulted.** A tool that writes output takes the
   destination as an argument and refuses to guess one.
4. **Resolve the version, never pin it.** Find the newest install and use it; do not
   hardcode a version or a path that a later update invalidates.
5. **No media in the workspace.** Tools write into the destination. Scratch goes to the
   project's `Saved/` folder. Nothing binary lands in this tree.
6. **Fail loudly.** A tool that cannot reach Unreal says so and says what it tried. A
   tool that half-succeeded is worse than one that failed.

## Writing one

Keep it small and honest. A tool that wraps one command is fine; a tool that wraps forty
decisions is a skill in disguise.
