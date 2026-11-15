---
name: ue-op-fix-large-ue-sample-project
description: Use when a large imported Unreal sample project or asset-pack demo map is slow, cluttered or broken in the editor - a level that takes minutes to open, thousands of assets dumped on one spot, duplicate lights, assets buried under the ground, or a save that silently does nothing - and the task is to make the project work smoothly again. Works headless through the editor's own Python, so it does not need an MCP connection and never takes over the user's screen. Skip for a single broken blueprint (use ue-op-fix-compile-error), moving assets between projects (use ue-op-relocate-assets), or authoring new gameplay.
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# ue-op-fix-large-ue-sample-project — make a big sample project usable again

## Why this exists

A large sample project or a marketplace asset pack arrives as a *dump*: every
asset in the pack is instantiated, usually on one spot, usually with the
pack's own debug labels and placeholder lights left switched on. It then
behaves badly in ways that look like engine bugs and are not:

- the level takes **minutes to open** the first time and seconds afterwards
- everything is stacked in one corner, or spread but half-buried
- the viewport is washed out, or pitch black on one side
- the editor prints warnings you cannot see the cause of
- **your edits vanish on save** and nothing says why

None of that is a rendering problem. It is an *authoring-time* problem, and it
has a small number of causes that this skill teaches you to find.

The single most valuable thing in this skill is §1. Almost every "my change
did nothing" symptom in the editor is that one rule, and it is invisible
because the API reports success.

---

## 1. The rule that makes everything work: function calls do not persist

**In the editor's Python, a plain function call does not mark the actor's
package dirty. The save then skips that actor, and it reverts on the next
load — while the save API still reports success.**

```python
# WRONG - the move happens in memory, is never marked dirty, and is
# silently dropped by the save
actor.set_actor_location(new_pos, False, False)
actor.set_actor_scale3d(new_scale)
actor.set_actor_rotation(new_rot)
actor.set_actor_hidden_in_game(True)
```

```python
# RIGHT - sets the root component's properties, which goes through
# PostEditChange and marks the package dirty
comp = actor.get_editor_property("root_component")
comp.set_editor_property("relative_location", unreal.Vector(x, y, z))
comp.set_editor_property("relative_rotation", unreal.Rotator(roll=r, pitch=p, yaw=y))
comp.set_editor_property("relative_scale3d", unreal.Vector(sx, sy, sz))
```

This applies to **every** plain setter, not just transforms:

| Call | Persists? |
|---|---|
| `actor.set_actor_location / scale / rotation` | **no** |
| `actor.set_actor_hidden_in_game(True)` | **no** |
| `actor.set_actor_label("X")` | unreliable — pair it with a property set |
| `comp.set_editor_property("intensity", 1.2)` | **yes** |
| `comp.set_editor_property("relative_location", v)` | **yes** |
| `actor.set_editor_property("hidden", True)` | **yes** (if the property exists) |

**Rule:** after any Python edit, set at least one root-component property on
that actor, or explicitly mark the package dirty. When in doubt, do both.

### Verify the save — never trust the return value

`save_map()` returning `True` means "the save ran", not "the change is on
disk". Always confirm with a **reload**:

```python
unreal.EditorLevelLibrary.load_level(MAP)      # or LevelEditorSubsystem
world = unreal.EditorLevelLibrary.get_editor_world()
# re-read the actor and check its transform
```

Or check the file's mtime changed, or grep the log for `Error saving`.

---

## 2. Procedure

Work in this order. Each step has a pass condition, and **do not start the
next step until the current one passes** — otherwise you are fixing
symptoms on top of an unverified baseline.

### Step 0 — locate the project, the engine, and the version

```bash
# engine: the launcher registry lists every installed version
powershell -NoProfile -Command "
  (Get-ItemProperty 'HKCU:\SOFTWARE\Epic Games\Unreal Engine\Builds').PSObject.Properties |
    Where-Object { \$_.Value -and (Test-Path \$_.Value) } |
    Select-Object Name, Value"

# version of the project you are opening
grep -m1 "EngineAssociation" <project>/<project>.uproject
```

Every API note below is written for UE 5.x. On 4.x the Python plugin may
not even be enabled. **When a call fails, look for the modern equivalent
rather than assuming the feature is missing** — see §5.

### Step 1 — measure the map before you touch it

Run the bundled inventory script. It is read-only and works on any map:

