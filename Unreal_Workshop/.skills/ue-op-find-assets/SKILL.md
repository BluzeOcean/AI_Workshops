---
name: ue-op-find-assets
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to locate project or engine assets — a blueprint, a mesh, an input action, an engine template — including checking what is inside a .uasset binary. Skip if no UE MCP connection, or if the exact asset path is already known.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - mcp__unreal-mcp__call_tool
---

# ue-op-find-assets — locate assets, including inside binaries

## When to apply

- You need the content path of an asset to pass to an MCP tool
- You need to know whether a project already has something (an input setup, a
  game mode, a reusable template) before building it again
- You need to see the skeleton/socket/enum names inside a `.uasset`

## When NOT to apply

- The path is already known → use it directly
- The asset is in a project that is not open → filesystem search only

---

## Procedure

### 1. Search the project on disk

```bash
find "D:/UE/<project>/Content" -iname "IMC_*" -o -iname "IA_*" -o -iname "*GameMode*"
```

`-iname` is case-insensitive; use `-iname` for asset names, since UE keeps
the original case but searches ignore it.

### 2. Search the engine

The engine ships reusable content worth reusing instead of authoring:

```bash
# Enhanced Input assets + the canonical third-person template
find "C:/Program Files/Epic Games/UE_5.8/Templates" -iname "IA_*.uasset" -o -iname "IMC_*.uasset"

# engine plugins that provide toolsets
grep -rl "ToolsetRegistry" "C:/Program Files/Epic Games/UE_5.8/Engine/Plugins" --include="*.uplugin"
```

The `Templates/TemplateResources/High/Input/` folder holds Epic's canonical
input assets — useful reference for what an Enhanced Input setup should
contain. The layout is:

```
TemplateResources/High/Input/Content/IMC_Default.uasset
TemplateResources/High/Input/Content/IMC_MouseLook.uasset
TemplateResources/High/Input/Content/Actions/IA_Jump.uasset
TemplateResources/High/Input/Content/Actions/IA_Look.uasset
TemplateResources/High/Input/Content/Actions/IA_MouseLook.uasset
TemplateResources/High/Input/Content/Actions/IA_Move.uasset
```

The `IA_*` assets are one level deeper, in `Content/Actions/`; only the
`IMC_*` sit directly in `Content/`. The base third-person template is at
`Templates/TP_ThirdPerson/` (with `TP_ThirdPersonBP/` alongside).

### 3. Inspect a `.uasset` binary without opening the editor

`.uasset` files keep their name table as plain strings, so a quick scan
reveals enums, socket names, bone names and referenced paths:

```bash
python - <<'PY'
import re
b = open("Content/Path/To/Asset.uasset",'rb').read()
ss = [s.decode('ascii') for s in re.findall(rb'[ -~]{3,}', b)]
seen = []
for s in ss:
    if s not in seen: seen.append(s)
print([t for t in seen if any(k in t for k in ('Spine','Socket','EInputActionValueType'))])
PY
```

This is how you discover that a mesh has a `spine_03` bone, or that an
`InputAction` is `EInputActionValueType::Axis2D` — without spending a round
trip on the editor.

### 4. Search the project through the editor

```python
import json

def T(tool, **kw):
    """Call a toolset tool from inside execute_tool_script and unwrap its
    {'returnValue': ...} envelope.  Tool names are fully qualified, e.g.
    'editor_toolset.toolsets.asset.AssetTools.load_asset'."""
    r = execute_tool(tool, json.dumps(kw))
    if isinstance(r, dict) and "returnValue" in r:
        return r["returnValue"]
    return r

T("editor_toolset.toolsets.asset.AssetTools.find_assets", folder_path="/Game", name="", recursive=True)
T("editor_toolset.toolsets.asset.AssetTools.list_folders", root_path="/Game", recursive=False)
```

`find_assets` takes a **folder path and a name filter**, not a glob. Use
`name="Murdock"` with `folder_path="/Game"`.

### 5. Check the log for what the editor actually loaded

```bash
grep -iE "Mounting Engine plugin|LogModelContextProtocol: Tool search enabled" \
  "D:/UE/<project>/Saved/Logs/<Project>.log" | tail -20
```

`Tool search enabled: registered 3 meta-tools (19 toolsets discoverable via
list_toolsets)` tells you exactly how many toolsets the project has.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `find_assets` returns nothing for a known asset | wrong folder root | use `/Game`, not the filesystem path |
| `find_assets` name filter misses it | the filter is case-sensitive in practice | use `name=""` and filter yourself |
| `AssetTools.get_asset_class` needed | to check what a path really is | `get_asset_class(asset_path=...)` |
| `save_assets` says the asset does not exist | PIE is running | stop PIE first |
| A referenced asset resolves oddly in a string dump | strings include noise | filter for the specific prefix you expect |

**Cross-project reuse:** copying a `.uasset` file between projects works for
self-contained assets (InputAction, InputMappingContext) as long as the
engine version matches. Assets that reference other packages need their
dependencies copied too, and internal references to moved packages must be
repointed.

**A `.uasset` in `Saved/Autosaves/` is not a real asset** — it is an
autosave of an unsaved blueprint. The asset may not exist on disk at all.

**`Content/__ExternalActors__/`** holds World Partition actor data, not
ordinary assets; ignore it in searches unless you are chasing a specific
actor.

## Output contract

A confirmed content path (`/Game/...`) for each asset, plus — where it
mattered — the names found inside the binary.

## Related

- `ue-op-inspect-blueprint` — once the path is known
- `ue-op-setup-input` — when looking for reusable input assets
