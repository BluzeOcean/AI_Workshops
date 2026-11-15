---
name: ue-op-verify-web
description: Use when a staged Unreal web build exists and the task is to prove it actually runs in a browser — headless Chrome boot with WebGPU error counting and screenshot capture, an optional visible Chrome window the user can review, and clean server teardown. Skip when the stage still has to be built (use ue-op-build-web) or only has to be zipped for hosting (use ue-op-ship-web).
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# ue-op-verify-web — prove a staged web build runs

A stage that scans clean is not a stage that works. The only trustworthy
oracle for "does the game actually show my level" is a **screenshot of the
running web build**.

**Do not trust the editor viewport for this.** The UE editor draws an
*infinite world grid* at z=0, so a beauty render of any flat map looks like a
giant grid plane — hiding the MeshPartition actor *and* the baked terrain
actors changes nothing, because that grid is the editor's, not the game's.

---

## When to apply

- "does the build work?", "I can't see my level in the browser"
- after every content change that has to be visible in the build
- before handing a stage to the user or to a host

## When NOT to apply

- the stage does not exist yet → `ue-op-build-web`
- the stage is already verified and only needs shipping → `ue-op-ship-web`

---

## Procedure

### 1. Headless run — the fast proof

```powershell
& 'C:\Program Files\Epic Games\UE_5.9\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' `
  'C:\Program Files\Epic Games\UE_5.9\Engine\Platforms\Wasm\Build\Tools\web\webrun.py' run `
  --stage D:\UE\EpicJam2026\Saved\WasmWeb7 `
  --fixture boot --out D:\UE\EpicJam2026\Saved\WasmTest7 `
  --net none --headless --shots 8,14,20 --timeout 300 --expect-tier forward
```

Expected output:

```
{"exit": null, "abort": null, "timed_out": false, "webgpu_errors": 0, "pass": true, "exit_code": 0, "reasons": []}
webrun WasmTest7: PASS | world None | config ? ? | ready 2.938 s | heap peak 512 MiB
```

- `pass: true` **and** `webgpu_errors: 0` — both must hold
- `ready <n> s` is the time to first frame; a page that boots but shows an
  empty level still reports PASS, so this number says nothing about content
- screenshots land in `--out` as `t008s.png`, `t014s.png`, `final.png`

### 2. Look at the screenshots

Read the PNGs in `--out`. They are the only evidence that the level content is
actually on screen. A sky-only frame means the level did not load (wrong map
token) or the content is not being drawn.

### 3. Optional: the experimental desktop tier

Only when `Config/DefaultEngine.ini` has `bTargetDesktopTier=True` (it must be
set **before** the cook, so this is a diagnostic, not a shipping tier):

```powershell
... webrun.py run --stage <stage> --out <out> --headless --query tier=desktop --expect-tier desktop
```

The staged `wasm-tiers.json` records which tiers shipped — `{"sm5":true,...}`
means the desktop tier was staged.

### 4. Visible Chrome, for the user to review

```powershell
# serve (COOP/COEP headers are required by the page)
Start-Process -FilePath 'C:\Program Files\Epic Games\UE_5.9\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' `
  -ArgumentList '-I','-B','serve.py','--root','WasmWeb7','--port','8936','--port-tries','5' `
  -WorkingDirectory 'D:\UE\EpicJam2026\Saved' -WindowStyle Hidden

Start-Sleep -Seconds 4
Get-NetTCPConnection -LocalPort 8936 -State Listen   # must be listening
Start-Process 'C:\Program Files\Google\Chrome\Application\chrome.exe' `
  -ArgumentList '--new-window','http://127.0.0.1:8936/index.html?ue-session=1'
```

`serve.py` is written next to the stage by the package step (it also exists at
`Engine\Platforms\Wasm\Build\Tools\web\serve.py`). The page needs
`?ue-session=1` so the session cookie/URL is set up.

### 5. Tear the server down

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like '*serve.py*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Get-NetTCPConnection -LocalPort 8936 -State Listen   # must be empty
```

Always release the port — a leftover server blocks the next run and holds the
port the user may want.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `pass: true` but the frame is empty | the map token was not re-patched, or the level is empty | re-run `ue-op-build-web` step 4, then check the screenshots |
| Editor render shows a grid "terrain" that is not in the build | the editor's infinite world grid | judge by the web screenshot only |
| `webgpu_errors > 0` | a shader/feature failed to compile on the tier | check the console output in the `--out` folder |
| page loads but nothing renders, no errors | the page still needs the click-to-start gesture | click in the visible tab; the headless fixture drives this itself |
| `expect-tier` mismatch | the stage shipped a different tier set | read `wasm-tiers.json` in the stage |
| `serve.py` exits immediately | another server already owns the port | `Get-NetTCPConnection -LocalPort 8936` and kill it first |
| Chrome shows a stale build | the service worker cached the old payload | hard-reload (Ctrl+Shift+R) or use a fresh `--port`/`--out` |

---

## Output contract

- a `PASS` line with `webgpu_errors: 0`
- screenshots in the `--out` folder that **show the level content**
- for a visible review: a live Chrome window on `http://127.0.0.1:8936/` and,
  afterwards, port 8936 released

## Related

- `ue-op-build-web` — produces the stage this skill verifies
- `ue-op-ship-web` — packages a verified stage for hosting
- `ue-op-capture-editor` — editor-side screenshots (different question)
