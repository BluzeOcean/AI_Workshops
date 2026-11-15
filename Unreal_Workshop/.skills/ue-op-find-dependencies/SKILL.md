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
through hard package references, transitively. Soft object paths are invisible to the
tools — sweep the `.uasset` bytes for those (ue-op-relocate-assets step 7).

This is the step that decides whether a set is "minimal". Guessing from folder
names is wrong — a Fab character material pulls in shared material layers,
their textures, and sometimes a texture from a *skin* folder.

## Procedure

`GetDependencies` is **one hop** — it returns the assets a package directly imports and
nothing beyond them. Verified on this build: `BP_Band` lists 2 direct dependencies, and the
4 dependencies of `BP_HoundTroop` (one of those 2) do not appear in that list. The closure
is the fixed point of iterating the call until the set stops growing, which is what step 2
does — one call is never the answer.

### 1. Get the universe of assets that exist

One call gives you every `/Game/` asset, which you need to avoid recursing
into paths that do not exist:

```powershell
python ...\mcp_call.py call EditorToolset.AssetToolset FindAssets '{"filter":{"folderPath":"/Game","bRecursive":true,"maxResults":0}}'
```

`"maxResults": 0` is not optional: the filter caps at 100 by default, which truncates
the universe and turns every asset past the cap into a false "missing" entry.

### 2. Walk the graph

The loop must run **inside** the editor — that is this skill's batched step. Pass the
Python block below as the `content` of one `execute_python` call. The namespace does
**not** survive between calls (`globals()` starts empty each time), so steps 2–4 below are
one script, appended in order, not three separate calls.

```powershell
python ...\mcp_call.py call editor_toolset.toolsets.python_scripting.PythonScriptingTools execute_python `
  '{"script":{"content":"<the Python block below>","language":"Python"}}'
```

```python
import json

roots = ["/Game/Jam/Characters/BP_Band.BP_Band"]

universe = set(await call_tool("EditorToolset.AssetToolset.FindAssets",
                               filter={"folderPath": "/Game", "bRecursive": True, "maxResults": 0}))

seen, missing, stack = set(), [], list(roots)
while stack:
    p = stack.pop()
    if p in seen:
        continue
    seen.add(p)
    if p not in universe:
        missing.append(p)      # dangling reference - report it
        continue
    for d in await call_tool("EditorToolset.AssetToolset.GetDependencies", assetPath=p) or []:
        if d.startswith("/Game/") and d not in seen:
            stack.append(d)

json.dumps({"closure": len(seen), "missing": missing})
```

`seen` is the closure. `missing` holds references to assets that do not
exist — usually Fab content referencing a sibling hero that was not shipped.

The count is not stable across a session: the same walk over `BP_Band` returned 18 assets
before those packages had been loaded and 19 afterwards, because registry dependency data
fills in as packages load. Re-run rather than reusing an old number.

### 3. Report it, grouped by source folder

Grouping by the source folder is what makes the closure actionable — it shows
at a glance how much of the result is shared library versus hero-specific.
Bucket on the two folder levels under `/Game`, or split on a hero/shared
boundary when the source is laid out that way:

```python
buckets = {}
for g in sorted(x for x in seen if x.startswith("/Game/")):
    key = "|".join(g.split("/")[2:4])        # /Game/<A>/<B>/... -> A|B
    buckets[key] = buckets.get(key, 0) + 1
json.dumps(dict(sorted(buckets.items(), key=lambda kv: (-kv[1], kv[0]))), indent=1)
```

### 4. Persist the result

Write the closure to `Saved/` so later scripts read it back instead of you
carrying hundreds of paths through context:

```python
out = "D:/UE/<project>/Saved/ue_asset_manifest.json"
open(out, "w").write(json.dumps({"closure": sorted(seen), "missing": sorted(missing)}, indent=1))
json.dumps({"wrote": out, "assets": len(seen), "missing": len(missing)})
```

The editor's Python writes the file itself — `AssetToolset` has no `write_file` /
`read_file` tool. Read it back with `json.load(open(out))` in the next script, or
`Get-Content` in the shell.

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `ToolsetToolInvocationError: Asset or folder does not exist: /Game/...` | `GetDependencies` was called on a path that is not in the registry | pre-filter with the `universe` set from step 1 |
| An exception killed the walk | a bad path reached the stack | the error class is `ToolsetToolInvocationError` and `try/except` around `call_tool` *does* catch it in this build — but pre-filtering is cheaper than handling |
| A dependency list is empty for an asset that clearly has references | `GetDependencies` reports hard package imports, one hop, and some assets resolve refs at load time | `BP_MechPawn` returns `[]` (still `[]` after `LoadAsset`) while `BP_Band` returns 2 — come at it from the other side with `GetReferencers`, or sweep the `.uasset` bytes (ue-op-relocate-assets step 7) |
| A dependency list looks too small | you expected the closure from one call | iterate until the set stops growing (step 2): 2 direct deps → 19 assets on `BP_Band` |
| Closure is far bigger than expected | shared material layers pull in their own textures | group by folder before deciding what to keep |
| The walk takes minutes | one tool call per asset, all inside one script | it is already one `execute_python` call, so there is no per-asset MCP round trip; ~400 assets ≈ 2–4 min |
| An array argument | the old "outer `call_tool` mangles arrays into `{"item": [...]}`, use `execute_tool_script`" note is dead | pass a JSON array — `ValidateAssets(assetPaths=[...])` received both paths and returned `numChecked: 2`; `execute_tool_script` does not exist in this build |

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
