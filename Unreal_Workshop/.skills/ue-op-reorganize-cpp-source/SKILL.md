---
name: ue-op-reorganize-cpp-source
description: Use when C++ files have been moved into new subfolders inside a UE module and the project no longer compiles — restores the build by fixing the module's include paths in the .Build.cs, and enumerates every unresolved #include in one pass instead of one compiler error at a time. Skip when the failure is a blueprint compile error (ue-op-fix-compile-error) or when the files were moved outside the engine (ue-op-restructure-content covers .uasset moves).
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# ue-op-reorganize-cpp-source — move module source files without breaking the build

Moving `.cpp` / `.h` files into subfolders is safe **only** if the module's
include paths cover the new folders. Unreal Build Tool does not discover them.

## When to apply

- The project stopped compiling right after someone reorganised `Source/<Module>/`
- `fatal error C1083: Cannot open include file: 'Something.h'` where `Something.h`
  visibly exists in the module, just in a different folder
- A new folder was added to a module and its headers cannot be found

## When NOT to apply

- The error is a **blueprint** compile error — see `ue-op-fix-compile-error`
- The files moved are **`.uasset` / `.umap`** — see `ue-op-restructure-content`
- The header genuinely does not exist anywhere (a typo or a deleted file)

---

## The rule that causes the whole failure

UBT resolves `#include "Foo.h"` against:

1. the directory of the **including file** (quoted includes only),
2. every directory in the module's `PublicIncludePaths` / `PrivateIncludePaths`.

A module that declares its own `PublicIncludePaths` does **not** get its
subdirectories auto-expanded. A newly created folder is invisible to the
compiler until it is listed in the `.Build.cs`.

`PublicIncludePaths` entries are relative to the module's **parent** directory
(`Source/`), so `"<Module>"` is the module root and `"<Module>/Core"` is a
subfolder of it.

## Procedure

### 1. Get the real error, not a guess

```
fatal error C1083: Cannot open include file: 'MyCharacter.h': No such file or directory
#include "MyCharacter.h"
```

The compiler stops at the **first** error. There are usually more. Do not
fix-one-rebuild-repeat — enumerate them all first (step 2).

### 2. Enumerate every unresolved include in one pass

```bash
ENGINE=$(find "C:/Program Files/Epic Games" -maxdepth 1 -name "UE_*" -type d | sort -V | tail -1)

python "V:/04_Projects/Workshops/Unreal_Workshop/.skills/ue-op-reorganize-cpp-source/scripts/check_cpp_includes.py" \
    "D:/UE/<Project>/Source/<Module>" \
    --engine "$ENGINE/Engine/Source"
```

It reads the `.Build.cs`, reproduces UBT's resolution exactly, and reports:

| Bucket | Meaning | Action |
|---|---|---|
| `MISSING` | a project header no include path reaches | **this is the bug** |
| `ABSENT` | the header exists nowhere | typo or deleted file |
| *(resolved elsewhere)* | engine headers and UHT `.generated.h` | fine, ignore |

It also prints the exact include-path list the build will use.

### 3. Read the authoritative include paths

Do not infer them. UBT writes the real `/I` list to:

```
Intermediate/Build/Win64/x64/UnrealEditor/Development/<Module>/<Module>.Shared.rsp
```

```
/I"D:/UE/<Project>/Source/<Module>"
/I"D:/UE/<Project>/Source/<Module>/<Folder>"
...
```

The sibling `<File>.cpp.obj.rsp.old` files record the **pre-move** source paths —
that is the oracle for "what did the layout look like before".

### 4. Fix it — pick one of two shapes

**(a) Add the folder to the include paths.** Keeps includes short and matches a
project that already lists every folder it references:

```csharp
PublicIncludePaths.AddRange(new string[] {
    "<Module>",
    "<Module>/Character",   // <-- added
    "<Module>/Core",        // <-- added
    "<Module>/<Variant>"
});
```

**(b) Make includes module-root-relative.** One include path instead of many, and
the include survives the *next* move:

```cpp
#include "Character/MyCharacter.h"   // resolved from the module root
```

(a) is the smaller diff when the project already lists folders. (b) is more
robust long-term and removes the need to keep the list in sync.

### 5. Build — with the editor closed

The linker cannot overwrite a loaded `UnrealEditor-<Module>.dll`.

```bash
powershell -NoProfile -Command "Get-Process UnrealEditor -ErrorAction SilentlyContinue"
```

Then build **both** targets:

```bash
ENGINE=$(find "C:/Program Files/Epic Games" -maxdepth 1 -name "UE_*" -type d | sort -V | tail -1)

"$ENGINE/Engine/Build/BatchFiles/Build.bat" <Project>Editor Win64 Development \
    -Project="D:/UE/<Project>/<Project>.uproject" -WaitMutex -NoHotReloadFromIDE

"$ENGINE/Engine/Build/BatchFiles/Build.bat" <Project> Win64 Development \
    -Project="D:/UE/<Project>/<Project>.uproject" -WaitMutex
```

`Result: Succeeded` and zero `warning` lines is the bar. Relaunch the editor
afterwards.

---

## Verified facts & gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `C1083: Cannot open include file` for a header that exists in the module | the folder holding it is not in the module's `PublicIncludePaths` | add the folder, or make the include module-root-relative |
| one error at a time, fix-and-rebuild cycles | the compiler stops at the first error | run `check_cpp_includes.py` to get the full set |
| include paths look right but the header still is not found | `.Build.cs` paths are relative to `Source/` (the module's **parent**), not to the module folder | `"<Module>/Core"`, not `"Core"` |
| a header in a **new** folder cannot be seen | a module with its own `PublicIncludePaths` does not get subdirectories auto-expanded | list the folder explicitly |
| suspect the module root is not searched | it is — the module root is always searched, and quoted includes also resolve relative to the including file | check a **sub**folder instead |
| UHT errors after a move | UHT is not the problem: generated headers are written **flat** to `Intermediate/Build/<Plat>/<Arch>/<Target>/Inc/<Module>/UHT/<Class>.generated.h` and included by bare class name | ignore; only the include paths break |
| linker error `cannot open file ... .dll` | the editor is running and holds the module DLL | close the editor, then build |
| a script "cannot find" a path that exists | Git Bash `/tmp` is `%TEMP%`, but Windows Python resolves `/tmp` against the current drive | use Windows-style `D:/...` paths in scripts |
| the build succeeds but the editor still has old code | the editor was never relaunched | relaunch it |

## Output contract

- The module's `.Build.cs` lists every folder that contains a referenced header
- `check_cpp_includes.py` reports `MISSING 0` for the module
- Both `<Project>Editor` and `<Project>` targets build with `Result: Succeeded`
  and no warnings
- The editor relaunches and loads the project module

## Related

- `ue-op-fix-compile-error` — blueprint compile errors, not C++
- `ue-op-restructure-content` — moving `.uasset` / `.umap` content, where the
  reference-rewriting rules are completely different
