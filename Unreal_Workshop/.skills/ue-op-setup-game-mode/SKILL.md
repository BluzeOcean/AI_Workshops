---
name: ue-op-setup-game-mode
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to make a level spawn a particular pawn — create a GameMode blueprint, set its DefaultPawnClass, and bind it to a level. Skip if no UE MCP connection, if the game mode already exists and only needs a class changed, or if the task is about the character's own behaviour.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - mcp__unreal-mcp__call_tool
---

# ue-op-setup-game-mode — bind a pawn to a level

## Why this exists

Which GameMode a level uses is decided in **two places**, and they behave
differently:

| Where | Where it lives | When it takes effect |
|---|---|---|
| Project default | `UGameMapsSettings::GlobalDefaultGameMode` → `Config/DefaultEngine.ini`, section `[/Script/EngineSettings.GameMapsSettings]` | the ini is loaded into the CDO at **editor startup** |
| Level override | the level's `WorldSettings.DefaultGameMode` | **immediately**, and it wins |

Editing the *ini file* while the editor is running changes nothing until you
restart, because the config CDO is populated at startup. Editing the
**`UGameMapsSettings` CDO live** does take effect on the next PIE — but the
level override is simpler, is saved into the `.umap`, and needs no restart.

**Resolution order** when a game mode is created
(`UGameInstance::CreateGameModeForURL`):

1. the level's `WorldSettings.DefaultGameMode`
2. a `?game=` URL option
3. a per-map-prefix mapping
4. `UGameMapsSettings::GetGlobalDefaultGameMode()`
5. `AGameModeBase`

So the level override is authoritative — set it and nothing else matters for
that map.

---

## Procedure

### 1. Check the current game mode

```powershell
Select-String -Path 'D:\UE\EpicJam2026\Config\DefaultEngine.ini' -Pattern 'GlobalDefaultGameMode' |
  ForEach-Object { "$($_.LineNumber): $($_.Line)" }
# 15: GlobalDefaultGameMode=/Game/Jam/Core/BP_MechGameMode.BP_MechGameMode_C

# and confirm the asset it names actually exists
python V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py call EditorToolset.AssetToolset FindAssets '{"filter":{"folderPath":"/Game/Jam/Core","name":"MechGameMode"}}'
# {"returnValue":["/Game/Jam/Core/BP_MechGameMode.BP_MechGameMode"]}
```

A dangling reference is common — a project pointing at `/Game/LabGameMode`
that only exists as an unsaved in-memory blueprint. PIE will then silently
use the wrong (or default) game mode.

### 2. Create the GameMode blueprint

```powershell
# (write step — signature-verified, not executed)
# skip this if step 1 already found a game mode asset: Create fails on an existing name
python V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py `
  call BlueprintToolsets.BlueprintToolset Create `
  '{"folderPath":"/Game/Jam/Core","assetName":"BP_MechGameMode","assetType":"/Script/Engine.GameModeBase"}'
```

### 3. Set the classes

```powershell
# the blueprint class default object (read)
python ...\mcp_call.py call BlueprintToolsets.BlueprintToolset GetDefaultObject `
  '{"blueprint":"/Game/Jam/Core/BP_MechGameMode.BP_MechGameMode"}'
# {"returnValue":{"refPath":"/Game/Jam/Core/BP_MechGameMode.Default__BP_MechGameMode_C"}}

# (write step — signature-verified, not executed)
# `values` is a JSON *string*, so it is escaped once inside the outer object
python ...\mcp_call.py call EditorToolset.ObjectToolset SetProperties `
  '{"instance":"/Game/Jam/Core/BP_MechGameMode.Default__BP_MechGameMode_C","values":"{\"DefaultPawnClass\":\"/Game/Jam/Core/BP_MechPawn.BP_MechPawn_C\",\"PlayerControllerClass\":\"/Game/Jam/Core/BP_MechController.BP_MechController_C\",\"PlayerStateClass\":\"/Script/Engine.PlayerState\",\"GameStateClass\":\"/Game/Jam/Core/BP_MechPlayerState.BP_MechPlayerState_C\",\"HUDClass\":\"/Game/Jam/Core/BP_MechHUD.BP_MechHUD_C\"}"}'
```

**`DefaultPawnClass` takes a *class* path, not an asset path** — it must end
in the generated `_C` suffix:
`/Game/Foo/BP_Foo.BP_Foo_C`, **not** `/Game/Foo/BP_Foo`.

Read it back to confirm it took:

```powershell
python ...\mcp_call.py call EditorToolset.ObjectToolset GetProperties '{"instance":"/Game/Jam/Core/BP_MechGameMode.Default__BP_MechGameMode_C","properties":["DefaultPawnClass"]}'
# {"returnValue":"{\"DefaultPawnClass\":{\"refPath\":\"/Game/Jam/Core/BP_MechPawn.BP_MechPawn_C\"}}"}
```

