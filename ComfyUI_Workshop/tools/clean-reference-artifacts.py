#!/usr/bin/env python
"""
clean-reference-artifacts.py - remove greebles from a reference image.

WHY
---
The MOSS-Image edit LoRA reproduces the reference's SURFACE faithfully - including the
parts you do not want. The r04_02 reference carries a vent grille on its upper back, a
painted emblem on its chest, a grid panel on its flank and a small recessed square on a
lower plate; every edit made from it copied all of them, and they read as "screens" and
"decal-like patches" in the output.

Telling the model to remove them in the PROMPT does NOT work: naming "the small
rectangular screen" hands the model the concept of a screen, and the next render had
MORE screens, on a different panel. So the reference is cleaned first, and the clean
copy becomes the reference.

WHAT IT DOES
------------
  "flat_grain"  - the default and the one that works.

      A greeble is a HOLE in the surface, and the material that belongs in the hole is
      the material that frames it. So the tool

        1. measures a RING of pixels around the hole - the frame - excluding the
           hole itself and excluding the greeble's own bright edges,
        2. fits a PLANE (least squares of value against x and y) to that ring, so the
           replacement carries the plate's own shading,
        3. fills the hole with that plane plus LUMINANCE grain sized from the ring's
           residuals, feathered into the surrounding.

      The grain is luminance, not per-channel: independent RGB noise reads as
      coloured static. The gradient is a plane, not per-row and per-column means:
      a column mean is taken from too few pixels, and the fill comes out RIBBED -
      and the edit model treats ribs as material and amplifies them into a grille.

      Fill a raised unit WHOLE, rim included. Filling only its interior leaves a
      flat face inside a raised rim, which is the shape of a MONITOR BEZEL, and the
      model draws a screen.

  "material_fill"  - a fallback: OpenCV's Telea inpainting fills the hole from its
      boundary, then real texture is transferred from a patch whose own low-frequency
      appearance matches the fill's. Smears less than the first attempt did, but it
      still smears.

  "context_clone"  - the weakest of the three and NOT recommended. It finds a patch
      by matching the SURROUNDINGS of a candidate, which is not the same as matching
      the material inside it; it will paste a rival colour into a plate.

  "inpaint"  - plain Telea inpainting. Cheap, and safe on a flat plate, but it smears.

The original file is never modified; a new file is written.

USAGE
-----
  python clean-reference-artifacts.py --spec <spec.json>

Spec:
  {
    "image": "<reference.png>",
    "out":   "<clean.png>",
    "regions": [
      { "fill_box": [x0, y0, x1, y1], "ring_box": [x0-6, y0-6, x1+6, y1+6],
        "mode": "flat_grain",
        "exclude": "dark",        # "dark" | "saturated" | "none"
        "thr": 95,                # threshold for the exclusion
        "feather": 5,             # blend band at the edge of the fill, px
        "max_noise": 3.0 }        # grain cap
    ]
  }

Boxes are PIXELS in the source image (x0, y0, x1, y1). The output goes wherever the
spec says - media never belongs in this workspace, so point "out" at the destination.

"fill_box" must cover the greeble WHOLE plus a margin; "ring_box" must NOT overlap
"fill_box", because the ring is where the material is measured from and a greeble's
own bright edge pollutes the measurement.

Requires numpy and OpenCV (the ComfyUI embedded Python has both):
D:\\ComfyUI\\python_embeded\\python.exe
"""

import argparse
import json
import os
import sys

import numpy as np

try:
    import cv2
except ImportError:
    sys.exit("cv2 is required. Use D:\\ComfyUI\\python_embeded\\python.exe.")

try:
    from PIL import Image
except ImportError:
    sys.exit("PIL is required. Use D:\\ComfyUI\\python_embeded\\python.exe.")


def ring_strips(img, box, t):
    """The four strips just OUTSIDE a box: top, bottom, left, right."""
    x0, y0, x1, y1 = box
    h, w = img.shape[:2]
    out = []
    if y0 - t >= 0:
        out.append(img[y0 - t:y0, x0:x1])
    if y1 + t <= h:
        out.append(img[y1:y1 + t, x0:x1])
    if x0 - t >= 0:
        out.append(img[y0:y1, x0 - t:x0])
    if x1 + t <= w:
        out.append(img[y0:y1, x1:x1 + t])
    return out


