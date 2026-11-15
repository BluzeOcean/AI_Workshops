# The Blender version is resolved, never pinned

**Date:** 2026-11-15
**Status:** active
**Decision:** Any script, tool or skill in this workspace picks the **newest Blender
installed** at run time. It does not hardcode `5.3`, and it does not hardcode
`C:\Program Files\Blender Foundation\Blender 5.3\blender.exe`.

Resolution order:

1. **Inside a running Blender** — `bpy.app.binary_path` is the executable actually in use;
   `bpy.app.version` is its version tuple. This is the authority.
2. **From the shell** — scan `C:\Program Files\Blender Foundation\Blender */blender.exe`,
   ask each candidate for `--version`, and take the highest. Compare on the **version
   tuple**, not the folder name.

A tool that resolves the version **updates its own path** when it finds a newer install,
and says so in its output. A skill that names a fixed version says the same thing in its
body.

**Reason:** the user asked for it directly: *"right now i'm using blender 5.3 the latest
one, so dont mistake it to use the 5.2 version. in fact make it check for the latest
version installed and use that (self update the skill's path if it finds a newer version
installed)."* The machine already has two versions side by side — 5.3.0 (current release)
and 5.2.1 LTS — so a hardcoded path is wrong the moment Blender updates, and Blender
updates often.

Blender's Python API is versioned and the changes are not additive: the EEVEE engine
identifier, operator names and parts of the compositor and node APIs have all moved between
releases. A tool pinned to a version is a tool that quietly produces different results
depending on when it was written.

**Applies when:** writing any tool, skill or script that launches Blender; reviewing one
that pins a path.

**Related:** `../lessons/2026-11-15-the-engine-enum-lies-in-background-mode.md`.
