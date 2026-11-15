---
name: ue-op-mcp-connect
description: Use when establishing or recovering an MCP bridge to an Unreal Engine 5.8+ editor — enables Epic's built-in ModelContextProtocol plugin in a project's .uproject, turns on auto-start, launches the editor, and verifies the HTTP MCP server so Claude Code can drive the editor. Skip for UE versions below 5.8 (the plugin does not exist there), for projects with no .uproject, or when the bridge is already healthy.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# ue-op-mcp-connect — establish a working MCP bridge to an Unreal editor

UE 5.8 ships Epic's own MCP server as an engine plugin:
`Engine/Plugins/Experimental/ModelContextProtocol` (FriendlyName "Unreal MCP",
CreatedBy Epic Games). It serves the Model Context Protocol over **HTTP
(JSON-RPC 2.0)** at `http://127.0.0.1:<port>/mcp` — there is no stdio bridge
and nothing to install.

The server runs **inside the Unreal Editor process**. That single fact drives
the whole workflow: no editor open means no MCP server, and the plugin
existing on disk means nothing until the editor boots.

This skill does the per-project work in a few seconds instead of the ~10
minutes of hunting through plugin source, config files and logs that it
otherwise takes.

---

## The three things that must be true

| # | Requirement | Where it lives |
|---|---|---|
| 1 | Plugin enabled | `<project>/<project>.uproject` → `Plugins[]` |
| 2 | Server auto-starts on editor boot | `Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini` → `[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]` → `bAutoStartServer=True` |
| 3 | Claude Code knows the URL | `claude mcp add` (see Step 4) — machine-wide already, so usually nothing to do |

Requirement 3 is already satisfied machine-wide on this box: a **user-scope**
entry named `unreal-mcp` → `http://127.0.0.1:8000/mcp` lives in
`C:\Users\Bluze\.claude\.claude.json`. Because it is user scope, every
Claude Code session in every directory sees it and connects automatically
when an editor is up. **Do not re-add it per project** — just verify it.

If that entry is ever missing, restore it with:

```bash
claude mcp add --scope user --transport http unreal-mcp http://127.0.0.1:8000/mcp
```

---

## When to apply

- The user says "connect to UE MCP", "set up MCP for Unreal", "the UE MCP
  tools aren't showing up"
- A project was just created or cloned and its `.uproject` has no
  `ModelContextProtocol` entry
- `mcp__unreal-mcp__*` tools are missing from the toolkit, or the server is
  listed as failed/disconnected in `claude mcp list`
- The editor is running but the MCP port is not bound

## When NOT to apply

- The project is **not** UE 5.8+. The plugin does not exist in 5.5/5.6/5.7 —
  `grep ModelContextProtocol` in `Engine/Plugins` will find nothing, and there
  is no supported way to add it to an older engine
- The project has no `.uproject` (not an Unreal project)
- The bridge is already healthy: `claude mcp list` shows `unreal-mcp: ...
  ✔ Connected` and a `tools/list` call returns toolsets — then do nothing
- The user only wants to *use* the MCP tools right now, not set up a new
  project — just call them

**Never modify a project the user did not point you at.** This skill edits
`.uproject` and config files in place. Work on the project in the current
working directory (or the one the user names) and nothing else — some
projects on this machine are disposable.

---

## Workflow

### 1. Read the project state

```bash
ls D:/UE/<project>/*.uproject
```

Then extract the engine version and the plugin list:

```bash
grep -o '"EngineAssociation": *"[^"]*"' D:/UE/<project>/<project>.uproject
grep -c "ModelContextProtocol" D:/UE/<project>/<project>.uproject
```

`EngineAssociation` must be `5.8` or newer. If it is `5.6`/`5.7`, stop and
tell the user — the built-in server does not exist for those engines, and
porting it would mean writing a C++ plugin from scratch.

### 2. Enable the plugin in the .uproject

If `ModelContextProtocol` is absent, add it to the `Plugins` array. Use
`Read` then `Edit` on the `.uproject` — it is small JSON and must stay valid.

```json
"Plugins": [
    {
        "Name": "ModelContextProtocol",
        "Enabled": true
    }
]
```

For a **rich** tool surface, also enable `EditorToolset` (actor/asset/level
/blueprint/material manipulation) and `Terminal` (shell access from the
editor). A project with only the MCP plugin still works but exposes a thin
set of toolsets.

`AllToolsets` enables every toolset in one entry — convenient, but it drags
in ~19 plugins and slows editor startup.