```bash
UE_MAP=/Game/Maps/MyMap \
  ./ue_run_headless.sh <project>/<project>.uproject ue_map_inventory.py
```

It reports, and writes to `Saved/ue_inventory.json`:

- actors per class, and the total
- **mesh instances vs distinct meshes** — the number that actually drives cost
- distinct materials, and distinct (mesh, material) pairs (= PSO count)
- **the biggest pile of actors sharing an identical transform** ← bulk-import debris
- the level's world extent
- **the furthest actors on each axis** ← strays and transposed scales; this is
  what catches a wall that ended up 15,000 units outside the map
- actors whose lowest point is below the ground
- every light with its intensity and `ForwardShadingPriority`
- every BSP brush with its bounds ← real ground, and a cause of buried assets

**Pass condition:** you can state, in numbers, how many distinct meshes the
map holds and how many instances sit on one spot.

### Step 2 — attribute the slow open

The cost is per *asset*, not per level, and it is one-time. Find it in the
editor log:

```bash
grep -c "Finished distance field build" Saved/Logs/*.log
grep -c "Finished mesh card build"     Saved/Logs/*.log
```

Measured on UE 5.8, one distinct mesh costs roughly:

| Per-asset build | Time | Applies to |
|---|---|---|
| Distance field (a `126³` sparse texture of distance-to-surface) | **~2.5 s** | every mesh with Lumen/DFAO/contact shadows |
| Nanite mesh card (a coarse stand-in for distant rendering) | **~1.9 s** | ~20 % of meshes |
| **Blended** | **~3 s per distinct mesh, once** | |

So a level with 1,400 distinct meshes costs ~70 minutes of build **the first
time it is ever opened**, and ~15 seconds every time after that. **This is
why the second open is fast and the first is not** — and it is why the
fix is not "make the materials simpler".

Confirm the attribution before you act: the counts must be attributable to
the map you are working on, not to the whole session.

### Step 3 — fix the load cost (the assets, not the level)

The distance field and mesh card are per-asset build products. The levers:

| Lever | How | Effect |
|---|---|---|
| **Kit and instance** | reuse a small set of meshes thousands of times instead of making thousands of unique ones | the only lever that scales the library |
| **Per-asset build settings** | turn distance-field / Nanite-card generation off for assets that do not need it (mesh editor → Build Settings) | skips the per-asset build for those assets |
| **Never bulk-import** | import 50 assets at a time, not 5,000 | keeps the editor responsive and the DDC warm |
| **Keep the DDC** | do not clear the Derived Data Cache | it is where the built assets live |

**Do not try to fix this with materials.** Material *instances* share the
parent's shader map, so there is one shader per master, not per instance —
consolidating instances to one master cannot remove a per-mesh build. An
A/B on the same map confirmed it: the material change moved a warm load by
about 12 seconds; the geometry work was hundreds of seconds and untouched.

### Step 4 — fix the map's content

Now the map itself. Use the inventory from step 1:

1. **Bulk-import debris.** The pile of actors sharing one transform is a
   leftover from the pack's own tooling. Either delete it, or — if the
   assets are wanted — spread it out (below).
2. **Scale the art to the map, not the map to the art.** Pack assets are
   built for the world the pack shipped with. If the pack's architrave is
   12 m long and your map is 30 m across, the piece is wrong at 1:1. Scale
   it to suit the map rather than fighting the collision.
   **A rotation transposes the scale axes** (see §5) — a scaled piece that
   looks wrong is often the right numbers on the wrong axis.
3. **Spread it out.** Decide the layout offline (a plain Python planner that
   checks each piece against the others and against the level's own
   geometry), then apply it. Planning offline takes seconds; doing it
   in-editor by trial and error takes many editor round-trips.
4. **Seat every asset on the real ground.** Do not assume z = 0. Cast a ray
   down at the target position and put the asset's bounds bottom on the hit.
   A BSP brush, a landscape or a raised platform in the middle of the map
   will otherwise bury your assets, and they will look like they are floating
   or half-sunk for reasons nobody can see.
5. **Fix the lights.** Duplicate directional lights all at priority 0 make
   UE pick one at random and warn. Give the main sun a higher
   `forward_shading_priority` than the fills, and delete the unused ones.
   A shadowless fill light (`cast_shadows=False`, low intensity) stops the
   shadowed side of every wall going solid black.
6. **Check the exposure.** A post-process volume with
   `bOverrideAutoExposureMaxBrightness=True` and a value of **0** clamps the
   auto exposure to nothing and leaves the scene black. Turn the override
   off so the project default applies.
