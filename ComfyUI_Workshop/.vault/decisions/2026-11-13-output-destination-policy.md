# The destination is always confirmed, never assumed

**Date:** 2026-11-13
**Status:** active
**Decision:** An agent working in this workspace must know the destination folder for a
generation task before it generates anything. If the user has not stated one, the agent
**asks**. It does not default to a known folder, does not reuse the destination from an
earlier task in the same session, and does not pick "somewhere sensible".

**Reason:** The user stated it directly and separately from everything else: the output
destination is the single most important parameter of the task. It is also mechanically
enforced — ComfyUI pins the destination to `--output-directory` at boot and refuses to
write outside it (see the lesson `2026-11-13-destination-is-a-boot-setting.md`). A guessed
destination means the work is in the wrong place, and re-running it costs a model load.

**What this is not:** it is not a reason to stall when the user already told you. If the
destination is in the request, use it and say which one you used.

**Current destination for the concept-art run:** `V:\04_Projects\EpicJam2026\MechConcept Art`
(given by the user on 2026-11-13).
