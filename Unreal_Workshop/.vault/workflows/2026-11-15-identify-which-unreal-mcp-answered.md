# Workflow — establish which Unreal MCP answered, and which editor it is

**Recorded:** 2026-11-15. **Run this before any write through MCP.**

Two MCP servers can be live at once, and every editor defaults to port 8000. This
sequence establishes the facts before anything is called.

## 1. Which editors are running, and on what?

```powershell
Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" |
  Select-Object ProcessId, CommandLine
```

The command line names the `.uproject`. **This is the authority on which project is
open** — not the MCP reply, not a remembered path.

## 2. Who owns the port?

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen |
  ForEach-Object { Get-CimInstance Win32_Process -Filter "ProcessId=$($_.OwningProcess)" } |
  Select-Object Name, ProcessId, CommandLine
```

`UnrealEditor.exe` owning it means Epic's plugin. Anything else means something else is
squatting — find out what before calling.

For the full socket map of the Unreal processes:

```powershell
netstat -ano -p TCP | Select-String "LISTENING" |
  Select-String ":8000|:5878|:8010"
```

## 3. Ask the server who it is

```bash
curl -s -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}'
```

Read two things in the reply:

- `_meta."com.epicgames.unrealengine/instance".projectFile` — **the project that
  answered**. Compare it against step 1. A mismatch means you are on the wrong editor.
- `serverInfo.name` — `unreal-mcp` means Epic's plugin; `merlin` means the canvas server.

## 4. If it is the canvas server, check its frontend

```json
"frontendBuild": { "known": true|false, "why": "..." }
```

`known: false` with *"No Unreal Canvas frontend is connected"* means the canvas tools are
listed but will not execute. Open the Unreal Canvas panel, or use a different surface.

## 5. Establish the session, if you are going to call tools

```bash
SID=$(curl -s -D - -o /dev/null -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}' \
  | grep -i "Mcp-Session-Id" | tr -d '\r' | awk '{print $2}')

curl -s -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' >/dev/null
```

Every later call needs the `Mcp-Session-Id` header. `notifications/initialized` must
precede `tools/list`.

**Or skip all of this** — `D:\UE\.ue-op-skillset\ue-mcp-connect\mcp_call.py` does the
handshake, tracks the session id and sends the right headers:

```bash
cd D:/UE/.ue-op-skillset/ue-mcp-connect
python mcp_call.py list_toolsets
python mcp_call.py call EditorToolset.EditorAppToolset GetOpenAssets
```

## Notes

- The `Accept` header must carry **both** `application/json` and `text/event-stream`.
- With tool search on (the default), the only directly callable tools are
  `list_toolsets`, `describe_toolset`, `call_tool`. Dispatch through `call_tool` with a
  **bare** `tool_name`.
