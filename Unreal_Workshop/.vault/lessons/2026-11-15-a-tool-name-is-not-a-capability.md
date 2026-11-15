# A tool name is not a capability — the skills went dead because one mechanism changed

**Date:** 2026-11-15
**Status:** active

## Symptom

Twelve `ue-op-*` skills looked fine and could not run. Their code blocks dispatched through
a top-level tool `execute_tool_script`, which does not exist in this build, calling
`execute_tool("editor_toolset.toolsets.blueprint.BlueprintTools.list_graphs", json.dumps(kw))`,
which does not exist either. Every call failed; the prose around it still read as verified.

Worse, the failure had been **promoted to a fact**: a model-note said Blueprint graph
authoring had *no fallback* in this build, so later agents reported the capability as
missing instead of looking for it.

## What was actually true (probed, 2026-11-15)

| Assumed | Reality |
|---|---|
| `execute_tool_script` runs Python in the editor | the runner is `editor_toolset.toolsets.python_scripting.PythonScriptingTools.execute_python`, and its `script` argument is a **CodeBlock struct** `{content, language}`, not a string |
| `execute_tool(name, json)` dispatches | `await call_tool("<Toolset>.<Tool>", **kwargs)` inside that script, full registered name |
| `editor_toolset.*` is unregistered | twelve live toolsets do the work: `BlueprintToolsets.BlueprintToolset`, `BlueprintToolsets.BlueprintDslToolset`, `EditorToolset.{Asset,Actor,Object,Level,SkeletalMesh,EditorApp}Toolset`, … Only three `editor_toolset.toolsets.*` names survive (DSL, diff, python) |
| snake_case parameters | UE camelCase: `assetPath`, `typeId`, `indexId`, `contextPins`, `bIncludeInherited`, `nodeTypeFilter`→`typeIdFilter` |
| `save_assets(asset_paths=[...])` | `SaveAsset(assetPath)` — one path, no batch |

The one-hop JSON form works for everything, including handles: a node returned as
`{refPath}` is accepted back as a string, and pins are
`{"node": <refPath>, "indexId": N, "direction": "EGPD_Input"}`.

## The repair

1. **Probe before rewriting.** `list_toolsets` (115 here), `describe_toolsets`, then
   `get_symbol` on each tool actually called. A signature fetched live is the only
   authority; a signature remembered from a previous build is a guess.
2. **Write the anchor once** — `.skills/ue-op-mcp-connect/references/calling-tools-in-this-build.md`
   (entry points, name map, signatures, argument shapes, gotchas). Every rewritten skill
   points at it instead of restating it.
3. **Rewrite each skill's code blocks**, not its prose: same procedure, real names,
   camelCase parameters, and a quoted real output under each read block.
4. **Execute every read block** and quote what came back. A block that cannot be executed
   (a write) is marked *signature-verified, not executed* — never left implying it ran.
5. **Delete the fact-table rows the build contradicts** instead of softening them. Rows
   that went: required `title` on `FindNodes`, required `contextPins`, mangled SCS names
   from `GetComponents`, `GetClass` as "parent class", the legacy pin-index table, the
   s-expression DSL grammar, `asset_paths` array mangling, `CaptureViewport`.

## The rules this leaves behind

- **A `not found` is a name problem until `list_toolsets` proves otherwise.** Enumerate
  the registry before concluding a capability is absent; a capability claim from one error
  message is how twelve skills stayed broken and one agent refused work it could do.
- **A skill that was never executed is a hypothesis.** The old blocks were written,
  reviewed and copied between projects without ever running in the build they targeted.
- **Record the probe, not the conclusion.** "Toolset X not found on 2026-11-15" ages well;
  "there is no way to author graphs" ages into a false fact.

## Where the evidence lives

- `.skills/ue-op-mcp-connect/references/calling-tools-in-this-build.md` — signatures, name map, shapes
- `model-notes/2026-11-15-mcp-tool-surface-reality-in-this-build.md` — the corrected note

**Reuse when:** any skill's code block fails, any agent reports a missing UE capability, or a
toolset name is about to be copied from another project.