### 3. Turn on auto-start

The setting lives in the **per-user, per-project** ini — note it is *not* in
`Config/Default*.ini`:

```
<project>/Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini
```

Section and keys:

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
ServerUrlPath=/mcp
ServerPortNumber=8000
bAutoStartServer=True
bEnableToolSearch=True
```

If the file does not exist, create it (UE reads it at startup regardless of
who wrote it). If it exists but lacks the section, append the block — do
not rewrite the whole file, it holds unrelated editor preferences.

`bEnableToolSearch=True` (the default) registers **3 meta-tools** instead of
every toolset tool natively:

- `list_toolsets` — list available toolsets
- `describe_toolset` — full tool list + input schemas for one toolset
- `call_tool` — invoke a tool by name

This keeps the tool list small. Set it to `False` only if a client cannot
handle the indirection.

**Alternative to editing the ini:** launch the editor with
`-ModelContextProtocolStartServer` and auto-start is forced on regardless of
the ini (and `bAutoStartServer` can stay `False`). Use this when the ini
approach is unwanted — see Step 5.

### 4. Confirm the Claude Code side

```bash
claude mcp list
```

Expected:

```
unreal-mcp: http://127.0.0.1:8000/mcp (HTTP) - ✔ Connected
```

If it shows `⏸ Pending approval`, the server was added at **project** scope
(a `.mcp.json` file) rather than user scope. Either approve it in the
`/mcp` panel, or remove the project-scoped copy and re-add at user scope:

```bash
claude mcp remove unreal-mcp -s project
claude mcp add --scope user --transport http unreal-mcp http://127.0.0.1:8000/mcp
```

Scope rules worth remembering:

| Scope | Stored in | Approval | Use for |
|---|---|---|---|
| `user` | `~/.claude.json` (top level) | none | **this setup** — works from any directory |
| `local` | `~/.claude.json` → `projects[<dir>]` | none | one project only |
| `project` | `<project>/.mcp.json` | prompt required | checked into version control |

### 5. Launch the editor (only if it is not already running)

```bash
tasklist | grep -i UnrealEditor
```

If an editor is already up, check whether it owns the port:

```bash
netstat -ano | grep ":8000"
```

If the port is bound by that editor, you are done — go to Step 6.

If not, start it with the MCP server forced on:

```bash
"C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe" \
  "D:/UE/<project>/<project>.uproject" -ModelContextProtocolStartServer
```

Run it in the background (`run_in_background: true`) so the session stays
usable. First launch of a project takes a while (shader compile, DDC) —
poll the log rather than sleeping a fixed amount.

### 6. Verify the server before involving Claude Code

Bypass the Claude Code client entirely. This tells you whether the *editor*
is serving, independently of any client config:

```bash
SID=$(curl -s -D - -o /dev/null -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}' \
  | grep -i "Mcp-Session-Id" | tr -d '\r' | awk '{print $2}')

curl -s -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' >/dev/null

curl -s -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

Expect three tools: `list_toolsets`, `describe_toolset`, `call_tool`.

Three details this protocol will bite on:

- The `Accept` header must include **both** `application/json` and
  `text/event-stream`
- The `Mcp-Session-Id` header returned by `initialize` is **required** on
  every subsequent call
- `notifications/initialized` must be sent before `tools/list`, or the
  session is not fully established

### 7. Confirm the tool surface

```bash
curl -s -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SID" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_toolsets","arguments":{}}}'
```

A healthy FabAssets-style project returns ~19 toolsets. A project with only
the MCP plugin enabled returns far fewer — add `EditorToolset` and
`Terminal` to enrich it.

### 8. Get the tools into the live session

Claude Code loads MCP servers at session start. A server registered *after*
the session began is not in the toolkit until:

- `/mcp` is used to reconnect, **or**
- Claude Code is restarted in the project

If `mcp__unreal-mcp__*` tools are missing from the toolkit but
`claude mcp list` says `✔ Connected`, this is the cause — restart the
session.

---

## Multiple editors at once

Every editor defaults to port **8000**, so a second editor cannot bind it.
The second editor's `StartServer` hits `ensure(HttpRouter.IsValid())` and
serves nothing — the harness stays connected to the *first* editor, which is
usually not the one you are looking at.

Give each editor its own port:

```bash
UnrealEditor.exe "D:/UE/<project>/<project>.uproject" \
  -ModelContextProtocolPort=8010 -ModelContextProtocolStartServer
```

Then register that port too:

