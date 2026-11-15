import json, struct, os, sys

def check(path):
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        raw = f.read(8)
        if len(raw) < 8:
            return f"{path}\n   TRUNCATED: header too short ({len(raw)} bytes)"
        n = struct.unpack('<Q', raw)[0]
        if n > size - 8:
            return f"{path}\n   TRUNCATED: header claims {n} bytes but file only has {size-8}"
        f.seek(8)
        hdr = f.read(n)
    try:
        meta = json.loads(hdr)
    except Exception as e:
        return f"{path}\n   CORRUPT HEADER: {type(e).__name__}: {e}"
    meta.pop('__metadata__', None)
    maxend = 0
    bad = []
    for k, v in meta.items():
        end = v['data_offsets'][1]
        if end > maxend:
            maxend = end
    expected = 8 + n + maxend
    ok = "OK " if expected == size else "BAD"
    out = f"{ok} {os.path.basename(path)}\n   file={size}  header={n}  data_end={maxend}  expected_total={expected}"
    if expected != size:
        out += f"  <-- SHORT BY {expected-size} bytes" if expected > size else f"  <-- {size-expected} bytes EXTRA"
    return out

for p in sys.argv[1:]:
    print(check(p))
