---
name: ue-op-bake-mesh-partition
description: Use when Mesh Terrain (the MeshPartition plugin) has to appear in a cooked or packaged build — bake the partition's section meshes to plain static meshes, including the triangle-winding fix that makes the imported mesh actually render. Skip when the partition already renders, when the task is only about the MeshPartition plugin's own compiled-sections build, or when the geometry comes from somewhere other than a partition.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# ue-op-bake-mesh-partition — get Mesh Terrain into a build

A `MeshPartition` actor in a map is an **editor preview** unless the plugin's
compiled sections exist. In a cooked build the actor carries only
editor-module components, so nothing renders — on *any* platform, web or
Windows. UE's own cook log says it outright:

```
Mesh Partition '…' BuildVariant:Common_GameplayData is missing compiled sections
for 20 base modifiers.  Cooked builds will not show these missing regions until
the compiled sections are built.
```

There are two routes. Route A is the plugin's own and needs one human click in
the editor. Route B is the bake and works today from script.

---

## Route A — the plugin's own path (one click)

**Build menu → Build Mesh Partition** in the editor generates the *Compiled
Sections* and the runtime transformer pipeline that makes the plugin's runtime
components appear in a cooked build.

There is **no console command, MCP tool or Python API** for it — verified:
`MeshPartition.Build*`, `MegaMesh.Build*` and `BuildMeshPartition` are all
invalid console commands, and the MCP `MeshPartitionEditor.MeshPartitionToolsetSubsystem`
exposes only `CreateRectangleMeshPartition`, `GetModifiersAffectingBounds` and
`IsModifierPreviewBuildPending`. It must be clicked in the UI.

---

## Route B — bake the sections to static meshes

Use when Route A is not available (or when you want a tier-agnostic result).

### 1. Export the section meshes to world-space OBJ

Run inside the editor (the MeshPartition preview owns a `DynamicMeshComponent`
per section):

```
python V:/04_Projects/Workshops/Unreal_Workshop/.skills/ue-op-mcp-connect/mcp_call.py meta RunConsoleCommand \
  '{"command":"py V:/04_Projects/Workshops/Unreal_Workshop/.skills/ue-op-bake-mesh-partition/scripts/extract_sections.py"}'
```

Writes one OBJ per section plus `sections.json` (vertex/triangle counts, world
bbox) into `<project>/Saved/bake`.

### 2. **Flip the winding** — the step that decides whether anything renders

```powershell
python V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-bake-mesh-partition\scripts\flip_winding.py `
  --dir D:\UE\EpicJam2026\Saved\bake
```

The exported triangles are wound **clockwise seen from above** (geometric
normal −Z). Imported as-is, UE back-face culls every one of them: the asset
imports with the right triangle count, passes every editor check, and renders
**nothing**. The flipped files are written next to the originals as
`*_flip.obj`, and the script prints the mean geometric normal Z — it must be
**positive** (it was `+100.0` after the fix).

### 3. Import, place, and save

```
python V:/04_Projects/Workshops/Unreal_Workshop/.skills/ue-op-mcp-connect/mcp_call.py meta RunConsoleCommand \
  '{"command":"py V:/04_Projects/Workshops/Unreal_Workshop/.skills/ue-op-bake-mesh-partition/scripts/import_sections.py"}'
```

The import script (edit its constants at the top first): Nanite **off**, one
`StaticMeshActor` per section at the origin (the OBJ already carries world
coordinates), the plugin material on the component, `BlockAll` collision, then
saves the level.

### 4. Build and verify

`ue-op-build-web`, then `ue-op-verify-web` — **read the screenshot**.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| imported mesh renders nothing, but has 100k triangles | winding is clockwise seen from above → back-face culled | flip the `f` index order before importing |
| `rename_asset` → "An asset already exists at this location" | the old asset still holds the name | delete the target asset **first**, then rename |
| `replace_existing=True` did not replace the asset | the import task names the asset after the **OBJ file**, so it creates a new package | import, then delete/rename deliberately |
| the imported mesh is invisible on the web tier | Nanite is on and the tier has no Nanite path | `nanite_settings.enabled = False`, then re-save |
| editor render shows a grid plane that is not in the build | the editor's **infinite world grid** at z=0 | judge only by the running build's screenshot |
| hiding the partition actor changes nothing in the viewport | that grid is the editor's, not the plugin's | same as above |
| the mesh z-fights with the editor preview | both sit at z=0 | lift the baked actors ~0.5 units (the plugin preview does not exist in a build) |
| the partition is perfectly flat | the modifier list has no heightmap/sculpt/noise modifier | the bake reproduces exactly what the partition contains — it is not a heightmap generator |
| `unreal.Component` does not exist | it does not | use `unreal.ActorComponent` |
| `unreal.Rotator` arguments are wrong | it is (roll, pitch, yaw) | keep the order |
| `spawn_actor_from_class` ignores the location | the passed location is not honoured | call `set_actor_location` afterwards |
| `MeshNaniteSettings` field not found | UE python drops the `b` prefix | the field is `enabled` |
| the level save pops a checkout dialog | source control cannot check the map out | the save still completes; confirm the `.umap` timestamp afterwards |

---

## Output contract

- one static mesh asset per partition section, Nanite off, correct winding
- one `StaticMeshActor` per section in the level, with collision and the plugin
  material
- a screenshot of a **running build** showing the terrain

## Related

- `ue-op-build-web` — packages the level with the baked terrain
- `ue-op-verify-web` — proves it renders in the browser
