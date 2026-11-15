---
name: ue-op-find-dependencies
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to compute what an asset actually drags in — the transitive dependency closure of one or more root assets, so a curated set can be sized, trimmed or audited before copying or migrating. Skip if no UE MCP connection, or if the task is only to search for assets by name/type/folder (use ue-op-find-assets).
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

# ue-op-find-dependencies — compute an asset's transitive dependency closure

## What it answers

> "If I copy or migrate this asset, what comes with it?"

The answer is the **closure**: the root plus every `/Game/` asset reachable
through hard or soft references, transitively.

This is the step that decides whether a set is "minimal". Guessing from folder
names is wrong — a Fab character material pulls in shared material layers,
their textures, and sometimes a texture from a *skin* folder.

## Procedure

### 1. Get the universe of assets that exist

One call gives you every `/Game/` asset, which you need to avoid recursing
into paths that do not exist:

```python
universe = set(T("editor_toolset.toolsets.asset.AssetTools.find_assets",
                 folder_path="/Game/", name="", recursive=True))
```

### 2. Walk the graph

```python
def deps(p):
    try:
        return T("editor_toolset.toolsets.asset.AssetTools.get_dependencies",
                 asset_path=p) or []
    except Exception:
        return []

seen, missing, stack = set(), [], list(roots)
while stack:
    p = stack.pop()
    if p in seen:
        continue
    seen.add(p)
    if p not in universe:
        missing.append(p)      # dangling reference - report it
        continue
    for d in deps(p):
        if d.startswith("/Game/") and d not in seen:
            stack.append(d)
```

`seen` is the closure. `missing` holds references to assets that do not
exist — usually Fab content referencing a sibling hero that was not shipped.

### 3. Report it, grouped by source folder

Grouping by the source folder is what makes the closure actionable — it shows
at a glance how much of the result is shared library versus hero-specific.

```python
buckets = {}
for g in sorted(x for x in seen if x.startswith("/Game/")):
    if g.startswith("/Game/ParagonMurdock/Characters/Global/"):
        k = "Shared|" + g.split("/Global/", 1)[1].rsplit("/", 1)[0]
    elif g.startswith("/Game/ParagonMurdock/Characters/Heroes/Murdock/"):
        k = "Murdock|" + g.split("/Murdock/", 1)[1].rsplit("/", 1)[0]
    else:
        k = "OTHER|" + g
    buckets[k] = buckets.get(k, 0) + 1
```

### 4. Persist the result

Write the closure to `Saved/` so later scripts read it back instead of you
carrying hundreds of paths through context:

```python
T("editor_toolset.toolsets.asset.AssetTools.write_file",
  file_path="D:/UE/<project>/Saved/ue_asset_manifest.json",
  content=json.dumps({"closure": sorted(seen), "missing": sorted(missing)}, indent=1))
```

Read it back with `AssetTools.read_file` on the same path.

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Script dies with "Asset does not exist: /Game/..." | `get_dependencies` was called on an asset that does not exist | pre-filter with the `universe` set from step 1 |
| The exception cannot be caught | tool errors propagate out of `execute_tool` | do not rely on try/except — pre-filter |
| A dependency list looks too small | `get_dependencies` on a never-loaded asset returns only partially resolved refs | `load_asset` the root first, then query |
| Closure is far bigger than expected | shared material layers pull in their own textures | group by folder before deciding what to keep |
| The walk takes minutes | one tool round-trip per asset | run it as a background task; ~400 assets ≈ 2–4 min |
| `asset_paths=[...]` is rejected | the outer `call_tool` mangles array arguments into `{"item": [...]}` | call array-taking tools through `execute_tool_script` with `json.dumps` |

**Missing dependencies are normal in Fab content.** A Paragon montage
referencing `/Game/ParagonShinbi/.../LevelStart` is a dangling reference in the
*original*, not something you broke. Report it; do not try to fix it.

## Output contract

- the closure, grouped by source folder, with asset counts
- the list of dangling references
- the on-disk size of the closure (sum the `.uasset` sizes under `Content/`)
- the manifest written to `Saved/`

## Related

- `ue-op-clone-assets` — clone a closure into a structured export tree
- `ue-op-find-assets` — search the registry by name/type/folder
