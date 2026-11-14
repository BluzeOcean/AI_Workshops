<#
.SYNOPSIS
    Stop the headless ComfyUI stack this workspace owns, and free the RAM/VRAM.

.DESCRIPTION
    Closes, in this order:

      1. The MCP supervisor and its server child, so port 9000 is released and
         the supervisor does not respawn the child.
      2. The ComfyUI server (port 8188), so its VRAM and its ~22 GB of staged
         weights are released.

    Then it reports the RAM/VRAM that came back.

    SCOPE - this only ever stops what THIS WORKSPACE started:
      - ComfyUI is tracked by pid in tools\.comfyui.pid (written by
        boot-comfyui.ps1) and by the '--port 8188' main.py command line.
      - The MCP supervisor is tracked in
        D:\ComfyUI\comfyui-mcp-server\supervisor.pid and claims a singleton.

    A ComfyUI the user started themselves (ComfyUI-EZi) is NOT touched: it is
    not in our pid file and it does not carry our --port/--output-directory
    flags. If the only ComfyUI running is the user's, this script says so and
    stops the MCP bridge only.

.EXAMPLE
    pwsh -File tools\stop-comfyui.ps1
#>
[CmdletBinding()]
param(
    # Do not stop anything; just report what is running and what it holds.
    [switch]$ReportOnly
)

$ErrorActionPreference = 'Stop'

$ComfyRoot = 'D:\ComfyUI'
$ComfyPort = 8188
$McpPort   = 9000
$Workspace = Split-Path -Parent $PSScriptRoot
$PidFile   = Join-Path $PSScriptRoot '.comfyui.pid'
$SupervisorPidFile = Join-Path $ComfyRoot 'comfyui-mcp-server\supervisor.pid'

function Get-GpuUsedMiB {
    try { return [int](& nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | Select-Object -First 1) }
    catch { return 0 }
}

function Get-ComfyProc {
    $c = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
         Where-Object { $_.CommandLine -like '*main.py*' } | Select-Object -First 1
    if (-not $c) { return $null }
    $p = Get-Process -Id $c.ProcessId -ErrorAction SilentlyContinue
    if (-not $p) { return $null }
    return [pscustomobject]@{
        pid        = $c.ProcessId
        command    = $c.CommandLine
        ours       = ($c.CommandLine -like "*--port $ComfyPort*") -and
                     (Test-Path $PidFile) -and
                     ((Get-Content $PidFile -Raw -ErrorAction SilentlyContinue).Trim() -eq "$($c.ProcessId)")
        wsGB       = [math]::Round($p.WorkingSet64 / 1GB, 2)
        privateGB  = [math]::Round($p.PrivateMemorySize64 / 1GB, 2)
    }
}

function Get-McpPids {
    $ids = @()
    if (Test-Path $SupervisorPidFile) {
        $t = (Get-Content $SupervisorPidFile -Raw -ErrorAction SilentlyContinue).Trim()
        if ($t -match '^\d+$') { $ids += [int]$t }
    }
    # the server child as well
    Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like '*comfyui-mcp-server*' } |
        ForEach-Object { $ids += $_.ProcessId }
    return @($ids | Sort-Object -Unique)
}

Write-Host '=== ComfyUI_Workshop :: stopping the headless stack ===' -ForegroundColor Cyan

$gpuBefore = Get-GpuUsedMiB
$comfy = Get-ComfyProc
$mcpPids = Get-McpPids

Write-Host ("before : GPU {0} MiB used | ComfyUI {1}" -f $gpuBefore, `
    $(if ($comfy) { "pid $($comfy.pid), RAM private $($comfy.privateGB) GB" } else { 'not running' }))
Write-Host ("         MCP processes: {0}" -f $(if ($mcpPids.Count) { $mcpPids -join ', ' } else { 'none' }))

if ($ReportOnly) {
    Write-Host '-ReportOnly: nothing was stopped.' -ForegroundColor DarkGray
    return
}

# --- 1. MCP supervisor + child ----------------------------------------------
# The supervisor RESPAWNS its child, so it must go first.
foreach ($id in $mcpPids) {
    try {
        Stop-Process -Id $id -Force -ErrorAction Stop
        Write-Host "  stopped MCP pid $id" -ForegroundColor Green
    } catch {
        Write-Verbose "MCP pid $id already gone"
    }
}
Start-Sleep -Seconds 2

# --- 2. ComfyUI --------------------------------------------------------------
if ($comfy) {
    if ($comfy.ours) {
        Stop-Process -Id $comfy.pid -Force -ErrorAction SilentlyContinue
        Write-Host "  stopped ComfyUI pid $($comfy.pid) (started by this workspace)" -ForegroundColor Green
    }
    else {
        Write-Warning "ComfyUI pid $($comfy.pid) was NOT started by this workspace - leaving it running."
        Write-Warning "  $($comfy.command)"
    }
}
else {
    Write-Host '  ComfyUI was not running.' -ForegroundColor DarkGray
}

# --- 3. Clean the pid files so the next boot starts clean --------------------
if (Test-Path $PidFile) { rm -- $PidFile 2>$null }
if (Test-Path $SupervisorPidFile) {
    $t = (Get-Content $SupervisorPidFile -Raw -ErrorAction SilentlyContinue).Trim()
    if ($t -match '^\d+$') {
        $alive = Get-Process -Id ([int]$t) -ErrorAction SilentlyContinue
        if (-not $alive) { rm -- $SupervisorPidFile 2>$null }
    }
}

# --- 4. Give the OS a moment to reclaim -------------------------------------
Start-Sleep -Seconds 6

$gpuAfter = Get-GpuUsedMiB
$still = Get-ComfyProc
$port8188 = (Get-NetTCPConnection -LocalPort $ComfyPort -State Listen -ErrorAction SilentlyContinue | Measure-Object).Count
$port9000 = (Get-NetTCPConnection -LocalPort $McpPort  -State Listen -ErrorAction SilentlyContinue | Measure-Object).Count

Write-Host ''
Write-Host '=== after ===' -ForegroundColor Cyan
Write-Host ("GPU used : {0} MiB (was {1}) - released {2} MiB ({3} GB)" -f $gpuAfter, $gpuBefore, ($gpuBefore - $gpuAfter), [math]::Round(($gpuBefore - $gpuAfter)/1024,1)) -ForegroundColor Yellow
if ($still) {
    Write-Host ("RAM still held by ComfyUI pid {0}: private {1} GB" -f $still.pid, $still.privateGB) -ForegroundColor Yellow
}
else {
    Write-Host 'ComfyUI : stopped, its RAM is released.' -ForegroundColor Green
}
Write-Host ("port {0} listeners: {1}   port {2} listeners: {3}" -f $ComfyPort, $port8188, $McpPort, $port9000) -ForegroundColor Green
if ($port8188 -eq 0 -and $port9000 -eq 0) {
    Write-Host 'Stack is fully closed.' -ForegroundColor Green
}
else {
    Write-Warning 'Something is still listening - check the ports above.'
}
