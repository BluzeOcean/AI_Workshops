"""Flip the triangle winding of OBJ files and report the geometric normal.

MeshPartition's exported section meshes are wound clockwise seen from above
(geometric normal -Z). Imported into UE as-is they are back-face culled and
render nothing. This writes a flipped copy next to each input
(*_flip.obj) and proves the result by averaging the geometric normal Z.

    python flip_winding.py --dir D:/path/to/bake
    python flip_winding.py a.obj b.obj
"""

import argparse
import glob
import os
import sys


def analyse(path):
    verts = []
    faces = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("v "):
                p = line.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith("f "):
                vals = line.split()[1:]
                faces.append([int(v.split("/")[0]) for v in vals])
    zsum = 0.0
    area_ok = 0
    for f3 in faces:
        p0, p1, p2 = [verts[i - 1] for i in f3[:3]]
        e1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        e2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
        fn = (e1[1] * e2[2] - e1[2] * e2[1],
              e1[2] * e2[0] - e1[0] * e2[2],
              e1[0] * e2[1] - e1[1] * e2[0])
        zsum += fn[2]
        if abs(fn[2]) > 1e-6:
            area_ok += 1
    return verts, faces, zsum / max(1, len(faces)), area_ok


def flip(src, dst):
    with open(src, "r", encoding="utf-8", errors="replace") as fi, \
         open(dst, "w", encoding="utf-8", newline="\n") as fo:
        for line in fi:
            if line.startswith("f "):
                parts = line.split()
                vals = parts[1:]
                if len(vals) == 3:
                    vals = [vals[0], vals[2], vals[1]]
                fo.write(parts[0] + " " + " ".join(vals) + "\n")
            else:
                fo.write(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", help="directory of .obj files to flip")
    ap.add_argument("files", nargs="*", help="explicit .obj files")
    args = ap.parse_args()

    srcs = list(args.files)
    if args.dir:
        srcs += sorted(glob.glob(os.path.join(args.dir, "*.obj")))
    srcs = [s for s in srcs if not s.endswith("_flip.obj")]
    if not srcs:
        print("no .obj files given", file=sys.stderr)
        return 2

    bad = 0
    for src in srcs:
        dst = src[:-4] + "_flip.obj" if src.endswith(".obj") else src + "_flip.obj"
        flip(src, dst)
        verts, faces, zmean, area_ok = analyse(dst)
        zs = [p[2] for p in verts] or [0.0]
        flag = "OK" if zmean > 0 else "STILL BACK-FACING"
        if zmean <= 0:
            bad += 1
        print("%-58s verts=%d faces=%d area_ok=%d mean_normalZ=%+.1f  Z[%.2f,%.2f]  %s" % (
            os.path.basename(dst), len(verts), len(faces), area_ok, zmean,
            min(zs), max(zs), flag))
    if bad:
        print("ERROR: %d file(s) still face down - do not import those" % bad)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
