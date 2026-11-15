"""
ue_map_inventory.py - drop-in editor script that measures a map without
changing it.

Run it headless (see SKILL.md). It writes a JSON report next to the map's
project in Saved/, and prints a human summary to the log.

    UE_MAP        the map to inspect, e.g. /Game/Maps/MyMap
    UE_OUT        where to write the report (default <project>/Saved/ue_inventory.json)
    UE_IGNORE     optional comma-separated actor labels to leave out of the
                  "stacked" heuristic

Everything here is defensive: APIs moved between engine versions, so every
call that is known to have moved is tried one way and then another.
"""

import collections
import json
import math
import os

import unreal

log = unreal.log

MAP = os.environ.get("UE_MAP", "/Game/Maps/FPSMap")
OUT = os.environ.get("UE_OUT", "")

if not OUT:
    OUT = os.path.join(unreal.Paths.project_saved_dir(), "ue_inventory.json")


# --------------------------------------------------------------- helpers --
def _bounds_of(asset_path):
    """World-space bounds of a mesh asset.

    AssetData.get_bounds() exists in some versions and not others; the loaded
    mesh's own get_bounds() is the reliable one. Returns (origin, extent).
    """
    if asset_path in _bcache:
        return _bcache[asset_path]
    mesh = unreal.load_asset(asset_path)
    b = mesh.get_bounds()
    v = ((float(b.origin.x), float(b.origin.y), float(b.origin.z)),
         (float(b.box_extent.x), float(b.box_extent.y), float(b.box_extent.z)))
    _bcache[asset_path] = v
    return v


_bcache = {}


def _aabb(path, loc, yaw, scale):
    o, e = _bounds_of(path)
    a = math.radians(yaw)
    ca, sa = math.cos(a), math.sin(a)
    sx, sy, sz = scale
    pts = []
    for dx in (-e[0], e[0]):
        for dy in (-e[1], e[1]):
            for dz in (-e[2], e[2]):
                lx, ly, lz = o[0] + dx, o[1] + dy, o[2] + dz
                pts.append((loc[0] + ca * lx * sx - sa * ly * sy,
                            loc[1] + sa * lx * sx + ca * ly * sy,
                            loc[2] + lz * sz))
    return (min(p[0] for p in pts), min(p[1] for p in pts), min(p[2] for p in pts),
            max(p[0] for p in pts), max(p[1] for p in pts), max(p[2] for p in pts))


def _load_level(path):
    """load_level moved onto the level editor subsystem in newer versions."""
    try:
        unreal.LevelEditorSubsystem().load_level(path)
        return True
    except Exception as e:
        log(f"[inv] LevelEditorSubsystem.load_level failed ({e}); trying EditorLevelLibrary")
    try:
        unreal.EditorLevelLibrary.load_level(path)
        return True
    except Exception as e:
        log(f"[inv] could not load {path}: {e}")
        return False


def _editor_world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        return unreal.EditorLevelLibrary.get_editor_world()


# ------------------------------------------------------------------ main --
log(f"[inv] loading {MAP}")
if not _load_level(MAP):
    raise SystemExit(1)

world = _editor_world()
if world is None:
    log("[inv] no editor world")
    raise SystemExit(1)

actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
report = {"map": MAP, "actor_count": len(actors),
          "by_class": {}, "meshes": {}, "materials": {},
          "lights": [], "brushes": [], "stacked": [], "worst_stacked": None,
          "level_bounds": None}

report["by_class"] = dict(collections.Counter(type(a).__name__ for a in actors))

# --- static meshes -------------------------------------------------------
mesh_actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor)
distinct_meshes = collections.Counter()
distinct_mats = set()
pairs = set()
transform_hist = collections.Counter()
mesh_rows = []
for a in mesh_actors:
    try:
        sm = a.static_mesh_component.get_editor_property("static_mesh")
    except Exception:
        sm = None
    if sm is None:
        continue
    path = sm.get_path_name()
    distinct_meshes[path] += 1
    loc = a.get_actor_location()
    rot = a.get_actor_rotation()
    sc = a.get_actor_scale3d()
    bb = _aabb(path, (loc.x, loc.y, loc.z), rot.yaw, (sc.x, sc.y, sc.z))
    mesh_rows.append((a.get_actor_label(), path, bb, (loc.x, loc.y, loc.z),
                      (sc.x, sc.y, sc.z)))
    # a bulk import drops many actors on the same spot: identical transform
    transform_hist[(round(loc.x, 1), round(loc.y, 1), round(loc.z, 1),
                    round(rot.yaw, 2), round(sc.x, 3))] += 1
    for i in range(8):
        try:
            m = a.static_mesh_component.get_material(i)
        except Exception:
            break
        if m is None:
            break
        distinct_mats.add(m.get_path_name())
        pairs.add((path, m.get_path_name()))
        break

report["meshes"] = {
    "instances": len(mesh_rows),
    "distinct": len(distinct_meshes),
    "materials": len(distinct_mats),
    "mesh_material_pairs": len(pairs),
}
report["materials"] = sorted(distinct_mats)

# the biggest pile of identical transforms is the bulk-import debris
if transform_hist:
    key, n = transform_hist.most_common(1)[0]
    report["worst_stacked"] = {"transform": list(key), "count": n}
    report["stacked"] = [{"transform": list(k), "count": v}
                         for k, v in transform_hist.most_common(12) if v > 1]

