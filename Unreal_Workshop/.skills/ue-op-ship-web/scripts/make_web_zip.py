import argparse
import os
import zipfile


def main():
    ap = argparse.ArgumentParser(description="Zip a staged UE web build for hosting.")
    ap.add_argument("--stage", required=True, help="stage folder to zip")
    ap.add_argument("--out", required=True, help="output .zip path")
    ap.add_argument("--include-br", action="store_true",
                    help="also zip the Brotli siblings (only for hosts that serve "
                         "them with Content-Encoding: br)")
    args = ap.parse_args()

    stage = os.path.abspath(args.stage)
    out = os.path.abspath(args.out)
    if not os.path.isdir(stage):
        raise SystemExit("stage folder missing: %s" % stage)

    entries = 0
    raw = 0
    skipped = 0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for root, _dirs, files in os.walk(stage):
            for f in files:
                if f.endswith(".br") and not args.include_br:
                    skipped += 1
                    continue
                p = os.path.join(root, f)
                raw += os.path.getsize(p)
                z.write(p, os.path.relpath(p, stage).replace("\\", "/"))
                entries += 1

    print("ZIP entries=%d skipped_br=%d uncompressed=%.1f MB -> %.1f MB  (%s)" % (
        entries, skipped, raw / 1048576, os.path.getsize(out) / 1048576, out))


if __name__ == "__main__":
    main()
