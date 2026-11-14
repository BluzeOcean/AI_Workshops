---
name: comfyui-boot
description: Bring the headless ComfyUI server and its MCP bridge up against a confirmed destination folder, and diagnose a stack that will not start. Use when a generation task needs ComfyUI and the 8188 or 9000 port is not answering, or when a task needs a different output destination than the running server has.
---

# Booting ComfyUI headless

ComfyUI on this machine is **a server, not an app**. It runs with no browser and no console
window. The goal is that the task works; the boot is a means.

## Before anything else: confirm the destination

The destination is the folder generated files land in. ComfyUI's
`folder_paths.get_save_image_path()` refuses to write outside `--output-directory`, so the
destination is fixed **when the server boots** and changing it needs a restart.

- If the user gave you a destination → use it exactly.
- If they did not → **ask.** Do not default, do not guess, do not reuse a previous one.

## Boot

```powershell
pwsh -File tools\boot-comfyui.ps1 -OutputDir "<DESTINATION>"
```

This is the whole sequence and it is ordered deliberately:

1. `GET http://127.0.0.1:8188/system_stats`. If it answers, ComfyUI is already up — the
   script leaves it alone and prints a warning if its destination is not the one you asked
   for. **Never kill or restart a server someone else started.**
2. If down, launch it detached and silent via `tools\comfy-boot.cmd`.
3. Poll `/system_stats` until it answers. Custom nodes have to load first: 30–90 s is
   normal, more than that is a stall.
4. Ensure the MCP bridge is up on `http://127.0.0.1:9000/mcp`.
5. Print `comfyctl health`.

### Restarting on a different destination

Only ever restarts the instance **this workspace** started (tracked in `tools\.comfyui.pid`):

```powershell
pwsh -File tools\boot-comfyui.ps1 -OutputDir "<DESTINATION>" -Restart
```

If the pidfile is missing, the script refuses to restart anything and says so. That is
intentional: the user's own ComfyUI-EZi instance is not ours to kill.

## Verify

```powershell
node D:\ComfyUI\harness\comfyctl.mjs health
```

Healthy output:

```json
{ "comfyui": { "up": true, "status": 200, "ms": 26 },
  "mcp":     { "up": true, "tools": 44, "ms": 8 } }
```

`tools: 44` is the full MCP surface. A low number means the bridge came up partially.

## When it does not come up

**MCP dead, ComfyUI also dead.** Expected — the MCP server exits after 60 s without
ComfyUI, and its supervisor respawns it every 60 s. Fix ComfyUI; the bridge binds itself
within a minute. Do not hand-launch the MCP server first. See
[`.vault/lessons/2026-11-13-mcp-bridge-needs-comfyui-first.md`](../../.vault/lessons/2026-11-13-mcp-bridge-needs-comfyui-first.md).

**ComfyUI never answers.** Read the log — this is where the answer is:

```powershell
Get-Content D:\ComfyUI\harness\comfyui-headless.log -Tail 40
```

- Last line is `Starting server` → it is up, the probe was too short.
- Last line is a node import → a custom node is stalling. Report it; do not retry blindly.
- Last line is a traceback → the error is there. Read it.

**A console window flashed open and closed.** Something launched ComfyUI without `/B`.
`tools\comfy-boot.cmd` uses `start "" /B`; anything that drops `/B` opens a visible console
on the user's desktop. Never reproduce that pattern.

**The MCP tool list is missing in your session.** The tool list freezes at session start —
if the server was down when the session opened, `mcp__comfyui__*` will never appear, and
restarting the server will not fix it. Use `comfyctl` instead; it works in any session.

```powershell
node D:\ComfyUI\harness\comfyctl.mjs tools
```

## Close it when the task is done

A finished task ends with the stack closed:

```powershell
pwsh -File tools\stop-comfyui.ps1
```

It stops the MCP supervisor first — otherwise the supervisor respawns its child and port
9000 never closes — then the ComfyUI server, then reports the VRAM and RAM that came back.
Typically **~11 GB of VRAM and ~17 GB of RAM** are released and both ports go quiet.

**Do not leave the server running between tasks.** MOSS-Image parks ~12 GB of VRAM and
~22 GB of RAM in the process; that is memory the rest of the machine wants.

The script only stops what this workspace started (tracked in `tools\.comfyui.pid`). If the
only ComfyUI running is the user's own, it says so and leaves it alone.

If you need the GPU back but still want ComfyUI up, use `tools\free-vram.ps1` instead — it
calls `POST /free`, which releases the models without closing the server, and the next
render only pays ~6 s to reload them.