# --- level extent --------------------------------------------------------
# A sky dome is thousands of units across and would swamp the extent, so
# oversized meshes are reported separately instead.
if mesh_rows:
    oversized = [r for r in mesh_rows
                 if max(r[2][3] - r[2][0], r[2][4] - r[2][1]) > 100000.0]
    ground_rows = [r for r in mesh_rows if r not in oversized]
    report["oversized_meshes"] = [
        {"label": r[0], "mesh": r[1],
         "size": [round(r[2][3] - r[2][0]), round(r[2][4] - r[2][1]),
                  round(r[2][5] - r[2][2])]}
        for r in oversized]
    if ground_rows:
        report["level_bounds"] = {
            "min": [min(r[2][0] for r in ground_rows), min(r[2][1] for r in ground_rows),
                    min(r[2][2] for r in ground_rows)],
            "max": [max(r[2][3] for r in ground_rows), max(r[2][4] for r in ground_rows),
                    max(r[2][5] for r in ground_rows)],
        }
        report["below_ground"] = [
            {"label": r[0], "min_z": round(r[2][2], 1)}
            for r in ground_rows if r[2][2] < -1.0
        ][:40]
        # the furthest actors in each direction - strays and mis-scaled assets
        report["extremes"] = {
            "min_x": [{"label": r[0], "x": round(r[2][0])} for r in
                      sorted(ground_rows, key=lambda r: r[2][0])[:4]],
            "max_x": [{"label": r[0], "x": round(r[2][3])} for r in
                      sorted(ground_rows, key=lambda r: -r[2][3])[:4]],
            "min_y": [{"label": r[0], "y": round(r[2][1])} for r in
                      sorted(ground_rows, key=lambda r: r[2][1])[:4]],
            "max_y": [{"label": r[0], "y": round(r[2][4])} for r in
                      sorted(ground_rows, key=lambda r: -r[2][4])[:4]],
        }

# --- lights --------------------------------------------------------------
for cls, name in ((unreal.DirectionalLight, "directional"),
                   (unreal.SkyLight, "sky"),
                   (unreal.PointLight, "point"),
                   (unreal.SpotLight, "spot")):
    try:
        lights = unreal.GameplayStatics.get_all_actors_of_class(world, cls)
    except Exception:
        continue
    for a in lights:
        row = {"class": name, "label": a.get_actor_label()}
        loc = a.get_actor_location()
        row["location"] = [round(loc.x), round(loc.y), round(loc.z)]
        try:
            comp = a.light_component
            row["intensity"] = round(float(comp.get_editor_property("intensity")), 3)
            row["shadows"] = bool(comp.get_editor_property("cast_shadows"))
            try:
                row["forward_shading_priority"] = round(
                    float(comp.get_editor_property("forward_shading_priority")), 3)
            except Exception:
                row["forward_shading_priority"] = None
        except Exception:
            pass
        report["lights"].append(row)

# --- BSP brushes (real ground, and a common cause of "buried" assets) ----
# unreal.Brush also catches AVolume subclasses (post process, physics
# volumes), so keep only the actual BSP brush.
try:
    brushes = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Brush)
except Exception:
    brushes = []
for b in brushes:
    if type(b).__name__ != "Brush":
        continue
    try:
        o, e = b.get_actor_bounds(False)
        report["brushes"].append({
            "label": b.get_actor_label(),
            "min": [round(o.x - e.x), round(o.y - e.y), round(o.z - e.z)],
            "max": [round(o.x + e.x), round(o.y + e.y), round(o.z + e.z)],
        })
    except Exception:
        pass

# --- summary -------------------------------------------------------------
log(f"[inv] {MAP}: {report['actor_count']} actors")
for k, v in sorted(report["by_class"].items(), key=lambda kv: -kv[1]):
    log(f"[inv]   {v:6d}  {k}")
log(f"[inv] mesh instances {report['meshes']['instances']}, "
    f"distinct {report['meshes']['distinct']}, "
    f"materials {report['meshes']['materials']}, "
    f"mesh+material pairs {report['meshes']['mesh_material_pairs']}")
if report["worst_stacked"]:
    log(f"[inv] biggest identical-transform pile: {report['worst_stacked']['count']} "
        f"actors at {report['worst_stacked']['transform']}")
if report.get("level_bounds"):
    log(f"[inv] extent {report['level_bounds']['min']} .. {report['level_bounds']['max']}")
log(f"[inv] lights: {len(report['lights'])}, brushes: {len(report['brushes'])}")
for l in report["lights"]:
    log(f"[inv]   {l['class']:12s} {l['label']:22s} i={l.get('intensity')} "
        f"prio={l.get('forward_shading_priority')} z={l['location'][2]}")
for b in report["brushes"]:
    log(f"[inv]   brush {b['label']}: {b['min']} .. {b['max']}")
log(f"[inv] actors below z=-1: {len(report.get('below_ground', []))}")

json.dump(report, open(OUT, "w", encoding="utf-8"), indent=1)
log(f"[inv] wrote {OUT}")

try:
    unreal.SystemLibrary.quit_editor()
except Exception:
    pass
