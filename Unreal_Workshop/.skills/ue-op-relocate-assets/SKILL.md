---
name: ue-op-relocate-assets
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to move a curated set of assets into a new folder so that folder is self-contained — relocating a character, its shared library and its FX into an export tree for migration to another project. Skip if no UE MCP connection, or if the task is to leave the originals in place (use ue-op-clone-assets).
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

# ue-op-relocate-assets — move an asset set into a self-contained folder

## Why this exists

Unreal's `duplicate` is a plain file copy and **does not remap references**.
A folder of copies therefore keeps pointing at the source assets, so it can
never be self-contained, and migrating it brings the sources along as well.

The only mechanism that produces a folder which stands on its own is
**relocation**: `move` renames a package and Unreal rewrites every reference
to it, project-wide.

Relocation is also the thing users are rightly afraid of — "renaming assets
breaks links and you can't repair them". It is not true, but only because of
three mechanisms you must know about, and only if you **verify**:

| Mechanism | What it does |
|---|---|
| `FAssetRenameManager` | rewrites references in every referencer, project-wide |
| **Redirectors** | UE leaves a tiny `UObjectRedirector` at the old path whenever a referencer could not be rewritten, so the link still resolves |
| **Resave** | after a mass rename the asset registry's dependency data is stale; a resave re-resolves and re-writes it |

And one place it genuinely does *not* reach: **soft object paths stored
inside a package** (see the skeletal-mesh case below). Those must be found
and fixed by hand.

## Procedure

### 1. Back up first

Relocation is the one destructive operation in this skillset. Copy the whole
`Content/` tree somewhere outside the project before touching anything:

```bash
cmd //c robocopy D:/UE/<Project>/Content D:/UE/_backups/<Project>_Content //E //NFL //NDL //NJH //NJS //NP //MT:16
```

> Git Bash rewrites `/E`-style switches into paths (`E:/`) — use `//E`, or set
> `MSYS_NO_PATHCONV=1`.

### 2. Compute the closure and the mapping

Use `ue-op-find-dependencies` for the closure, then write one `dest()` function
that maps every source path to its destination. `ue-op-clone-assets` has the
mapping shape; reuse it.

### 2b. Check whether a "shared" library is actually shared

**Before you give a shared library its own folder, check whether the sources
really share one.** Content that looks shared is often a per-item duplicate:

```bash
for h in HeroA HeroB; do
  md5sum $h/Characters/Global/MaterialFunctions/MF_SomeFunc.uasset
done
```

Different hashes with the same asset name mean **different content under the
same name**. Relocating both to one destination path then collides, and the
two are not interchangeable. In the Paragon Fab content, each of the five
heroes carries its own `Characters/Global/` with *overlapping names and
different content* (MF_HitFlash is 118 KB / 83 KB / 62 KB / 119 KB across
heroes) — so the "shared" library is **per-hero**, not per-package.

### 2c. Namespace by source package, then by item

Anything that gets migrated over several trips needs a namespace per source
package, or a later title's assets mix with an earlier one's:

```
/Game/Assets/<SourcePackage>/<Item>/
    Blueprints/ Mesh/ Materials/ Textures/ Animations/ FX/
    Shared/          <- this item's OWN copy of the library
/Game/Assets/<OtherPackage>/<Item>/...
```

Two levels are needed: the package level stops different Fab bundles mixing,
and the item level stops same-named assets in different bundles colliding.
Keep a per-item library **inside** the item folder — that way migrating one
item folder brings everything it needs in a single selection.

### 3. Move, one asset at a time

```python
moved, failed = [], []
for src, dst in plan:
    try:
        r = T(AT + ".move", path=src, new_path=dst)
    except Exception:
        r = False
    (moved if r else failed).append((src, dst))
T(AT + ".save_assets", asset_paths=[])
```

`move` on a *folder* recurses, but only if the destination does not already
exist. Per-asset moves are slower but give exact control over the layout.

Write progress to `Saved/` every N assets — a mass rename can run for several
minutes and the MCP call will background itself.

### 4. Resave everything

**This is not optional.** After a mass rename the asset registry still holds
the pre-move dependency data, so `get_dependencies` reports paths that no
longer exist. Resaving re-resolves the import tables and re-tags the packages:

