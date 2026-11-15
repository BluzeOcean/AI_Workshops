import json, struct, os, sys

def analyze(path, block=1<<20):
    size = os.path.getsize(path)
    with open(path,'rb') as f:
        n = struct.unpack('<Q', f.read(8))[0]
        hdr = json.loads(f.read(n))
    hdr.pop('__metadata__', None)
    base = 8+n

    # 1) find comfy_quant tensors and dump their bytes
    for k,v in hdr.items():
        if 'comfy_quant' in k:
            s,e = v['data_offsets']
            with open(path,'rb') as f:
                f.seek(base+s); b = f.read(e-s)
            print(f"  comfy_quant key: {k}")
            print(f"    range={s}..{e} len={len(b)}")
            print(f"    first 64 bytes: {b[:64]!r}")
            print(f"    all-zero? {b == bytes(len(b))}")

    # 2) scan for zero-filled holes
    holes = []
    with open(path,'rb') as f:
        pos = 0
        run = 0
        while True:
            chunk = f.read(block)
            if not chunk: break
            if chunk.count(0) == len(chunk):
                if run == 0: start = pos
                run += len(chunk)
            else:
                if run > 0:
                    holes.append((start, run)); run = 0
            pos += len(chunk)
        if run > 0: holes.append((start, run))
    holes.sort(key=lambda x:-x[1])
    print(f"  zero-holes >=1MB: {len(holes)}")
    for s,l in holes[:8]:
        print(f"    {s:>14,} .. {s+l:>14,}  ({l:,} bytes)")
    if not holes:
        print("    (none found)")

for p in sys.argv[1:]:
    print(f"=== {os.path.basename(p)} ===")
    analyze(p)
