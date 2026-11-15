# `recipes/` — what produced something good

A script plus the settings that produced a good result, written down so the next agent can
reuse it without re-deriving it.

```
recipes/<name>.md
recipes/<name>.py        <- the script, if it is worth keeping
recipes/<name>.json      <- the settings, if they are worth keeping
```

**Text only.** The artifact is not — artifacts live in the destination the user confirmed,
not in this folder.

```markdown
# <one-line title>

**Date:** YYYY-MM-DD
**What was run:** the exact command / script / settings.
**Result:** what came out, and where it landed.
**Reuse when:** the situation where this is the right starting point.
```