```bash
claude mcp add --scope user --transport http unreal-mcp-8010 http://127.0.0.1:8010/mcp
```

`FModelContextProtocolServer::StartServer` binds `MainMcpRoute` (POST),
`SseMcpRoute` (GET) and `DeleteMcpRoute` (DELETE) all on the same path.

---

## Console commands inside the editor

Useful from the editor's Output Log console (`~` key) or a Terminal-plugin
command:

| Command | Effect |
|---|---|
| `ModelContextProtocol.StartServer [port]` | start the HTTP server (optional port override) |
| `ModelContextProtocol.StopServer` | stop it |
| `ModelContextProtocol.RefreshTools` | rebuild the tool list, drop cached schemas |
| `ModelContextProtocol.GenerateClientConfig <ClaudeCode\|Cursor\|VSCode\|Gemini\|Codex\|All>` | write client config files |

`GenerateClientConfig ClaudeCode` writes `<project>/.mcp.json` containing:

```json
{
  "mcpServers": {
    "unreal-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

That file is **project scope** and will show as `⏸ Pending approval` — which
is why the user-scope entry registered in Step 4 is the better default here.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `claude mcp list` → `⏸ Pending approval` | server is in `<project>/.mcp.json` (project scope) | approve in `/mcp`, or re-add with `--scope user` |
| `claude mcp list` → connection refused | no editor running, or editor bound a different port | launch editor; check `netstat -ano \| grep :8000` |
| `✔ Connected` but no `mcp__unreal-mcp__*` tools | server registered after session start | `/mcp` or restart Claude Code |
| Editor up, port not bound | `bAutoStartServer=False` in the ini | set it `True`, or launch with `-ModelContextProtocolStartServer` |
| Port 8000 bound by the wrong editor | two editors, both default to 8000 | relaunch one with `-ModelContextProtocolPort=8010` |
| `ensure(HttpRouter.IsValid())` in the log | port already taken | same as above — give it its own port |
| `tools/list` returns nothing useful | `Mcp-Session-Id` missing, or `notifications/initialized` not sent | follow the Step 6 recipe exactly |
| `tools/call` with a toolset-qualified name returns **HTTP 400** | tool search is on, so only the 3 meta-tools are directly callable | dispatch through the `call_tool` meta-tool instead — see below |
| Plugin missing from `.uproject` after enabling | engine is < 5.8 | the built-in server does not exist there |
| Editor slow to open after adding plugins | shaders/DDC compiling on first launch | wait it out; subsequent launches are fast |

### Calling tools: the `call_tool` indirection

With `bEnableToolSearch=True` (the default) the server registers only
`list_toolsets`, `describe_toolset` and `call_tool`. The individual toolset
tools are **not** directly callable — `tools/call` with a name like
`EditorToolset.EditorAppToolset.GetOpenAssets` returns HTTP 400.

Go through the meta-tool instead:

```json
{
  "method": "tools/call",
  "params": {
    "name": "call_tool",
    "arguments": {
      "toolset_name": "EditorToolset.EditorAppToolset",
      "tool_name": "GetOpenAssets",
      "arguments": {}
    }
  }
}
```

`tool_name` is the bare name **without** the toolset prefix. Use
`describe_toolset` to get the exact names and input schemas first.

---

## Talking to the server without Claude Code's MCP client

`mcp_call.py` (next to this file) is a dependency-free client for the same
endpoint. Useful when the MCP server is up but the tools are not in the
current session's toolkit yet, or for scripted checks.

```bash
cd V:/04_Projects/Workshops/Unreal_Workshop/.skills/ue-op-mcp-connect