def strip_score(a, b):
    """Normalised SSD between two strips.

    The pixels arrive already blurred: blurring the WHOLE image once and slicing it
    is hundreds of times faster than blurring every candidate strip, and for a
    scoring metric the tiny edge difference is irrelevant.
    """
    if a is None or b is None or a.size == 0 or b.size == 0:
        return 1e9
    if a.shape != b.shape:
        return 1e9
    a = a.astype(np.float32)
    b = b.astype(np.float32)
    d = a - b
    return float((d * d).mean())


def find_best_patch(blurred, box, exclude_mask, context, step):
    """Find the patch whose surroundings best match the hole's surroundings.

    Returns (src_box, score). score is the mean per-strip SSD; lower is better.
    """
    h, w = blurred.shape[:2]
    x0, y0, x1, y1 = box
    pw, ph = x1 - x0, y1 - y0
    target_strips = ring_strips(blurred, box, context)
    if not target_strips:
        return None, 1e9

    best = None
    best_score = 1e9
    for cy in range(0, h - ph + 1, step):
        for cx in range(0, w - pw + 1, step):
            cand = (cx, cy, cx + pw, cy + ph)
            # the candidate must not sit inside the hole, nor inside any greeble
            if _overlap(cand, box):
                continue
            if exclude_mask is not None:
                sub = exclude_mask[cy:cy + ph, cx:cx + pw]
                if sub.size and sub.mean() > 8:      # a few % of the patch is greeble
                    continue
            cand_strips = ring_strips(blurred, cand, context)
            if len(cand_strips) != len(target_strips):
                continue
            score = np.mean([strip_score(a, b) for a, b in zip(target_strips, cand_strips)])
            if score < best_score:
                best_score = score
                best = cand
    return best, best_score


def _overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 <= bx0 or bx0 >= bx1 or ay1 <= by0 or ay0 >= by1)


def build_exclude_mask(shape, regions, pad=8):
    m = np.zeros(shape[:2], np.uint8)
    for r in regions:
        box = r.get("box") or r.get("fill_box")
        if not box:
            continue
        x0, y0, x1, y1 = box
        m[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad] = 255
    return m


def find_material_match(img, hole, fill_region, exclude_mask, sigma, step):
    """Find the patch whose MATERIAL matches what the fill says belongs in the hole.

    The fill (an inpaint) already carries the right colour and the right gradient -
    it knows what the plate around the hole is doing. What the fill lacks is
    TEXTURE: real grain, rivets, grime. So the patch to copy the texture from is
    the one whose own low-frequency appearance matches the fill's low-frequency
    appearance. Matching on the low frequency (the material) and not on the high
    frequency (the detail) is what stops the copy from dragging a rival colour
    into the plate - an earlier version matched the SURROUNDINGS of a candidate
    instead, and painted an orange emblem into a grey chest plate with blue in it.
    """
    h, w = img.shape[:2]
    hx0, hy0, hx1, hy1 = hole
    pw, ph = hx1 - hx0, hy1 - hy0
    low_fill = cv2.GaussianBlur(fill_region.astype(np.float32), (0, 0), sigma)

    best = None
    best_score = 1e18
    for cy in range(0, h - ph + 1, step):
        for cx in range(0, w - pw + 1, step):
            cand = (cx, cy, cx + pw, cy + ph)
            if _overlap(cand, hole):
                continue
            if exclude_mask is not None:
                sub = exclude_mask[cy:cy + ph, cx:cx + pw]
                if sub.size and sub.mean() > 8:
                    continue
            c = img[cy:cy + ph, cx:cx + pw].astype(np.float32)
            low_c = cv2.GaussianBlur(c, (0, 0), sigma)
            d = low_c - low_fill
            score = float((d * d).mean())
            if score < best_score:
                best_score = score
                best = (c, low_c)
    return best, best_score


