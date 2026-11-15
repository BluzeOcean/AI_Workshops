# The destination is always confirmed, never assumed

**Date:** 2026-11-15
**Status:** active
**Decision:** An agent working in this workspace must know the destination folder for a task
before it produces anything. If the user has not stated one, the agent **asks**. It does
not default to a known folder, does not reuse the destination from an earlier task in the
same session, and does not pick "somewhere sensible".

Two rules ride on top of it:

- **Save As, never Save.** Writes go to `bpy.ops.wm.save_as_mainfile(filepath=...)` with an
  explicit path. `bpy.ops.wm.save_mainfile()` overwrites whatever file is already open —
  which, when the user has their own scene open in the running Blender, is their work.
- **Never write into the live scene by accident.** The running Blender holds the user's
  actual scene. Nothing in it gets reset, cleared or replaced without being asked for.

**Reason:** Blender will write a `.blend` to any path it is given, so a guessed destination
produces no error — it just produces the work in the wrong place. Worse, the running
instance on this machine already has a scene open with real work in it (50 objects, 25
materials, as of 2026-11-15), and the cheapest way to destroy that is an agent deciding
the destination for itself.

**What this is not:** it is not a reason to stall when the user already told you. If the
destination is in the request, use it and say which one you used.

**Related:** `2026-11-15-workspace-holds-no-media.md`.
