---
name: ue-op-clone-assets
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to copy a curated set of assets into a structured export folder — cloning a character, its animations and its FX into Content/Assets for later migration to another project. Skip if no UE MCP connection, or if the task is to move/rename assets in place, or to delete them.
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

# ue-op-clone-assets — clone a curated asset set into an export tree

## Why this exists

Copying a dependency-closed set of assets into a folder so it can be migrated
to another project sounds like a copy operation. In Unreal it is **not** — and
getting this wrong is how you end up with a package that silently points back
at the source project.

## The three facts that decide everything

### 1. `Duplicate` is a plain file copy — it does NOT remap references

Verified: after duplicating `M_Murdock_Body`, the copy's dependencies still
listed `/Game/ParagonMurdock/.../MF_MatLayerBlend_Decal` and
`.../T_Murdock_Body_RGB`. A copy's references always point at the **source**
assets.

Consequence: a cloned tree is a *manifest*, not a standalone package. This is
not fixable through the exposed tools, because a material's texture references
live inside its **expression graph** (`UMaterial::Expressions`), not in a
UPROPERTY that `SetProperties` can rewrite. The same is true of material-layer
overrides and material-function references.

### 2. `Move` rewrites references — but it consumes the original

Verified: moving an asset re-pointed *both* the original referencer and an
unrelated duplicate copy at the new path, and moving it back restored both.
There is no separate rename tool in this build — `Move(path, newPath)` is the
project-wide referencer sweep.

So `Move` is the only way to make a tree self-contained — but it is a
**relocation, not a clone**. Do not do it to the user's source assets unless
they have explicitly asked for it: it is not reversible from the user's point
of view and the harness's permission layer will (correctly) block it.

### 3. Migrate is closure-based

UE's *Migrate* copies the selected assets **and their dependency closure**,
remapping references in the destination. So a cloned manifest is a perfectly
valid migration source: migrating it pulls the originals along and remaps them
into the destination.

The trap: if you migrate the clones *and* their dependencies, the destination
gets **both** — the clone set and the original set — roughly doubling the
payload. See "Migration recipes" below.

## Procedure

### 1. Decide the roots, then compute the closure

Use `ue-op-find-dependencies`. Roots are the assets the user actually wants;
the closure is everything that must travel with them.

### 2. Design the destination structure

Mirror the source organisation but flatten the noise. A shape that worked:

```
/Game/Assets/<Hero>/
  Blueprints/      the character BP and the animation BP
  Mesh/            skeletal mesh, skeleton, shadow/extent meshes
  Materials/       the hero's own materials
  Textures/
  Animations/      Sequences/ BlendSpaces/ AimOffsets/ Montages/
  FX/              Niagara/ Meshes/ Materials/ Textures/ VectorFields/
/Game/Assets/Shared/
  MaterialLayers/  MaterialFunctions/  ParameterCollections/
  Eyes/  Mouth/  Textures/  Profiles/
```

Rule of thumb: **anything the hero shares with another hero goes in `Shared`**;
everything else stays with the hero.

### 3. Map source path → destination path

Write one `dest()` function and derive every destination from it. Doing this
per-asset by hand is where mistakes creep in.

```python
def dest(p):
    if p.startswith(HERO + "/"):
        rest = p[len(HERO) + 1:]
        folder, _, name = rest.partition("/")
        if rest == "MurdockPlayerCharacter":
            return "/Game/Assets/Murdock/Blueprints/MurdockPlayerCharacter"
        if folder == "Meshes":    return "/Game/Assets/Murdock/Mesh/" + name
        if folder == "Materials": return "/Game/Assets/Murdock/Materials/" + name
        if folder == "Textures":  return "/Game/Assets/Murdock/Textures/" + name
        if folder == "Animations":
            # sequences vs blend spaces vs aim offsets vs montages
            ...
        if folder == "Skins":
            return "/Game/Assets/Shared/Profiles/" + name
    if p.startswith(GLOB + "/"):
        ...
    if p.startswith(FXROOT + "/"):
        ...
    return None       # unmapped - report it, never guess
```

`None` means "I have no rule for this" — surface it rather than silently
dropping it.

### 4. Create every destination folder first

`Duplicate` on a **folder** fails if the destination already exists, so create
all leaf folders up front, then duplicate **per asset** (which is the only
form that lets you control the destination path).

