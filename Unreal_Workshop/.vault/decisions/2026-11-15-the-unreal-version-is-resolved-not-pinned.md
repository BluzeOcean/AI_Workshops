# The Unreal version is resolved, not pinned

**Date:** 2026-11-15
**Status:** active
**Decision:** Every script, skill and tool in this workspace determines the engine version
**at run time** by scanning `C:\Program Files\Epic Games\UE_*/Engine/Build/Build.version`,
parsing `MajorVersion`/`MinorVersion`/`PatchVersion` and taking the highest tuple. No
version string is hardcoded into a path, and the launcher registry is **not** used as the
resolver.
**Reason:** UE 5.9.0 is installed and running on this machine but is **not** in
`HKLM\SOFTWARE\EpicGames\Unreal Engine\` — the registry lists 5.2, 5.4, 5.5, 5.6, 5.7 and
5.8 only. The registry is a record of *launcher* installs over time, not of what is on
disk. A registry-based resolver picks 5.8 on a machine whose current editor is 5.9, and
then produces assets the 5.9 editor cannot load. The version matters because the content
format is forward-locked to the engine that wrote it, and because the Python API and
Blueprint node ids change between releases.
**Supersedes:** —
