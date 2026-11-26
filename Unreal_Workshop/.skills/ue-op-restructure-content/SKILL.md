---
name: ue-op-restructure-content
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to reorganise a project's existing content tree under a new root folder — every top-level content folder moved beneath one new parent, in place, with the project still working afterwards. Covers One-File-Per-Actor maps, the .ini paths a rename does not fix, and the redirector purge. Skip for moving a curated set out for export (ue-op-relocate-assets), for copying instead of moving (ue-op-clone-assets), or for only proving a bulk operation was lossless (ue-op-verify-content-integrity).
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

# ue-op-restructure-content — move a content tree under a new root, in place

## When to apply

- "Put everything under `ContentPack` / under a new folder" — the whole tree moves, not a
  curated set
- The project must keep working: same maps, same gameplay, same default map
- The project has **One-File-Per-Actor** maps (most UE5 projects do) and/or `.ini` paths
  that name content

## When NOT to apply

- Moving a curated set **out** for export → `ue-op-relocate-assets`
- Copying, keeping the originals → `ue-op-clone-assets`
- You only need to *prove* a bulk operation was lossless → `ue-op-verify-content-integrity`
- Only fixing a path reference → `ue-op-fix-compile-error`

---

## The decision that saves the whole task

**Do not move the files in Windows Explorer.** Move them with the editor's own rename,
then delete the leftovers at Explorer level.

A raw file move strands every reference, because **Unreal does not create a redirector for
a file it did not move itself** — verified by test: move a `.uasset` on disk while the
editor is running, rescan the asset registry, and no `ObjectRedirector` appears at the old
path. The references point at a package that no longer exists, and there is no repair
handle. The editor's `Move` rewrites every reference project-wide and leaves a redirector
where a referencer could not be rewritten, so there is always something to fix.

The user's instinct ("Explorer, then repair the pointers by hand") is right about the
*goal* — no stale old-path references — and wrong about the *route*. The editor's route
reaches the same end state with the references already correct.

---

## Procedure

### 1. Resolve the project and its engine — never hardcode either

```bash
find "C:/Program Files/Epic Games" -maxdepth 1 -name "UE_*" -type d | sort -V | tail -1
```

The engine source is the authority for path rules and is worth reading (step 8).

### 2. Capture the baseline BEFORE touching anything

This is the only evidence that the operation was lossless. Per map: the actor count and
the class breakdown.

```python
import unreal
MAPS = ["/Game/MapA", "/Game/MapB"]
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

**Write it to `Saved/`** — it is the reference for the whole task, and it is disposable
(engine-owned), not a project artifact.

### 3. Back up `Content/` and `Config/` outside the project

```bash
cmd //c robocopy D:/UE/<Project>/Content D:/UE/_backups/<Project>_Content //E //NFL //NDL //NJH //NJS //NP //MT:16
```

> Git Bash rewrites `/E`-style switches into paths (`E:/`) — use `//E`, or set
> `MSYS_NO_PATHCONV=1`.

### 4. Find the folders to move, and what references them

```bash
find Content -maxdepth 1 -type d | sed 's|^Content/||'
grep -rn "/Game/" Config/*.ini
```

Two things to establish here:

- the **top-level folders** that move, and the new root (create it first:
  `EditorToolset.AssetToolset.CreateFolder(path="/Game/ContentPack")` — `Move` returns
  false if the destination already exists)
- every `.ini` line that names content — **a rename does not touch `.ini`** (step 7)

### 5. Move, one top-level folder at a time

```python
# one execute_python call per folder; Move recurses into subfolders
for old, new in [("/Game/Characters", "/Game/ContentPack/Characters"),
                 ("/Game/Cursor",     "/Game/ContentPack/Cursor")]:
    if not await call_tool("EditorToolset.AssetToolset.Move", path=old, newPath=new):
        raise RuntimeError("move failed: " + old)
```

Move **every** folder in the set before checking anything: each `Move` rewrites
references project-wide, so a reference from folder A to folder B is rewritten by
whichever move happens last, and a partial set leaves a window in which a reference is
briefly wrong.

**What is left at the old path after a move is the signal.** An asset that nothing
referenced moves cleanly and its old folder disappears. An asset that *was* referenced
leaves a small `ObjectRedirector` at the old path — that is the whole list of references
the rename could not rewrite.

### 6. Purge the redirectors — on the OLD path

```python
await call_tool("EditorToolset.AssetToolset.FixUpRedirectors",
                path="/Game/Characters", bDeleteRedirectors=True)
```

`FixUpRedirectors` searches **recursively under the path you give it**, so pass the
*emptied old folder*, not the new one. It rewires every reference that still points at a
redirector to point at the final asset, then deletes the redirector.