```python
T(AT + ".save_assets", asset_paths=[dst for _, dst in moved])
```

Resaving does **not** rewrite soft object paths (step 6).

### 5. Verify no reference was missed

`get_referencers` on each **old** path must come back empty. Anything still
listed there is a reference the rename manager could not rewrite, and it
names the asset holding it:

```python
stale = []
for src, dst in moved:
    if T(AT + ".get_referencers", asset_path=src):
        stale.append((src, dst))
```

Expect a handful of stale referencers — usually Fab demo maps and test
blueprints inside the folder being emptied. Those resolve through redirectors.

### 6. Verify the package is closed

Every `/Game` dependency of every relocated asset must resolve **inside** the
new folder:

```python
for dst in moved:
    for d in deps(dst):
        if d.startswith("/Game/") and not d.startswith("/Game/Assets/"):
            if d in universe:
                leaks.append((dst, d))      # points outside - must be zero
            else:
                dangling.append((dst, d))   # broken link - must be zero
```

### 7. Sweep the files — the check that actually catches soft references

`get_dependencies` only reports **hard** dependencies. Soft object paths
inside a package are invisible to it. Grep the raw `.uasset` bytes instead:

```bash
grep -rlao "/Game/" --include=*.uasset Content/Assets | ...
grep -rhao "/Game/[A-Za-z0-9_/.]*" --include=*.uasset Content/Assets \
  | grep -v "^/Game/Assets/" | sort -u
```

**Zero lines out is the pass condition.**

### 8. Fix what the sweep finds

The known case: a **skeletal mesh** stores its material slots as
`FSoftObjectPath` in the `materials` array, and those soft paths are *not*
rewritten by the rename manager or by a resave. The mesh then renders with
default materials once the old folders are gone.

`ObjectTools.set_properties` on the `materials` array does **not** fix it —
it writes the resolved pointer and the serialized soft path stays stale. Use
the dedicated tool, which writes through the proper UE path:

```python
SMT = "editor_toolset.toolsets.skeletal_mesh.SkeletalMeshTools"
for slot, path in SLOTS.items():
    T(SMT + ".set_material", mesh=mesh, slot_name=slot,
      material={"refPath": path})
T(AT + ".save_assets", asset_paths=[mesh_path])
```

Re-run the file sweep afterwards to confirm.

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `get_dependencies` reports paths that do not exist | stale asset registry after a mass rename | resave every moved package |
| A copy still points at the source | `duplicate` does not remap | use `move`, not `duplicate` |
| Old path still has a referencer | the rename manager could not rewrite it | UE left a redirector; it still resolves |
| A skeletal mesh renders with default materials | its material slots are soft paths, untouched by rename/resave | `SkeletalMeshTools.set_material` per slot |
| `set_properties` on a complex array silently does nothing | the array is a struct array | use the type-specific tool |
| `move` on a folder returns false | the destination folder already exists | create it, or move per asset |
| An asset cannot be moved at all | its class cannot be loaded (e.g. `URig` with the Control Rig plugin disabled) | exclude it; the log says `its class (Rig) does not exist` |
| `asset_paths=[...]` rejected | outer `call_tool` mangles arrays into `{"item": [...]}` | use `execute_tool_script` with `json.dumps` |
| A mass rename runs for minutes | one referencer sweep per asset | background it, write progress to `Saved/` |

**Redirectors are the safety net, not debris.** UE creates one at an old path
whenever it could not rewrite a referencer, so an unfixed link still resolves.
They disappear with the old folder, which is fine when that folder is being
disposed of anyway.

## Output contract

- the assets are at their new paths and the old ones are gone (or are
  redirectors)
- every asset in the new folder compiles
- the closure check reports zero leaks and zero dangling references
- the file-level sweep reports zero `/Game` paths outside the new folder
- anything that could not be moved is listed, with the reason

## Related

- `ue-op-find-dependencies` — compute the closure to relocate
- `ue-op-clone-assets` — copy a closure instead (keeps the originals)
- `ue-op-fix-compile-error` — if a blueprint stops compiling afterwards
