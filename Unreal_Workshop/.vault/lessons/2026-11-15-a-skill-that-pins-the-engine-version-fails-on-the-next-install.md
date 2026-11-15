# A skill that pins the engine version fails on the next install

**Status:** active

**Date:** 2026-11-15
**Symptom:** Two of the workshop's own skills carried a hardcoded engine path:

- `ue-op-find-assets` searched `C:/Program Files/Epic Games/UE_5.8/Templates` for the
  canonical `IA_*` / `IMC_*` input assets, and `UE_5.8/Engine/Plugins` for the plugins
  that provide toolsets.
- `ue-op-mcp-connect` launched
  `C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe` to bring up
  the MCP server.

Neither **failed loudly**. 5.8 is installed, so the paths resolved and the commands ran —
against the *wrong* engine. The current engine on this machine is **5.9**, and 5.9 is the
one the user's projects are saved for. The MCP one is the dangerous case: it starts a
5.8 editor against a 5.9 project, which cannot load that project's assets.

**Cause:** A version written into a path is a snapshot of the machine at the moment the
skill was written. The workshop's own rule — *never hardcode a version or an install
path; resolve it at run time* — was in `.skills/README.md`, and both skills violated it.

**Fix:** Resolve the engine before using it, every time:

```bash
ENGINE=$(find "C:/Program Files/Epic Games" -maxdepth 1 -name "UE_*" -type d | sort -V | tail -1)
```

then use `"$ENGINE/..."` in place of the pinned path. In PowerShell, scan
`C:\Program Files\Epic Games\UE_*\Engine\Build\Build.version` and take the highest version
tuple — never the launcher registry, which does not list 5.9 at all.

**Applies when:** writing or editing any skill, script or tool that touches an engine
path; after any engine update; and when a skill "works" but produces results from an
older install than the one the project needs.