def do_material_fill(img, region, exclude_mask, log):
    """Inpaint the hole, then give it real texture from a material-matched patch."""
    x0, y0, x1, y1 = region["box"]
    pad = int(region.get("pad", 3))
    hx0, hy0 = max(0, x0 - pad), max(0, y0 - pad)
    hx1, hy1 = min(img.shape[1], x1 + pad), min(img.shape[0], y1 + pad)
    hole = (hx0, hy0, hx1, hy1)

    mask = np.zeros(img.shape[:2], np.uint8)
    mask[hy0:hy1, hx0:hx1] = 255
    radius = int(region.get("radius", 7))
    flag = cv2.INPAINT_TELEA if region.get("method", "telea") == "telea" else cv2.INPAINT_NS
    filled = cv2.inpaint(img, mask, radius, flag)
    fill_reg = filled[hy0:hy1, hx0:hx1]

    sigma = float(region.get("sigma", 6))
    cand, score = find_material_match(
        img, hole, fill_reg, exclude_mask, sigma, int(region.get("search_step", 4)))
    if cand is None:
        log("    no material match -> keeping the plain inpaint")
        return filled

    c, low_c = cand
    low_fill = cv2.GaussianBlur(fill_reg.astype(np.float32), (0, 0), sigma)
    hf_c = c - low_c                       # the source's texture
    gain = float(region.get("texture", 1.0))
    out_reg = np.clip(low_fill + hf_c * gain, 0, 255).astype(np.uint8)

    # feather the border so the transferred texture does not end on a hard line
    feather = int(region.get("feather", 3))
    if feather > 0:
        w = hx1 - hx0
        h = hy1 - hy0
        m = np.zeros((h, w), np.float32)
        for y in range(h):
            for x in range(w):
                d = min(x, y, w - 1 - x, h - 1 - y)
                m[y, x] = 1.0 if d >= feather else d / float(feather)
        out_reg = (out_reg.astype(np.float32) * m[:, :, None] +
                   fill_reg.astype(np.float32) * (1.0 - m)[:, :, None]).astype(np.uint8)

    out = filled.copy()
    out[hy0:hy1, hx0:hx1] = out_reg
    log("    material match score %.1f, texture gain %.2f" % (score, gain))
    return out


