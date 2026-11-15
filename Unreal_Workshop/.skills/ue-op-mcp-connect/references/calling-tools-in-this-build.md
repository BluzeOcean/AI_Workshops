# Calling editor tools in this build (UE 5.9, MCP server on :8000)

**Verified 2026-11-15** against the running EpicJam2026 editor. Every signature and every
call form below was executed, not inferred. This file exists because the `ue-op-*` skills
were written against an older dispatch mechanism that **no longer exists**, so their code
blocks failed as written.

---

## The two entry points

### A. One hop — JSON through the client you already have

Any agent that can reach the server (Claude Code's `call_tool` MCP tool, or the shell
client below) calls a tool directly:

```powershell
python V:\04_Projects\Workshops\Unreal_Workshop\.skills\ue-op-mcp-connect\mcp_call.py `
  call BlueprintToolsets.BlueprintToolset ListGraphs `
  '{"blueprint":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn"}'
```

```json
{"returnValue":[{"refPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:UserConstructionScript"},
                {"refPath":"/Game/Jam/Core/BP_MechPawn.BP_MechPawn:EventGraph"}]}
```

This is the **default** for a skill step: one tool, one JSON object. `toolset_name` and
`tool_name` are the registered names (below), and every argument is the tool's own
parameter name in UE camelCase.

### B. In-editor Python — when one step needs a handle from the previous one

```powershell
python ...\mcp_call.py call editor_toolset.toolsets.python_scripting.PythonScriptingTools execute_python `
  '{"script":{"content":"import json\n...python...","language":"Python"}}'