python mcp_call.py list_toolsets
python mcp_call.py describe_toolset EditorToolset.EditorAppToolset
python mcp_call.py call EditorToolset.EditorAppToolset GetOpenAssets
python mcp_call.py call EditorToolset.EditorAppToolset SelectActors '{"names":["Foo"]}'
python mcp_call.py meta list_toolsets
```

It handles the `initialize` → `notifications/initialized` handshake, tracks
the `Mcp-Session-Id` header, and sends the correct `Accept` header.

**Image tools** (`CaptureEditorImage`, `CaptureViewport`, `CaptureAssetImage`)
return a base64 PNG inside a JSON-wrapped text block, not an image content
block. Unwrap it and decode:

```python
import base64, json
payload = json.loads(text_block)          # {"returnValue": {"mimeType": ..., "data": "..."}}
raw = base64.b64decode(payload["returnValue"]["data"])
open("shot.png", "wb").write(raw)
```

---

## Useful facts

- Default port **8000**, default path **/mcp**, default server name
  `unreal-mcp`
- Protocol versions accepted: `2025-11-25`, `2025-06-18`, `2024-11-05`; the
  server negotiates down to the client's version if it is supported
- Auto-start is **skipped in commandlets** (a cook would race the editor for
  the port); pass `-ModelContextProtocolStartServer` to force it on
- `-StartModelContextProtocolServer` is the deprecated spelling of
  `-ModelContextProtocolStartServer`
- The server binds `127.0.0.1` only — it is not reachable from the network
- The plugin sends analytics through the engine's analytics provider; UE
  warns that data reaching the LLM service is licensed technology under the
  UE EULA (§6(e)) and that using it as training data is the user's
  responsibility
- Settings class: `UModelContextProtocolSettings`
  (`config=EditorPerProjectUserSettings`), defined in
  `ModelContextProtocolEngine/Public/ModelContextProtocolSettings.h`

## The UE operation skills (`ue-op-*`)

Once the bridge is up, the actual work happens in the **`ue-op-*` skills**.
They live in `V:\04_Projects\Workshops\Unreal_Workshop\.skills\` — deliberately **outside**
`~/.claude/skills`, and registered **project-scoped** so that agents working
in non-UE projects never load them.

**Read the matching skill's `SKILL.md` directly from disk** when the task
calls for it — that is the intended access path:

| Skill | Do this when |
|---|---|
| `ue-op-inspect-blueprint` | read a blueprint's graphs, components, variables, parent class |
| `ue-op-setup-input` | bind keys so a character responds (legacy axis/action mappings) |
| `ue-op-create-blueprint` | make a new blueprint — a child of an existing one, or from a base class |
| `ue-op-add-component` | add/configure a component on a blueprint (spring arm, camera, mesh) |
| `ue-op-wire-graph` | create, connect or delete blueprint graph nodes |
| `ue-op-fix-compile-error` | a blueprint will not compile, or the editor is wedged behind the modal |
| `ue-op-setup-game-mode` | make a level spawn a particular pawn |
| `ue-op-test-pie` | run PIE, inject input, verify runtime state |
| `ue-op-find-assets` | locate project/engine assets, including inside `.uasset` binaries |
| `ue-op-find-dependencies` | compute an asset's transitive dependency closure |
| `ue-op-clone-assets` | copy a curated asset set into a structured export folder for migration |
| `ue-op-relocate-assets` | move a curated asset set so the folder is self-contained for migration |
| `ue-op-capture-editor` | screenshot the editor or viewport through MCP |
| `ue-op-setup-playable-character` | make a character controllable end to end (composite) |
| `ue-op-build-web` | cook, package and stage a UE 5.9 Wasm/WebGPU web build |
| `ue-op-verify-web` | prove a staged web build boots in a real browser |
| `ue-op-ship-web` | zip a verified stage for hosting (launcher, COOP/COEP, itch.io) |
| `ue-op-bake-mesh-partition` | get Mesh Terrain geometry into a cooked build |
| `ue-op-editor-script` | drive the live editor with Python when its MCP tools fall short |
| `ue-op-extract-to-skill` | capture a finished operation as a new/reusable skill |

Base path: `V:\04_Projects\Workshops\Unreal_Workshop\.skills\<name>\SKILL.md`

To make them callable as `/ue-op-<name>` inside a UE project, junction them
project-scoped:

```bash
powershell -NoProfile -Command "New-Item -ItemType Junction -Path 'D:\UE\<Project>\.claude\skills\<name>' -Target 'V:\04_Projects\Workshops\Unreal_Workshop\.skills\<name>'"
```

`D:\UE\FabAssets\.claude\skills\` is already wired for all twelve.
`D:\UE\EpicJam2026\.claude\skills\` is wired for the web-build set
(`ue-op-build-web`, `ue-op-verify-web`, `ue-op-ship-web`,
`ue-op-bake-mesh-partition`).

## Related

- [[gd-mcp-connect]] — the Godot equivalent of this skill; same shape,
  different transport (stdio bridge over TCP instead of HTTP)
- The **`ue-op-*` skills** above are where the actual work happens. This skill
  is only the bridge; those cover key bindings, blueprint node ids, adding
  components, compile-error recovery and the PIE sharp edges.
- `mcp_call.py` (next to this file) — a dependency-free client for the same
  endpoint, for when the MCP server is up but the tools are not in the
  current session's toolkit yet, or for scripted checks.
