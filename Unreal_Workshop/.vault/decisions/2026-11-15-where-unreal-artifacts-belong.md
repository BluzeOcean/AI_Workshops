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

**Never** in `Unreal_Workshop/` — not a `.uasset`, not a `.umap`, not a picture, not a render,
not a cooked tree, not any other large or binary file. This workshop holds **skills, the
vault and the tools**: text only. Everything binary belongs to a project.

**There is deliberately no `.gitignore` in the workshop.** Nothing needs excluding, because
nothing that belongs here is media. If a file would need a `.gitignore` rule to stay out of
the tree, it does not belong here — and the answer is not to add the rule.

**Reason:** A `.uasset`/`.umap` is a binary package carrying absolute paths, a source-control
revision and internal references. It is only meaningful inside the project that owns it, so
copying one into a documentation tree breaks it. Pictures and other large files break the
other half of the bargain: the workshop travels between machines in git, and a repository of
text stays reviewable, diffable and cheap to clone. A `.gitignore` would only hide the
violation at commit time, after the file was already written where it does not belong.
The Content/Saved split matters too: `Saved/` is engine-owned and disposable — it is pruned
without warning — so a deliverable written there is lost.
**Supersedes:** —
**Superseded by:** —
