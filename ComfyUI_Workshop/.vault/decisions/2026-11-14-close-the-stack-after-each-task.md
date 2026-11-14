# The stack is closed after every task, not left running

**Date:** 2026-11-14
**Status:** active
**Decision:** When a task in this workspace is finished, the agent **closes the headless
ComfyUI and its MCP port** and releases the RAM and VRAM. The stack is not left running
between tasks.

```powershell
pwsh -File tools\stop-comfyui.ps1
```

**Reason:** The user asked for it explicitly: "note (if not already stated) it in the AGENTS.md
file to close the headless comfyui (and its mcp port) and release the ram/vram after the task
is completed." The measured cost of leaving it up is real: MOSS-Image parks **~12 GB of
VRAM and ~22 GB of RAM** in the server (see
`.vault/model-notes/moss-image-resource-footprint.md`). That is memory another local model
could be using.

**This reverses an earlier decision.** The first version of AGENTS.md said the opposite —
"do not clean it up on the way out unless the user asks" — because the stack was detached and
survived the session, which made it tempting to leave it up for the next task. The rule is
now: **survive the session, but not the task.**

**Scope:** the stop script only ever stops what this workspace started
(`tools\.comfyui.pid`). A ComfyUI the user started themselves is never touched.

**Mechanics worth remembering:**

- The MCP **supervisor respawns its child**, so it must be stopped FIRST. Kill the child
  alone and a new one appears within 5 seconds and port 9000 never closes.
- `POST /free` is the lighter alternative when the server should stay up but the GPU is
  needed: it releases ~11 GB of VRAM and ~17 GB of RAM in ~8 s, and the next render pays
  only ~6 s extra to reload. See `tools\free-vram.ps1`.
- The boot script deliberately leaves a *running* server alone even when the destination
  does not match. That is about not killing the user's server, not about leaving ours up —
  the task still ends with a stop.

**Applies when:** any task in this workspace that booted the stack.
