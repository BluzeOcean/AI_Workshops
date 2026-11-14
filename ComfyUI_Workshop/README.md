# ComfyUI_Workshop

A workspace that gives any agent the ability to produce assets with ComfyUI.

It contains no media. It contains the **instructions**, the **skills**, and the **memory**.

```
AGENTS.md        <- start here. the whole onboarding.
.skills/         <- procedures: one folder per skill, each with a SKILL.md
.vault/          <- the memory bank: lessons, decisions, model notes, recipes
tools/           <- the scripts
.mcp.json        <- registers the ComfyUI MCP bridge for MCP-capable agents
```

## Quick start for an agent

1. Read `AGENTS.md`. It covers the destination rule, the headless boot, the tool surface,
   and the mistakes that cost the most time.
2. Confirm the **destination** for the task. If the user has not said, ask.
3. `pwsh -File tools\boot-comfyui.ps1 -OutputDir "<DESTINATION>"`
4. Build a graph and submit it — see `.skills/comfyui-generate/SKILL.md`.
5. **Log the memory** in `.vault/` when the task is done. See `.vault/README.md`.

## The three ideas

**The destination is a boot-time setting.** ComfyUI refuses to write outside
`--output-directory`, so where the assets land is decided before the server starts. The
agent must know it, and must ask if nobody has said.

**ComfyUI here is a server, not an app.** It boots headless — no browser, no console
window — and it stays up for the next task.

**The vault is a memory bank.** Written after each task, searched when something breaks.
It is what stops the workspace from making the same mistake twice.
