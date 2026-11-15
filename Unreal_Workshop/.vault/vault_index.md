# Vault index — every entry, one row

**The map of `.vault/`.** An agent that wants to fetch wisdom reads **this file**, picks the
row, and opens only that entry. **Never read the vault end to end** — grep it (see
`../AGENTS.md` §5) or read this index.

**`Status` is the first column to read.** Only `active` rows are worth opening. A
`superseded` row names its replacement. A `stale` row was once true and no longer is.

| Status | Entry | What it saves you |
|---|---|---|
| active | [`decisions/2026-11-15-where-unreal-artifacts-belong.md`](decisions/2026-11-15-where-unreal-artifacts-belong.md) | Content vs Saved vs export — where an artifact goes, and what must be created *through the editor* |
| active | [`decisions/2026-11-15-the-unit-scale-is-decided-at-export-time.md`](decisions/2026-11-15-the-unit-scale-is-decided-at-export-time.md) | The ×100 Blender/Unity → Unreal scale, decided at export, not at import |
| active | [`decisions/2026-11-15-the-unreal-version-is-resolved-not-pinned.md`](decisions/2026-11-15-the-unreal-version-is-resolved-not-pinned.md) | Why the launcher registry cannot be trusted here |
| active | [`decisions/2026-11-15-the-two-unreal-mcp-surfaces-are-not-interchangeable.md`](decisions/2026-11-15-the-two-unreal-mcp-surfaces-are-not-interchangeable.md) | Telling Epic's plugin from the canvas bridge |
| active | [`decisions/2026-11-15-this-workshop-carries-no-mcp-configuration.md`](decisions/2026-11-15-this-workshop-carries-no-mcp-configuration.md) | Why the workshop ships no MCP config, and where the client definition lives instead |
| superseded → [`agents-md-is-a-router-not-a-manual.md`](decisions/2026-11-15-agents-md-is-a-router-not-a-manual.md) | [`decisions/2026-11-15-the-workshop-is-loaded-lazily-and-pruned.md`](decisions/2026-11-15-the-workshop-is-loaded-lazily-and-pruned.md) — two indexes, lazy loading, and why the vault is pruned; now merged into the router decision |
| active | [`decisions/2026-11-15-agents-md-is-a-router-not-a-manual.md`](decisions/2026-11-15-agents-md-is-a-router-not-a-manual.md) | What `AGENTS.md` may contain, the two indexes, the lazy-load discipline, and the rule for deciding where a new rule, fact, lesson or procedure goes |
| active | [`decisions/2026-11-15-working-in-a-live-unreal-project.md`](decisions/2026-11-15-working-in-a-live-unreal-project.md) | Confirm the destination before writing, and the rules that stop an agent destroying the user's work |
| active | [`decisions/2026-11-15-the-workshop-is-the-only-copy-of-the-skillset.md`](decisions/2026-11-15-the-workshop-is-the-only-copy-of-the-skillset.md) | The workshop is the only copy; a project consumes a skill by copying it, and the copy is a snapshot to re-copy |
| active | [`lessons/2026-11-15-the-launcher-registry-does-not-list-ue-5-9.md`](lessons/2026-11-15-the-launcher-registry-does-not-list-ue-5-9.md) | The resolver trap, with the scan command |
| active | [`lessons/2026-11-15-verify-the-port-and-its-owner-before-trusting-an-mcp-connection.md`](lessons/2026-11-15-verify-the-port-and-its-owner-before-trusting-an-mcp-connection.md) | "Connected but about the wrong project" |
| active | [`lessons/2026-11-15-ue-5-5-has-no-mcp-plugin.md`](lessons/2026-11-15-ue-5-5-has-no-mcp-plugin.md) | Why an old engine has no MCP at all |
| active | [`lessons/2026-11-15-a-copied-index-goes-stale-without-an-owner.md`](lessons/2026-11-15-a-copied-index-goes-stale-without-an-owner.md) | A hand-copied table of contents has no owner, so a revoked decision stays listed as live forever |
| active | [`lessons/2026-11-15-a-skill-that-pins-the-engine-version-fails-on-the-next-install.md`](lessons/2026-11-15-a-skill-that-pins-the-engine-version-fails-on-the-next-install.md) | Two skills hardcoded `UE_5.8` paths and kept working — against the wrong engine |
| active | [`model-notes/2026-11-15-mcp-tool-surface-reality-in-this-build.md`](model-notes/2026-11-15-mcp-tool-surface-reality-in-this-build.md) | The tool surface as it really is: the live toolset names (`BlueprintToolsets.*`, `EditorToolset.*Toolset`), `execute_python` as the runner, and the two claims that were wrong for a day — the tools were never absent, and `base64` works |
| active | [`model-notes/2026-11-15-ue-installs-and-mcp-capability.md`](model-notes/2026-11-15-ue-installs-and-mcp-capability.md) | Which engine can do what; verified commandlets; reusable engine assets |
| active | [`model-notes/2026-11-15-unreal-mcp-surfaces-on-this-machine.md`](model-notes/2026-11-15-unreal-mcp-surfaces-on-this-machine.md) | Ports, protocol versions, config keys, console commands |
| active | [`workflows/2026-11-15-identify-which-unreal-mcp-answered.md`](workflows/2026-11-15-identify-which-unreal-mcp-answered.md) | The copy-pasteable "which server answered" sequence |
| active | [`lessons/2026-11-15-a-tool-name-is-not-a-capability.md`](lessons/2026-11-15-a-tool-name-is-not-a-capability.md) | Twelve skills died on one renamed dispatch mechanism, and a `not found` got recorded as a missing capability |
| active | [`lessons/2026-11-15-a-client-registration-is-per-agent-not-per-machine.md`](lessons/2026-11-15-a-client-registration-is-per-agent-not-per-machine.md) | A "user scope" registration reaches one agent only — and the no-registration route that works for everyone else |
| active | [`lessons/2026-11-15-a-material-graph-link-that-does-not-raise.md`](lessons/2026-11-15-a-material-graph-link-that-does-not-raise.md) | connect_material_expressions no-ops on a wrong pin name — the read-back that proves a link, the enum connect_material_property needs, and why a rebuilt material orphans the level |
| active | [`decisions/2026-11-15-the-prefab-is-a-blueprint-actor-not-a-level-instance.md`](decisions/2026-11-15-the-prefab-is-a-blueprint-actor-not-a-level-instance.md) | Unreal's prefab: Blueprint actor vs Level Instance vs Packed Level Actor, and what must stay in the level |
| active | [`lessons/2026-11-15-the-subobject-api-will-not-tell-you-it-succeeded.md`](lessons/2026-11-15-the-subobject-api-will-not-tell-you-it-succeeded.md) | Scripting Blueprint components: the Text failure reason that is always truthy, the handle → data → object chain, and components not being on the CDO |
| active | [`lessons/2026-11-15-forward-shading-priority-does-not-silence-the-light-warning.md`](lessons/2026-11-15-forward-shading-priority-does-not-silence-the-light-warning.md) | Three directional lights warn on screen and priority does not stop it; one sun plus a SkyLight does |
| active | [`lessons/2026-11-15-a-translucent-decal-lands-on-a-stencil.md`](lessons/2026-11-15-a-translucent-decal-lands-on-a-stencil.md) | Translucent decals ignore material response and receives-decals and test a custom-depth stencil; a replacement floor loses it |
| active | [`model-notes/2026-11-15-the-mission-camera-shows-no-horizon.md`](model-notes/2026-11-15-the-mission-camera-shows-no-horizon.md) | The -38 deg / 32 deg mission rig never sees the horizon: why far scenery must be a ground plate, and how far out it must reach |
| active | [`lessons/2026-11-16-a-modal-dialog-blocks-every-editor-tool.md`](lessons/2026-11-16-a-modal-dialog-blocks-every-editor-tool.md) | Delete-then-create over a referenced asset raises Slate's "Overwrite Existing Object?" — and every editor tool then answers "not run" while the dialog is up |
| active | [`lessons/2026-11-16-in-a-top-down-arena-the-floor-is-the-mood.md`](lessons/2026-11-16-in-a-top-down-arena-the-floor-is-the-mood.md) | Why the sun barely touches a top-down deck: the SkyLight and the floor's albedo tint ARE the mood, and where the post-process/sky-atmosphere dials live in Python |
| active | [`lessons/2026-11-16-a-default-on-cpp-overlay-ships-to-the-player.md`](lessons/2026-11-16-a-default-on-cpp-overlay-ships-to-the-player.md) | A `bDevMode = true` C++ default put DEV STATS in the browser build; gate on WITH_EDITOR / -JamDevMode, then rebuild wasm + recook |

**28 entries.** Folder charters (`decisions/README.md`, `lessons/README.md`, and the rest)
are **not** entries — they say how a folder is written, not what is known.

The `skills` have their own index: `.skills/skill_catalog.md`. The two indexes together are
the whole workshop: **one map of procedures, one map of memory.**

---

## Rules for this index

1. **Every entry has a row here, added in the same commit that created the file.** A vault
   file that is not in this index **does not exist** — no agent will find it, and the prune
   will delete it. If you wrote an entry and it is not in the index, the entry is unfinished.
2. **A row says enough to decide whether to open the file.** If the row is longer than the
   entry behind it, the entry is unnecessary — fold the row's content back and shorten it.
3. **The status changes when the fact changes.** Revoking a decision is a four-step
   write-back — `../AGENTS.md` §5, *Revoking a decision*.
4. **The index is pruned with the vault, never after it.** A prune pass that ends with an
   index that still lists a deleted file is a failed prune.

---

## Maintenance

The index is also the **pruning surface**: one row per entry means the vault's size is
visible at a glance, and a stale row is a stale fact that gets pointed at.

The prune procedure — when to run it, what to delete, what to keep marked stale — is in
[`README.md`](README.md) → *Maintenance*.