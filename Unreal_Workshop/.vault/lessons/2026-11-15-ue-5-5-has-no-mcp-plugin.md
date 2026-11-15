# UE 5.5 has no MCP plugin

**Date:** 2026-11-15
**Symptom:** A project set to `EngineAssociation` 5.5 has no MCP endpoint, no
`mcp__unreal-mcp__*` tools, and nothing listening on 8000 — while the same commands work
against a 5.9 project.

**Cause:** Epic's `ModelContextProtocol` plugin ships with **UE 5.8 and newer only**.
Verified: `Engine/Plugins/Experimental/ModelContextProtocol/` exists in `UE_5.8` and
`UE_5.9`; the same directory in `UE_5.5` has no such entry. It is not a matter of not
enabling it — the plugin is not there.

**Fix:** On 5.5 and older, use the surfaces that need no plugin:

```powershell
& "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "D:\UE\<Project>\<Project>.uproject" -run=<Commandlet> -unattended -nosplash
```

or `-ExecutePythonScript=` with the `PythonScriptPlugin` enabled in the `.uproject`.

**Do not attempt to backport the plugin to an older engine** — it is an engine-version
feature, and porting it means writing a C++ plugin from scratch.

**Applies when:** a project is opened with an engine older than 5.8, or a machine has the
5.5 install selected by a stale version resolver.
