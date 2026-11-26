# Moving C++ files into subfolders breaks the build unless the include paths list them

**Status:** active

**Date:** 2026-11-26
**Symptom:** After moving a project's character sources into
`Source/<Module>/Character/` and its game-mode and controller sources into
`Source/<Module>/Core/`, the project stopped compiling with:

```
Source/<Module>/Core/<Module>PlayerController.cpp(8,1):
fatal error C1083: Cannot open include file: '<Module>Character.h': No such file or directory
```

The header existed, one folder away. UHT was happy. Nothing else in the module was
wrong — exactly **one** include in the whole module was unresolvable.
**Cause:** Unreal Build Tool resolves `#include "Foo.h"` against the directory of the
including file and against the directories in the module's
`PublicIncludePaths` / `PrivateIncludePaths`. A module that declares its own
`PublicIncludePaths` does **not** get its subdirectories auto-expanded, so a folder
created after the list was written is invisible to the compiler. Two facts made this
cost time: the `.Build.cs` paths are relative to the module's **parent** directory
(`Source/`), not to the module folder — so `"<Module>/Core"`, not `"Core"` — and the
compiler reports only the **first** failing include, so fix-and-rebuild cycles
reveal them one at a time.
**Fix:** Add each folder that holds a referenced header to the module's
`PublicIncludePaths`, or make the include module-root-relative
(`#include "Character/<Module>Character.h"`, resolved from the module root) so it
survives the next move. To find every broken include at once rather than one
compiler error per rebuild, run
[`ue-op-reorganize-cpp-source`](../../.skills/ue-op-reorganize-cpp-source/SKILL.md)'s
`scripts/check_cpp_includes.py`, which reproduces UBT's resolution from the
`.Build.cs` and separates project headers (broken) from engine headers and UHT
`.generated.h` (fine). The authoritative include-path list is in
`Intermediate/Build/Win64/x64/UnrealEditor/Development/<Module>/<Module>.Shared.rsp`.
**Applies when:** Anyone creates a folder inside `Source/<Module>/` and moves
`.cpp`/`.h` files into it — and to the reverse question, "is a C++ file move safe
without touching the `.Build.cs`?" (no, unless the folder was already listed).

**Related:** the procedure is
[`ue-op-reorganize-cpp-source`](../../.skills/ue-op-reorganize-cpp-source/SKILL.md).
The content-side counterpart, where a raw file move strands references instead, is
[`a raw file move strands every reference`](2026-11-26-a-raw-file-move-strands-every-reference.md).
