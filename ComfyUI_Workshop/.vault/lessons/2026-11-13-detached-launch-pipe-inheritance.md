# A detached grandchild inherits your .NET pipe and hangs `ReadToEnd()`

**Date:** 2026-11-13
**Symptom:** `tools/boot-comfyui.ps1` printed its first line and then **hung forever** — no
output, no error, the task never finished. ComfyUI itself was fine: it was up, serving on
8188, with the MCP bridge healthy. Only the script was stuck.

**Cause:** the launcher helper captured the child's output through a .NET pipe:

```powershell
$psi.RedirectStandardOutput = $true
$p = [System.Diagnostics.Process]::Start($psi)
$out = $p.StandardOutput.ReadToEnd()   # <-- never returns
```

`ProcessStartInfo` with a redirect creates the pipe with `bInheritHandles = TRUE`. The
`cmd.exe` launcher inherited it, and so did the **detached grandchild** it started with
`start "" /B`. Python does not write to that handle — but it holds it **open**. `ReadToEnd()`
waits for EOF, and EOF never comes because a process that is not going to exit for hours
still holds the write end.

**Fix:** do not use a .NET pipe for a launcher that spawns a detached child. Let the `.cmd`
redirect its own output to a log file, and do not redirect in .NET at all:

```powershell
$psi.RedirectStandardOutput = $false
$psi.RedirectStandardError  = $false
$p = [System.Diagnostics.Process]::Start($psi)
$p.WaitForExit(20000) | Out-Null     # bounded wait; the detached child continues
```

The `.cmd` files already redirect the long-lived child's output to a log file, which is
what you want to read afterwards anyway.

**Applies when:** launching any long-lived process from a script on Windows — the same
trap applies to `Process.StandardOutput.ReadToEnd()` on a process that spawns detached
children.

**Verified:** after the fix, the same boot ran to completion and ComfyUI **survived the
tool call being cancelled** — it kept serving across the boundary, which is the whole point
of the detached launch.
