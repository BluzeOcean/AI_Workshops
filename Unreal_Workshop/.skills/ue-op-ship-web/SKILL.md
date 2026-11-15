---
name: ue-op-ship-web
description: Use when a verified Unreal web stage has to be turned into something a user or a host can consume — a zip without the Brotli siblings, a double-click launcher that serves the stage with COOP/COEP and opens the browser, and the hosting requirements (SharedArrayBuffer, cross-origin headers, itch.io embed options). Skip when the stage still has to be built (use ue-op-build-web) or only has to be proven in a browser (use ue-op-verify-web).
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# ue-op-ship-web — package a verified web stage for a host

**Never upload or publish it yourself.** The user owns the hosting account and
the deployment decision; produce the artifacts and hand them over.

---

## When to apply

- "zip it up", "make it uploadable", "send me the files for itch.io"
- the user wants a double-clickable way to play the build locally

## When NOT to apply

- the stage has not been verified yet → `ue-op-verify-web` first
- the stage does not exist → `ue-op-build-web`

---

## Procedure

### 1. Zip the stage

```powershell
& 'C:\Program Files\Epic Games\UE_5.9\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' `
  V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-ship-web\scripts\make_web_zip.py `
  --stage D:\UE\EpicJam2026\Saved\WasmWeb7 `
  --out   D:\UE\EpicJam2026\Saved\EpicJam2026-Web.zip
```

Output: `ZIP entries=26 uncompressed=174.3 MB -> 73.6 MB`.

**Skip the `.br` files.** The stage contains Brotli-compressed siblings
(`*.br`) that the page prefers *only* when the server advertises
`Content-Encoding: br`. A zip that carries them works only on a host that
serves them with that header; a zip without them works everywhere, because the
loader falls back to the plain file. The plain files are bigger on the wire,
but they never break.

### 2. Local launcher

The package step already writes `Play_<Project>_<Stage>.bat` and `serve.py`
into `<project>/Saved`. The launcher finds a Python 3.8+ (tries `py -3`,
`python`, `python3`, then the engine's own Python via the registry), serves the
stage on port 8936 with the COOP/COEP headers the page needs, opens the
browser, and stops the server ~10 s after the game tab closes.

### 3. Deliver into the folder the user names

When the user names a destination folder ("put the build on the Desktop"), that folder is
**theirs**, and its path is **an argument, never a constant**. Do not bake a project path
into a script, a launcher or a skill: the same procedure has to work for the next project.

- **Read what is already there first.** A previous build is the user's work, not clutter:
  move it into `version 1` (or ask which name they want) rather than deleting it, then
  put the new stage in `version 2`. One folder per version, the newest named last.
- **Copy the stage, do not move it.** The stage under `Saved/<Stage>` stays the source of
  truth for the next rebuild; the delivered folder is a copy that the user can move, zip
  or hand to a host.
- **Make the folder self-contained.** Copy `serve.py` into it next to `index.html` and
  write the launcher against `%~dp0serve.py`, so the folder still runs after it is moved
  off this machine or the project is deleted. Take the port as an optional argument.
- **Write a `VERSION.txt`** into it: build time, engine and tier, stage name, the map token
  that the page opens on, what changed since the previous version, how to run it, and the
  payload sizes. It is the only record the delivered folder carries.
- **Serve the delivered folder — not the stage — when you verify.** The copy is what the
  user will open; a path that broke in the copy (a space in `version 2`) has to fail in
  front of you.

```powershell
# the destination is a parameter; there is no default that points at this machine
$dest = '<user-named folder>\version N'
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item "$stage\*" $dest -Recurse -Force
Copy-Item "<workshop>\..\..\<project>\Tools\serve_web_lab.py" "$dest\serve.py" -Force
```

Space in a path is a live hazard here: `Start-Process -ArgumentList` splits on spaces, so
`"C:\...\version 2"` arrives as `C:\...\version` and the server answers *stage not found*.
Quote the whole argument inside the argument list.

### 4. Hosting requirements

| Requirement | Why | Where |
|---|---|---|
| `Cross-Origin-Opener-Policy: same-origin` | SharedArrayBuffer | server config |
| `Cross-Origin-Embedder-Policy: require-corp` | SharedArrayBuffer | server config |
| HTTPS | SharedArrayBuffer needs a secure context | host |
| "SharedArrayBuffer support" enabled | itch.io embed option | itch.io embed panel |
| `.wasm` served as `application/wasm` | streaming instantiation | server config |

The local `serve.py` sets the COOP/COEP headers for you; a static host must be
configured separately. itch.io's embed panel has an explicit checkbox for
SharedArrayBuffer support — it must be on, or the page will not start.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| page does not start on the host | SharedArrayBuffer blocked | enable COOP/COEP (+ HTTPS), tick itch.io's SharedArrayBuffer option |
| page starts but the engine never boots | `.wasm` served with the wrong MIME type | serve `.wasm` as `application/wasm` |
| download is much larger than the stage | the `.br` siblings were zipped | exclude `*.br` (the loader falls back to the plain files) |
| the zip is far bigger than expected | the stage contains `-Debug` payloads | ship the public stage only; `-Debug` never deploys |
| the browser loads an old build | the service worker cached the payload | hard-reload, or bump the cache/URL |

---

## Output contract

- a zip containing the public stage files (no `.br`, no debug payloads)
- a launcher `.bat` next to `serve.py` that starts the game locally
- the hosting requirement list handed to the user with the file paths

## Related

- `ue-op-build-web` — produces the stage
- `ue-op-verify-web` — proves it runs before shipping