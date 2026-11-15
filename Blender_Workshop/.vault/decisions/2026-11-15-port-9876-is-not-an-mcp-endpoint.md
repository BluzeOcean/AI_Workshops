# Port 9876 is not an MCP endpoint — `.mcp.json` stays a reserved example

**Date:** 2026-11-15
**Status:** active
**Decision:** The live Blender instance listens on `127.0.0.1:9876` and speaks the **DSH
Blender Bridge's own JSON command protocol**, not MCP/JSON-RPC. Therefore:

- **`.mcp.json` is not created yet.** It ships as `.mcp.json.example`, a documented
  reserved slot. Shipping a real `.mcp.json` pointed at a non-MCP port would make every
  MCP client fail to connect at startup, for no benefit.
- When the MCP bridge is built, it points at a **free** port — 9876 is taken — and
  `.mcp.json` is created from the example.

**Verified on 2026-11-15** by probing the running instance:

| Probe | Result |
|---|---|
| `{"type":"ping"}` | `{"status":"success","result":{"pong":true}}` |
| `{"type":"get_scene_info"}` | `{"status":"success","result":{...}}` — scene, objects, materials |
| `{"type":"get_object_info","params":{"name":"landing_deck"}}` | `{"status":"success","result":{...}}` |
| `{"type":"execute_code","params":{"code":"import bpy; print(bpy.app.version_string)"}}` | `{"status":"success","result":{"executed":true,"result":"5.3.0\n"}}` |
| `{"type":"bogus_command"}` | `{"status":"error","message":"Unknown command type: 'bogus_command'"}` |

A JSON-RPC `initialize` request against this port does **not** work — the addon answers in
its own vocabulary.

**The real MCP surface** is the official Blender extension installed at
`…\Blender\5.3\extensions\lab_blender_org\mcp\`, runnable as:

```
blender.exe --background <file.blend> --command blender_mcp --port <PORT>
```

It speaks real MCP. Its wire format differs from the DSH bridge's: requests are
null-byte-terminated JSON `{"type":"execute","code":"<python>","strict_json":true}`, the
executed Python sets a `result` dict, and the response is `{"status":"ok","result":{...}}`
with captured `stdout`/`stderr`.

**Reason:** the two surfaces look alike and are not, and the difference is the kind that
produces a confusing "connection refused" or a silent no-op three steps later. Recording
it once, with the actual probe results, is cheaper than rediscovering it.

**Also note:** the official add-on refuses to start unless **Online Access** is enabled in
Blender's Preferences → System → Network.

**Applies when:** writing the MCP bridge; pointing any MCP client at a Blender port; when
a Blender MCP tool call returns nothing and the port looks alive.
