"""Extract MeshPartition section meshes to world-space OBJ.

Runs inside the Unreal editor:
    python mcp_call.py meta RunConsoleCommand '{"command":"py <this file>"}'

The MeshPartition preview owns one DynamicMeshComponent per section. Each
section is written as a world-space OBJ (vertices already transformed into
world space, so the imported static mesh needs no actor offset).

Edit OUT_DIR if the project does not live in the default place.
"""

import json
import math
import os

import unreal

OUT_DIR = r"D:\UE\EpicJam2026\Saved\bake"

os.makedirs(OUT_DIR, exist_ok=True)
res = {"sections": [], "errors": []}


def to_array(wrapper):
    """GeometryScript list wrappers expose convert_<x>_to_array()."""
    for name in dir(wrapper):
        if name.startswith("convert_") and name.endswith("_to_array"):
            return list(getattr(wrapper, name)())
    return list(wrapper)


comps = [o for o in unreal.ObjectIterator(unreal.DynamicMeshComponent)
         if o.get_path_name().startswith("/Game/")]
unreal.log("BAKE_FOUND %d" % len(comps))

for c in comps:
    rec = {"comp": c.get_name(), "path": c.get_path_name()}
    wt = c.get_world_transform()
    loc = wt.translation
    rot = wt.rotation.rotator()          # unreal.Rotator is (roll, pitch, yaw)
    sc = wt.scale3d
    rec["world_translation"] = [loc.x, loc.y, loc.z]
    rec["world_rotation"] = [round(rot.pitch, 3), round(rot.yaw, 3), round(rot.roll, 3)]
    rec["world_scale"] = [sc.x, sc.y, sc.z]

    dm = c.get_dynamic_mesh()
    if dm is None:
        rec["no_dynamic_mesh"] = True
        res["sections"].append(rec)
        continue

    verts = to_array(dm.get_all_vertex_positions(False)[1])
    rec["vert_count"] = len(verts)
    tris_raw = to_array(dm.get_all_triangle_indices(False)[1])
    try:
        uvs = to_array(dm.get_mesh_per_vertex_u_vs(0)[1])
    except Exception as e:
        uvs = []
        rec["uv_error"] = str(e)[:100]
    rec["uv_count"] = len(uvs)

    tri_index = []
    if tris_raw:
        first = tris_raw[0]
        if hasattr(first, "v0"):
            tri_index = [(int(t.v0), int(t.v1), int(t.v2)) for t in tris_raw]
        elif hasattr(first, "x"):
            tri_index = [(int(t.x), int(t.y), int(t.z)) for t in tris_raw]
        else:
            flat = [int(x) for x in tris_raw]
            tri_index = [(flat[i], flat[i + 1], flat[i + 2])
                         for i in range(0, len(flat) - 2, 3)]
    rec["tri_count"] = len(tri_index)

    pr, yr, rr = (math.radians(rot.pitch), math.radians(rot.yaw),
                   math.radians(rot.roll))
    cz, sz = math.cos(yr), math.sin(yr)
    cy, sy = math.cos(pr), math.sin(pr)
    cx, sx = math.cos(rr), math.sin(rr)

    def rot_xyz(v):
        x, y, z = v.x * sc.x, v.y * sc.y, v.z * sc.z
        y, z = y * cx - z * sx, y * sx + z * cx
        x, z = x * cy + z * sy, -x * sy + z * cy
        x, y = x * cz - y * sz, x * sz + y * cz
        return (x + loc.x, y + loc.y, z + loc.z)

    world = [rot_xyz(v) for v in verts]
    rec["world_bbox"] = [
        round(min(p[0] for p in world), 1), round(min(p[1] for p in world), 1),
        round(min(p[2] for p in world), 1), round(max(p[0] for p in world), 1),
        round(max(p[1] for p in world), 1), round(max(p[2] for p in world), 1),
    ]

    have_uv = len(uvs) == len(verts) and len(verts) > 0
    owner = c.get_owner()
    owner_name = owner.get_name() if owner else "owner"
    path = os.path.join(OUT_DIR, "%s_%s.obj" % (owner_name, c.get_name()))
    rec["owner"] = owner_name
    try:
        mats = c.get_materials()
        rec["materials"] = [str(m.get_path_name()) if m else None for m in mats]
    except Exception:
        rec["materials"] = []

    with open(path, "w", encoding="utf-8") as f:
        f.write("# UE MeshPartition section baked from %s\n" % c.get_path_name())
        f.write("o %s\n" % c.get_name())
        for p in world:
            f.write("v %.4f %.4f %.4f\n" % p)
        if have_uv:
            for u in uvs:
                f.write("vt %.6f %.6f\n" % (u.x, u.y))
        f.write("s 1\n")
        for (a1, b1, c1) in tri_index:
            if have_uv:
                f.write("f %d/%d %d/%d %d/%d\n"
                        % (a1 + 1, a1 + 1, b1 + 1, b1 + 1, c1 + 1, c1 + 1))
            else:
                f.write("f %d %d %d\n" % (a1 + 1, b1 + 1, c1 + 1))
    rec["obj"] = path
    rec["obj_bytes"] = os.path.getsize(path)
    res["sections"].append(rec)
    unreal.log("BAKE_SECTION %s verts=%d tris=%d uv=%d world_bbox=%s obj=%d" % (
        c.get_name(), rec["vert_count"], rec["tri_count"], rec["uv_count"],
        rec["world_bbox"], rec["obj_bytes"]))

with open(os.path.join(OUT_DIR, "sections.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, default=str)
unreal.log("BAKE_DONE %d sections -> %s" % (len(res["sections"]), OUT_DIR))
