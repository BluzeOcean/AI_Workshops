# A content move leaves empty external-actor trees that git cannot show you

**Status:** active

**Date:** 2026-11-26
**Symptom:** After a content restructure that moved a map under a new root — `Content/TopDown`
became `Content/ContentPack/TopDown` — the old mount-point trees are still on disk:
`Content/__ExternalActors__/TopDown/...` and `Content/__ExternalObjects__/TopDown/...`,
alongside the new `Content/__ExternalActors__/ContentPack/...`. They hold **no files at
all** — only empty directories, a couple of hundred of them, nested down to the two-letter
shard level. `git status` shows nothing, because **git does not track empty directories**,
and a file count over the old tree returns zero, which reads as "already cleaned up".
**Cause:** Unreal writes external actor packages at
`MountPoint/__ExternalActors__/<PackagePath>/<Map>/<shard>/…`. Moving the content moves
the *packages*; nothing removes the *directory structure* they were written into. The
mount point is a separate thing from the content it describes, and the restructure moved
one and not the other.
**Fix:** After any content restructure, sweep for directory trees that contain no files
and delete their roots. The detection counts **files per directory subtree**, not
directory entries — a directory with empty children still holds no files. A walk that
tests `not dirs and not files` finds the empty leaves; the thing to delete is the
**topmost** such tree, not each leaf.
**Applies when:** a content restructure has just happened, or an agent is about to prove
one was lossless. The empty trees are not loss — they are invisible to git, invisible to
a file count, and they will make any check that compares directory listings across the
move report a difference that is not there.

**Related:** the rule for where the packages live is
[the OFPA package path rule](../model-notes/2026-11-26-the-ofpa-package-path-rule.md);
the procedure for the restructure itself is
[`ue-op-restructure-content`](../../.skills/ue-op-restructure-content/SKILL.md), and
[`ue-op-verify-content-integrity`](../../.skills/ue-op-verify-content-integrity/SKILL.md)
is what proves nothing was lost.
