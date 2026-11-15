---
name: ue-op-create-blueprint
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to create a new blueprint asset — a child of an existing blueprint, or a fresh one from a base class, in a chosen folder. Skip if no UE MCP connection, or if the asset is a plain data asset rather than a blueprint.
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

# ue-op-create-blueprint — make a new blueprint asset

## When to apply

- You need a variant of an existing character/actor without touching the
  original (the "keep the source asset clean, put new work in a Lab folder"
  pattern)
- You need a GameMode, PlayerController or other actor blueprint from scratch

## When NOT to apply

- The asset should be a plain data asset (InputAction, DataTable, …) —
  `create` only makes Blueprints
- The blueprint exists already → `ue-op-inspect-blueprint`

---

## Procedure

### 1. Resolve the parent class

`create` takes a **class**, not an asset. For a blueprint parent that is the
*generated* class:

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

bp   = T("editor_toolset.toolsets.asset.AssetTools.load_asset", asset_path="/Game/Existing/ExistingBlueprint")
cls  = T("editor_toolset.toolsets.object.ObjectTools.get_class", instance=bp)      # -> refPath of the _C class
```

For a native base class, pass the script path directly:
`"/Script/Engine.GameModeBase"`.

### 2. Create the folder and the blueprint

```python
T("editor_toolset.toolsets.asset.AssetTools.create_folder", folder_path="/Game/Lab/Characters")   # may already exist

newbp = T("editor_toolset.toolsets.blueprint.BlueprintTools.create",
          folder_path="/Game/Lab/Characters",
          asset_name="BP_LabTPSCharacter",
          asset_type=cls)
```

`create_folder` raising "already exists" is harmless — `create` makes the
directory anyway.

`create` asserts that the class can be stored in a Blueprint; it will refuse
non-blueprintable classes (data assets).

### 3. Configure and compile

A new child blueprint's **EventGraph starts empty** — the parent's EventGraph
is a separate graph and both run (parent first). You do not need to copy the
parent's logic; you only add what is new.

```python
T("editor_toolset.toolsets.blueprint.BlueprintTools.compile_blueprint", blueprint=newbp)
```

### 4. Save

```python
T("editor_toolset.toolsets.asset.AssetTools.save_assets", asset_paths=[newbp])
```

**`save_assets` fails with "Asset does not exist" while PIE is running.**
Stop PIE first (see `ue-op-test-pie`).

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `create` raises "cannot be stored in a Blueprint" | the class is a data-asset class | use a different mechanism for data assets |
| `save_assets` → "Asset does not exist" | PIE is running | stop PIE, then save |
| Child blueprint's EventGraph is empty | expected — the parent's graph is separate | add only the new logic |
| `get_class` returns the asset, not a class | use `ObjectTools.get_class`, not the raw asset | it returns `..._C` |
| Blueprint appears but has no components | child inherits them; `get_components` on the CDO shows them | nothing to do |

**Always create under a dedicated folder** (e.g. `/Game/Lab/…`) when the parent
is a marketplace or sample asset. It keeps the source pristine, makes the
diff reviewable, and makes it trivial to delete the experiment later.

**Naming convention:** `BP_<Purpose>` for the asset name, matching the
project's existing style.

## Output contract

- The blueprint exists at the requested path
- It compiles
- It is saved to disk
- `get_components` on its CDO lists the inherited components

## Related

- `ue-op-inspect-blueprint` — inspect the parent before copying it
- `ue-op-add-component` — add the components the new blueprint needs
- `ue-op-wire-graph` — add the new logic
