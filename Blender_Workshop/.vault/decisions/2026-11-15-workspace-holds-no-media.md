# The workspace holds no media — only instructions, skills and memory

**Date:** 2026-11-15
**Status:** active
**Decision:** The Blender_Workshop workspace contains **no `.blend` files, no renders, no
textures, no exports and no caches**. It holds three things only:

1. **Instructions** — `AGENTS.md`, and the skills under `.skills/`.
2. **The memory bank** — `.vault/`: lessons, decisions, notes, recipes, workflows.
3. **The tools** — `tools/`: the scripts that drive Blender.

Blender output always lands in the **destination the user confirmed**, outside this folder.
The workspace keeps the *text* that describes how it was made — the script, the settings,
the export options, the version — and never the artifact itself.

**Reason:** the same rule the ComfyUI workshop works under, applied to Blender. Blender
artifacts are worse offenders than renders: a `.blend` is a binary with absolute paths into
some other project, and it is the user's own working file. Keeping them out of the tree
means the workspace stays small, reviewable, diffable and safe under version control, and
it means nobody can accidentally commit a 200 MB scene or overwrite somebody's work.

**Enforcement:** `.gitignore` excludes `*.blend`, every common render and image format,
every exchange format (`.fbx`, `.obj`, `.gltf`, `.glb`, `.abc`, `.usd`, `.stl`), and
`work/`.

**Applies when:** writing a recipe (store the script + settings, not the `.blend`), logging
a lesson (store the settings, not the output), or building a tool (never write media into
the tree).

**Related:** `2026-11-15-the-destination-is-confirmed-not-assumed.md`.
