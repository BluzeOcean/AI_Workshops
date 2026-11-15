# The workshop is the only copy of the skillset; projects consume it by copy

**Date:** 2026-11-15
**Status:** active
**Decision:** `V:\04_Projects\Workshops\Unreal_Workshop\.skills\` is **the only copy** of the
`ue-op-*` skills. The original set at `D:\UE\.ue-op-skillset\` is **deprecated** — no longer
wired into anything, no longer maintained, and a duplicate scan that finds it is finding
this workshop's own past rather than a skill to upgrade.

A UE project consumes a skill by **copying** it in, not by linking it:

```powershell
Copy-Item -Recurse -Force `
  "V:\04_Projects\Workshops\Unreal_Workshop\.skills\<name>" `
  "D:\UE\<Project>\.claude\skills\<name>"
```

**A copy is a snapshot, not a link.** When a skill changes in the workshop, it must be
copied again into every project that has it. The `sync_skills` tool in `tools/README.md`
is the specified way to do that.

**Reason:** The junction it replaces was the wrong shape for this workshop. A junction
makes the project's copy *be* the workshop's folder, so an edit in the project silently
changes the workshop's skill, and the two drift apart in the other direction — the
workshop stops being the source of truth, which is the one thing it is for. A copy keeps
the workshop authoritative and the project's skill a plain, readable, editable file that
an agent can also adjust for that project without corrupting the workshop. The cost of a
copy is staleness, and staleness is visible and cheap to fix; the cost of a junction is
silent divergence, which is not.

**Supersedes:** —
**Superseded by:** —

**Reuse when:** adding a skill to a UE project; changing a skill that a project has;
deciding whether a skill is worth installing in a project at all; finding a duplicate.
