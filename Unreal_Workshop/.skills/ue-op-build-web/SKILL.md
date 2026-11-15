---
name: ue-op-build-web
description: Use when the task is to produce or rebuild a browser-playable build of an Unreal project — cook, package and stage a UE 5.9 Wasm/WebGPU web build, fix the map the page opens, and release-scan the stage folder. Skip when the task is only to change content inside the editor, only to verify a stage that already exists (use ue-op-verify-web), or only to zip/upload an already-verified stage (use ue-op-ship-web).
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# ue-op-build-web — cook, package and stage a UE web build

UE 5.9's browser target is **Wasm + WebGPU**, not WebGL. WebGL was the UE4
HTML5 path and no longer exists in UE5. The shipped tier is forward-shader
`SP_WEBGPU_ES3_1`; `SP_WEBGPU_SM5` (deferred/SM5/compute) exists only as an
experimental desktop tier. If the user says "webgl build", they mean this.

The whole pipeline is one UAT invocation plus two fix-ups. The fix-ups are the
part that is easy to forget and that silently ships the wrong map.

---

## When to apply

- "build a web version", "make it runnable in a browser", "package for itch.io"
- a content change has to reach a web build
- the map the page opens is wrong, or the page opens an empty level

## When NOT to apply

- The task is only to edit content/blueprints → do that in the editor, then use
  this skill to rebuild
- The stage already exists and only needs checking → `ue-op-verify-web`
- The stage is verified and only needs zipping/upload → `ue-op-ship-web`
- The project has no `Wasm` platform support (no `Engine/Platforms/Wasm` in the
  engine install) → that engine cannot build for the browser at all

---

## Fast path

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-build-web\scripts\build_web.ps1" `
  -Project "D:\UE\EpicJam2026" -Map "/Game/Map/MeshTerrain" -Stage "WasmWeb7"
```

The script does all five steps below and ends with the release scan. It takes
**4–6 minutes**, of which ~221 s is Brotli compression of the payload and ~1 min
is the emscripten link — that is the long tail, not a hang.

---

## Procedure

### 1. Preconditions

```powershell
Get-Content "D:\UE\EpicJam2026\EpicJam2026.uproject" | Select-String "EngineAssociation"
Test-Path "C:\Program Files\Epic Games\UE_5.9\Engine\Platforms\Wasm"
Test-Path "D:\emsdk-6.0.10"   # emscripten 6.0.10 exactly
```

`EngineAssociation` must be `5.9`. The emsdk version must match the engine's
`Engine/Platforms/Wasm/Build/…` expectation — 6.0.10 for this engine.

### 2. Set the emsdk root inline, every time

```powershell
$env:WASM_EMSDK_ROOT = 'D:\emsdk-6.0.10'
```

The agent shell's `WASM_EMSDK_ROOT` is stale — always set it in the same
invocation as the build.

### 3. Cook + package

```powershell
& 'C:\Program Files\Epic Games\UE_5.9\Engine\Build\BatchFiles\RunUAT.bat' `
  BuildCookRun -project=D:\UE\EpicJam2026\EpicJam2026.uproject `
  -platform=Wasm -clientconfig=Shipping -cook -stage -pak -iostore -package `
  -archive -archivedirectory=D:\UE\EpicJam2026\Saved\WasmWeb7 `
  -map=/Game/Map/MeshTerrain `
  -AdditionalCookerOptions="-unattended -nopause -nosplash -nullrhi" `
  -nocompileeditor -unattended -utf8output
```

- `-map=` is what selects the level that gets cooked; without it the whole
  project is cooked.
- `-nocompileeditor` keeps the build from rebuilding the editor target.
- The editor may stay open during the build — but the **map must be saved
  first**, or the cook reads the older on-disk level.
- Check the exit code (`$LASTEXITCODE`), and grep the log for `BUILD SUCCESSFUL`.

### 4. Re-patch the map token — UAT overwrites it

```powershell
Set-Content -Path 'D:\UE\EpicJam2026\Saved\WasmWeb7\UECommandLine.txt' `
  -Value '/Game/Map/MeshTerrain -project="../../../EpicJam2026/EpicJam2026.uproject"' `
  -Encoding utf8 -NoNewline
```

**UAT rewrites the staged `UECommandLine.txt` on every package.** The page
builds the engine command line as `[map] + queryArgs + stagedArgs + defaults`,
so the **first token of that file is the only thing that selects the map** —
`GameDefaultMap`, `?args=` and page arguments all arrive too late to be read
as a map. Skip this step and the build boots the default map, which looks
exactly like "my level is empty".

### 5. Release-scan the stage

```powershell
& 'C:\Program Files\Epic Games\UE_5.9\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' `
  'C:\Program Files\Epic Games\UE_5.9\Engine\Platforms\Wasm\Build\Tools\deploy\check_stage.py' `
  D:\UE\EpicJam2026\Saved\WasmWeb7
```

Run it **with python** — PowerShell refuses to execute a `.py` file directly
("Cannot run a document in the middle of a pipeline"). Expect
`release scan: 0 findings, 1 warnings`; the warning about a stock engine font
path is benign.

---

## What the stage folder contains

| File | Meaning |
|---|---|
| `index.html` + `*.js` | the page and the loader glue |
| `EpicJam2026/Binaries/Wasm/*.wasm` / `*.js` | the engine payload |
| `EpicJam2026/Content/Paks/*` | cooked content (pak + iostore `.utoc`/`.ucas`) |
| `UECommandLine.txt` | **the map token** — re-patched in step 4 |
| `wasm-tiers.json` | which tiers shipped (`forward` only by default) |
| `wasm-manifest.json` / `wasm-cache.json` | file lists + sha1s the loader checks |

The package step also writes `Play_<Project>_<Stage>.bat` and `serve.py` into
`<project>/Saved`, and moves debug files to `<Stage>-Debug` (never deployed).

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Page boots the default/empty map | UAT rewrote `UECommandLine.txt` during packaging | re-patch the map token **after every package** (step 4) |
| Page loads but the level is empty | `GameDefaultMap` / `?args=` used instead of the staged token | the staged file's first token is the only map selector |
| `check_stage.py` fails to start | executed as a document | run it with `python` |
| Build fails with an emsdk error | stale/absent `WASM_EMSDK_ROOT` | set it inline to the exact version (step 2) |
| Build succeeds but the page 404s on the wasm | `UECommandLine.txt` re-patch broke the file | keep it single-line, UTF-8, no BOM |
| Cook log: "missing compiled sections … Cooked builds will not show these missing regions" | the MeshPartition plugin has no built sections | expected; see `ue-op-bake-mesh-partition` |
| Editor shows the old level after a rebuild | level not saved before cooking | save in the editor, then cook |
| `wasm-tiers.json` lists `sm5`/`deferred` unexpectedly | `bTargetDesktopTier=True` in `Config/DefaultEngine.ini` | set it back to `False` for the shipping tier |

---

## Output contract

- `<project>/Saved/<Stage>/` exists and contains the payload
- `<Stage>/UECommandLine.txt` starts with the requested map
- the release scan reports **0 findings**
- `<Stage>/wasm-tiers.json` shows the expected tier set
- the UAT log ends with `BUILD SUCCESSFUL`

Verify the stage with `ue-op-verify-web` before shipping it.

## Related

- `ue-op-verify-web` — prove the stage runs in a real browser
- `ue-op-ship-web` — zip / launcher / hosting headers
- `ue-op-bake-mesh-partition` — getting Mesh Terrain geometry into the stage