7. **Delete the pack's debris** — floating text labels, editor-only
   placeholder actors, duplicate VFX. Use `destroy_actor`, and save.

### Step 5 — verify

- the map reopens and the actors are where you put them (reload, do not trust
  the in-memory state)
- the editor log shows no `Error saving`
- the slow-open cost is attributed and reduced
- render the map and **look** at it (§4) — a level that "should" be right is
  often not

---

## 3. Headless recipes

Everything here is done through the editor's own Python with
`ue_run_headless.sh`, which renders offscreen. **It never opens a window and
never takes over the user's screen**, and it does not need an MCP connection —
which matters, because the MCP bridge is often the thing that is already
wedged.

### Run a script in the editor

```bash
UE_MAP=/Game/Maps/MyMap ./ue_run_headless.sh <proj>.uproject my_script.py
```

The runner finds the engine itself (standard install folder, then the
launcher registry), and passes every `UE_*` variable through to the script.

### `-ExecCmds`, not `-ExecutePythonScript`

`-ExecutePythonScript=<file>` runs the script during startup and **quits the
editor as soon as the script returns**. Any work the script deferred to a
tick callback is truncated without a word. Use:

```
-ExecCmds="py exec(open(r'<script>.read())"
```

which runs the script and leaves the editor up.

**The path must be absolute.** The editor's working directory is the project
folder, not where you launched from, so a relative path fails with
`FileNotFoundError` — and the editor then sits there idle forever, holding
the map open, because nothing asked it to quit. `ue_run_headless.sh` resolves
the path and wraps the script in a launcher that registers the watchdog.

### Every script needs a watchdog

If the script raises, the editor stays open forever and the next run fights
it. Put this at the top of every script:

```python
import time
_T0 = time.time()

def _watchdog(delta):
    if time.time() - _T0 > 600:
        try:
            unreal.SystemLibrary.quit_editor()
        except Exception:
            pass

unreal.register_slate_post_tick_callback(_watchdog)
```

### Render the map without a window

```python
def on_tick(delta):
    world = unreal.EditorLevelLibrary.get_editor_world()
    now = unreal.SystemLibrary.get_game_time_in_seconds(world)
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(
        unreal.Vector(x, y, z), unreal.Rotator(roll=0, pitch=pitch, yaw=yaw))
    unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, "/abs/path.png")
```

**Gate on the world's clock, not on a tick count.** The editor can spend
many seconds inside a single frame while it streams textures and compiles
shaders, so a shot requested by tick count lands on a frame that has not
rendered yet — and you get a black or stale image. The world clock only
advances when frames are actually being produced.

Also note: the console command `HighResShot` renders **black** in some
editor configurations; `take_high_res_screenshot` does not.

### Ray-cast the ground

```python
hits = unreal.SystemLibrary.line_trace_multi(
    world,
    unreal.Vector(x, y, 20000.0), unreal.Vector(x, y, -3000.0),
    unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True,
    list(actors_to_ignore),          # required argument
    unreal.DrawDebugTrace.NONE, True)
ground_z = min(float(h.location.z) for h in hits)   # attribute name varies by version
```

The argument list differs between versions (`actors_to_ignore` is
positional and required in some). If it throws, try
`unreal.SystemLibrary.line_trace_single`, and read the hit position from
`location`, `impact_point` or `hit_location` — which one exists varies.

---

## 4. Measuring the result

- **Editor open time**: time a cold open (first ever) versus a warm one.
  The ratio tells you whether you are still paying per-asset build cost.
- **Attribute the cost**: `grep -c "Finished distance field build"` in the
  log, per map.
- **Look at it**: render from a plan view and from ground level. A plan view
  exposes "everything is on one spot" and "the ground does not reach the
  horizon"; a ground-level view exposes "the walls are solid black" and
  "the assets are half-buried".
- **Count the light warning**: multiple directional lights at the same
  `forward_shading_priority` is the cause.

---

