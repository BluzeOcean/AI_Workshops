---
name: ue-op-mcp-diagnose
description: Use when an agent needs to reach a running Unreal editor over MCP — to check the bridge is alive, to tell Epic's built-in plugin from the Unreal Canvas bridge, to register an MCP client against the right port, or to start a second editor without colliding on port 8000. Skip when no editor is running (use commandlets instead) or when the engine is older than 5.8 (no MCP plugin exists).
---

# ue-op-mcp-diagnose — reach the Unreal editor over MCP, and know which server answered

Unreal exposes **two** MCP servers, they look alike, and confusing them is the most
expensive mistake on this machine. This skill is the procedure for getting a connection
*and* for proving which server it is.

For the broader connect-and-use workflow (toolsets, `call_tool` dispatch, image payloads)
see the sibling `V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\SKILL.md`. This skill covers the
part that is specific to **this** machine: two engines, three installs, one registry that
lies, and two servers.

---

## Before you start — what you actually need

| You need | Then use |
|---|---|
| the editor alive, project identified | this skill, steps 1–4 |
| to call a tool | this skill, step 4, then the sibling `ue-op-mcp-connect` skill |
| the editor **not** running | a commandlet — `AGENTS.md` §4d. There is no bridge without an editor. |
| an engine older than 5.8 | a commandlet. The MCP plugin does not exist before 5.8. |

---

## Step 1 — resolve the engine (do not read the registry)

The launcher registry is **not** a list of what is installed: UE 5.9 is on disk and running
but absent from `HKLM\SOFTWARE\EpicGames\Unreal Engine\`, and four versions it names are
not on disk. Scan instead:

```powershell
Get-ChildItem "C:\Program Files\Epic Games\UE_*\Engine\Build\Build.version" |
  ForEach-Object {
    $v = Get-Content $_.FullName -Raw | ConvertFrom-Json
    [pscustomobject]@{ Engine = $_.Directory.Parent.Parent.FullName
                       Version = [version]"$($v.MajorVersion).$($v.MinorVersion).$($v.PatchVersion)"
                       CL = $v.Changelist }
  } | Sort-Object Version -Descending | Select-Object -First 1
```

Take the first row. Compare on the version tuple — `5.9` > `5.8`, and `5.9.1` beats `5.9`.

**If the version is below 5.8, stop.** The MCP plugin ships with 5.8 and newer only.

---

## Step 2 — find the editor and the project it has open

```powershell
Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" |
  Select-Object ProcessId, CommandLine
```

The `.uproject` in the command line is the **authority** on which project is open — not
the MCP reply, not a remembered path.

No output means no editor: use a commandlet (`AGENTS.md` §4d).

---

## Step 3 — find who owns the port

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen |
  ForEach-Object { Get-CimInstance Win32_Process -Filter "ProcessId=$($_.OwningProcess)" } |
  Select-Object Name, ProcessId, CommandLine
```

`UnrealEditor.exe` owning 8000 means Epic's plugin is serving. **Anything else** — the
Unreal Canvas server, a squatting process — means you are not talking to the editor's
plugin.

For the full picture (the canvas server binds ports of its own):

```powershell
netstat -ano -p TCP | Select-String "LISTENING" | Select-String ":8000|:5878|:8010"
```

---

## Step 4 — identify the server and the project

```bash
curl -s -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}'
```

Read two things from the reply:

| Field | Reading |
|---|---|
| `_meta."com.epicgames.unrealengine/instance".projectFile` | the project that answered — **compare it against step 2** |
| `serverInfo.name` | `unreal-mcp` → Epic's plugin · `merlin` → the Unreal Canvas bridge |

If the project does not match, you are on the **wrong editor**. Stop and start the right one
with its own port (step 6).

### The three protocol details that bite

- The `Accept` header must carry **both** `application/json` and `text/event-stream`.
- The `Mcp-Session-Id` header returned by `initialize` is **required** on every later call.
- `notifications/initialized` must be sent **before** `tools/list`.

---

## Step 5 — register a client (only if none is registered)

Check first:

```bash
claude mcp list          # shows the server, its URL, and whether it is connected
```

If the Unreal entry is missing, add it at **user scope** — user scope is visible from every
directory and needs no approval:

```bash
claude mcp add --scope user --transport http unreal-mcp http://127.0.0.1:8000/mcp
```

The server definition to register is in `references/client-config.json`. It is exactly what
the plugin's own console command writes:

```
ModelContextProtocol.GenerateClientConfig ClaudeCode
```

> **Never register this at project scope inside a project that already has the user-scope
> entry.** A duplicate shows as "⏸ Pending approval" and shadows the working one.

---

## Step 6 — a second editor needs its own port

Every editor defaults to **8000**. A second one cannot bind it: its `StartServer` hits
`ensure(HttpRouter.IsValid())` and serves nothing, while the client stays happily connected
to the **first** editor — healthy, answering promptly, pointed at entirely different
content.

```powershell
UnrealEditor.exe "D:\UE\<Project>\<Project>.uproject" `
  -ModelContextProtocolPort=8010 -ModelContextProtocolStartServer
```

Then register that port as a second client entry.

---

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| No `mcp__unreal-mcp__*` tools, but `claude mcp list` says connected | the server was registered after the session started | `/mcp` to reconnect, or restart Claude Code. The tool list **freezes at session start** |
| Connected, but results describe the wrong project | a second editor holds 8000 | give it its own port (step 6) |
| `tools/list` returns nothing useful | missing `Mcp-Session-Id`, or `notifications/initialized` not sent | do the handshake in order |
| `tools/call` on a qualified name returns **HTTP 400** | tool search is on, so only `list_toolsets` / `describe_toolset` / `call_tool` are directly callable | dispatch through `call_tool`, with `tool_name` as the **bare** name, no toolset prefix |
| Canvas tools are listed but do nothing | no canvas frontend is connected — the server says so in its `frontendBuild` note | open the Unreal Canvas panel, or use a different surface |
| `Toolset 'editor_toolset.BlueprintTools' not found` | `editor_toolset` is **not registered in this build** | use the editor's own Python through the console-command bridge; Blueprint *graph* authoring has no fallback — say so |
| The resolved engine is 5.8 but the editor is 5.9 | the resolver read the launcher registry | scan `Build.version` (step 1) |
| The server is on a port you did not expect | `--mcp-port` is a **request**, not a reservation | read the sockets (step 3) |
| `ensure(HttpRouter.IsValid())` in the editor log | the port was already taken | give the editor its own port (step 6) |

---

## Related

- `AGENTS.md` §4b and §4c — the two surfaces, in full
- `.vault/lessons/2026-11-15-verify-the-port-and-its-owner-before-trusting-an-mcp-connection.md`
- `.vault/lessons/2026-11-15-the-launcher-registry-does-not-list-ue-5-9.md`
- `.vault/lessons/2026-11-15-ue-5-5-has-no-mcp-plugin.md`
- `.vault/workflows/2026-11-15-identify-which-unreal-mcp-answered.md` — the same sequence as a workflow
- `V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\SKILL.md` — the fuller connect workflow
