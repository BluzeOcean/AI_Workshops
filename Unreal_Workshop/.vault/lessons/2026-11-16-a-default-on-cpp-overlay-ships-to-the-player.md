# A default-on C++ overlay ships to the player

**Trigger.** The browser build of *Mech Tactic Cut* put the DEV STATS panel in the top
right of every mission frame. It was correct in the editor, so nobody looked for it
until the user opened the build and said "we forgot to turn off the dev stats panel".

**Cause.** The panel is game code — `UJamDevStatsWidget`, created by
`AJamGameMode::RefreshDevStats()` — and its master switch is a C++ default:

```cpp
/** The master switch. ON by default, and that is deliberate. ... */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Jam|Dev")
bool bDevMode = true;
```

That default was chosen so the overlay could not be "missing", and it is right for an
editor. But `BuildCookRun` compiles the same class into the wasm payload, where the
default is still `true` — so a shipping build carries the diagnostic bill. Two things
made it hard to see: the panel reads as part of the HUD, and PIE looks identical in both
states because PIE is the editor.

**Fix.** Gate the overlay on the build type, not on a checkbox someone has to remember:

```cpp
static bool AJamGameMode::IsDevOverlayAllowed()
{
#if WITH_EDITOR
    return true;                      // the editor keeps the panel
#else
    return FParse::Param(FCommandLine::Get(), TEXT("JamDevMode"));   // a build must ask
#endif
}
```

`RefreshDevStats()` early-outs on `!bDevMode || !IsDevOverlayAllowed()`, so the widget is
never created in a package. `-JamDevMode` still turns it on, which is what the playtest,
the trailer and the capture scripts pass.

**What it costs to fix late.** The panel is compiled into the wasm, so hiding it is not a
page edit and not a config flag: the project must be rebuilt (editor target for the
cooker, `EpicJam2026 Wasm Shipping` for the payload) and the four maps recooked —
about 12 minutes. Check the corner of one mission frame in a real browser afterwards;
the fix is only proven by a screenshot with that corner empty.

**The general rule.** Anything that is on by default in C++ — a debug draw, a stats
overlay, a `UE_LOG` spew, a cheat binding — reaches the player. Decide its shipping state
at the point it is created (`WITH_EDITOR`, `UE_BUILD_SHIPPING`, or a command-line
parameter), and treat "it is only in the editor" as a claim that needs a screenshot from
the package, not from PIE.
