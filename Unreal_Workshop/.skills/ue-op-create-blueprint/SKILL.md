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
  `Create` only makes Blueprints
- The blueprint exists already → `ue-op-inspect-blueprint`

---

## Procedure

```powershell
$mcp = "V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py"
```

### 1. Resolve the parent class

`Create` takes a **class**, not an asset. For a blueprint parent that is the
*generated* class, and `ObjectToolset.GetClass` on the asset answers exactly
that:

```powershell
python $mcp call EditorToolset.ObjectToolset GetClass '{"instance":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn"}'
```

```json
{"returnValue":{"refPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn_C"}}
```

Do not confuse that with the asset's parent class, which is a different
question and a different tool:

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset GetParent '{"blueprint":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn"}'
```

```json
{"returnValue":{"refPath":"/Script/EpicJam2026.JamPawn"}}
```

For a native base class, pass the script path directly:
`"/Script/Engine.GameModeBase"`, `"/Script/Engine.Actor"`.

### 2. Create the folder and the blueprint

*(write step — signature-verified, not executed)*

```powershell
python $mcp call EditorToolset.AssetToolset CreateFolder '{"path":"/Game/Lab/Characters"}'
python $mcp call BlueprintToolsets.BlueprintToolset Create '{"folderPath":"/Game/Lab/Characters","assetName":"BP_LabTPSCharacter","assetType":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn_C"}'
```

`Create(folderPath, assetName, assetType) -> Blueprint`. `CreateFolder(path)`
raising "already exists" is harmless — `Create` makes the directory anyway.

**`assetType` is a class *path*, and a bare class name is not one.** A bare
name is rejected during parameter conversion, before the tool body runs, and
nothing is created. The wording recorded against `Create` in
`ue-op-mcp-connect/references/calling-tools-in-this-build.md` is:

```
Actor is not a valid object path for property 'AssetType'
```

The same rule, re-reproduced here on a read-only tool so no asset could be
created — `GetComponents` with `"componentType":"Actor"` answers:

```
Parameter error: Actor is not a valid object path for property 'ComponentType'.
```

while `"componentType":"/Script/Engine.Actor"` is accepted. Pass
`"/Script/Engine.Actor"`, `"/Script/Engine.GameModeBase"`, or the `…_C` path
`GetClass` gave you above.

`Create` also asserts that the class can be stored in a Blueprint; it refuses
non-blueprintable classes (data assets).

### 3. Configure and compile

*(write step — signature-verified, not executed)*

A new child blueprint's **EventGraph starts empty**, and `ListGraphs` returns
only the child's own graphs: the parent's nodes are not copied into it, so you
add only what is new.

```powershell
python $mcp call BlueprintToolsets.BlueprintToolset CompileBlueprint '{"blueprint":"/Game/Lab/Characters/BP_LabTPSCharacter.BP_LabTPSCharacter"}'
```

### 4. Save

*(write step — signature-verified, not executed)*

```powershell
python $mcp call EditorToolset.AssetToolset SaveAsset '{"assetPath":"/Game/Lab/Characters/BP_LabTPSCharacter.BP_LabTPSCharacter"}'
```

`SaveAsset` takes **one** path. This build has no `save_assets(list)` — a
`search_symbols` for that name returns zero matches — so save each asset with
its own call.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `save_assets(...)` → Unknown tool | no batch save exists in this build | `AssetToolset.SaveAsset` one path per call |
| `Create` → "… is not a valid object path for property 'AssetType'" | a bare class name is not a class path | `"/Script/Engine.Actor"` or `…_C` from `GetClass` |
| `Create` → "cannot be stored in a Blueprint" | the class is a data-asset class | use a different mechanism for data assets |
| `Create`/`CreateFolder` → "unrecognized parameter" | the old snake_case names | `folderPath`, `assetName`, `assetType`, `path` |
| Child blueprint's EventGraph is empty | expected — the parent's graph is separate | add only the new logic |
| `GetClass` returns `…_C` | that is the generated class, not the asset | it is what `Create` wants as `assetType` |
| Blueprint appears but has no components | child inherits them; `GetComponents` on the CDO shows them | nothing to do |

**Always create under a dedicated folder** (e.g. `/Game/Lab/…`) when the parent
is a marketplace or sample asset. It keeps the source pristine, makes the
diff reviewable, and makes it trivial to delete the experiment later.

**Naming convention:** `BP_<Purpose>` for the asset name, matching the
project's existing style.

## Output contract

- The blueprint exists at the requested path
- It compiles
- It is saved to disk
- `GetComponents` on its CDO lists the inherited components

## Related

- `ue-op-inspect-blueprint` — inspect the parent before copying it
- `ue-op-add-component` — add the components the new blueprint needs
- `ue-op-wire-graph` — add the new logic