# The destination is a boot-time setting, not a per-save path

**Date:** 2026-11-13
**Symptom:** It is natural to assume you can point a single `SaveImage` node at any folder
by giving `filename_prefix` an absolute path, and to write files anywhere the script has
permission to touch.

**Cause:** ComfyUI will not allow it. `folder_paths.get_save_image_path()` does:

```python
subfolder = os.path.dirname(os.path.normpath(filename_prefix))
filename  = os.path.basename(os.path.normpath(filename_prefix))
full_output_folder = os.path.join(output_dir, subfolder)

if not is_within_directory(output_dir, full_output_folder):
    raise Exception("**** ERROR: Saving image outside the output folder is not allowed.")
```

So the destination is **fixed when the server boots** (`--output-directory`), and anything
outside it raises. An absolute `filename_prefix` does not escape it.

**Fix:**

1. **Ask for the destination before booting.** If the user did not say where, ask — do not
   guess, do not default, do not reuse the last one.
2. Boot with it: `pwsh -File tools\boot-comfyui.ps1 -OutputDir "<DESTINATION>"`.
3. The boot script warns when a *running* server was started with a different destination.
   That warning is correct — resolve it rather than ignoring it.
4. Changing the destination later means a restart of the instance **this workspace** owns
   (`-Restart`, tracked in `tools\.comfyui.pid`). Never restart the user's own instance.

**Applies when:** a task needs its output somewhere other than the server's current
`--output-directory`, or a render "vanished" from where it was expected.

**Related:** the same principle drives the input side — `--input-directory` decides which
folder `LoadImage` can read from.