**Then delete the emptied old folders at Explorer level** — that is the "no stale old
path" the user wants, and the redirectors are the only thing that was still there:

```bash
for d in Characters Cursor LevelPrototyping; do
  find "Content/$d" -depth -type d -empty -delete 2>/dev/null
done
```

### 7. Fix the `.ini` paths by hand — the rename does not

| Setting | File |
|---|---|
| `GameDefaultMap`, `EditorStartupMap`, `GlobalDefaultGameMode` | `Config/DefaultEngine.ini` |
| `SimpleMapName` | `Config/DefaultEditor.ini` |
| `ContentBrowserTab1.SelectedPaths` | `Config/DefaultEditorPerProjectUserSettings.ini` |

**Order matters — the editor rewrites its own settings on exit**, so:

1. save every dirty package: `unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)`
2. `EditorToolset.EditorAppToolset.ExitEditor(bDiscardUnsavedChanges=False)`
3. **then** edit the `.ini` files
4. restart the editor

Editing `DefaultEditorPerProjectUserSettings.ini` while the editor runs is pointless —
the exit overwrites it.

### 8. Know where the One-File-Per-Actor packages go

UE stores each map's external actors in `Content/__ExternalActors__/<path>/<map>/...`,
and the path rule is in the engine source — read it, do not infer it:

```bash
grep -rn -A 20 "FString ULevel::GetExternalActorsPath" \
  "<ENGINE>/Engine/Source/Runtime/Engine/Private/Level.cpp"
```

The rule is `MountPoint + "__ExternalActors__/" + PackagePath + ShortName`, so
`/Game/TopDown/Lvl_TopDown` lives at `/Game/__ExternalActors__/TopDown/Lvl_TopDown`, and
moving it to `/Game/ContentPack/TopDown/Lvl_TopDown` puts its actors at
`/Game/__ExternalActors__/ContentPack/TopDown/Lvl_TopDown` — **not**
`/Game/ContentPack/__ExternalActors__/...`.

The editor's `Move` applies this automatically. A manual file move does not, and every
actor in the map is orphaned.

**Moving a map re-hashes the external actor package names** — the GUID filenames and
their hash folders all change. A before/after file-path diff of the OFPA tree therefore
always shows every file "missing". **Compare counts and actor lists, never paths.**

### 9. Restart and verify

See `ue-op-verify-content-integrity` for the verification procedure — actor counts
against the baseline, a load-every-asset pass, and the log sweep.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `tool_name` "not found" | the dispatcher wants the **bare** tool name plus `toolset_name` | `tool_name="Move"`, `toolset_name="EditorToolset.AssetToolset"`; a fully-qualified `Toolset.Tool` in `tool_name` fails |
| `RenameFolder` renamed actor folders, not content | it is the **outliner** folder renamer | the content move is `EditorToolset.AssetToolset.Move` |
| `Move` returned false | the destination folder already exists | `CreateFolder` first, or move per asset |
| Old path still holds a tiny `.uasset` | it is an `ObjectRedirector` — a reference the rename could not rewrite | `FixUpRedirectors(oldPath, bDeleteRedirectors=True)` |
| `FixUpRedirectors` did nothing | it searches under the path given | pass the **old** folder, not the new one |
| The map's actors vanished | the OFPA tree did not follow the map | it must sit at `__ExternalActors__/<new path>/<map>/` (step 8) |
| Every OFPA file reads as "missing" | moving a map re-hashes the package names | compare counts, not paths |
| The default map did not load | `.ini` still names the old path | fix `.ini` by hand — the rename never touches it (step 7) |
| `.ini` edits were reverted | the editor rewrites its settings on exit | edit `.ini` **after** `ExitEditor` (step 7) |
| An asset's name changed that should not have | a **pre-existing** redirector in the project collapsed into its target during the move | the redirector becomes the real asset and its target is deleted — rename it back if the original name mattered |
| `load_asset` returned None for `__ExternalActors__` packages | they are not standalone assets | normal — they load with their map |

---

## Output contract

- every moved asset is under the new root, and the old folders are gone from disk
- **zero** redirectors remain anywhere in the project
- the `.ini` paths name the new locations
- the editor restarts and loads the new default map
- the actor counts match the baseline exactly, and the class breakdowns match
- the log has no `Skipped package` and no blueprint compile errors

## Related

- `ue-op-verify-content-integrity` — the proof that the operation was lossless
- `ue-op-relocate-assets` — the same `Move` machinery, for a curated set moving out for export
- `ue-op-find-assets` — locate content paths, including inside `.uasset` binaries
