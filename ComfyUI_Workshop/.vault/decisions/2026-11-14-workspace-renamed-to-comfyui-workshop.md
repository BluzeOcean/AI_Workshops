# The workspace is `ComfyUI_Workshop`

**Date:** 2026-11-14
**Status:** active
**Decision:** This workspace's folder name is **`ComfyUI_Workshop`**, matching the naming
convention of its siblings in `V:\04_Projects\Workshops\` — `Blender_Workshop`,
`Unreal_Workshop`, `Unity_Workshop`. It was previously `AssetFactory`.

**Reason:** the user renamed it for consistency with the sibling workshop folders, and
specified the capitalisation explicitly: `ComfyUI_Workshop`, capital **W** in "Workshop".

**What changed on 2026-11-14:**

- The folder on disk was renamed. The **git history is unaffected** — the repo lives *inside*
  the folder, and git tracks content, not the name of the directory that contains it. Every
  commit, branch and tag is intact.
- The name was updated in the seven places that spelled it out: `README.md`, `AGENTS.md`,
  `.gitignore`, `tools/boot-comfyui.ps1` (twice), `tools\stop-comfyui.ps1`, and this
  decision record in `.vault/decisions/2026-11-13-workspace-holds-no-media.md`.
- **No path inside the workspace changed.** Every internal reference is relative
  (`tools\…`, `.vault\…`) or uses `$PSScriptRoot`, so nothing broke and no link had to be
  rewritten. The scripts resolve their own location at runtime, not by name.

**Applies when:** an agent searches the vault or the git history for "AssetFactory" and
finds nothing but this file. The old name is history, not a live reference — do not
"restore" it.

**Note the capitalisation.** Windows paths are case-insensitive, so `ComfyUI_workshop` and
`ComfyUI_Workshop` are the *same folder* on disk and Windows will happily treat them as
identical. The capital **W** is only enforced in the **text** of the documents and scripts.
See
`.vault/lessons/2026-11-14-renaming-the-workspace-folder.md`.
