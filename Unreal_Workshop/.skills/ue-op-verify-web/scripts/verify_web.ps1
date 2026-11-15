<#
  ue-op-verify-web/scripts/verify_web.ps1

  Actions:
    headless  boot the stage in headless Chrome, report WebGPU errors, keep screenshots
    visible   serve the stage and open a real Chrome window for the user
    stop      kill the local server and release the port

  Examples:
    powershell -NoProfile -ExecutionPolicy Bypass -File verify_web.ps1 -Action headless `
      -Project D:\UE\EpicJam2026 -Stage WasmWeb7 -Out WasmTest7
    powershell -NoProfile -ExecutionPolicy Bypass -File verify_web.ps1 -Action visible `
      -Project D:\UE\EpicJam2026 -Stage WasmWeb7 -Port 8936
    powershell -NoProfile -ExecutionPolicy Bypass -File verify_web.ps1 -Action stop -Port 8936
#>
[CmdletBinding()]
param(
    [ValidateSet('headless', 'visible', 'stop')]
    [string]$Action = 'headless',
    [string]$Project    = 'D:\UE\EpicJam2026',
    [string]$Stage      = 'WasmWeb',
    [string]$Out        = '',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.9',
    [string]$ExpectTier = 'forward',
    [int]$Port          = 8936,
    [int]$Timeout       = 300
)

$ErrorActionPreference = 'Stop'

$python     = Join-Path $EngineRoot 'Engine\Binaries\ThirdParty\Python3\Win64\python.exe'
$webrun     = Join-Path $EngineRoot 'Engine\Platforms\Wasm\Build\Tools\web\webrun.py'
$stageDir   = Join-Path $Project "Saved\$Stage"
$savedDir   = Join-Path $Project 'Saved'
$chrome     = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

function Stop-Serve {
    $procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
             Where-Object { $_.CommandLine -like '*serve.py*' }
    foreach ($p in $procs) { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    $left = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($left) { Write-Warning "port $Port still held by pid $($left.OwningProcess)" }
    else { Write-Host "port $Port released" -ForegroundColor Green }
}

switch ($Action) {

    'headless' {
        if (-not (Test-Path $stageDir)) { throw "no stage folder: $stageDir" }
        if (-not $Out) { $Out = "$Stage-test" }
        $outDir = Join-Path $savedDir $Out
        Write-Host "[headless] booting $stageDir -> $outDir" -ForegroundColor Cyan
        & $python $webrun run --stage $stageDir --fixture boot --out $outDir `
            --net none --headless --shots 8,14,20 --timeout $Timeout --expect-tier $ExpectTier
        $rc = $LASTEXITCODE
        Write-Host "[headless] screenshots:" -ForegroundColor Cyan
        Get-ChildItem $outDir -Filter '*.png' -ErrorAction SilentlyContinue |
            ForEach-Object { Write-Host "   $($_.FullName)" }
        Write-Host "[headless] READ THE SCREENSHOTS - a PASS alone does not mean the level is visible"
        exit $rc
    }

    'visible' {
        if (-not (Test-Path $stageDir)) { throw "no stage folder: $stageDir" }
        Stop-Serve | Out-Null
        Write-Host "[visible] serving $stageDir on port $Port" -ForegroundColor Cyan
        Start-Process -FilePath $python `
            -ArgumentList '-I', '-B', 'serve.py', '--root', $Stage, '--port', "$Port", '--port-tries', '5' `
            -WorkingDirectory $savedDir -WindowStyle Hidden
        Start-Sleep -Seconds 4
        $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if (-not $conn) { throw "server did not come up on port $Port" }
        Write-Host "[visible] server pid $($conn.OwningProcess)" -ForegroundColor Cyan
        if (Test-Path $chrome) {
            Start-Process $chrome -ArgumentList '--new-window', "http://127.0.0.1:$Port/index.html?ue-session=1"
            Write-Host "[visible] Chrome opened at http://127.0.0.1:$Port/index.html?ue-session=1" -ForegroundColor Green
        } else {
            Write-Warning "Chrome not found at $chrome - open the URL manually"
        }
        Write-Host "[visible] when the user is done:  verify_web.ps1 -Action stop -Port $Port"
    }

    'stop' { Stop-Serve }
}
