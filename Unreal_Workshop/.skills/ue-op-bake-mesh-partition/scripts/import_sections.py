"""Import baked MeshPartition sections as static meshes and place them.

Runs inside the Unreal editor:
    python mcp_call.py meta RunConsoleCommand '{"command":"py <this file>"}'

Order matters:
  1. destroy the actors from the previous bake
  2. delete the target assets - rename_asset fails if the name is taken
  3. import the (already winding-flipped) OBJ - the task names the asset after
     the FILE, so the imported package is renamed afterwards
  4. Nanite off, save the asset
  5. place one StaticMeshActor per section, set the material + collision
  6. save the level

Edit the constants at the top for another project.
"""

import json
import os

import unreal

BAKE_DIR = r"D:\UE\EpicJam2026\Saved\bake"
DEST = "/Game/Map/WebProtoTerrain"          # where the static meshes live
MATERIAL = "/MeshPartition/Materials/M_MeshPartition_Default"
ACTOR_PREFIX = "WebProtoTerrain"
ASSET_PREFIX = "SM_WebTerrain"
Z_OFF = 0.5        # lift off z=0 so the mesh does not z-fight the editor preview
USE_FLIPPED = True  # import the *_flip.obj produced by flip_winding.py

res = {"actors": [], "errors": [], "steps": []}

subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
mat = unreal.load_asset(MATERIAL)

sections_path = os.path.join(BAKE_DIR, "sections.json")
if not os.path.exists(sections_path):
    raise SystemExit("no sections.json in %s - run extract_sections.py first" % BAKE_DIR)
sections = json.load(open(sections_path, encoding="utf-8"))["sections"]

# 1. remove the actors from the previous bake
for a in list(subsys.get_all_level_actors()):
    if a.get_actor_label().startswith(ACTOR_PREFIX):
        res["steps"].append("destroy actor %s" % a.get_actor_label())
        subsys.destroy_actor(a)

for idx, s in enumerate(sections):
    obj = s["obj"]
    if USE_FLIPPED:
        flipped = obj[:-4] + "_flip.obj" if obj.endswith(".obj") else obj + "_flip.obj"
        if os.path.exists(flipped):
            obj = flipped
        else:
            res["errors"].append("no flipped OBJ for %s - run flip_winding.py" % s["obj"])
            continue

    tag = s.get("owner", "Section%d" % idx).split("_")[-1]
    asset_name = "%s_%s" % (ASSET_PREFIX, tag)
    final_path = "%s/%s" % (DEST, asset_name)

    # 2. free the name (rename_asset fails when the destination exists)
    if unreal.EditorAssetLibrary.does_asset_exist(final_path):
        ok = unreal.EditorAssetLibrary.delete_asset(final_path)
        res["steps"].append("delete %s -> %s" % (final_path, ok))

    # 3. import - the task names the asset after the OBJ file
    task = unreal.AssetImportTask()
    task.filename = obj
    task.destination_path = DEST
    task.automated = True
    task.replace_existing = True
    task.save = True
    tools.import_asset_tasks([task])
    paths = list(task.imported_object_paths)
    if not paths:
        res["errors"].append("no import for %s" % obj)
        continue
    imported_path = paths[0].split(".")[0]

    ok = unreal.EditorAssetLibrary.rename_asset(imported_path, final_path)
    res["steps"].append("rename %s -> %s (%s)" % (imported_path, final_path, ok))
    mesh = unreal.load_asset(final_path)
    if mesh is None:
        res["errors"].append("reload failed %s" % final_path)
        continue

    # 4. the web tier has no Nanite -> force the classic LOD path
    nan = "?"
    try:
        ns = mesh.get_editor_property("nanite_settings")
        ns.set_editor_property("enabled", False)   # UE python drops the "b" prefix
        mesh.set_editor_property("nanite_settings", ns)
        nan = str(mesh.get_editor_property("nanite_settings").get_editor_property("enabled"))
    except Exception as e:
        nan = "ERR %s" % str(e)[:120]
    unreal.EditorAssetLibrary.save_asset(final_path, only_if_is_dirty=False)

    # 5. place it - the OBJ already carries world-space coordinates
    actor = subsys.spawn_actor_from_class(unreal.StaticMeshActor,
                                          unreal.Vector(0.0, 0.0, 0.0),
                                          unreal.Rotator(0.0, 0.0, 0.0))
    actor.set_actor_location(unreal.Vector(0.0, 0.0, Z_OFF), False, True)
    comp = actor.static_mesh_component
    comp.set_static_mesh(mesh)
    if mat:
        comp.set_material(0, mat)
    comp.set_collision_profile_name("BlockAll")
    actor.set_actor_label("%s_%s" % (ACTOR_PREFIX, tag))
    loc = actor.get_actor_location()
    res["actors"].append({"label": actor.get_actor_label(), "mesh": mesh.get_path_name(),
                          "loc": [round(loc.x, 2), round(loc.y, 2), round(loc.z, 2)],
                          "nanite": nan, "src": os.path.basename(obj)})
    unreal.log("BAKE_PLACED %s mesh=%s loc=(%.1f,%.1f,%.1f) nanite=%s" % (
        actor.get_actor_label(), mesh.get_path_name(), loc.x, loc.y, loc.z, nan))

# 6. save the level (a source-control checkout dialog may pop up; the save still lands)
try:
    res["saved"] = str(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
except Exception as e:
    res["errors"].append("save: %s" % str(e)[:200])

with open(os.path.join(BAKE_DIR, "import_result.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, default=str)
unreal.log("BAKE_DONE actors=%d errors=%s" % (len(res["actors"]), res["errors"][:3]))
