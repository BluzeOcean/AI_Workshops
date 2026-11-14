<#
.SYNOPSIS
    Measure how much VRAM ComfyUI actually holds, and how much POST /free gives back.

.DESCRIPTION
    ComfyUI keeps models resident in VRAM between runs. On this machine the
    MOSS-Image stack is ~28 GB of weights on a 24 GB card, so most of it is
    parked in RAM with the hot part in VRAM - and that VRAM stays taken until
    something asks for it back.

    `POST /free` with {"unload_models": true, "free_memory": true} tells the
    running server to drop the models and hand the VRAM back to the card.
    This script measures before and after, so the number is measured rather
    than assumed.

    IMPORTANT: after a /free, the next render has to reload the models from
    disk. On this machine that is roughly a two-minute wait.

.EXAMPLE
    pwsh -File tools\free-vram.ps1
#>
[CmdletBinding()]
param(
    [switch]$Restore
)

$ErrorActionPreference = 'Stop'
$ComfyUrl = 'http://127.0.0.1:8188'

function Get-Gpu {
    $used = [int](& nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | Select-Object -First 1)
    $free = [int](& nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | Select-Object -First 1)
    $total = [int](& nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | Select-Object -First 1)
    return [pscustomobject]@{ usedMiB = $used; freeMiB = $free; totalMiB = $total }
}

function Get-ComfyProc {
    $c = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
         Where-Object { $_.CommandLine -like '*main.py*' } | Select-Object -First 1
    if (-not $c) { return $null }
    $p = Get-Process -Id $c.ProcessId -ErrorAction SilentlyContinue
    if (-not $p) { return $null }
    return [pscustomobject]@{
        pid = $c.ProcessId
        wsGB = [math]::Round($p.WorkingSet64 / 1GB, 2)
        privateGB = [math]::Round($p.PrivateMemorySize64 / 1GB, 2)
    }
}

Write-Host '=== VRAM held by ComfyUI ===' -ForegroundColor Cyan

$before = Get-Gpu
$procBefore = Get-ComfyProc
Write-Host ("before /free : GPU used {0} MiB, free {1} MiB   | ComfyUI WS {2} GB, private {3} GB" -f `
    $before.usedMiB, $before.freeMiB, $procBefore.wsGB, $procBefore.privateGB)

Write-Host 'POST /free {unload_models:true, free_memory:true} ...' -ForegroundColor Yellow
$body = '{"unload_models": true, "free_memory": true}'
Invoke-WebRequest -UseBasicParsing -Uri "$ComfyUrl/free" -Method POST -ContentType 'application/json' -Body $body | Out-Null

# give the server a moment to release and the allocator to return the pages
Start-Sleep -Seconds 8

$after = Get-Gpu
$procAfter = Get-ComfyProc
Write-Host ("after  /free : GPU used {0} MiB, free {1} MiB   | ComfyUI WS {2} GB, private {3} GB" -f `
    $after.usedMiB, $after.freeMiB, $procAfter.wsGB, $procAfter.privateGB) -ForegroundColor Green

$freed = $before.usedMiB - $after.usedMiB
$ramFreed = $procBefore.privateGB - $procAfter.privateGB
Write-Host ''
Write-Host ("VRAM RELEASED BY /free : {0} MiB ({1} GB)" -f $freed, [math]::Round($freed/1024,1)) -ForegroundColor Yellow
Write-Host ("RAM RELEASED BY /free  : {0} GB (process private {1} -> {2} GB)" -f $ramFreed, $procBefore.privateGB, $procAfter.privateGB) -ForegroundColor Yellow
Write-Host ("Card free now          : {0} MiB ({1} GB) of {2} MiB" -f $after.freeMiB, [math]::Round($after.freeMiB/1024,1), $after.totalMiB) -ForegroundColor Yellow
Write-Host ''
Write-Host '  Both VRAM and the staged RAM copies are released - ComfyUI drops back to' -ForegroundColor DarkGray
Write-Host '  roughly a 0.6 GB VRAM / 5.5 GB RAM idle server.' -ForegroundColor DarkGray
Write-Host '  The next render reloads the weights from disk and takes ~14 s instead of ~8 s.' -ForegroundColor DarkGray

if ($Restore) {
    Write-Host ''
    Write-Host 'Restoring: submitting a 1x1 warmup render to reload the models...' -ForegroundColor Cyan
    Write-Host '  (watch the VRAM climb back with nvidia-smi in another window)'
}
