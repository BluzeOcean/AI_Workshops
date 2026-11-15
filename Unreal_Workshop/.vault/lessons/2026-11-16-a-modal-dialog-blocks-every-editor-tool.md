# A modal dialog blocks every editor tool, and nothing says so

**Date:** 2026-11-16
**Status:** active

## Symptom

A Python script run through the MCP bridge was deleting and recreating material
instances. The levels had been stamped with those instances a minute earlier, so:

- `EditorAssetLibrary.delete_asset` quietly refused (still referenced),
- `create_asset` with the same name raised Slate's **"Overwrite Existing Object?"**
  dialog,
- the script stopped inside that call, and the dialog stayed up.

From the outside every editor tool then answered a single canned line:

    Not run: the Unreal Editor is showing a modal dialog, which blocks editor tools.

No tool raised, no log line appeared, and the tool that "refused" had in fact not
run at all. A script that is mid-call is paused, so one dialog per asset is queued
behind the first.

## What did not work

- `SendKeys("{ESC}")` after `AppActivate` — the dialog stayed up (focus landed on the
  editor frame, not the Slate modal).
- Waiting. Nothing times out; the bridge simply declines every call.

## What worked, in order of preference

1. **Do not create over a referenced asset.** Load it, set its parameters, call
   `update_material_instance`, save. "Delete then create" is only safe while nothing
   points at the asset — which stops being true the moment a level is stamped.
2. If a dialog is already up: `AppActivate` the editor and send `{ENTER}` about twice
   per queued asset (the default button is the affirmative one). Here 14 presses
   cleared ten queued overwrites, and the next `GetCurrentLevel` call answered
   normally.

## Prevention

- Treat "delete + recreate" as a **first-run-only** script shape. A script that will
  be re-run must be idempotent by **editing in place**.
- When a tool call suddenly returns "not run", read it literally: a modal is up. Ask
  the user, or clear it, before diagnosing the script.
