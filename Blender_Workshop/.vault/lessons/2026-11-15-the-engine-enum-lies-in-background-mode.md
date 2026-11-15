# The render-engine enum does not list Cycles in background mode — set it and catch the failure

**Date:** 2026-11-15
**Symptom:** enumerating the available render engines in a headless Blender 5.3 reported
only one engine:

```
DYN_ENGINES ['BLENDER_EEVEE']
```

even though the `cycles` add-on was enabled (`'cycles' in bpy.context.preferences.addons` →
`True`) and Cycles renders perfectly well in this install.

**Cause:** the engine list is populated dynamically by add-ons, and the enumeration taken
through `bpy.types.RenderSettings.bl_rna` / `scene.render.bl_rna` in a background process
does not reflect the registered engines. Reading the enum to decide what is available is
therefore not a reliable probe.

**Fix:** **set the engine and catch the failure**, instead of asking the enum what is
allowed:

```python
import bpy
try:
    bpy.context.scene.render.engine = 'CYCLES'
except TypeError as ex:
    # engine genuinely unavailable in this build
    raise
```

Verified on Blender 5.3.0: `scene.render.engine = 'CYCLES'` succeeds even though the enum
listing showed only `BLENDER_EEVEE`.

**Applies when:** choosing a render engine, writing a headless render script, or when a
script decides "Cycles is not installed here" from an enum listing — it is wrong.

**Related:** the engine **identifier** changed between releases: 5.x uses `BLENDER_EEVEE`,
4.2–4.5 used `BLENDER_EEVEE_NEXT`. A script written for 4.x raises on 5.x. Check
`bpy.app.version` before trusting an engine id.
