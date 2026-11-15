# The vault is a memory bank: written AFTER a task, searched when something breaks

**Date:** 2026-11-15
**Status:** active
**Decision:** `.vault/` is a **memory bank** — a running record of what worked and what did
not, so a future agent can trace the history and solve a problem that has already been
solved.

- It is **written after a task completes**, not read at the start of one. Reading it
  pre-emptively burns context on a log that is mostly irrelevant to the current task.
- It is **searched** when something goes wrong, when the user asks what has worked before,
  or before repeating an expensive operation (a long render, a big scene build).
- Every task that produces a durable fact logs at least one entry — including a task that
  went perfectly well. "This approach, at this version, with these settings, produced a
  good result" is exactly what the next agent needs and cannot re-derive.
- Entries are **append-only**. Never overwrite a lesson; add a new one and mark the old
  decision `superseded`, so the history of what was true stays readable.
- Every entry that depends on the Blender API records **the Blender version it was
  verified against**. Blender's API is versioned by release and the community answers are
  heavily mixed across versions.

**Reason:** inherited from the ComfyUI workshop, where the vault proved its worth over a
long run of real tasks. A workshop that only keeps instructions re-learns the same
mistakes; a workshop that keeps a memory does not.

**Applies when:** finishing any task in this workspace; searching when something breaks.