The blocks from here on are the `content` of one `execute_python` call, so they
run inside the editor and `await call_tool(...)` reaches the registered tool by
its full name:

```powershell
python ...\mcp_call.py call editor_toolset.toolsets.python_scripting.PythonScriptingTools execute_python `
  '{"script":{"content":"<the Python block below>","language":"Python"}}'
```

```python
for _, d in plan:
    parts = d.split("/")
    for i in range(3, len(parts)):
        await call_tool("EditorToolset.AssetToolset.CreateFolder", path="/".join(parts[:i]))
```

### 5. Duplicate, then save

```python
ok, fail = [], []
for src, dst in plan:
    if await call_tool("EditorToolset.AssetToolset.Duplicate", path=src, newPath=dst):
        ok.append((src, dst))
    else:
        fail.append((src, dst))

# SaveAsset takes one path; there is no batch save.
for _, dst in ok:
    await call_tool("EditorToolset.AssetToolset.SaveAsset", assetPath=dst)
```

**Duplicates live in memory until `SaveAsset` runs on each of them** — until
then nothing is on disk and `GetDependencies` on a copy returns nothing.

### 6. Verify

- file count and size on disk under `Content/Assets`
- `GetDependencies` on a few copies — confirm they point at the sources
  (that is correct for a clone)
- `CompileBlueprint` on a copied blueprint — must not raise
- the source tree must be **byte-identical** in count and size

## Migration recipes

**If the goal is a standalone folder in the destination project, copying is
the wrong tool.** A clone's references point at the source assets, so migrating
it brings the sources along as dependencies and the destination ends up with
both the clones (unreferenced) and the sources (live). Use
`ue-op-relocate-assets` instead — it moves the assets so the folder is closed
over its own references, and verifies that it is.

Pick one deliberately — they are not equivalent.

| Recipe | Destination contains | Payload |
|---|---|---|
| **A. Migrate one clone** | the clone + the full closure at the source's paths | ~1× closure, but the clone set is dead weight |
| **B. Migrate the closure's originals** | the closure at the source's paths, no clones | 1× closure, cleanest |
| **C. Migrate clones, then reorganise in the destination** | closure at source paths, then `Move` it into the curated structure | 1× closure + one pass of folder moves |
| **D. Relocate first, then migrate** | only the curated folder, self-contained | 1× closure, nothing else — **best** |

Recipe D is `ue-op-relocate-assets` followed by a plain Migrate of the
curated folder: the destination receives one standalone folder and the other
project references it directly, with no restructuring on their side.

Recipe C is the fallback when the source project must not be touched at all:
migrate, then `Move` the migrated assets into the curated structure *in the
destination*, where a broken reference is cheap to fix.


## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `Duplicate` of a folder returns false | the destination folder already exists | create it as a folder first, or duplicate assets individually |
| `Duplicate` of an asset returns false | the asset is not registered yet, or its class cannot be loaded | check the log for the class name; the call returns a plain boolean, with no reason |
| Duplicates vanish | they were never saved | `SaveAsset` each copy after the loop |
| A copied asset has no dependencies | it was never saved/loaded | save first, then query |
| `SetProperties` cannot re-point a texture | texture refs live in the expression graph | accept it — use the move-based recipe |
| An asset cannot be duplicated at all | its plugin is disabled (e.g. `Rig` / Control Rig) | exclude it; confirm with the log: `its class (Rig) does not exist` |
| A batch save | there is no `save_assets(list)`, and `execute_tool_script` does not exist in this build | `SaveAsset` per copy — one path per call; arrays themselves pass through fine (`ValidateAssets(assetPaths=[...])` received both entries) |
| The clone is 600 MB but the closure is 700 MB | some assets failed to duplicate | diff the file lists and report the gaps |

**Always report what did not copy.** A silently missing asset is a broken
package later.

## Output contract

- the clone tree exists on disk with the intended structure
- the source tree is unchanged (file count and size verified)
- every copy's references are understood and stated
- a manifest of the mapping written to `Saved/`
- an explicit list of anything that could not be cloned, and why

## Related

- `ue-op-find-dependencies` — compute the closure to clone
- `ue-op-find-assets` — search the registry
- `ue-op-setup-playable-character` — make the cloned character playable
