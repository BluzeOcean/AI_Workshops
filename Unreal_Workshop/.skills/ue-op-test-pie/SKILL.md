---
name: ue-op-test-pie
description: Use only when an Unreal MCP server is connected in this session (mcp__unreal-mcp__* tools present) and the task is to run and verify gameplay in Play-In-Editor — start or stop PIE, survive the modal dialogs that block it, inject synthetic keyboard/mouse input, and read back runtime state. Skip if no UE MCP connection, or if the task is only to author content.
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

# ue-op-test-pie — run PIE and verify it actually works

## Procedure

### 1. Start PIE

```json
{"options": {"bSimulate": false, "playMode": "PlayMode_InViewPort", "warmupSeconds": 4}}
```

The arguments go **nested under `options`** — `{"bSimulate": …}` at the top
level fails with "input param 'options' is required".

`bSimulate: true` runs the world without a player pawn — useful for checking
initialisation, useless for testing input.

### 2. Survive the modal dialogs

PIE can wedge the editor. The tell: **MCP calls time out** and a visible
dialog sits on screen.

| Dialog | Cause | Action |
|---|---|---|
| "Blueprint Asset Compilation Error" | a blueprint does not compile | `ue-op-fix-compile-error`, then close the dialog externally |
| "Message" (Slate) | transient PIE popup | close with `WM_CLOSE` |

Close it from outside the editor:

```powershell
# EnumWindows for the editor PID -> GetWindowText matches the title
# PostMessage(hwnd, 0x0010, 0, 0)   # WM_CLOSE
```

### 3. Verify the spawn

```bash
grep -E "Game class is|Bringing World|LogSpawn" "D:/UE/<project>/Saved/Logs/<Project>.log" | tail -8
```

- `Game class is 'BP_LabGameMode_C'` — the intended game mode is in play
- `LogSpawn: Warning: Login failed: PlayerState is null` — the game mode is
  wrong or half-configured
- The pawn should appear in `find_actors` results

### 4. Inject input

The editor may be **minimised** — synthetic input goes nowhere until it is
restored.

```python
import ctypes, ctypes.wintypes as wt, time
u = ctypes.windll.user32
u.SetProcessDPIAware()
hwnd = <editor hwnd>

u.ShowWindow(hwnd, 9)              # SW_RESTORE  (skip if already visible)
time.sleep(1.0)
u.SetForegroundWindow(hwnd)
time.sleep(0.5)

r = wt.RECT(); u.GetWindowRect(hwnd, ctypes.byref(r))
u.SetCursorPos(r.left + int((r.right-r.left)*0.52),
               r.top  + int((r.bottom-r.top)*0.45))
time.sleep(0.25)
u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(0.05)   # LEFTDOWN
u.mouse_event(0x0004, 0, 0, 0, 0); time.sleep(0.5)    # LEFTUP  -> viewport focus

u.keybd_event(0x57, 0, 0, 0); time.sleep(2.0)          # W down  (0x57)
u.keybd_event(0x57, 0, 0x0002, 0)                      # W up    (KEYEVENTF_KEYUP)
```

Order matters: **focus first, then move the cursor, then click**. A click
sent before `SetForegroundWindow` lands on whatever was under the cursor.

Virtual keys: `W` = 0x57, `A` = 0x41, `S` = 0x53, `D` = 0x44,
`SpaceBar` = 0x20, `LeftShift` = 0xA0.

### 5. Read the result back — and wait for the tick

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

T("editor_toolset.toolsets.actor.ActorTools.get_actor_transform", actor=pawn_ref)
```

**Read the transform only after the world has ticked.** This is the single most
common false negative in this whole workflow — a character that *did* move
reads as stationary.

Observed in the FabAssets session: input was injected, and the very next read
showed the pawn still at its spawn position; a later read showed it
displaced and rotated. The log for those PIE sessions recorded
`Bringing World ... up for play (max tick rate 3)` — later sessions recorded
`max tick rate 0`. The editor window had been **minimised** for part of that
testing, and a hidden editor does not tick normally.

So the rules are:

1. **Restore the editor window before injecting input** (step 4 does this).
   A minimised editor also receives no synthetic input at all.
2. **Wait, then read.** Give the world a moment to tick, then read; if the
   value is unchanged, read again before concluding anything.
3. Cross-check the tick rate in the log — `max tick rate 3` on a session you
   expected to be full-speed is the tell that the window was hidden.

| What changed | Proves |
|---|---|
| position | the axis mapping reached `AddMovementInput` |
| yaw / pitch | mouse look reached `AddControllerYawInput` / `AddControllerPitchInput` |
| `MaxWalkSpeed` on the movement component | a held action fired (sprint) |

### 6. Stop PIE and save

```python
T("EditorToolset.EditorAppToolset.StopPIE")
```

**`save_assets` fails with "Asset does not exist" while PIE is running** — stop
PIE before saving, always.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `StartPIE` hangs >120 s | a modal dialog is blocking the editor | close it externally; fix the underlying error |
| `input param 'options' is required` | arguments not nested | wrap in `{"options": {...}}` |
| Injecting keys does nothing | the editor is minimised | `ShowWindow(hwnd, 9)` first |
| Injecting keys does nothing | the click landed before focus | focus → move cursor → click → key |
| The pawn reads as unmoved after W | read before the world ticked | wait, then read again |
| `save_assets` → "Asset does not exist" | PIE still running | stop PIE, then save |
| `Login failed: PlayerState is null` | wrong game mode | check `Game class is '...'` |
| `CaptureViewport` shows no PIE actors | it renders the *editor* world | verify numerically instead |

**A restart of PIE is required after changing blueprints or the game mode** —
the running session keeps the old compiled state.

**Stop PIE before saving anything.** This one bites repeatedly.

## Output contract

- PIE starts and stops without wedging the editor
- the log shows the intended game mode and a spawn
- the runtime state read back matches the intended behaviour (position,
  rotation, speed)

## Related

- `ue-op-fix-compile-error` — when PIE will not start
- `ue-op-setup-game-mode` — what PIE is verifying
- `ue-op-setup-input` — the bindings being exercised
