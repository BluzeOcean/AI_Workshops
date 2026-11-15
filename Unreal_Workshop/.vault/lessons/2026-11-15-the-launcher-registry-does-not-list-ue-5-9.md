# The launcher registry does not list UE 5.9

**Status:** active

**Date:** 2026-11-15
**Symptom:** A version resolver built on the Epic launcher registry reports **5.8** as the
installed engine, while `UnrealEditor.exe` is demonstrably running from
`C:\Program Files\Epic Games\UE_5.9\`.

```powershell
reg query "HKLM\SOFTWARE\EpicGames\Unreal Engine" //s
```

returns `5.2, 5.4, 5.5, 5.6, 5.7, 5.8` — and no `5.9`. Meanwhile the directory
`C:\Program Files\Epic Games\UE_5.9\Engine\Build\Build.version` says `5.9.0`, and the
running editor's command line is
`"C:\Program Files\Epic Games\UE_5.9\Engine\Binaries\Win64\UnrealEditor.exe" "D:\UE\EpicJam2026\EpicJam2026.uproject"`.

**Cause:** The registry records *launcher* installs, not every install on disk. UE 5.9 was
installed without a launcher registry entry (installed outside the launcher, or the entry
was removed). It is a hint, not an authority.

**Fix:** Resolve the version by scanning the install directory:

```powershell
Get-ChildItem "C:\Program Files\Epic Games\UE_*\Engine\Build\Build.version" |
  ForEach-Object {
    $v = Get-Content $_.FullName | ConvertFrom-Json
    [pscustomobject]@{ Path = $_.FullName
                       Version = "$($v.MajorVersion).$($v.MinorVersion).$($v.PatchVersion)"
                       CL = $v.Changelist }
  } | Sort-Object { [version]$_.Version } -Descending
```

Take the highest version tuple. Use the registry only to double-check, never to decide.

**Applies when:** anything picks an Unreal install — a script, a tool, a skill's path, a
batch file. Also when the resolver and the running editor disagree: **the running editor's
executable path wins**, and the registry is simply wrong.
