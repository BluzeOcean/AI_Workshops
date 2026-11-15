# Verify the port and its owner before trusting an MCP connection

**Status:** active

**Date:** 2026-11-15
**Symptom:** Two failure modes with the same shape — the MCP client reports
`✔ Connected`, every call succeeds, and the results are **about the wrong thing**.

1. **Two editors.** A second `UnrealEditor.exe` is launched and its log shows
   `ensure(HttpRouter.IsValid())`. Every editor defaults to MCP port **8000**, so the
   second one binds nothing — while the client stays connected to the *first*, which is
   healthy, answering promptly, and has a **different project** open.
2. **A requested port that is not the bound port.** The Unreal Canvas server was launched
   with `--mcp-port 8000`, but it did not get 8000 — the editor already held it. The
   canvas server's MCP route is actually on `58784`:

   ```powershell
   Get-CimInstance Win32_Process -Filter "Name='unrealcanvas-server.exe'" |
     Select-Object -ExpandProperty CommandLine
   ```

   Note also `--viewport-port 58782`, which is not 58782 either.

**Cause:** In both cases the port in a command line was treated as a fact about the
listener. It is not: `--mcp-port` is a **request**, and 8000 is a **default**, not a
reservation.

**Fix:** Read the sockets and map the owning PID back to a process. One command answers
both:

```powershell
netstat -ano -p TCP | Select-String "LISTENING" |
  Select-String ":8000|:5878|:8010"
```

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen |
  ForEach-Object { Get-CimInstance Win32_Process -Filter "ProcessId=$($_.OwningProcess)" } |
  Select-Object Name, ProcessId, CommandLine
```

Then confirm the *project* the server is serving, from the `initialize` reply's
`_meta."com.epicgames.unrealengine/instance".projectFile` — and compare it against the
`.uproject` in the editor's own command line. Full sequence:
`.vault/workflows/2026-11-15-identify-which-unreal-mcp-answered.md`.

**Applies when:** an MCP connection is about to be trusted with a write; a second editor
is launched; a tool's result does not match the project being worked on; or any port for
the canvas bridge, the viewport stream, or the editor's MCP server is assumed rather than
read.
