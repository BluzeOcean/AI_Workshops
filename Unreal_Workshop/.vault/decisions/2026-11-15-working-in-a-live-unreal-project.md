# Working in a live Unreal project without destroying the user's work

**Date:** 2026-11-15
**Status:** active
**Decision:** An agent that touches an Unreal project on this machine follows these rules.
They are not style preferences — each one exists because breaking it costs somebody real
work.

## Before you produce anything

**Confirm the destination.** You must know **which project** and **which folder inside it**.
Unreal projects live under `D:\UE\<Project>\`.

- The user named a project → use **exactly** that path, character for character.
- The user did **not** → **ask.** Do not guess. Do not fall back to "the last project I
  saw". Do not pick the one that happens to have an editor running.

A guessed project produces work in the wrong place **with no error to tell you**. The
project is often open in a running editor, and writing over it destroys the user's work
silently.

## The two rules that cost data

> **Never save over the asset the user has open.** Unreal's "save" writes the in-memory
> state back onto the same package. If the user has `BP_Hero` open and a script calls
> `unreal.EditorAssetLibrary.save_asset(asset, only_if_is_dirty=False)`, you have just
> overwritten their work. Save into the destination as a **new** path, or use an explicit
> save-as. Never call a plain "save" on an asset the user did not hand you.

> **Never write into `Content/` by hand.** Assets are created **through the editor** (or
> the asset tools), not by copying files into `Content/`. A `.uasset` copied in from
> outside loses its package metadata, its source-control state, and often its references.
> The destination inside a project is a content folder, but the *means* of getting an asset
> there is the editor.

## While the editor is running

- **Never kill an editor the user started.** Check the PID *and* the command line first.
  Restarting the editor is the user's call. If an instance is wedged, ask.
- **Never write into a live level or session by accident.** No "reset the level", no
  "clear the world", no "new blank map" — not even "to start clean". Start from what is
  there, or work in a headless commandlet against a project you were given.
- **The running editor is a shared resource.** Two agents — or an agent and a human — can
  hit the same editor. Assume the level may change under you: read what you need
  immediately before you act, and re-read after anything slow. **Never restart it to "get a
  clean slate."**

## Two things that look like what they are not

- **A deleted asset in the editor is not a deleted file.** Deleting a referenced asset
  leaves a **redirector** behind, and the file may survive in source control. Check
  `git status` in the project before assuming anything was removed.
- **Autosaves are not the destination.** `Saved/Autosaves` and `Saved/Backup` hold recovery
  copies of the user's level. They are disposable and the engine prunes them. Never treat
  one as a deliverable, and never restore one over the user's work without asking.

**Reason:** An Unreal editor session holds the user's actual, unsaved, in-progress work,
and Unreal's tooling is happy to overwrite it without complaint. Every one of these rules
guards a failure mode that is *silent* — no error, no log line, and the damage is only
visible when the user notices something missing. The rules also exist because the safe
alternative always exists: ask, or work headless (`ue-op-run-headless`) against a project
you were given.

**Supersedes:** —
**Superseded by:** —

**Reuse when:** any task that writes into an Unreal project, touches a running editor, or
saves an asset.