def do_context_clone(img, region, exclude_mask, log):
    box = tuple(region["box"])
    x0, y0, x1, y1 = box
    pad = int(region.get("pad", 3))
    hx0, hy0 = max(0, x0 - pad), max(0, y0 - pad)
    hx1, hy1 = min(img.shape[1], x1 + pad), min(img.shape[0], y1 + pad)
    hole = (hx0, hy0, hx1, hy1)

    blurred = cv2.GaussianBlur(img, (0, 0), 1.6)
    src_box, score = find_best_patch(
        blurred, hole, exclude_mask,
        int(region.get("context", 14)), int(region.get("search_step", 4)))

    if src_box is None:
        log("    no candidate patch found -> telea inpaint")
        mask = np.zeros(img.shape[:2], np.uint8)
        mask[hy0:hy1, hx0:hx1] = 255
        return cv2.inpaint(img, mask, 7, cv2.INPAINT_TELEA)

    log("    best source %s  score %.1f" % (str(src_box), score))
    patch = img[src_box[1]:src_box[3], src_box[0]:src_box[2]].copy()
    if patch.shape[0] != (hy1 - hy0) or patch.shape[1] != (hx1 - hx0):
        patch = cv2.resize(patch, (hx1 - hx0, hy1 - hy0), interpolation=cv2.INTER_AREA)

    # Poisson blend: the patch brings texture, the destination brings the lighting.
    # seamlessClone takes the mask of the SOURCE region to clone (sized to the
    # source patch) and the centre, in destination coordinates, where it lands.
    src_mask = np.full(patch.shape[:2], 255, np.uint8)
    centre = ((hx0 + hx1) // 2, (hy0 + hy1) // 2)
    try:
        out = cv2.seamlessClone(patch, img, src_mask, centre, cv2.NORMAL_CLONE)
        # seamlessClone works on the masked area of DST - confirm the hole moved
        before = img[hy0:hy1, hx0:hx1].astype(np.int16)
        after = out[hy0:hy1, hx0:hx1].astype(np.int16)
        if np.abs(after - before).mean() < 0.5:
            log("    seamlessClone was a no-op -> telea inpaint")
            return cv2.inpaint(img, mask, 7, cv2.INPAINT_TELEA)
        return out
    except cv2.error as e:
        log("    seamlessClone failed (%s) -> telea inpaint" % str(e).replace("\n", " ")[:120])
        return cv2.inpaint(img, mask, 7, cv2.INPAINT_TELEA)


def do_inpaint(img, region, log):
    x0, y0, x1, y1 = region["box"]
    pad = int(region.get("pad", 3))
    hx0, hy0 = max(0, x0 - pad), max(0, y0 - pad)
    hx1, hy1 = min(img.shape[1], x1 + pad), min(img.shape[0], y1 + pad)
    mask = np.zeros(img.shape[:2], np.uint8)
    mask[hy0:hy1, hx0:hx1] = 255
    log("    telea inpaint radius %d" % int(region.get("radius", 7)))
    return cv2.inpaint(img, mask, int(region.get("radius", 7)), cv2.INPAINT_TELEA)


def do_flat_grain(img, region, log):
    """Flatten a greeble's interior to the colour of its own surrounding frame.

    A greeble is usually a DARK SCREEN-LIKE THING sitting in a frame of ordinary
    plate. Filling only the interior - and filling it with the frame's own colour -
    is a far smaller edit than replacing the whole rectangle:

      the slats of a vent become a solid rust block, the grid of a panel becomes a
      solid panel, a painted emblem becomes bare plate.

    The colour and the grain are read from a RING of pixels around the hole, so
    they belong to the same piece of material by construction. The fill is
    feathered into the surrounding so no rectangle edge is left behind.
    """
    fx0, fy0, fx1, fy1 = region["fill_box"]
    rx0, ry0, rx1, ry1 = region.get("ring_box", region["fill_box"])
    grow = int(region.get("grow", 0))
    fx0, fy0 = max(0, fx0 - grow), max(0, fy0 - grow)
    fx1, fy1 = min(img.shape[1], fx1 + grow), min(img.shape[0], fy1 + grow)
    thr = int(region.get("thr", 110))
    excl = region.get("exclude", "dark")
    feather = int(region.get("feather", 3))
    max_noise = float(region.get("max_noise", 5.0))

    roi = img[ry0:ry1, rx0:rx1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    if excl == "dark":
        keep = (gray >= thr) & (gray < 235)
    elif excl == "saturated":
        keep = (hsv[:, :, 1] < thr) & (gray < 235)
    else:
        keep = (gray < 235)

    # The ring must NOT include the hole. Sampling the greeble's own bright edges
    # pollutes the colour estimate (the vent's lit slats turn the estimate into
    # stripes) and sampling its anti-aliased halo drags the emblem's orange back
    # into the very plate that is supposed to have lost it.
    inside = np.zeros_like(keep)
    ix0, iy0 = max(rx0, fx0), max(ry0, fy0)
    ix1, iy1 = min(rx1, fx1), min(ry1, fy1)
    inside[iy0 - ry0:iy1 - ry0, ix0 - rx0:ix1 - rx0] = True
    keep = keep & ~inside

    ring = roi[keep]
    if ring.shape[0] < 12:
        log("    ring too small (%d px) -> plain inpaint" % ring.shape[0])
        mask = np.zeros(img.shape[:2], np.uint8)
        mask[fy0:fy1, fx0:fx1] = 255
        return cv2.inpaint(img, mask, 7, cv2.INPAINT_TELEA)

    # The plate is graded, so ONE flat colour leaves a visible patch. Fit a PLANE
    # to the ring instead: a least-squares fit of value against (x, y) is smooth
    # by construction. Per-row and per-column means were tried first and they
    # striate - a column's mean is taken from too few pixels, so the fill came
    # out ribbed, and the model amplified those ribs into a grille.
    ring_f = ring.astype(np.float32)
    ys, xs = np.where(keep)
    ys_abs = ys.astype(np.float32) + ry0
    xs_abs = xs.astype(np.float32) + rx0
    A = np.stack([np.ones_like(xs_abs), xs_abs, ys_abs], axis=1)
    coeffs = np.zeros((3, 3), np.float32)
    for ch in range(3):
        c, *_ = np.linalg.lstsq(A, ring_f[:, ch], rcond=None)
        coeffs[:, ch] = c
    # a wild extrapolation is worse than a flat fill - clamp the plane to the
    # ring's own value range
    lo = ring_f.min(axis=0) - 12.0
    hi = ring_f.max(axis=0) + 12.0

    h = fy1 - fy0
    w = fx1 - fx0
    gx = (np.arange(fx0, fx1, dtype=np.float32))[None, :]
    gy = (np.arange(fy0, fy1, dtype=np.float32))[:, None]
    base = (coeffs[0][None, None, :]
            + coeffs[1][None, None, :] * gx[:, :, None]
            + coeffs[2][None, None, :] * gy[:, :, None])
    base = np.clip(base, lo[None, None, :], hi[None, None, :])

    # Grain is LUMINANCE noise, not per-channel noise: independent RGB noise
    # reads as coloured static, which on a painted plate looks like a new
    # artifact rather than paint. The size comes from the ring's RESIDUALS
    # around the plane, not from the ring's spread - the spread includes the
    # shading across the plate and overstates the grain by an order of magnitude.
    resid = ring_f - (coeffs[0][None, :] + coeffs[1][None, :] * xs_abs[:, None]
                      + coeffs[2][None, :] * ys_abs[:, None])
    mad = np.median(np.abs(resid - np.median(resid, axis=0)), axis=0)
    noise = min(float(1.4826 * mad.mean()), max_noise)
    rng = np.random.RandomState(0)
    lum = rng.normal(0.0, noise, size=(h, w, 1))
    fill = np.clip(base + lum, 0, 255)

    alpha = np.zeros((h, w), np.float32)
    for y in range(h):
        for x in range(w):
            d = min(x, y, w - 1 - x, h - 1 - y)
            alpha[y, x] = 1.0 if d >= feather else d / float(max(feather, 1))
    region_img = img[fy0:fy1, fx0:fx1].astype(np.float32)
    blended = region_img * (1 - alpha[:, :, None]) + fill * alpha[:, :, None]
    out = img.copy()
    out[fy0:fy1, fx0:fx1] = np.clip(blended, 0, 255).astype(np.uint8)
    log("    ring %d px  base BGR %s  noise %.2f  fill %s" % (
        ring.shape[0], np.round(ring_f.mean(axis=0), 1).tolist(), noise,
        str((fx0, fy0, fx1, fy1))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()

    with open(args.spec, "r", encoding="utf8") as f:
        spec = json.load(f)
    src = spec["image"]
    dst = spec["out"]
    if not os.path.isfile(src):
        sys.exit("source not found: %s" % src)

    bgr = cv2.imread(src, cv2.IMREAD_COLOR)
    if bgr is None:
        sys.exit("cannot read %s" % src)
    print("loaded %s (%dx%d)" % (src, bgr.shape[1], bgr.shape[0]))

    regions = spec.get("regions", [])
    exclude_mask = build_exclude_mask(bgr.shape, regions,
                                      int(spec.get("exclude_pad", 2)))

    out = bgr
    for r in regions:
        box = tuple(r.get("box") or r.get("fill_box"))
        mode = r.get("mode", "context_clone")
        print("  %-12s %-22s" % (mode, str(box)))
        if mode == "context_clone":
            out = do_context_clone(out, r, exclude_mask, print)
        elif mode == "material_fill":
            out = do_material_fill(out, r, exclude_mask, print)
        elif mode == "flat_grain":
            out = do_flat_grain(out, r, print)
        elif mode == "inpaint":
            out = do_inpaint(out, r, print)
        else:
            sys.exit("unknown mode: %s" % mode)

    outdir = os.path.dirname(dst)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    ok = cv2.imwrite(dst, out)
    if not ok:
        sys.exit("failed to write %s" % dst)
    print("wrote %s (%dx%d)" % (dst, out.shape[1], out.shape[0]))


if __name__ == "__main__":
    main()
