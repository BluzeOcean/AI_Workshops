# Where Unreal artifacts belong — Content, Saved, or outside the project

**Date:** 2026-11-15
**Status:** active
**Decision:** Unreal output goes to one of exactly three places, and the agent confirms
which before it produces anything:

| Tier | Where | What goes there | How it gets there |
|---|---|---|---|
| **Deliverable** | `<project>\Content\<Folder>\` | assets and levels the project ships | **created through the editor** (asset tools, import, MCP), never copied in by hand |
| **Scratch** | `<project>\Saved\` | scripts, intermediate JSON, captured results, logs | written directly |
| **Export** | a path the user names, outside the project | renders, staged builds, mesh exports | written directly |

**Never** in `Unreal_Workshop/` — not a `.uasset`, not a `.umap`, not a render, not a cooked
tree. This workspace is instructions and memory; everything binary belongs to a project.

**Reason:** A `.uasset`/`.umap` is a binary package carrying absolute paths, a source-control
revision and internal references. It is only meaningful inside the project that owns it, so
copying one into a documentation tree breaks it and makes the tree unreviewable. The
Content/Saved split matters too: `Saved/` is engine-owned and disposable — it is pruned
without warning — so a deliverable written there is lost.
**Supersedes:** —
