#!/usr/bin/env python3
"""
Minimal MCP (Streamable HTTP) client for talking to the Unreal Editor's
built-in ModelContextProtocol server.

Usage:
    python mcp_call.py list_toolsets
    python mcp_call.py describe_toolset EditorToolset.EditorAppToolset
    python mcp_call.py call <toolset> <tool_name> ['{"arg":"value"}']
    python mcp_call.py meta <meta_tool_name> ['{"arg":"value"}']
    python mcp_call.py raw '{"jsonrpc":"2.0","id":99,"method":"tools/list"}'

The server is Epic's engine plugin; it requires:
  - Accept: application/json, text/event-stream
  - the Mcp-Session-Id header returned by initialize on every later call
  - a notifications/initialized handshake before tools/list
"""
import json
import sys
import urllib.request

DEFAULT_URL = "http://127.0.0.1:8000/mcp"


class MCPClient:
    def __init__(self, url=DEFAULT_URL):
        self.url = url
        self.session_id = None
        self._rpc_id = 0

    def _post(self, payload):
        self._rpc_id += 1
        body = dict(payload)
        body.setdefault("jsonrpc", "2.0")
        body.setdefault("id", self._rpc_id)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        req = urllib.request.Request(
            self.url, data=json.dumps(body).encode(), headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid
            raw = resp.read().decode("utf-8", "replace")

        if not raw.strip():
            return None
        # Server may answer as application/json or as an SSE data: frame.
        if raw.lstrip().startswith("{"):
            return json.loads(raw)
        for line in raw.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        return json.loads(raw)

    def initialize(self):
        result = self._post({
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "mcp_call.py", "version": "1.0"},
            },
        })
        self._post({"method": "notifications/initialized"})
        return result

    def call(self, method, params=None):
        return self._post({"method": method, "params": params or {}})

    def tools(self):
        return self.call("tools/list")

    def tool(self, name, arguments=None):
        return self.call("tools/call", {"name": name, "arguments": arguments or {}})

    def call_tool(self, toolset_name, tool_name, arguments=None):
        """Dispatch through the `call_tool` meta-tool.

        With bEnableToolSearch=True (the default) the server registers only the
        three meta-tools (list_toolsets / describe_toolset / call_tool). The
        individual toolset tools are NOT directly callable by name -- going
        straight to tools/call with a toolset-qualified name returns HTTP 400.
        """
        return self.tool("call_tool", {
            "toolset_name": toolset_name,
            "tool_name": tool_name,
            "arguments": arguments or {},
        })


def as_text(result):
    """Pull the text blocks out of an MCP tool result."""
    if result is None:
        return ""
    res = result.get("result", result)
    if isinstance(res, dict) and "content" in res:
        return "\n".join(
            c.get("text", "") for c in res["content"] if c.get("type") == "text"
        )
    return json.dumps(res, indent=2)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    client = MCPClient()
    client.initialize()
    cmd = argv[0]

    if cmd == "raw":
        print(json.dumps(client.call(json.loads(argv[1]).get("method"),
                                     json.loads(argv[1]).get("params")),
                         indent=2))
    elif cmd == "list_toolsets":
        print(as_text(client.tool("list_toolsets")))
    elif cmd == "describe_toolset":
        print(as_text(client.tool("describe_toolset", {"toolset_name": argv[1]})))
    elif cmd == "tools":
        for t in client.tools().get("result", {}).get("tools", []):
            print(f"- {t['name']}: {t.get('description', '').splitlines()[0]}")
    elif cmd == "call":
        args = json.loads(argv[3]) if len(argv) > 3 else {}
        print(as_text(client.call_tool(argv[1], argv[2], args)))
    elif cmd == "meta":
        args = json.loads(argv[2]) if len(argv) > 2 else {}
        print(as_text(client.tool(argv[1], args)))
    else:
        print(f"unknown command: {cmd}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