```

- `script` is a **CodeBlock struct**: `{"content": "<source>", "language": "Python"}`.
  Passing a bare string fails with *"Unable to import JSON string into CodeBlock"*.
- Inside the script, `unreal` is preimported, top-level `await` works, and the tool that
  matters is already bound: `await call_tool('<Toolset>.<Tool>', **kwargs)` — the **full**
  registered name, keyword arguments as parameters, real Unreal objects allowed.
- The call returns the value of the script's final expression (as JSON for non-strings).
- Call `read_me` once per conversation for the environment rules (what is rejected:
  network calls, `time.sleep`, `subprocess.run`, star imports).

```python
import json
bp = "/Game/Jam/Core/BP_MechPawn.BP_MechPawn"
g  = await call_tool("BlueprintToolsets.BlueprintToolset.ListGraphs", blueprint=bp)
json.dumps({"count": len(g), "graphs": [str(x) for x in g]})
```

---

## What is gone

| The skills were written against | This build |
|---|---|
| Tool `execute_tool_script` (top-level MCP tool) | **does not exist** — 70 top-level tools, none of them that; the runner is `PythonScriptingTools.execute_python` |
| `execute_tool("<toolset>.<tool>", json.dumps(kw))` inside the script | **does not exist** — use `await call_tool("<Toolset>.<Tool>", **kw)` |
| `editor_toolset.toolsets.blueprint.BlueprintTools` … | **not registered**: *"editor_toolset.toolsets.blueprint.BlueprintTools is not registered"*. Only three `editor_toolset.toolsets.*` entries survive: `blueprint.BlueprintDslTools`, `blueprint_diff.BlueprintDiffTools`, `python_scripting.PythonScriptingTools` |
| snake_case parameters (`asset_path`, `type_id_filter`, `context_pins`, `index_id`) | **camelCase**: `assetPath`, `typeIdFilter`, `contextPins`, `indexId` |

---

## Name map (skills → this build)

| Skills' name | Registered name |
|---|---|
| `…blueprint.BlueprintTools` | `BlueprintToolsets.BlueprintToolset` |
| `…blueprint.BlueprintDslTools` | `BlueprintToolsets.BlueprintDslToolset` (the old spelling also resolves) |
| `…actor.ActorTools` | `EditorToolset.ActorToolset` |
| `…asset.AssetTools` | `EditorToolset.AssetToolset` |
| `…object.ObjectTools` | `EditorToolset.ObjectToolset` |
| `…scene.SceneTools` (`find_actors`) | `EditorToolset.LevelToolset.FindActors` |
| `…skeletal_mesh.SkeletalMeshTools` | `EditorToolset.SkeletalMeshToolset` |
| `…python_scripting.PythonScriptingTools` | same name — still registered |
| editor Python runner | `editor_toolset.toolsets.python_scripting.PythonScriptingTools.execute_python` |

---

## Signatures that replace the skills' calls

`get_symbol(name="<full tool name>")` on `PythonScriptingTools` prints the live signature.
These were fetched that way on 2026-11-15:

```
EditorToolset.AssetToolset.LoadAsset(assetPath: string) -> Object
EditorToolset.AssetToolset.SaveAsset(assetPath: string)                 # singular; no save_assets(list)
EditorToolset.AssetToolset.Delete(path: string)
EditorToolset.AssetToolset.Duplicate(path: string, newPath: string) -> boolean
EditorToolset.AssetToolset.CreateFolder(path: string) -> boolean
EditorToolset.AssetToolset.FindAssets(filter: AssetSearchFilter = ...) -> list[string]
EditorToolset.ObjectToolset.GetClass(instance: Object) -> type[Object]
EditorToolset.ObjectToolset.SetProperties(instance: Object, values: string) -> boolean
EditorToolset.ActorToolset.GetComponents(actor: Actor, componentType: type[Object] = null)
EditorToolset.ActorToolset.AddComponent(owner: Object, componentType: type[Object], name: string)
EditorToolset.LevelToolset.FindActors(filter: ActorSearchFilter = ...) -> list[ActorDesc]
BlueprintToolsets.BlueprintToolset.Create(folderPath: string, assetName: string, assetType: type[Object]) -> Blueprint
BlueprintToolsets.BlueprintToolset.GetDefaultObject(blueprint: Blueprint) -> Object
BlueprintToolsets.BlueprintToolset.ListGraphs(blueprint: Blueprint) -> list[EdGraph]
BlueprintToolsets.BlueprintToolset.ListVariables(blueprint, scope=null, graph=null, bIncludeInherited=false)
BlueprintToolsets.BlueprintToolset.FindNodes(graph: EdGraph, title: string = "", nodeClass = null, bEntryPointsOnly = false)
BlueprintToolsets.BlueprintToolset.FindNodeTypes(graph: EdGraph, typeIdFilter: string, contextPins: list[BlueprintPinID] = null)
BlueprintToolsets.BlueprintToolset.CreateNode(graph: EdGraph, typeId: string, pos: IntPoint, declaringClass = null)
BlueprintToolsets.BlueprintToolset.AddEvent(blueprint: Blueprint, eventName: string, position: IntPoint = null)
BlueprintToolsets.BlueprintToolset.GetNodeInfos(nodes: list[EdGraphNode]) -> list[BlueprintNodeInfo]
BlueprintToolsets.BlueprintToolset.ConnectPins(outputPin: BlueprintPinID, inputPin: BlueprintPinID)
BlueprintToolsets.BlueprintToolset.SetPinValue(pin: BlueprintPinID, value: string)
BlueprintToolsets.BlueprintToolset.CompileBlueprint(blueprint: Blueprint, bWarningsAsErrors: boolean = false)
BlueprintToolsets.BlueprintDslToolset.Read(assetPath: string, scope: string = "", bIncludePositions: boolean = false)
BlueprintToolsets.BlueprintDslToolset.Write(assetPath: string, dsl: string, scope: string = "")
BlueprintToolsets.BlueprintDslToolset.Edit(assetPath: string, edits: list[GraphDslTextReplacement], revision: string, scope = "")
BlueprintToolsets.BlueprintDslToolset.Docs() -> string
```

Verify any name with `search_symbols`; verify any signature with `get_symbol`. Both read
this editor session, so a name they do not return is unavailable here.

---

## Argument shapes (JSON, from outside)

| Parameter type | Accepted JSON |
|---|---|
| an asset (`Blueprint`, `Object`) | the asset path string `"/Game/X/BP_Y.BP_Y"`, or `{"refPath": "/Game/…"}` |
| a graph | the graph's `refPath`: `"/Game/X/BP_Y.BP_Y:EventGraph"` |
| a node | the node's `refPath`: `"/Game/X/BP_Y.BP_Y:EventGraph.K2Node_Event_0"` |
| a pin id (`BlueprintPinID`) | `{"node": "<node refPath>", "indexId": 1, "direction": "EGPD_Output"}` — **`indexId`, not `index_id`** |
| `IntPoint` | `{"x": 0, "y": 0}` |
| `type[Object]` (a class) | a class path: `"/Script/Engine.Actor"` — a bare name like `"Actor"` fails with *"Actor is not a valid object path for property 'AssetType'"* |
| `list[X]` | a JSON array of any of the above |

Nothing needs the in-editor Python path for this: a `Create`d node's `refPath`, fed back in
as a string, is resolved. That was verified by creating a node, reading its pins back by
refPath, compiling and deleting the scratch asset.

---

## Gotchas that cost a call

- `describe_toolset` (singular) is **not** registered; the meta-tool is `describe_toolsets`.
- `describe_toolsets` nests its answer: the JSON is inside `content[0].text` as a string —
  `json.loads(as_text(result))`, not `result["toolsets"]`.
- `SaveAsset` takes one path; there is no batch save. `CompileBlueprint` before saving.
- The graph-DSL text this build returns is **not** the old s-expression style. A whole
  empty EventGraph reads:
  ```
  (event `self.ReceiveBeginPlay`)

  (event `self.ReceiveActorBeginOverlap`
    (params (OtherActor :type "Actor Object Reference")))

  (event `self.ReceiveTick`
    (params (DeltaSeconds :type "Float (single-precision)")))
  ```
  `Docs()` on `BlueprintDslToolset` returns the current grammar; read it before writing DSL.
- The two **search** tools take a filter *struct*, not keyword arguments, and the struct
  is passed under the parameter name `filter`:

  ```powershell
  # verified: ["/Game/Jam/Input/IMC_Jam.IMC_Jam"]
  python mcp_call.py call EditorToolset.AssetToolset FindAssets ^
    '{"filter":{"folderPath":"/Game/Jam/Input","name":"IMC"}}'

  # verified: returns actor descs (guid, class.refPath, name, label, actorPath …)
  python mcp_call.py call EditorToolset.LevelToolset FindActors '{"filter":{"name":"Band"}}'
  ```

  `AssetSearchFilter` fields: `folderPath`, `name`, `assetType` (a class path), and more —
  see `get_symbol("EditorToolset.AssetToolset.FindAssets")`.
  `ActorSearchFilter` fields: `root`, `name` (matches the **label**), `actorType`, `tag`.
- Only the three meta-tools plus the UnrealCanvas/asset tools are top-level. Everything
  else is reached through `call_tool` — see *Calling tools: the `call_tool` indirection*
  in the parent skill.
## More signatures, and three behaviours worth knowing

Verified with `get_symbol` on the same editor:

```
EditorToolset.ObjectToolset.GetProperties(instance: Object, properties: list[string]) -> string   # properties is REQUIRED
EditorToolset.ObjectToolset.ListProperties(instance, root="", nameFilter="", maxDepth=1) -> list[string]
BlueprintToolsets.BlueprintToolset.GetParent(blueprint: Blueprint) -> type[Object]                 # the PARENT class
BlueprintToolsets.BlueprintToolset.DeleteNode(node: EdGraphNode)
EditorToolset.EditorAppToolset.StartPIE(options: PIESessionOptions = null)
```

**A Blueprint asset's parent class is `GetParent(blueprint)`, not `GetClass(instance=bp)`.**
`GetClass` on the asset returns the asset's own generated class
(`/Game/…/BP_MechPawn.BP_MechPawn_C`), which reads like a parent class and is not one.

**`GetComponents` on a Blueprint's CDO returns the *variable* names** on this build:
`SceneRoot`, `BattleCamera`, `PathPreview`, `FacingArrow` — not mangled SCS names like
`SpringArmComponent_0__A9892D03`. Matching on the last `:`/`.` segment still works; the
CDO-vs-instance naming difference older notes describe does not.

**An empty list is an answer.** `ListVariables` on a Blueprint that declares none returns
`[]`; that is not a failed call.