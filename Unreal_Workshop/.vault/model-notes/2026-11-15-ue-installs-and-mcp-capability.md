# Engine capability matrix — what each installed version can do

**Status:** active

**Recorded:** 2026-11-15. Versions read from each install's `Engine/Build/Build.version`.

| Install | Version | CL | MCP plugin | Python | Registry entry |
|---|---|---|---|---|---|
| `UE_5.9` | **5.9.0** | 60351404 | yes | 3.11.8 | **absent** |
| `UE_5.8` | 5.8.4 | 58902052 | yes | — | present |
| `UE_5.5` | 5.5.4 | 40574608 | **no** | — | present |

The registry also names 5.2, 5.4, 5.6 and 5.7, whose **directories are not on disk** — it
is a log of launcher installs over time, not a list of what exists.

## Capability by version

| | 5.5.4 | 5.8.4 | 5.9.0 |
|---|---|---|---|
| `Engine/Plugins/Experimental/ModelContextProtocol/` | absent | present | present |
| HTTP MCP server (`127.0.0.1:8000/mcp`) | no | yes | yes |
| `Engine/Plugins/Experimental/PythonScriptPlugin/` | present | present | present |
| `Engine/Binaries/ThirdParty/Python3/Win64/python.exe` | — | — | 3.11.8 |

The MCP plugin is an **engine-version** feature, not a project setting — it cannot be
backported to 5.5 without writing a C++ plugin from scratch.

## Commandlets verified in 5.9

`Engine/Source/Editor/UnrealEd/Classes/Commandlets/` contains `ResavePackagesCommandlet.h`,
`CookCommandlet.h`, `DerivedDataCacheCommandlet.h`, `DumpAssetRegistryCommandlet.h`.

**There is no `AutomationCommandlet` in 5.9** and no `RunUnreal` AutomationTool script.
Automation tests run from the editor console (`Automation RunTests <TestName>`), or
headless via `-ExecCmds="Automation RunTests <TestName>;Quit"`.

## Engine content worth reusing instead of authoring

| What | Where |
|---|---|
| Project templates | `<engine>\Templates\` — `TP_ThirdPerson\`, `TP_FirstPerson\`, `TP_Blank\`, `TP_AEC_*\`, `TP_ME_*` |
| Canonical Enhanced Input assets | `<engine>\Templates\TemplateResources\High\Input\Content\` |
| → the `IMC_*` context maps | `…\High\Input\Content\IMC_Default.uasset`, `IMC_MouseLook.uasset` |
| → the `IA_*` actions | `…\High\Input\Content\Actions\` — `IA_Jump`, `IA_Look`, `IA_MouseLook`, `IA_Move` |

The `IA_*` action assets sit **one level deeper** than the `IMC_*` maps, in `Content\Actions\`.
A flat search for `IA_*.uasset` finds nothing.

## Why the version matters at all

Unreal's API and content format are versioned, and the differences are **not additive**:

- **Asset format.** A `.uasset`/`.umap` saved by 5.9 does not open in 5.8, and cannot be
  cooked by 5.8. Content is forward-locked to the engine that wrote it.
- **Enhanced Input** replaced the legacy Axis/Action mappings. A project on the new system
  does not respond to a project on the old one.
- **Blueprint node ids change.** `ue-op-wire-graph` and friends fail on nodes that moved
  between releases; `ue-op-fix-compile-error` exists because a blueprint will not compile
  against the engine in front of it.
- **Python API renames.** `get_editor_property` field names are not stable across releases.
  The community answers are heavily mixed across versions — a snippet from 5.3 may name a
  field that 5.9 renamed, and the renamed field is **silently ignored**.

**Check the engine version before you rely on an API detail.**

## Paths on this machine

**These move when the engine is updated, and the launcher registry does not list every
install. Resolve them (§ above), never hardcode them.**

| What | Where |
|---|---|
| Engine install root | `C:\Program Files\Epic Games\` |
| Engine version file | `<engine>\Engine\Build\Build.version` |
| Editor executable | `<engine>\Engine\Binaries\Win64\UnrealEditor.exe` |
| Commandlet executable | `<engine>\Engine\Binaries\Win64\UnrealEditor-Cmd.exe` |
| Build / UAT | `<engine>\Engine\Build\BatchFiles\Build.bat`, `RunUAT.bat` |
| Unreal's Python 3.11.8 | `<engine>\Engine\Binaries\ThirdParty\Python3\Win64\python.exe` (no `unreal` module outside the editor) |
| Epic MCP plugin (5.8+) | `<engine>\Engine\Plugins\Experimental\ModelContextProtocol\` |
| Editor Python plugin | `<engine>\Engine\Plugins\Experimental\PythonScriptPlugin\` |
| Unreal Canvas / merlin build | `C:\Users\Bluze\AppData\Local\UnrealCanvas\Builds\v0.21.0\` |
| Unreal Canvas version | `…\v0.21.0\merlin-version.txt` |
| Unreal projects | `D:\UE\<Project>\<Project>.uproject` |
| Original skillset (still wired into the UE projects) | `D:\UE\.ue-op-skillset\<name>\SKILL.md` |

## Reuse when

- Choosing which engine to launch: **the newest one present on disk**, not the newest in
  the registry.
- Deciding whether a project can have an MCP bridge at all: **5.8 or newer**.
- Looking for an existing input setup to copy rather than author.
