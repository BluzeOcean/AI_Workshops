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

`EditorToolset.AssetToolset.Duplicate` is a plain copy and
**does not remap references**. A folder of copies therefore keeps pointing at
the source assets, so it can never be self-contained, and migrating it brings
the sources along as well.

The only mechanism that produces a folder which stands on its own is
**relocation**: `Move(path, newPath)` renames a package and Unreal rewrites
every reference to it, project-wide.

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

The blocks in this procedure are the `content` of one `execute_python` call, so
they run inside the editor and `await call_tool(...)` reaches the registered
tool by its full name. The namespace does **not** survive between calls
(`globals()` starts empty each time), so steps 3–6 below are one script,
appended in order:

```powershell
python ...\mcp_call.py call editor_toolset.toolsets.python_scripting.PythonScriptingTools execute_python `
  '{"script":{"content":"<the Python block below>","language":"Python"}}'
```

```python
moved, failed = [], []
for src, dst in plan:
    if await call_tool("EditorToolset.AssetToolset.Move", path=src, newPath=dst):
        moved.append((src, dst))
    else:
        failed.append((src, dst))
```

`Move` on a *folder* recurses, but only if the destination does not already
exist. Per-asset moves are slower but give exact control over the layout.

Write progress to `Saved/` every N assets — a mass rename can run for several
minutes and the MCP call will background itself.

### 4. Resave everything

**This is not optional.** After a mass rename the asset registry still holds
the pre-move dependency data, so `GetDependencies` reports paths that no
longer exist. Resaving re-resolves the import tables and re-tags the packages:

```python
for _, dst in moved:
    await call_tool("EditorToolset.AssetToolset.SaveAsset", assetPath=dst)
```

Resaving does **not** rewrite soft object paths (step 7).

### 5. Verify no reference was missed

`GetReferencers` on each **old** path must come back empty. Anything still
listed there is a reference the rename manager could not rewrite, and it
names the asset holding it:

```python
stale = []
for src, dst in moved:
    if await call_tool("EditorToolset.AssetToolset.GetReferencers", assetPath=src):
        stale.append((src, dst))
```

Expect a handful of stale referencers — usually Fab demo maps and test
blueprints inside the folder being emptied. Those resolve through redirectors.

The live tool for finishing that off is
`FixUpRedirectors(path, bDeleteRedirectors=false)`: it rewires everything still
pointing at a redirector and, with `bDeleteRedirectors=true`, removes it. Pass
the emptied folder (searched recursively) or a single redirector path.

### 6. Verify the package is closed

Every `/Game` dependency of every relocated asset must resolve **inside** the
new folder:

```python
FOLDER = "/Game/Assets/"

leaks, dangling = [], []
for _, dst in moved:
    for d in await call_tool("EditorToolset.AssetToolset.GetDependencies", assetPath=dst) or []:
        if d.startswith("/Game/") and not d.startswith(FOLDER):
            if d in universe:
                leaks.append((dst, d))      # points outside - must be zero
            else:
                dangling.append((dst, d))   # broken link - must be zero
len(leaks), len(dangling)
```

One hop per asset is enough here — every asset in the folder is checked, so each
one's own direct imports are covered.

### 7. Sweep the files — the check that actually catches soft references

`GetDependencies` only reports **hard** dependencies. Soft object paths
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

`EditorToolset.ObjectToolset.SetProperties` on the `materials` array does **not**
fix it — it writes the resolved pointer and the serialized soft path stays
stale. Use the dedicated tool, which writes through the proper UE path:

```python
for slot, path in SLOTS.items():
    await call_tool("EditorToolset.SkeletalMeshToolset.SetMaterial",
                    mesh=mesh, slotName=slot, material={"refPath": path})
await call_tool("EditorToolset.AssetToolset.SaveAsset", assetPath=mesh)
```

Re-run the file sweep afterwards to confirm.

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `GetDependencies` reports paths that do not exist | stale asset registry after a mass rename | resave every moved package |
| A copy still points at the source | `Duplicate` does not remap | use `Move`, not `Duplicate` |
| Old path still has a referencer | the rename manager could not rewrite it | UE left a redirector; it still resolves, and `FixUpRedirectors` clears it |
| A skeletal mesh renders with default materials | its material slots are soft paths, untouched by rename/resave | `EditorToolset.SkeletalMeshToolset.SetMaterial(mesh, slotName, material)` per slot |
| `SetProperties` on a complex array silently does nothing | the array is a struct array | use the type-specific tool |
| `Move` on a folder returns false | the destination folder already exists | create it, or move per asset |
| An asset cannot be moved at all | its class cannot be loaded (e.g. `URig` with the Control Rig plugin disabled) | exclude it; the log says `its class (Rig) does not exist` |
| A batch save | there is no `save_assets(list)`, and `execute_tool_script` does not exist in this build | `SaveAsset` per moved asset — one path per call |
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
