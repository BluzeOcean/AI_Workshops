# `workflows/` — known-good command sequences

A sequence of commands that is known to work end to end, plus the notes on when to use it
and what to watch out for.

```
workflows/<name>.md
```

Candidates for this folder, once they have been run at least once for real:

- Bringing a Blender instance up and confirming it is reachable.
- Handshaking with the DSH bridge on `127.0.0.1:9876`.
- A headless build → save → render chain against a confirmed destination.
- An export chain for `../Unreal_Workshop/` or `../Unity_Workshop/`.

Do not write one speculatively. A workflow that has never been run is a guess with a
confident tone.
