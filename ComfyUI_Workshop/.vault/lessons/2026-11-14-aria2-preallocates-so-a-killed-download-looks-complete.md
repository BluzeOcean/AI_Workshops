# A killed aria2 download leaves a full-size file that is mostly zeros

**Date:** 2026-11-14
**Symptom:** ComfyUI failed on a MOSS-Image edit workflow with
`CLIPLoader` → `json.loads(layer_conf.numpy().tobytes())` →
`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`,
in `comfy/ops.py::_load_from_state_dict`. The file on disk was the **full expected
size** and its safetensors **header parsed cleanly**. The machine had a hard reset
during a download.

**Cause:** aria2 preallocates the target file at its final length and fills the
segments in as they arrive. A hard reset kills aria2 mid-flight; the parts it had
not yet fetched stay as zeros. The header is at the front of the file, so it is
usually among the first segments written — it parses fine, and every size check
passes. Only the *body* is missing. On this incident the CLIP was 7.34 GB with
~640 MB real and **8 zero-holes**; the UNET was 5.41 GB with ~875 MB real and
**8 zero-holes**. The `.aria2` control file next to each file is the tell: aria2
deletes it only on success.

**Fix:** measure the holes, not the size. Two checks, both cheap:

```
# 1. a leftover control file = an interrupted download
ls -la <dir>/*.aria2

# 2. scan for zero-filled runs (>=1 MB) in the body
```

`tools\check-model-holes.py` does this and also dumps the `comfy_quant` tensors,
which are the exact bytes that blew up the JSON parse.
`tools\check-safetensors.py` checks header length against the declared data end —
it will say **OK** on a zero-holed file, so it is **not** sufficient on its own.

To repair: re-run the **same** aria2c command. The surviving `.aria2` control
file makes it resume and fetch only the missing segments. Always pass
`--checksum=sha-256=<hash>` so aria2 verifies before it drops the control file —
exit code 0 then means the bytes are right, not merely that the bytes arrived.

**Applies when:** any model file fails to load with a JSON/safetensors parse
error, any download was interrupted by a crash or reset, or a file's size looks
right but its contents behave like noise. Do not trust the file size, and do not
conclude "the file is truncated" — check for holes.

**Do not** reach for `--allow-overwrite` to "fix" this. It makes aria2 discard
the control file and re-fetch from zero, throwing away the segments that are
already correct. Plain `--continue=true` plus the surviving control file is the
resume path.
