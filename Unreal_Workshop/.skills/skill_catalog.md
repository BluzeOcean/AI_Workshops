# Skill catalog — every skill in this workshop

**One row per skill.** Read the `When to use it` column and open the one that matches. Do
not read them all.

Naming: every folder is `ue-op-<verb-noun>` — see the convention in
[`README.md`](README.md).

---

## Reaching the editor (MCP and the live session)

| Skill | What it does | When to use it |
|---|---|---|
| [`ue-op-mcp-connect`](ue-op-mcp-connect/SKILL.md) | Brings the MCP bridge up: enables Epic's plugin in the `.uproject`, turns on auto-start, registers the client, walks the handshake | The editor has no MCP surface, or the bridge needs recovering |
| [`ue-op-mcp-diagnose`](ue-op-mcp-diagnose/SKILL.md) | Works out **which editor and which MCP server** you are talking to — resolves the engine, finds the project, finds the port owner, tells Epic's plugin from the Canvas bridge | A tool call succeeds but does the wrong thing, or you are not sure which project answered |
| [`ue-op-editor-script`](ue-op-editor-script/SKILL.md) | Drives the live editor with Python when the MCP tools cannot express the job | Batch asset edits, reading a scene, a calculation you need as data |
| [`ue-op-run-headless`](ue-op-run-headless/SKILL.md) | Runs Unreal with no GUI on screen — commandlets, editor Python, automation tests | No editor is running, the user's editor is busy, or you want a cook or a bulk resave out of the way |
| [`ue-op-capture-editor`](ue-op-capture-editor/SKILL.md) | Screenshots the editor or the viewport through MCP | You need to *show* what the editor looks like |
| [`ue-op-offscreen-verify`](ue-op-offscreen-verify/SKILL.md) | Proves a mesh renders and animates without a desktop screenshot | You need visual proof but the user is at the machine |

## Blueprints and the graph

| Skill | What it does | When to use it |
|---|---|---|
| [`ue-op-inspect-blueprint`](ue-op-inspect-blueprint/SKILL.md) | Reads a blueprint's structure — graphs, components, variables, parent class | You need to know what a blueprint already is before changing it |
| [`ue-op-create-blueprint`](ue-op-create-blueprint/SKILL.md) | Creates a blueprint — a child of an existing one, or from a base class | A new blueprint asset is needed |
| [`ue-op-add-component`](ue-op-add-component/SKILL.md) | Adds or configures a component — spring arm, camera, mesh | The blueprint needs a part it does not have |
| [`ue-op-wire-graph`](ue-op-wire-graph/SKILL.md) | Creates, connects or deletes blueprint graph nodes | The logic, not the assets, is the job |
| [`ue-op-fix-compile-error`](ue-op-fix-compile-error/SKILL.md) | Recovers a blueprint that will not compile, or an editor wedged behind the modal | A blueprint is broken and the editor is blocked |

## Gameplay and play

| Skill | What it does | When to use it |
|---|---|---|
| [`ue-op-setup-game-mode`](ue-op-setup-game-mode/SKILL.md) | Makes a level spawn a particular pawn — create a GameMode blueprint and wire it up | A level spawns the wrong default pawn |
| [`ue-op-setup-input`](ue-op-setup-input/SKILL.md) | Binds keys so a character responds — legacy axis/action mappings and Enhanced Input | The character does not move |
| [`ue-op-setup-playable-character`](ue-op-setup-playable-character/SKILL.md) | Makes a character controllable in a level end to end — camera, movement, possession | You need a character a player can actually drive |
| [`ue-op-test-pie`](ue-op-test-pie/SKILL.md) | Runs and verifies gameplay in Play-In-Editor — start or stop PIE, inject input, check runtime state | You need to *prove* it works, not just that it compiles |

## Assets and content

| Skill | What it does | When to use it |
|---|---|---|
| [`ue-op-find-assets`](ue-op-find-assets/SKILL.md) | Locates project or engine assets, including inside `.uasset` binaries | You need the content path of something |
| [`ue-op-find-dependencies`](ue-op-find-dependencies/SKILL.md) | Computes an asset's transitive dependency closure | You need to know what an asset drags in |
| [`ue-op-clone-assets`](ue-op-clone-assets/SKILL.md) | Copies a curated asset set into a structured export folder | Migrating a set of assets out |
| [`ue-op-relocate-assets`](ue-op-relocate-assets/SKILL.md) | Moves a curated asset set so the folder is self-contained | Tidying a folder that has become entangled |
| [`ue-op-bake-mesh-partition`](ue-op-bake-mesh-partition/SKILL.md) | Gets Mesh Terrain geometry into a cooked build — bakes the partition's section meshes to plain static meshes, with the triangle-winding fix | Mesh Terrain is missing from a packaged build |

## Characters and rigs

