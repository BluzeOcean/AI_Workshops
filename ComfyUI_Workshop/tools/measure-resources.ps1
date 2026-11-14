<#
.SYNOPSIS
    Sample GPU VRAM and process RAM over time, and report the peaks.

.DESCRIPTION
    Answers the question "how much VRAM and RAM does this task really need?"
    with measured numbers instead of a guess.

    Samples two things on an interval:
      - GPU memory used (nvidia-smi, MiB across the whole card)
      - The target process's Working Set and Private Bytes (bytes)

    Averages are nearly useless here - what matters is the PEAK, because that
    is what collides with whatever else wants the GPU.

.PARAMETER ProcessId
    The process to watch (e.g. ComfyUI's python.exe).

.PARAMETER DurationSec
    How long to sample.

.PARAMETER Out
    Write a JSON report (with the full timeline) to this path.

.EXAMPLE
    pwsh -File tools\measure-resources.ps1 -ProcessId 4700 -DurationSec 120 -Out work\measure.json
#>
[CmdletBinding()]
param(
    [int]$ProcessId = 0,
    # Match the process by name instead of a fixed pid - for a cold-boot
    # measurement the process does not exist yet when sampling starts.
    [string]$ProcessNameMatch = '',
    # Match a python.exe by its command line (e.g. '*main.py*').
    [string]$CommandLineMatch = '',
    [int]$DurationSec = 60,
    [int]$IntervalMs = 200,
    [string]$Out = ''
)

$ErrorActionPreference = 'Stop'

function Resolve-Target {
    if ($CommandLineMatch) {
        $c = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
             Where-Object { $_.CommandLine -like $CommandLineMatch } |
             Sort-Object CreationDate -Descending | Select-Object -First 1
        if (-not $c) { return $null }
        return (Get-Process -Id $c.ProcessId -ErrorAction SilentlyContinue)
    }
    if ($ProcessNameMatch) {
        $p = Get-Process | Where-Object { $_.ProcessName -like $ProcessNameMatch } |
             Sort-Object StartTime -Descending | Select-Object -First 1
        return $p
    }
    if ($ProcessId) { return (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue) }
    return $null
}

function Get-GpuUsedMiB {
    try {
        $v = & nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>$null
        return [int]($v | Select-Object -First 1)
    } catch { return 0 }
}

function Get-GpuTotalMiB {
    try {
        $v = & nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>$null
        return [int]($v | Select-Object -First 1)
    } catch { return 0 }
}

$total = Get-GpuTotalMiB
$samples = New-Object System.Collections.Generic.List[object]
$stop = (Get-Date).AddSeconds($DurationSec)

while ((Get-Date) -lt $stop) {
    $gpu = Get-GpuUsedMiB
    $ws = 0; $priv = 0; $pidNow = 0
    $p = Resolve-Target
    if ($p) {
        $pidNow = $p.Id
        $ws = $p.WorkingSet64
        $priv = $p.PrivateMemorySize64
    }

    $samples.Add([pscustomobject]@{
        t           = (Get-Date).ToString('HH:mm:ss')
        pid         = $pidNow
        gpuMiB      = $gpu
        gpuFreeMiB  = $total - $gpu
        wsGB        = [math]::Round($ws / 1GB, 2)
        privateGB   = [math]::Round($priv / 1GB, 2)
    })
    Start-Sleep -Milliseconds $IntervalMs
}

$gpuVals = @($samples | ForEach-Object { $_.gpuMiB })
$wsVals  = @($samples | ForEach-Object { $_.wsGB })
$pvVals  = @($samples | ForEach-Object { $_.privateGB })

$report = [pscustomobject]@{
    processId        = $ProcessId
    samples          = $samples.Count
    durationSec      = $DurationSec
    gpuTotalMiB      = $total
    gpuPeakMiB       = ($gpuVals | Measure-Object -Maximum).Maximum
    gpuMinMiB        = ($gpuVals | Measure-Object -Minimum).Minimum
    gpuAvgMiB        = [math]::Round(($gpuVals | Measure-Object -Average).Average)
    gpuPeakFreeMiB   = $total - ($gpuVals | Measure-Object -Maximum).Maximum
    ramWorkingSetMaxGB  = ($wsVals | Measure-Object -Maximum).Maximum
    ramPrivateMaxGB     = ($pvVals | Measure-Object -Maximum).Maximum
    ramWorkingSetAvgGB  = [math]::Round(($wsVals | Measure-Object -Average).Average)
    timeline         = $samples
}

Write-Host ''
Write-Host '=== resource measurement ===' -ForegroundColor Cyan
Write-Host ("GPU total        : {0} MiB ({1} GB)" -f $report.gpuTotalMiB, [math]::Round($report.gpuTotalMiB/1024,1))
Write-Host ("GPU peak used    : {0} MiB ({1} GB)" -f $report.gpuPeakMiB, [math]::Round($report.gpuPeakMiB/1024,1)) -ForegroundColor Yellow
Write-Host ("GPU peak free    : {0} MiB ({1} GB)" -f $report.gpuPeakFreeMiB, [math]::Round($report.gpuPeakFreeMiB/1024,1)) -ForegroundColor Yellow
Write-Host ("GPU min used     : {0} MiB" -f $report.gpuMinMiB)
Write-Host ("GPU avg used     : {0} MiB" -f $report.gpuAvgMiB)
Write-Host ("RAM peak WS      : {0} GB" -f $report.ramWorkingSetMaxGB) -ForegroundColor Yellow
Write-Host ("RAM peak private : {0} GB" -f $report.ramPrivateMaxGB) -ForegroundColor Yellow
Write-Host ("RAM avg WS       : {0} GB" -f $report.ramWorkingSetAvgGB)

if ($Out) {
    $dir = Split-Path -Parent $Out
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $report | ConvertTo-Json -Depth 5 | Set-Content -Path $Out -Encoding utf8
    Write-Host "report: $Out"
}