### 4. Bind it to the level

```powershell
# the level's WorldSettings actor (read)
python ...\mcp_call.py call EditorToolset.LevelToolset FindActors '{"filter":{"actorType":"/Script/Engine.WorldSettings"}}'
# -> actorPath "/Game/Map/Mission1.Mission1:PersistentLevel.WorldSettings"

# (write step — signature-verified, not executed)
python ...\mcp_call.py call EditorToolset.ObjectToolset SetProperties '{"instance":"/Game/Map/Mission1.Mission1:PersistentLevel.WorldSettings","values":"{\"DefaultGameMode\":\"/Game/Jam/Core/BP_MechGameMode.BP_MechGameMode_C\"}"}'
```

`FindActors` takes **one `filter` struct**, not keyword arguments. Its fields are
`root`, `name` (a case-insensitive substring of the actor **label**), `actorType`
(a class path), `tag`, `bounds`, `collisionChannels` and `dataLayer` — all optional.
Passing `name`/`tag`/`collision_channels` at the top level is rejected:
*"unrecognized parameter(s) [collision_channels, name, tag]. Valid parameters: [filter]"*.

Read it back with `GetProperties` on the same `actorPath`: `{"DefaultGameMode":null}`
means the level has **no** override and the project default is in force — that is the
state of `/Game/Map/Mission1` today.

### 5. Save the level and the blueprint

```powershell
# (write step — signature-verified, not executed)
python ...\mcp_call.py call EditorToolset.EditorAppToolset IsPIERunning      # false = safe to save
python ...\mcp_call.py call EditorToolset.AssetToolset SaveAsset '{"assetPath":"/Game/Jam/Core/BP_MechGameMode.BP_MechGameMode"}'
python ...\mcp_call.py call EditorToolset.AssetToolset SaveAsset '{"assetPath":"/Game/Map/Mission1"}'
```

**One path per call.** There is no `save_assets(list)` in this build —
*"Unknown tool save_assets in toolset EditorToolset.AssetToolset"*.

**Stop PIE first** — the save does not go through while a PIE session is
running. `IsPIERunning` is the check; `EditorToolset.EditorAppToolset.StopPIE`
ends the session.

### 6. Point the project default at it too (optional)

`GlobalDefaultGameMode` lives on **`UGameMapsSettings`**, not `UEngine`, so
the section is `[/Script/EngineSettings.GameMapsSettings]` in
`Config/DefaultEngine.ini`:

```ini
[/Script/EngineSettings.GameMapsSettings]
GlobalDefaultGameMode=/Game/Jam/Core/BP_MechGameMode.BP_MechGameMode_C
```

Do this for consistency; the level override is what makes it live now.

> If the file already has a `GlobalDefaultGameMode=` line, **edit that line in
> place** — do not add a second `[/Script/EngineSettings.GameMapsSettings]`
> section, and never write the setting under `[/Script/Engine.Engine]`
> (that section belongs to `UEngine`, which has no such property).

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| PIE uses the old game mode | the ini was edited but the CDO was loaded at startup | set `WorldSettings.DefaultGameMode` instead |
| The ini edit did nothing | wrong section — it belongs on `UGameMapsSettings` | use `[/Script/EngineSettings.GameMapsSettings]`, not `[/Script/Engine.Engine]` |
| `Login failed: PlayerState is null` | the active GameMode is wrong or half-configured | check `Game class is '...'` in the log |
| `DefaultPawnClass` does not take | wrong path form | it needs the `_C` generated-class path |
| The player does not spawn | no `PlayerStart` in the level | `FindActors '{"filter":{"name":"PlayerStart"}}'`; add one if missing |
| The player spawns but is the wrong pawn | the GameMode in play is not the one you edited | read `LogLoad: Game class is '...'` in the log |
| `SaveAsset` → "Asset does not exist" | PIE is running | check `IsPIERunning`, `StopPIE`, then save |
| `assetType` → "GameModeBase is not a valid object path for property 'AssetType'" | a bare class name was passed | pass the class path, `/Script/Engine.GameModeBase` |
| `FindActors` → "unrecognized parameter(s) [name, tag, …]" | arguments passed as keywords | one `filter` struct: `{"filter":{"name":"…"}}` |

**A GameMode spawns the player pawn at the level's `PlayerStart`
automatically.** You do not need to place the character in the level — and
placing one as well gives you two characters.

**A player pawn is possessed automatically**, so `AutoPossessAI` and
`PlayerController` setup are not needed for the default flow.

## Output contract

- The GameMode blueprint exists, compiles and is saved
- `DefaultPawnClass` reads back as the intended `_C` class
- The level's `WorldSettings.DefaultGameMode` reads back correctly
- The level is saved

## Related

- `ue-op-create-blueprint` — make the pawn blueprint the GameMode points at
- `ue-op-test-pie` — confirm the pawn spawns
