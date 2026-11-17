# `tools/` — the tool layer

The scripts that drive RigBy2D. Each one is a repeatable mechanical action that a skill
can call: start something, stop something, run a command, read a state.

## What belongs here

A tool is something that can be **run**, not read. If the answer to "how do I do it?" is a
paragraph, it is a skill. If it is a script with arguments, it is a tool.

| Tool | Purpose |
|---|---|
| _(none yet)_ | |

## What RigBy2D specifically needs

**Unknown — and deliberately not guessed.** Which tools this workshop needs follows from
what RigBy2D actually exposes, and that is one of the open questions in `../AGENTS.md` §4.
Write this section once the control surface has been probed, and keep it in the order an
agent is most likely to want the tools.

The generic rules below are inherited from the house shape. They hold whatever the answers
turn out to be.

## Rules every tool obeys

1. **Never kill something the user started.** If a tool starts RigBy2D, it records the
   PID and only ever stops *that* PID. An instance the user launched themselves is never
   touched. Restarting the app is the user's call.
2. **Never write into a live scene or session by accident.** A running instance may hold
   the user's real work. No tool resets it, clears it, or saves over it.
3. **The destination is required, not defaulted.** A tool that writes output takes the
   destination as an argument and refuses to guess one.
4. **Resolve the version, never pin it.** Find the newest install and use it; do not
   hardcode a version or a path that a later update invalidates.
5. **No media in the workspace.** Tools write into the destination. Scratch goes outside
   this tree. Nothing binary lands here.
6. **Fail loudly.** A tool that cannot reach RigBy2D says so and says what it tried. A
   tool that half-succeeded is worse than one that failed.

## Writing one

Keep it small and honest. A tool that wraps one command is fine; a tool that wraps forty
decisions is a skill in disguise.
