# This workspace holds no media — only instructions, skills and memory

**Date:** 2026-11-13
**Status:** active
**Decision:** The ComfyUI_Workshop workspace contains **no images, video, audio, meshes or model
files**. It holds three things only:

1. **Instructions** — `AGENTS.md`, and the skills under `.skills/`.
2. **The memory bank** — `.vault/`: lessons, decisions, model notes, recipes.
3. **The tools** — `tools/`: the scripts that boot ComfyUI and build graphs.

Generated media always lands in the **destination the user confirmed**, outside this
folder. The workspace keeps the *text* that describes how an asset was made — the prompt,
the layout boxes, the seed, the settings — and never the asset itself.

**Reason:** The user was explicit: "The asset factory workspace does not hold any media
files like pictures/video/models. It is designed to be a set of instructions and skills and
a memory bank for agents to equip with the capability to work with comfyui asset
generations." Keeping the workspace text-only means it stays small, reviewable, diffable,
and safe to put under version control — and it keeps the media next to the project the
media is for.

**Enforcement:** `.gitignore` excludes every common media extension, so a stray render
cannot be committed by accident.

**Applies when:** writing a recipe (store the prompt + settings, not the PNG), logging a
lesson (store the settings, not the output), or building a tool (never write media into
the tree).
