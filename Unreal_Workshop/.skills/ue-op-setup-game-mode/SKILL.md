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

```bash
grep -n "GlobalDefaultGameMode" "D:/UE/<project>/Config/DefaultEngine.ini"
```

A dangling reference is common — a project pointing at `/Game/LabGameMode`
that only exists as an unsaved in-memory blueprint. PIE will then silently
use the wrong (or default) game mode.

### 2. Create the GameMode blueprint

```python
import json

def T(tool, **kw):
    """Call a toolset tool from inside execute_tool_script and unwrap its
    {'returnValue': ...} envelope.  Tool names are fully qualified, e.g.
    'editor_toolset.toolsets.asset.AssetTools.load_asset'."""
    r = execute_tool(tool, json.dumps(kw))
    if isinstance(r, dict) and "returnValue" in r:
        return r["returnValue"]
    return r

gm = T("editor_toolset.toolsets.blueprint.BlueprintTools.create",
       folder_path="/Game/Lab",
       asset_name="BP_LabGameMode",
       asset_type="/Script/Engine.GameModeBase")
```

### 3. Set the classes

```python
cdo = T("editor_toolset.toolsets.blueprint.BlueprintTools.get_default_object", blueprint=gm)
T("editor_toolset.toolsets.object.ObjectTools.set_properties", instance=cdo, values=json.dumps({
    "DefaultPawnClass":      "/Game/Lab/Characters/BP_LabTPSCharacter.BP_LabTPSCharacter_C",
    "PlayerControllerClass": "/Script/Engine.PlayerController",
    "PlayerStateClass":      "/Script/Engine.PlayerState",
    "GameStateClass":        "/Script/Engine.GameStateBase",
    "HUDClass":              "/Script/Engine.HUD",
}))
```

**`DefaultPawnClass` takes a *class* path, not an asset path** — it must end
in the generated `_C` suffix:
`/Game/Foo/BP_Foo.BP_Foo_C`, **not** `/Game/Foo/BP_Foo`.

Read it back to confirm it took:
`get_properties(instance=cdo, properties=["DefaultPawnClass"])`.

### 4. Bind it to the level

```python
ws = T("editor_toolset.toolsets.scene.SceneTools.find_actors", name="WorldSettings", tag="",
       collision_channels=[])[0]
T("editor_toolset.toolsets.object.ObjectTools.set_properties", instance=ws,
  values=json.dumps({"DefaultGameMode": "/Game/Lab/BP_LabGameMode.BP_LabGameMode_C"}))
```

`find_actors` requires **all three** of `name`, `tag` and `collision_channels`
even when you only want one. Use `name=""`, `tag=""`, `collision_channels=[]`
to match everything.

### 5. Save the level and the blueprint

```python
T("editor_toolset.toolsets.asset.AssetTools.save_assets", asset_paths=["/Game/Main", gm])
```

**Stop PIE first** — `save_assets` fails with "Asset does not exist" while a
PIE session is running.

### 6. Point the project default at it too (optional)

`GlobalDefaultGameMode` lives on **`UGameMapsSettings`**, not `UEngine`, so
the section is `[/Script/EngineSettings.GameMapsSettings]` in
`Config/DefaultEngine.ini`:

```ini
[/Script/EngineSettings.GameMapsSettings]
GlobalDefaultGameMode=/Game/Lab/BP_LabGameMode.BP_LabGameMode_C
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
| The player does not spawn | no `PlayerStart` in the level | `find_actors` for `PlayerStart`; add one if missing |
| The player spawns but is the wrong pawn | the GameMode in play is not the one you edited | read `LogLoad: Game class is '...'` in the log |
| `save_assets` → "Asset does not exist" | PIE is running | stop PIE, then save |

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
