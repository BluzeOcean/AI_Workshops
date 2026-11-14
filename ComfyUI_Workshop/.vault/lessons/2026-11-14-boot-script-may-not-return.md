# `boot-comfyui.ps1` can hang forever even though the boot succeeded — check health, not the exit code

**Date:** 2026-11-14
**Symptom:** `pwsh -File tools\boot-comfyui.ps1 -OutputDir "…\MechConcept Art" -InputDir "…"`
was started in the background and **never returned**. The background task was finally
killed at its 600 s timeout and reported **failed** — while ComfyUI had been up and
serving correctly for the whole time.

**Cause:** not fully diagnosed. The script finishes its real job in roughly 30 s (ComfyUI
answers `/system_stats`, the MCP bridge binds 9000, the pid file is written), then blocks
on something that never completes — most likely a wait on the MCP supervisor's child
handle, which is respawned forever and therefore never closes. The boot itself is fine;
only the script's return is broken.

**Fix:** treat a hung boot as a **success** once the stack answers:

```powershell
node D:\ComfyUI\harness\comfyctl.mjs health        # comfyui.up AND mcp.up
node D:\ComfyUI\harness\comfyctl.mjs get /system_stats   # check --output-directory
```

Check `argv` in `/system_stats` — it echoes `--output-directory` and `--input-directory`.
If they are right, the destination is right and you can go straight to rendering.

**Do not re-run the boot script** to "fix" it: a second boot will try to start a second
ComfyUI on port 8188. Probe health instead.

**Applies when:** the boot script reports a timeout or a non-zero exit. Also applies to
any background bash task that reports *failed* — a task failure is not proof that the
underlying work failed.

**Related:** the stack is torn down normally with `tools\stop-comfyui.ps1`, which uses
`tools\.comfyui.pid` and did release 13.3 GB of VRAM with both ports free.