## 5. Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Edits vanish on save; the API still returns `True` | a plain function call never marked the package dirty | set the root component's properties instead (§1) |
| `save_map` returns `True` but the file is unchanged | the package was not dirty, or the save failed silently | reload and check; grep the log for `Error saving` |
| `MoveFile was unable to move '<map>.umap' to temp directory` | another editor process holds the file open | close the other editor, or save to a **new map path** with `save_map(world, "/Game/Maps/Other")` |
| The editor quits the moment your script returns | `-ExecutePythonScript` | use `-ExecCmds="py exec(open(r'...').read())"` |
| `FileNotFoundError` for a script that exists, and the editor never exits | the path was relative — the editor's CWD is the project folder | pass an absolute path, and wrap the script in a launcher that registers the watchdog and quits on failure |
| The editor stays open forever after a script error | no watchdog | add the tick watchdog (§3) |
| A screenshot comes out black or stale | the shot was requested on a frame that had not rendered | gate on the world clock, not a tick count |
| The console `HighResShot` renders black | editor configuration | use `AutomationLibrary.take_high_res_screenshot` |
| An actor moves but does not survive a reload | dirty-flag rule (§1) | set a root-component property |
| `set_actor_hidden_in_game(True)` does not stick | same dirty-flag rule | `set_editor_property("hidden", True)` |
| A Niagara system ignores its actor's transform | it is simulated in **world space** | move the emitter's parameters, or delete the actor; scaling the actor does nothing |
| "Multiple directional lights are competing" | several lights share the top `forward_shading_priority` | give the main sun a higher priority, delete the unused ones |
| Assets half-buried in the floor | they were placed at z = 0 but the real surface is elsewhere | ray-cast down to seat them |
| The level is black on one side | the shadow-side faces get no fill | add a shadowless fill light, and check the exposure override |
| Everything looks grey and flat | the auto-exposure override is clamped to 0 | turn off `bOverrideAutoExposureMaxBrightness` |
| Every asset is the same size / all on one spot | the mesh's **bounds** were read from the wrong source | read `mesh.get_bounds()` from the loaded asset; `AssetData.get_bounds()` does not exist in some versions and a silent fallback makes everything uniform |
| A mesh is scaled to fit but still overlaps its neighbour | the scale was computed from a fallback dummy size | measure real bounds, and fit on **all three axes** |
| A wall or slab is miles long, or lies on the wrong edge | **a rotation transposes the scale axes**: under a 90° yaw the mesh's local X becomes world Y and local Y becomes world X, so `scale (5, 175, 4)` puts the 175 on the *thickness* axis | check the actor's yaw before trusting a scale. The engine's `get_actor_bounds()` tells you the truth — compare it against what you intended to build |
| A piece is rotated but its footprint is still wrong | the mesh's **bounds origin is not its centre** (a 100-unit cube often has its origin at (50,50,50)), so the box runs from the actor's position, not around it | compute the world box from the bounds origin and extent, not from the actor location |
| The ground runs out and the sky shows underneath | the sky dome mesh is smaller than the level | scale the sky dome up to enclose the level |
| The level looks cramped no matter how much you spread things | the assets are sized for a much larger world than this one | scale the art to the map |

### Version and API portability

- `unreal.EditorLevelLibrary` is deprecated in 5.x in favour of
  `unreal.LevelEditorSubsystem`; both usually work. Try the modern one, fall
  back to the old one.
- `AssetData.get_bounds()` exists in some versions and not others. The loaded
  asset's `get_bounds()` is reliable everywhere.
- `NiagaraActor` does not expose `deactivate()` or `set_actor_enabled()` in
  some versions. Reach the component instead.
- `line_trace_multi` argument lists shift between versions. Pass
  `actors_to_ignore` explicitly and read the hit position from whichever of
  `location` / `impact_point` / `hit_location` exists.
- Everything in §1 is engine-fundamental, not version-specific: it is about
  `Modify()` not being called outside an undo transaction.

---

## 6. Output contract

A finished pass leaves:

- the map's contents measured and written down (distinct meshes, instances,
  materials, PSOs, light count, extent)
- the slow-open cost attributed to a specific cause, with the number
- the bulk-import debris gone or deliberately spread out
- every asset seated on the real ground, verified by a reload
- one directional light with the winning priority, and the competing ones
  either given a lower priority or removed
- the save confirmed by a reload, not by the API's return value
- renders from a plan view and from ground level, so the result is seen and
  not just asserted
- anything that could not be fixed is listed, with the reason

---

## 7. Related

- `ue-op-find-dependencies` — compute a closure before moving anything
- `ue-op-relocate-assets` — move an asset set into a self-contained folder
- `ue-op-fix-compile-error` — if a blueprint stops compiling afterwards
- `ue-op-test-pie` — verify the result runs, not just that it opens
- `ue-op-capture-editor` — editor-window screenshots, when MCP is connected
