<#
  ue-op-build-web/scripts/build_web.ps1

  Cook + package a UE 5.9 Wasm/WebGPU web build, re-patch the map token that
  UAT overwrites, and release-scan the stage.

  Example:
    powershell -NoProfile -ExecutionPolicy Bypass -File build_web.ps1 `
      -Project D:\UE\EpicJam2026 -Map /Game/Map/MeshTerrain -Stage WasmWeb7
#>
[CmdletBinding()]
param(
    [string]$Project    = 'D:\UE\EpicJam2026',
    [string]$Map        = '/Game/Map/MeshTerrain',
    [string]$Stage      = 'WasmWeb',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.9',
    [string]$Emsdk      = 'D:\emsdk-6.0.10',
    [switch]$SkipBuild  # re-patch + re-scan an existing stage only
)

$ErrorActionPreference = 'Stop'

$projectName = Split-Path $Project -Leaf
$uproject   = Join-Path $Project "$projectName.uproject"
$uat        = Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
$python     = Join-Path $EngineRoot 'Engine\Binaries\ThirdParty\Python3\Win64\python.exe'
$checkStage = Join-Path $EngineRoot 'Engine\Platforms\Wasm\Build\Tools\deploy\check_stage.py'
$stageDir   = Join-Path $Project "Saved\$Stage"
$uatLog     = Join-Path $Project "Saved\$Stage.uat.log"

foreach ($p in @($uproject, $uat, $python, $checkStage)) {
    if (-not (Test-Path $p)) { throw "missing: $p" }
}
if (-not $SkipBuild -and -not (Test-Path $Emsdk)) { throw "missing emsdk: $Emsdk" }

# the agent shell's WASM_EMSDK_ROOT is stale -> always set it here
$env:WASM_EMSDK_ROOT = $Emsdk

if (-not $SkipBuild) {
    Write-Host "[1/5] cook + package -> $stageDir" -ForegroundColor Cyan
    $uatArgs = @(
        'BuildCookRun',
        "-project=$uproject",
        '-platform=Wasm',
        '-clientconfig=Shipping',
        '-cook', '-stage', '-pak', '-iostore', '-package', '-archive',
        "-archivedirectory=$stageDir",
        "-map=$Map",
        '-AdditionalCookerOptions="-unattended -nopause -nosplash -nullrhi"',
        '-nocompileeditor', '-unattended', '-utf8output'
    )
    & $uat @uatArgs 2>&1 | Tee-Object -FilePath $uatLog
    if ($LASTEXITCODE -ne 0) { throw "UAT failed (exit $LASTEXITCODE) - see $uatLog" }
    if (-not (Test-Path $stageDir)) { throw "no stage folder at $stageDir" }
} else {
    Write-Host "[1/5] -SkipBuild: reusing $stageDir" -ForegroundColor Yellow
}

# UAT rewrites UECommandLine.txt during packaging -> the map token must be
# rewritten afterwards, or the page boots the default map.
Write-Host "[2/5] re-patch the map token" -ForegroundColor Cyan
$cmdline = '{0} -project="../../../{1}/{1}.uproject"' -f $Map, $projectName
Set-Content -Path (Join-Path $stageDir 'UECommandLine.txt') -Value $cmdline -Encoding utf8 -NoNewline
Write-Host "       $cmdline"

Write-Host "[3/5] release scan" -ForegroundColor Cyan
& $python $checkStage $stageDir
if ($LASTEXITCODE -ne 0) { throw "release scan reported problems in $stageDir" }

Write-Host "[4/5] stage summary" -ForegroundColor Cyan
$files = Get-ChildItem $stageDir -Recurse -File
$mb = [math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Host "       files=$($files.Count)  size=${mb} MB"
foreach ($j in @('wasm-tiers.json', 'wasm-manifest.json')) {
    $p = Join-Path $stageDir $j
    if (Test-Path $p) { Write-Host "       $j = $((Get-Content $p -Raw).Trim())" }
}

Write-Host "[5/5] done" -ForegroundColor Green
Write-Host "       stage : $stageDir"
Write-Host "       next  : ue-op-verify-web -Stage $Stage"
