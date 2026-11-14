# Two PowerShell traps in the boot tooling — `-like` is not regex, and a pipe handle is inherited

**Date:** 2026-11-13
**Symptom:** Two separate false results in `tools/boot-comfyui.ps1`, both of which made the
script *lie* about the state of the server.

**1. The destination check always warned, even when it was correct.**

The running server had been started with exactly the requested destination, and the script
still said "Assets will NOT land where you asked". The check was:

```powershell
if ($cmdline -notlike "*--output-directory*" -or $cmdline -notlike [regex]::Escape($OutputDir)) {
```

`-like` is a **wildcard** match, not a regex match. `[regex]::Escape()` doubles every
backslash, producing a pattern with `\\` where the real command line has a single `\`, so
the pattern never matched.

**Fix:** parse and compare, do not pattern-match a whole command line.

```powershell
$outDir = if ($cmdline -match '--output-directory\s+"([^"]+)"') { $Matches[1] } else { '' }
if ($outDir.TrimEnd('\') -ne $OutputDir.TrimEnd('\')) { ... }
```

**2. The MCP bridge probe always reported "down".**

`Test-Http` did a plain `GET` on `http://127.0.0.1:9000/mcp`. **That endpoint hangs open
on purpose** — it is an SSE stream that never ends. The request never completes, so the
probe always timed out and always said "down", while the bridge was in fact serving 44
tools. The boot script then spent 120 s trying to launch a bridge that was already up.

**Fix:** ask the tool that speaks the protocol, not the endpoint.

```powershell
$raw = & node $ComfyCtl health          # does a real JSON-RPC initialize POST
$health = ($raw -join "`n") | ConvertFrom-Json
$health.mcp.up
```

**Why this matters beyond this script:** a health check that always fails is worse than no
health check, because it teaches you to ignore it. When a probe reports a problem, confirm
the probe is right before acting on it.

**Applies when:** writing any liveness probe, or matching against a command line.
