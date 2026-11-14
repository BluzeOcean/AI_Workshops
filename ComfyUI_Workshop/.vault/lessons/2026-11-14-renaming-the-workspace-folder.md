# Renaming the workspace folder needs the ComfyUI stack closed, and a two-step rename to change the capitalisation

**Date:** 2026-11-14
**Symptom:** Renaming the workspace folder from Git Bash failed twice:

```
$ mv AssetFactory ComfyUI_workshop
mv: cannot move 'AssetFactory' to 'ComfyUI_workshop': Device or resource busy
```

The first failure was a **lock**: the headless ComfyUI server was running, and
`tools\boot-comfyui.ps1` starts it with `WorkingDirectory = $PSScriptRoot` — the `tools`
folder. A running process holds its own working directory open, and Windows refuses to
rename a directory that is somebody's current directory.

The second failure was after the stack was stopped and the rename had succeeded, when the
folder had to be re-cased from `ComfyUI_workshop` to `ComfyUI_Workshop`:

```
Rename-Item -LiteralPath '...\ComfyUI_workshop' -NewName 'ComfyUI_Workshop'
FAIL: Source and destination path must be different.
```

**Cause:** two separate Windows behaviours.

1. **A live ComfyUI locks the workspace folder.** The server's working directory is the
   `tools/` folder *inside* the tree being renamed, so the rename fails with EBUSY.
2. **Windows path comparison is case-insensitive.** `Rename-Item` compares the source and
   the destination with a case-insensitive equality test, so a change of *capitalisation
   only* reads as "rename a path onto itself" and is refused. The folder's real casing on
   disk is not updated by the refusal, so the old casing persists.

**Fix:**

1. **Stop the stack first**, with the workspace's own script, before touching the folder:

   ```powershell
   pwsh -File tools\stop-comfyui.ps1
   ```

   It stops the MCP supervisor, then the ComfyUI server, and reports the ports free. (The
   queue was checked and empty first — do not kill a server that is mid-render.)

2. **Do the rename with PowerShell from outside the tree**, not with Git Bash `mv`:

   ```powershell
   Rename-Item -LiteralPath 'V:\04_Projects\Workshops\ComfyUI_workshop' -NewName 'ComfyUI_Workshop'
   ```

   Git Bash's `mv` reported `Device or resource busy` where `Rename-Item` succeeded. It
   must be run from a directory that is **not** the folder being renamed, and the calling
   shell must not be sitting inside the tree.

3. **To change only the capitalisation, rename through a temporary name** — two steps,
   because a single step is rejected as a no-op:

   ```powershell
   Rename-Item -LiteralPath '...\ComfyUI_workshop' -NewName '__tmp_ws'
   Rename-Item -LiteralPath '...\__tmp_ws'            -NewName 'ComfyUI_Workshop'
   ```

**Applies when:** the workspace folder is renamed, moved, or re-cased, or when a rename
fails with `Device or resource busy` or `Source and destination path must be different`.

**Two things that do NOT break, and do not need fixing:**

- **Git history is untouched.** The repo lives inside the renamed folder, and git tracks
  content, not the name of the containing directory. No `git mv`, no commit, no re-init.
- **No internal path needs rewriting.** Every reference inside the workspace is relative
  (`tools\…`, `.vault\…`) or resolves itself at runtime via `$PSScriptRoot`. Only the
  *name* spelled out in prose had to change.

**A stale build artefact can still hold the old path.** `tools\__pycache__\` caches a
compiled `.pyc` that embeds the absolute source path it was compiled from, so it can
contain the folder's **old** name or an older path entirely. It is git-ignored and
harmless — Python rewrites it on the next import — but do not be surprised by it, and do
not read a hit there as a live reference.
