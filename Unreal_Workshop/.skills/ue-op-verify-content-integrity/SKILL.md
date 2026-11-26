---
name: ue-op-verify-content-integrity
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to prove a bulk content operation lost nothing — after a mass rename, a folder restructure, an import batch, or a cook. Compares map actor counts against a baseline, loads every asset, sweeps the log for broken imports, and classifies every dangling path as a harmless name-table leftover or a live broken reference. Skip if no UE MCP connection, or if the task is to perform the operation rather than prove it (ue-op-restructure-content, ue-op-relocate-assets).
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - mcp__unreal-mcp__call_tool
---

# ue-op-verify-content-integrity — prove a bulk content operation was lossless

## When to apply

- After any mass rename, folder restructure, import batch or asset-management pass
- Before telling the user "it is done" on an operation that touched many packages
- When the user asks "did anything break?" and the answer must be evidence, not a guess

## When NOT to apply

- The operation is still running — verify **after** it
- Nothing was changed yet — there is nothing to verify against
- The task is to perform the operation → `ue-op-restructure-content`

---

## Why this needs its own procedure

The obvious checks all lie. A file count matches while a map has lost its actors; a
`grep` finds old paths in binaries that are perfectly healthy; a `load_asset` call
returns `None` for packages that are fine. Every check below has a failure mode that
looks like a pass.

---

## Procedure

### 1. The baseline must exist — take it BEFORE the operation

Without a baseline there is nothing to compare against, and the actor count is the only
measurement that catches a lost map. Write it to `Saved/` (engine-owned, disposable):

```python
import unreal
MAPS = ["/Game/MapA"]
def all_actors():
    try:
        return unreal.EditorLevelLibrary.get_all_level_actors()
    except Exception:
        return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
out = {}
for m in MAPS:
    unreal.EditorLevelLibrary.load_level(m)
    actors = all_actors()
    counts = {}
    for a in actors:
        cn = a.get_class().get_name()
        counts[cn] = counts.get(cn, 0) + 1
    out[m] = {"actors": len(actors), "classes": counts}
out
```

**Count the class breakdown, not just the total.** 65 actors can be 65 actors with a
different mix — a map that silently swapped a `BP_StrategyUnit_C` for a `StaticMeshActor`
keeps the same total.

### 2. Compare the maps after the operation

Same script, same map paths at their **new** locations. Pass when both the total and
every class count match.

```python
{"actors": 130, "baseline": 130, "match": True,
 "classes": {"BP_StrategyUnit_C": 6, "StaticMeshActor": 108, ...}}
```

### 3. Load every asset — and know which `None` is normal

```python
import unreal, asyncio
ar = unreal.AssetRegistryHelpers.get_asset_registry()
paths = sorted(str(ad.package_name) for ad in ar.get_assets_by_path("/Game/", recursive=True))
failed = []
for i, p in enumerate(paths):
    try:
        if unreal.load_asset(p) is None:
            failed.append(p)
    except Exception as e:
        failed.append([p, str(e)[:120]])
    if i % 20 == 0:
        await asyncio.sleep(0)
{"total": len(paths), "failed": len(failed)}
```

**`__ExternalActors__` and `__ExternalObjects__` packages always return `None`** — they are
not standalone assets, they load with their map. A failure count equal to the OFPA
package count is a clean pass, not a failure. Filter them out before judging:

```python
real_failures = [f for f in failed if "/__ExternalActors__/" not in f and "/__ExternalObjects__/" not in f]
```

### 4. Sweep the log — this is the authoritative broken-import check

```bash
grep -iE "Skipped package|Failed to load package|Cannot find package" \
  "D:/UE/<Project>/Saved/Logs/<Project>.log" | grep -viE "aqProf|VtuneApi|WinPixGpu"
```

`FPackageName: Skipped package /Game/...` is what a **hard import that cannot be
resolved** looks like. **Zero lines is the pass condition** — across the whole log, not
just the tail.

Noise to ignore: `Failed to load 'aqProf.dll'`, `'VtuneApi.dll'`, `'WinPixGpuCapturer.dll'`
are optional profiling DLLs, and `No default SoundConcurrencyObject specified` is a
display message.

Blueprint compile failures show up as:

```bash
grep -iE "LogBlueprint.*Error|CompilerResults" "D:/UE/<Project>/Saved/Logs/<Project>.log"
```

### 5. Check the state the operation was supposed to produce

```python
ar = unreal.AssetRegistryHelpers.get_asset_registry()
redirectors = [str(ad.package_name) for ad in ar.get_assets_by_path("/Game/", recursive=True)
               if unreal.AssetRegistryHelpers.is_redirector(ad)]
```

Pass when: **zero** redirectors, and nothing left under the old paths.

### 6. Classify every dangling path — a grep alone is not a verdict

**Unreal keeps stale name-table entries forever.** An old path string stays in a
`.uasset` long after the reference it belonged to was correctly rewritten. Grepping
binaries for old paths therefore produces false positives, and a "fix every hit" pass
will corrupt healthy files.

The classifier is in `scripts/audit_dangling_refs.py`:

```bash
python "V:/04_Projects/Workshops/Unreal_Workshop/.skills/ue-op-verify-content-integrity/scripts/audit_dangling_refs.py" \
  "D:/UE/<Project>/Content"
```

It walks every `.uasset`/`.umap`, extracts the `/Game/...` path strings, and for each
one that names no package on disk it reports:

- **name-table leftover** — the corrected path is *also* present in the same file, so the
  reference was rewritten and the old string is inert. Harmless.
- **live broken** — no corrected path exists. This one needs a decision: point it at the
  right asset, or null it.

**Only the "live broken" list is work.** Everything else is noise from the original
template.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| A grep finds old paths in healthy binaries | Unreal never prunes stale name-table entries | classify (step 6); only "live broken" counts |
| A file count matches but a map lost actors | a total can hide a changed class mix | compare the class breakdown, not just the total |
| Every OFPA package "failed to load" | they are not standalone assets | filter `__ExternalActors__` / `__ExternalObjects__` out |
| A file diff says every OFPA file is missing | moving a map re-hashes the external actor package names | compare counts, never paths |
| `AssetData` has no `get_object_path()` | the Python binding exposes `package_name` | use `ad.package_name` / `ad.get_asset_name()` |
| `get_asset_by_object_path` returns an entry with no class | the asset was renamed away — the entry is a ghost | treat a `None` class as "no longer at this path" |
| `get_class()` returns `None` on an `AssetData` | same ghost case | guard before calling `get_name()` |
| A dangling path names content from another Epic template | the project never had it | it was already broken before the operation — report it, do not "fix" it by guessing |
| The log shows `Skipped package` only at the *start* | the editor resolved it once and cached it | re-read the whole log, and load every asset fresh (step 3) |

**A pre-existing broken reference is not damage you caused.** Capture the log before the
operation and compare — otherwise you will be blamed for the template's leftovers.

---

## Output contract

- per map: actor count and class breakdown, matching the baseline, or the exact delta
- every asset loads, excluding the OFPA packages that never load standalone
- the log has zero `Skipped package` and zero blueprint compile errors
- zero redirectors; nothing left under the old paths
- the dangling paths split into **name-table leftovers** (ignored) and **live broken**
  (listed, each with the holder and a proposed target)

## Related

- `ue-op-restructure-content` — the operation this verifies
- `ue-op-relocate-assets` — the export variant of the same operation
- `ue-op-find-assets` — locate content paths, including inside `.uasset` binaries
