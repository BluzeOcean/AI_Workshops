# The linker cannot overwrite a module DLL the editor has loaded — verify the link in a scratch copy

**Status:** active

**Date:** 2026-11-26
**Symptom:** A module restructure compiled cleanly — every file, no errors — and then
the link failed:

```
[28/30] Link [x64] UnrealEditor-IronPath.lib
[29/30] Link [x64] UnrealEditor-IronPath.dll
LINK : fatal error LNK1104: cannot open file
       'D:\UE\IronPath\Binaries\Win64\UnrealEditor-IronPath.dll'
```

UBA first retried for 20 seconds and gave the real reason: *"The process cannot access
the file because it is being used by another process — UnrealEditor.exe"*. The editor
was running, and it has that DLL open.

**Cause:** Windows will not let the linker overwrite a loaded DLL. The module's output
path is fixed by the target, so `-OutputDir=` does not move it — the build still tried to
write `Binaries/Win64/UnrealEditor-<Module>.dll`. The only ways past it are to close the
editor, or to link somewhere the editor is not holding the file.

**Fix:** Build a **scratch copy of the project** and link there. The editor never has
those binaries open, so the link runs:

```bash
rm -rf "<Project>/Saved/LinkCheck"
mkdir -p "<Project>/Saved/LinkCheck"
cd "<Project>"
cp <Project>.uproject "<Project>/Saved/LinkCheck/"
cp -r Config "<Project>/Saved/LinkCheck/"
mkdir -p "<Project>/Saved/LinkCheck/Source"
cp -r Source/<Module> "<Project>/Saved/LinkCheck/Source/"
cp Source/*.Target.cs "<Project>/Saved/LinkCheck/Source/"

"C:/Program Files/Epic Games/UE_5.9/Engine/Build/BatchFiles/Build.bat" \
    <Module>Editor Win64 Development \
    -Project="<Project>/Saved/LinkCheck/<Project>.uproject" -WaitMutex -NoHotReloadFromIDE
```

`Result: Succeeded` there means the module compiles **and** links. The copy needs only
the `.uproject`, `Config/` and `Source/` — no content, no assets. Put it under `Saved/`,
which is engine-owned and gitignored. A Development **game** target is not an
alternative: only `DebugGame` and `Shipping` engine binaries ship with an installed
engine, so a Development game target rebuilds the engine from source.

**Applies when:** The editor is running, the project cannot be closed (it holds the
user's unsaved work), and a link needs verifying anyway — a module restructure, a new
dependency, a first build of a ported module.

**Related:** the procedure is
[`ue-op-reorganize-cpp-source`](../../.skills/ue-op-reorganize-cpp-source/SKILL.md),
whose step 5 says to build with the editor closed; this is the alternative when you
cannot close it. A scratch copy proves the link but does **not** load the new module
into the running editor — the editor still needs a restart for a module layout change.
