#!/usr/bin/env python3
"""
contact-sheet.py - tile a folder of renders into one reviewable sheet.

WHY
---
A set of ten renders is impossible to judge one file at a time. A single
contact sheet makes the set readable at a glance: silhouettes, framing,
palette and consistency across the set.

The sheet is MEDIA, so it must never be written into this workspace. Point
--out at a temp path or at the task destination.

USAGE
    D:\\ComfyUI\\python_embeded\\python.exe tools\\contact-sheet.py ^
        --dir "V:\\04_Projects\\EpicJam2026\\MechConcept Art" ^
        --out "$env:TEMP\\mech_r01_sheet.png" --cols 5 --cell 420
"""

import argparse
import pathlib
import sys

from PIL import Image, ImageDraw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="folder of images")
    ap.add_argument("--out", required=True, help="output PNG path")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--cell", type=int, default=420, help="cell width in px")
    ap.add_argument("--pattern", default="", help="only files matching this substring")
    ap.add_argument("--label", action="store_true", help="draw the filename on each cell")
    args = ap.parse_args()

    src = pathlib.Path(args.dir)
    files = sorted(
        p for p in src.iterdir()
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        and args.pattern in p.name
    )
    if not files:
        print(f"no images found in {src} (pattern={args.pattern!r})", file=sys.stderr)
        return 1

    cols = max(1, args.cols)
    rows = (len(files) + cols - 1) // cols
    cell = args.cell
    label_h = 26 if args.label else 0
    sheet = Image.new("RGB", (cols * cell, rows * (cell + label_h)), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)

    for i, f in enumerate(files):
        try:
            im = Image.open(f).convert("RGB")
        except Exception as exc:                      # noqa: BLE001
            print(f"skip {f.name}: {exc}", file=sys.stderr)
            continue
        im.thumbnail((cell, cell), Image.LANCZOS)
        x = (i % cols) * cell + (cell - im.width) // 2
        y = (i // cols) * (cell + label_h) + (cell - im.height) // 2
        sheet.paste(im, (x, y))
        if args.label:
            name = f.stem.replace("_00001_", "")
            draw.text(((i % cols) * cell + 6, (i // cols) * (cell + label_h) + cell + 6),
                      name, fill=(200, 200, 205))

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"{len(files)} images -> {out}  ({sheet.width}x{sheet.height})")
    for f in files:
        print(f"  {f.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
