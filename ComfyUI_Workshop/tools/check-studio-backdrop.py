#!/usr/bin/env python
"""
check-studio-backdrop.py - verify that a concept-art render has an EVENLY LIT floor.

WHY
---
The house studio backdrop used to come out with a warm pool of light on the floor's
bottom-left corner: an orange patch, ~40 levels brighter than the rest of the floor,
with the backdrop's left side warm as well. It was not a "reflection" of anything -
it was the model obeying two phrases in the house style:

    "a warm golden rim light running down the left edge of the silhouette"
    "soft bounced light from the grey floor"

Together they let the model put a warm light source low and to the left, and it
painted the corner of the floor with it.

The eye catches it, but the numbers catch it faster and without a fresh pair of
eyes: the pool is a measurable WARMTH EXCESS and a BRIGHTNESS EXCESS against the
rest of the floor. This tool measures both.

WHAT IT CHECKS
--------------
For each render, on the floor band (the bottom 10% of the frame):

    floor_ref  - the median colour of the floor, taken from the left and right
                 thirds only (the middle is where the machine's feet and its
                 contact shadow are)
    corners    - the bottom-left and bottom-right patches

    warmth excess  = corner (R - B) - floor_ref (R - B)
                     a neutral floor has R - B near 0; a warm pool has R - B high
    value excess   = corner brightness - floor_ref brightness

A corner more than 12 units warm or 12 units brighter than the rest of the floor
is a light pool, and the render FAILS.

USAGE
-----
    python check-studio-backdrop.py <image.png> [<image.png> ...]
    python check-studio-backdrop.py --dir "<DESTINATION>" --pattern "moss_mech_r10_"

Exits 0 when every image is clean, 1 when any image has a pool of light.
"""

import argparse
import glob
import os
import sys

try:
    import cv2
    import numpy as np
except ImportError:
    sys.exit("cv2 and numpy are required. Use D:\\ComfyUI\\python_embeded\\python.exe.")

# A corner this much warmer or brighter than the rest of the floor is a pool.
WARM_EXCESS_LIMIT = 12.0
VALUE_EXCESS_LIMIT = 12.0


def warmth(bgr):
    """R - B. 0 on a neutral grey floor, high on an orange pool."""
    return float(bgr[..., 2].mean() - bgr[..., 0].mean())


def measure(img):
    h, w = img.shape[:2]
    y0, y1 = int(h * 0.90), int(h * 0.99)
    band = img[y0:y1]

    # the floor reference: the outer thirds of the band, clear of the machine
    left_third = band[:, :int(w * 0.30)]
    right_third = band[:, int(w * 0.70):]
    ref = np.concatenate([left_third.reshape(-1, 3), right_third.reshape(-1, 3)], axis=0)
    ref_med = np.median(ref.astype(np.float32), axis=0)

    corners = {
        "bottom-LEFT ": band[:, :int(w * 0.18)],
        "bottom-RIGHT": band[:, int(w * 0.82):],
    }
    out = {}
    for name, patch in corners.items():
        p = patch.astype(np.float32)
        out[name] = {
            "warmth": warmth(p),
            "value": float(p[..., 2].mean()),
            "bgr": p.reshape(-1, 3).mean(axis=0),
        }
    return out, ref_med


def check(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        return None, "cannot read %s" % path
    corners, ref = measure(img)
    ref_warm = warmth(ref[None, None, :])
    ref_val = float(ref[2])

    bad = []
    for name, c in corners.items():
        dw = c["warmth"] - ref_warm
        dv = c["value"] - ref_val
        if dw > WARM_EXCESS_LIMIT:
            bad.append("%s is %.0f too warm" % (name, dw))
        if dv > VALUE_EXCESS_LIMIT:
            bad.append("%s is %.0f too bright" % (name, dv))

    print("%-52s floor ref BGR %s" % (os.path.basename(path), np.round(ref, 0).astype(int).tolist()))
    for name, c in corners.items():
        print("    %s  BGR %-18s warmth %+6.1f (%+6.1f vs floor)  value %6.1f (%+6.1f vs floor)" % (
            name, np.round(c["bgr"], 0).astype(int).tolist(),
            c["warmth"], c["warmth"] - ref_warm, c["value"], c["value"] - ref_val))
    if bad:
        print("    FAIL - light pool on the floor: %s" % "; ".join(bad))
        return False, "; ".join(bad)
    print("    OK - the floor is evenly lit")
    return True, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="*", help="image files to check")
    ap.add_argument("--dir", help="folder to scan")
    ap.add_argument("--pattern", default="", help="filename filter for --dir")
    args = ap.parse_args()

    paths = list(args.images)
    if args.dir:
        paths += sorted(glob.glob(os.path.join(args.dir, "*" + args.pattern + "*.png")))
    if not paths:
        ap.error("give at least one image, or --dir")

    failures = 0
    for p in paths:
        if not os.path.isfile(p):
            print("%-52s MISSING" % p)
            failures += 1
            continue
        ok, _ = check(p)
        if not ok:
            failures += 1
        print()

    if failures:
        print("%d of %d renders have a pool of light on the floor." % (failures, len(paths)))
        print("Fix the HOUSE STYLE, not the image. The cause is a light SOURCE in the")
        print("scene with a lateral offset - the rim light along the left edge of the")
        print("silhouette - which rakes the studio floor and brightens the corner.")
        print("Describe the rim as a PROPERTY of the machine (an edge highlight), not as")
        print("a light source, and keep the key light off to the left only.")
        print("See .skills/comfyui-generate/SKILL.md and AGENTS.md.")
        return 1
    print("all %d renders have an evenly lit floor." % len(paths))
    return 0


if __name__ == "__main__":
    sys.exit(main())
