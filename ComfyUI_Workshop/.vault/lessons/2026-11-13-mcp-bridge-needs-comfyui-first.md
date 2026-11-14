# ComfyUI's MCP bridge dies without ComfyUI — boot order matters

**Date:** 2026-11-13
**Symptom:** The MCP port `9000` was dead, but a `pythonw.exe` supervisor and a
`pythonw.exe` server child were both alive in Task Manager. `supervisor.log` showed the
child being respawned every ~60 seconds, forever:

```
[supervisor 2026-11-13 21:26:37] spawned child pid=28092
[supervisor 2026-11-13 21:27:38] child pid=28092 exited with code 1 — respawning
[supervisor 2026-11-13 21:27:43] spawned child pid=44904
[supervisor 2026-11-13 21:28:44] child pid=44904 exited with code 1 — respawning
```

`supervisor-child.stderr` had grown to 84 MB of the same failure.

**Cause:** The MCP server connects to `ws://127.0.0.1:8188/ws` at startup and **exits after
60 seconds if ComfyUI is not reachable**. The supervisor respawns it on exit, so with
ComfyUI down the loop runs forever and never recovers. `comfyui-mcp-server/server.py` has a
startup wait for ComfyUI, but the 60 s liveness budget expires before a cold ComfyUI
finishes loading its custom nodes.

**Fix:** **ComfyUI first, MCP second.** Always.

- Boot ComfyUI and wait for `GET http://127.0.0.1:8188/system_stats` to answer.
- *Then* the MCP bridge binds on its own — the supervisor's next respawn succeeds and
  stays alive. Verified: the child spawned at 21:33:13, after ComfyUI came up, survived
  and served 44 tools.
- `tools/boot-comfyui.ps1` already sequences this correctly.

**Do not** hand-launch the MCP server first, and do not kill the supervisor — it is
self-healing once ComfyUI is up.

**Applies when:** port 9000 is dead, `comfyctl health` reports `mcp.up: false`, or
`supervisor.log` shows a repeating respawn loop.

**Cost:** ~25 minutes of confusion on 2026-11-13, plus an 84 MB stderr file.
