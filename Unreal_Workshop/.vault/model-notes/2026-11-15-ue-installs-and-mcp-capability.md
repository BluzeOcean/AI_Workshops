# Engine capability matrix — what each installed version can do

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

## Reuse when

- Choosing which engine to launch: **the newest one present on disk**, not the newest in
  the registry.
- Deciding whether a project can have an MCP bridge at all: **5.8 or newer**.
- Looking for an existing input setup to copy rather than author.
