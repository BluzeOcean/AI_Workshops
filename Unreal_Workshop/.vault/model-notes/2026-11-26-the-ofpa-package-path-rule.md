# Where a map's external actor packages live

**Status:** active
**Recorded:** 2026-11-26 — verified against UE 5.9 source

UE stores the actors of a One-File-Per-Actor map in packages under
`Content/__ExternalActors__/<the map's path>/<the map's name>/<hash>/<hash>/<guid>.uasset`.
The path is computed by `ULevel::GetExternalActorsPath` in
`Engine/Source/Runtime/Engine/Private/Level.cpp`:

```
MountPoint + "__ExternalActors__/" + PackagePath + ShortName
```

So `/Game/TopDown/Lvl_TopDown` → `/Game/__ExternalActors__/TopDown/Lvl_TopDown`, and
moving that map to `/Game/ContentPack/TopDown/Lvl_TopDown` puts its actors at
`/Game/__ExternalActors__/ContentPack/TopDown/Lvl_TopDown` — **not**
`/Game/ContentPack/__ExternalActors__/...`. The `__ExternalActors__` folder sits at the
**mount point root**; the map's whole path is appended after it. `__ExternalObjects__`
follows the same rule.

Two consequences that cost time when unknown:

- The editor's `Move` applies this itself. A **manual file move does not**, and every
  actor in the map is then silently orphaned — the map still opens, with fewer actors.
- **Moving a map re-hashes the external actor package names.** The GUID filenames and
  their hash folders all change, so a before/after file-path diff of the tree reports
  every file "missing". **Compare counts and actor lists, never paths.**

Read the rule from the engine source; do not infer it from a directory tree — the tree
gives one example, not the rule.

**Related:** [`ue-op-restructure-content`](../../.skills/ue-op-restructure-content/SKILL.md),
[`ue-op-verify-content-integrity`](../../.skills/ue-op-verify-content-integrity/SKILL.md).
