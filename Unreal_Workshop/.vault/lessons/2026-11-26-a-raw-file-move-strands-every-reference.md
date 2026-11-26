# A raw file move strands every reference, and Unreal creates no redirector for it

**Status:** active

**Date:** 2026-11-26
**Symptom:** After moving a `.uasset` to another folder on disk while the editor was running,
the asset registry listed the asset at its **new** path and the old path entry had **no
class** — but **no `ObjectRedirector` was created at the old path**, and no reference was
rewritten. The old path resolved to nothing and nothing was there to repair it with.
**Cause:** Unreal creates an `ObjectRedirector` only when **it** renames a package, as a
fallback for a referencer it could not rewrite. A file moved by something outside the
engine is, to the engine, a deletion plus a creation — and there is no fallback for
that. Every reference to the old path is broken with no handle to fix it.
**Fix:** Move content with the editor's own rename —
`EditorToolset.AssetToolset.Move(path, newPath)` — which rewrites references
project-wide and leaves a redirector wherever it could not. Then
`FixUpRedirectors(oldPath, bDeleteRedirectors=True)` rewires through those redirectors and
deletes them. If the files have already been moved by hand, the only repair is to
reconstruct the redirectors — and `ObjectRedirector` is **not constructible from Unreal
Python** (no class, no factory, no tool), so the route is closed.
**Applies when:** Anyone proposes moving, renaming or re-foldering `.uasset` / `.umap`
files in Windows Explorer, a file manager, a script or a git operation — and to the
reverse question, "can I repair it after a manual move?" (no, not without rebuilding the
redirectors by hand).

**Related:** the procedure is
[`ue-op-restructure-content`](../../.skills/ue-op-restructure-content/SKILL.md); the
OFPA half of the same problem is
[the OFPA package path rule](../model-notes/2026-11-26-the-ofpa-package-path-rule.md).
