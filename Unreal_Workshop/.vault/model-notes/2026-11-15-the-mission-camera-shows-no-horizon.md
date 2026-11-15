# The mission camera shows no horizon - and what that forces on a backdrop

**Status:** active

**Recorded:** 2026-11-15, against D:\UE\EpicJam2026 Mission1. Numbers read from
AJamPlayerController / AJamPawn, not estimated.

## The rig

| Knob | Value | Where |
| --- | --- | --- |
| pitch | **-38 deg** | AJamPlayerController::CameraPitch (spec range 30-45) |
| distance along view axis | 9000 cm | CameraDistance |
| width at the focus plane | **5200 cm** on a mission (2600 at the lab bench) | AJamGameMode::MissionOrthoWidth |
| lens | FOV_x = 2*atan((W/2)/D) = **32.23 deg**, perspective, x-FOV maintained | AJamPawn::ApplyCameraRig |
| pan | +-2200 cm X, +-2400 cm Y | AJamPawn |

At 16:9 that is a **vertical** field of 18.45 deg, so the top edge of the frame is
38 - 9.22 = 28.78 deg **below horizontal** - it still points at the ground. Consequences:

- **The horizon is never in frame, at any zoom or pan.** Sky would need a pitch under
  9.2 deg, which is not this game.
- The top of the frame hits z = 0 about **2990 cm** ahead of the pawn; the bottom about
  **1960 cm** behind. The visible ground is a band ~4950 cm deep and ~5200 cm wide.
- Anything standing beyond that ~2990 cm point is **above the top edge of the frame at
  every height** - a tall object further away does not 'poke into' the shot.

## What a far-scenery backdrop has to be

A **ground-plane plate, not a standing billboard.** Past the deck's far edge the view rays
continue downward, so the space below and beyond the deck is visible even though the ground
there is not. The concept art's city therefore lives on a horizontal plane at z around
-1600 beyond the deck edge, and only the band between the deck edge and the top of the
frame (about 18% of screen height, panned up-field) ever shows it.

Practical sizing rule: place the plate from the deck edge out to where the **topmost view
ray** meets the plate's Z - at pitch 38 / FOV 32 / z = -1600 that is ~8100 cm from the
pawn. A deeper plate only ever shows its far end, and if that end is sky the backdrop
renders as white fog. That happened twice before the size was computed.

## Correction to a natural assumption

'Billboard behind the fortress' is the obvious concept-art reading and it cannot be built
at this pitch. The fortress itself is cut by the top edge of the frame at the centre
position and appears whole only when the player pans up-field toward the enemy.
