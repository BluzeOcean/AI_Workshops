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

The engine ships reusable content worth reusing instead of authoring. **Resolve the engine
first — never pin a version**, because the templates and the plugin inventory differ
between installs:

```bash
ENGINE=$(find "C:/Program Files/Epic Games" -maxdepth 1 -name "UE_*" -type d | sort -V | tail -1)

# Enhanced Input assets + the canonical third-person template
find "$ENGINE/Templates" -iname "IA_*.uasset" -o -iname "IMC_*.uasset"

# engine plugins that provide toolsets
grep -rl "ToolsetRegistry" "$ENGINE/Engine/Plugins" --include="*.uplugin"
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
keys = ('spine', 'socket', 'einputactionvaluetype')   # lowercase - the dump is case-sensitive
print([t for t in seen if any(k in t.lower() for k in keys)])
PY
```

This is how you discover that a mesh has a `spine_03` bone, or that an
`InputAction` is `EInputActionValueType::Axis2D` — without spending a round
trip on the editor.

### 4. Search the project through the editor

One hop, one tool, one JSON object. `mcp_call.py` (in `ue-op-mcp-connect`) performs the
MCP handshake itself, so the shell is enough:

```powershell
$MCP = "V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py"

# -> ["/Game/Jam/Input/IMC_Jam.IMC_Jam"]
python $MCP call EditorToolset.AssetToolset FindAssets '{"filter":{"folderPath":"/Game/Jam/Input","name":"IMC"}}'

# -> ["/Game/Jam/Audio/", "/Game/Jam/Characters/", ...]   (trailing slash preserved)
python $MCP call EditorToolset.AssetToolset ListFolders '{"rootPath":"/Game/Jam","bRecursive":false}'

# -> "InputMappingContext"   (a class NAME string, not a class object)
python $MCP call EditorToolset.AssetToolset GetAssetClass '{"assetPath":"/Game/Jam/Input/IMC_Jam.IMC_Jam"}'
```

`FindAssets` takes **one filter struct, under the parameter name `filter`** — not keyword
arguments, and not a glob. Its fields are `folderPath`, `name` (a case-insensitive
substring: `"imc"` finds `IMC_Jam`), `assetType` (a class path such as
`/Script/EnhancedInput.InputAction`), `bRecursive`, `maxResults`. **`maxResults`
defaults to 100**, so pass `"maxResults": 0` for "no limit" — otherwise a whole-project
search silently stops at 100 paths. Only assets **saved to disk** are in the registry.

### 5. Check the log for what the editor actually loaded

```bash
grep -iE "Mounting Engine plugin|LogModelContextProtocol: Tool search enabled" \
  "D:/UE/<project>/Saved/Logs/<Project>.log" | tail -20
```

The line is emitted once per toolset while they register, and this build reports **4**
meta-tools, so read the **last** line rather than the first:

```
LogModelContextProtocol: Tool search enabled: registered 4 meta-tools (109 toolsets discoverable via list_toolsets)
```

That number is a snapshot of startup, not a limit on the session — `list_toolsets` against
the live editor returned **115** toolsets. Do not hardcode either count; ask the server.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `FindAssets` returns nothing for a known asset | wrong folder root, or the asset is only in memory | use a content path (`/Game/...`), not a filesystem path; only assets saved to disk are indexed |
| A whole-project search looks truncated | `maxResults` defaults to 100 | pass `"maxResults": 0` for no limit (496 assets in this project, against 100 by default) |
| `FindAssets` name filter misses it | `name` is a case-insensitive substring — the old "case-sensitive in practice" note is wrong | `"imc"` finds `IMC_Jam`; check `folderPath` and that the asset is saved |
| "what is this path really?" | — | `GetAssetClass(assetPath=...)` → `"InputMappingContext"`, a class **name** string |
| A batch save | there is no `save_assets(list)` | `SaveAsset(assetPath)` — one path per call |
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