| Skill | What it does | When to use it |
|---|---|---|
| [`ue-op-blender-rig-for-ue`](ue-op-blender-rig-for-ue/SKILL.md) | Consolidates a Blender character onto one armature with one name before FBX export | Unreal reports a duplicate-root skeleton |
| [`ue-op-skeletal-import-and-skeleton`](ue-op-skeletal-import-and-skeleton/SKILL.md) | Imports skeletal meshes so they genuinely share one skeleton — and verifies it | Imported meshes will not animate together |
| [`ue-op-animate-foreign-rig`](ue-op-animate-foreign-rig/SKILL.md) | The evidence for why retargeting an animation onto an AI-generated rig fails, plus the authoring recipe that actually drives the mesh | A retarget produces a dead mesh |
| [`ue-op-tripo-pipeline`](ue-op-tripo-pipeline/SKILL.md) | Entry point for bringing a Tripo/AI-generated character into Unreal — the ordered pipeline and the rules that are never optional | Starting a Tripo/AI character |
| [`ue-op-tripo-triage-asset`](ue-op-tripo-triage-asset/SKILL.md) | Decides which half of a Tripo hi-lo delivery is the game asset, and whether a bake is needed — by measuring, not assuming | Two files arrived and only one is the asset |

## Web and browser builds

| Skill | What it does | When to use it |
|---|---|---|
| [`ue-op-build-web`](ue-op-build-web/SKILL.md) | Cooks, packages and stages a UE 5.9 Wasm/WebGPU web build, and fixes the map the page opens on | A browser-playable build is needed |
| [`ue-op-verify-web`](ue-op-verify-web/SKILL.md) | Proves a staged web build actually runs — headless Chrome boot, WebGPU error counting, screenshot capture | The build is staged and you need it proven |
| [`ue-op-ship-web`](ue-op-ship-web/SKILL.md) | Turns a verified stage into something a user or host can consume — a launcher that serves it with the right headers | Hosting it |
| [`ue-op-browser-look-budget`](ue-op-browser-look-budget/SKILL.md) | Makes AI-generated characters read correctly under a web/Wasm budget — metallic from the measured map, ambient instead of lights, blob shadows | The browser build looks flat or black |

## Project surgery and language

| Skill | What it does | When to use it |
|---|---|---|
| [`ue-op-fix-large-ue-sample-project`](ue-op-fix-large-ue-sample-project/SKILL.md) | Makes a heavy imported sample project or asset-pack demo map usable again — slow level opens, assets dumped on one spot, duplicate lights | A level takes minutes to open, or the editor is buried |
| [`ue-op-python-gotchas`](ue-op-python-gotchas/SKILL.md) | Unreal Python that fails silently — struct write-back loss, renamed play-data fields, root-component moves, Live Coding limits | A Python snippet appears to do nothing |

## Forging new skills

| Skill | What it does | When to use it |
|---|---|---|
| [`ue-op-extract-to-skill`](ue-op-extract-to-skill/SKILL.md) | Captures a finished operation as a new, reusable skill — checks for duplicates, writes it with the optimized steps, and wires it in | An operation worked and would work again |

---

## Where the helpers live

| Helper | Path |
|---|---|
| the MCP client used by several skills | `ue-op-mcp-connect/mcp_call.py` |
| Mesh Terrain baking | `ue-op-bake-mesh-partition/scripts/` |
| web build | `ue-op-build-web/scripts/build_web.ps1` |
| web verification | `ue-op-verify-web/scripts/verify_web.ps1` |
| web packaging | `ue-op-ship-web/scripts/make_web_zip.py` |
| sample-project repair | `ue-op-fix-large-ue-sample-project/` |

The absolute path the skills use is
`V:\04_Projects\Workshops\Unreal_Workshop\.skills\` — the skills are runnable as written.

## One copy — this workshop

**This workshop is the only copy of the skillset.** The original set at
`D:\UE\.ue-op-skillset\` is **deprecated**: no longer wired into the UE projects, no
longer maintained, and a duplicate scan that finds it is finding this workshop's own
past. Change a skill here.

A UE project consumes a skill by **copying** it in:

```powershell
Copy-Item -Recurse -Force `
  "V:\04_Projects\Workshops\Unreal_Workshop\.skills\<name>" `
  "D:\UE\<Project>\.claude\skills\<name>"
```

**A copy is a snapshot** — re-copy a skill into every project that has it when it
changes here.

**Three folders are new or renamed since the deprecated copy** — the naming convention
requires the `ue-op-` prefix, and two procedures did not exist when the original set
was forged:

| Workshop (canonical) | Original (deprecated) |
|---|---|
| `ue-op-mcp-connect` | `ue-mcp-connect` |
| `ue-op-mcp-diagnose` | *(new here — no original)* |
| `ue-op-run-headless` | *(new here — no original)* |

**New skills are forged here**, into `.skills/ue-op-<name>/SKILL.md`.
