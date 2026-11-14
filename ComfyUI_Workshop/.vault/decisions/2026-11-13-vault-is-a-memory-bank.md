# The vault is a memory bank: written AFTER a task, searched when something breaks

**Date:** 2026-11-13
**Status:** active
**Decision:** `.vault/` is a **memory bank** — a running record of what worked and what did
not, so a future agent can trace the history and solve a problem that has already been
solved.

- It is **written after a task completes**, not read at the start of one. Reading it
  pre-emptively burns context on a log that is mostly irrelevant to the current task.
- It is **searched** when something goes wrong, when the user asks what has worked before,
  or before repeating an expensive operation.
- Every task that produces a durable fact logs at least one entry — including a task that
  went perfectly well. "This model, at these settings, with that layout and seed, produced
  a good result" is exactly what the next agent needs and cannot re-derive.
- Entries are **append-only**. Never overwrite a lesson; add a new one and mark the old
  decision `superseded`, so the history of what was true stays readable.

**Reason:** The user defined the vault this way: "the .vault is a log / memory system that
will store the memories of what works and what doesn't, its like a memory bank. so future
agents can trace it. its not an active read for the agents working with this workspace.
its a user request or when something goes wrong, agent can search the vault for solutions
and see if the issue has happened before and if there's a solution guide to it."

**Applies when:** finishing any task in this workspace; searching when something breaks.
