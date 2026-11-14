<#
.SYNOPSIS
    Boot ComfyUI headless for the ComfyUI_Workshop workspace, then report health.

.DESCRIPTION
    One command an agent runs to get a working ComfyUI control surface:

        pwsh -File tools\boot-comfyui.ps1 -OutputDir "V:\some\folder"

    Steps, in order:
      1. Probe http://127.0.0.1:8188/system_stats.
         - If it answers, ComfyUI is already up. NEVER kill or restart it -
           that is the user's server and the user's call.
      2. If it is down, launch it DETACHED via tools\comfy-boot.cmd
         (no console window, survives this script, logs to a file).
      3. Poll /system_stats until it answers (ComfyUI must load custom nodes
         first - on this machine that takes ~30-90 seconds).
      4. Ensure the MCP bridge is up on http://127.0.0.1:9000/mcp.
         The MCP server refuses to stay alive without ComfyUI, so it MUST
         come after step 3. A supervisor is usually already running and
         will bind the port by itself once ComfyUI is reachable.
      5. Print health from the zero-dependency CLI:
         node D:\ComfyUI\harness\comfyctl.mjs health

.PARAMETER OutputDir
    DESTINATION for generated files. This is a SERVER-level setting in
    ComfyUI: folder_paths.get_save_image_path() refuses to write outside
    --output-directory. So this must be decided BEFORE booting, and it
    cannot be changed without a restart. If you do not know it, ASK.

.PARAMETER InputDir
    Folder ComfyUI reads input images from (LoadImage). Defaults to the
    install's own input dir.

.PARAMETER Restart
    Stop the instance THIS WORKSPACE started (tracked in tools\.comfyui.pid)
    and start a new one. Only ever restarts our own instance - never a
    server the user started.

.EXAMPLE
    pwsh -File tools\boot-comfyui.ps1 -OutputDir "V:\04_Projects\EpicJam2026\MechConcept Art"
#>
[CmdletBinding()]
param(
    # DESTINATION for generated files. Ask the user if unknown.
    [string]$OutputDir = 'V:\05_Media\Comfy_output',

    # Folder ComfyUI reads input images from.
    [string]$InputDir = 'D:\ComfyUI\ComfyUI\input',

    # How long to wait for ComfyUI to finish loading and answer on its port.
    [int]$TimeoutSec = 420,

    # Restart the instance this workspace started (never the user's).
    [switch]$Restart,

    # Skip the MCP bridge step (ComfyUI REST only).
    [switch]$SkipMcp
)

$ErrorActionPreference = 'Stop'

$ComfyRoot = 'D:\ComfyUI'
$ComfyPort = 8188
$McpPort   = 9000
$ComfyUrl  = "http://127.0.0.1:$ComfyPort"
$McpUrl    = "http://127.0.0.1:$McpPort/mcp"
$ComfyCtl  = Join-Path $ComfyRoot 'harness\comfyctl.mjs'
$BootCmd   = Join-Path $PSScriptRoot 'comfy-boot.cmd'
$PidFile   = Join-Path $PSScriptRoot '.comfyui.pid'

function Test-Http {
    param([string]$Url, [int]$TimeoutSec = 3)
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec $TimeoutSec
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400)
    } catch {
        return $false
    }
}

function Get-McpHealth {
    <#
        Ask comfyctl, not the raw endpoint.

        GET http://127.0.0.1:9000/mcp HANGS OPEN ON PURPOSE - it is an SSE
        stream that never ends. Probing it with a plain GET therefore always
        looks like "down" (the request never completes), which is a false
        negative: the bridge is up and healthy while the probe reports it dead.

        comfyctl does a real JSON-RPC initialize POST and parses the answer.
    #>
    if (-not (Test-Path $ComfyCtl)) { return $null }
    $raw = & node $ComfyCtl health 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { return $null }
    try { return (($raw -join "`n") | ConvertFrom-Json) } catch { return $null }
}

function Invoke-Detached {
    <#
        Run a .cmd in a hidden, windowless console so it can spawn a
        DETACHED long-lived child.

        NOTE: do NOT redirect stdout/stderr to a .NET pipe here. The pipe
        handle is inheritable, so the detached grandchild inherits it too and
        never closes its end - ReadToEnd() then blocks forever. The .cmd
        scripts redirect their own output to a log file instead.
    #>
    param([string]$File, [string[]]$Arguments = @())
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName         = $File
    $psi.Arguments        = ($Arguments -join ' ')
    $psi.WorkingDirectory = $PSScriptRoot
    $psi.UseShellExecute  = $false
    $psi.CreateNoWindow   = $true
    $psi.WindowStyle      = [System.Diagnostics.ProcessWindowStyle]::Hidden

    $p = [System.Diagnostics.Process]::Start($psi)
    if (-not $p.WaitForExit(20000)) {
        Write-Verbose 'launcher still running after 20s; the detached child continues'
    }
}

function Get-OurComfyPid {
    if (-not (Test-Path $PidFile)) { return $null }
    $pidText = (Get-Content $PidFile -Raw -ErrorAction SilentlyContinue).Trim()
    if (-not $pidText) { return $null }
    $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $pidText" -ErrorAction SilentlyContinue
    # Only trust it if it is still a ComfyUI main.py process.
    if ($proc -and $proc.CommandLine -like '*main.py*') { return [int]$pidText }
    return $null
}

function Save-OurComfyPid {
    $proc = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -like '*main.py*' -and $_.CommandLine -like "*--port $ComfyPort*" } |
            Sort-Object CreationDate -Descending |
            Select-Object -First 1
    if ($proc) { Set-Content -Path $PidFile -Value $proc.ProcessId -Encoding ascii; return $proc.ProcessId }
    return $null
}

Write-Host '=== ComfyUI_Workshop :: ComfyUI headless boot ===' -ForegroundColor Cyan
Write-Host "    destination : $OutputDir" -ForegroundColor DarkGray
Write-Host "    input dir   : $InputDir"    -ForegroundColor DarkGray

# --- 0. Optional restart of OUR instance -------------------------------------
if ($Restart) {
    $ours = Get-OurComfyPid
    if ($ours) {
        Write-Host "[0/4] Stopping our ComfyUI instance (pid $ours)..." -ForegroundColor Yellow
        Stop-Process -Id $ours -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
    else {
        Write-Host '[0/4] No instance started by this workspace - not restarting anything.' -ForegroundColor DarkGray
    }
}

# --- 1. Is ComfyUI already running? -----------------------------------------
if (Test-Http -Url "$ComfyUrl/system_stats") {
    Write-Host "[1/4] ComfyUI already running on $ComfyPort - leaving it alone." -ForegroundColor Green
    $existing = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
                Where-Object { $_.CommandLine -like '*main.py*' } | Select-Object -First 1
    if ($existing) {
        Write-Host "      running pid $($existing.ProcessId)" -ForegroundColor DarkGray
        $cmdline = $existing.CommandLine
        # Use .Contains(), not -like: -like is a WILDCARD match, and the path
        # contains backslashes that [regex]::Escape would double. That mismatch
        # produced a false "wrong destination" warning on a server that was
        # started with exactly the right destination.
        $hasOut = $cmdline.Contains('--output-directory')
        $outDir = if ($cmdline -match '--output-directory\s+"([^"]+)"') { $Matches[1] } else { '' }
        if (-not $hasOut -or $outDir.TrimEnd('\') -ne $OutputDir.TrimEnd('\')) {
            Write-Warning "The running instance was NOT started with this destination."
            Write-Warning "  wanted : $OutputDir"
            Write-Warning "  actual : $(if($outDir){$outDir}else{'<no --output-directory>'})"
            Write-Warning "Assets will NOT land where you asked. Restart it with -Restart."
        }
        else {
            Write-Host "      destination matches: $outDir" -ForegroundColor DarkGray
        }
    }
}
else {
    Write-Host "[1/4] ComfyUI is DOWN on $ComfyPort - starting it detached." -ForegroundColor Yellow

    if (-not (Test-Path $BootCmd)) { throw "missing launcher: $BootCmd" }

    $env:COMFY_ROOT = $ComfyRoot
    $env:COMFY_PORT = "$ComfyPort"
    $env:COMFY_OUT  = $OutputDir
    $env:COMFY_IN   = $InputDir

    Invoke-Detached -File 'cmd.exe' -Arguments @('/c', "`"$BootCmd`"")

    # --- 2/3. Wait for it to finish loading nodes and answer ---------------
    Write-Host "[2/4] Waiting up to $TimeoutSec s for ComfyUI to answer..." -ForegroundColor Yellow
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    $up = $false
    while ((Get-Date) -lt $deadline) {
        if (Test-Http -Url "$ComfyUrl/system_stats") { $up = $true; break }
        Start-Sleep -Seconds 3
    }
    if (-not $up) {
        Write-Warning "ComfyUI did not answer within $TimeoutSec s."
        Write-Warning "Log: $ComfyRoot\harness\comfyui-headless.log"
        Write-Warning 'A stalled custom node is the usual cause - check the log tail before retrying.'
        exit 1
    }
    Write-Host '[3/4] ComfyUI is up.' -ForegroundColor Green
    $newPid = Save-OurComfyPid
    if ($newPid) { Write-Host "      pid $newPid (tracked in $PidFile)" -ForegroundColor DarkGray }
}

# --- 4. MCP bridge -----------------------------------------------------------
if ($SkipMcp) {
    Write-Host '[4/4] Skipped MCP bridge (-SkipMcp).' -ForegroundColor DarkGray
}
else {
    $health = Get-McpHealth
    if ($health -and $health.mcp.up) {
        Write-Host "[4/4] MCP bridge already up on $McpPort ($($health.mcp.tools) tools)." -ForegroundColor Green
    }
    else {
        Write-Host "[4/4] MCP bridge down - launching supervisor." -ForegroundColor Yellow
        $mcpLauncher = Join-Path $ComfyRoot 'comfyui-mcp-server\run-server-detached.cmd'
        if (Test-Path $mcpLauncher) {
            Invoke-Detached -File 'cmd.exe' -Arguments @('/c', "`"$mcpLauncher`"")
        }
        else {
            Write-Warning "MCP launcher not found at $mcpLauncher"
        }

        $deadline = (Get-Date).AddSeconds(120)
        $mcpUp = $false
        while ((Get-Date) -lt $deadline) {
            $h = Get-McpHealth
            if ($h -and $h.mcp.up) { $mcpUp = $true; break }
            Start-Sleep -Seconds 3
        }
        if ($mcpUp) { Write-Host "      MCP bridge up on $McpPort." -ForegroundColor Green }
        else        { Write-Warning "MCP bridge did not answer within 120 s - see server.log" }
    }
}

# --- 5. Health via comfyctl --------------------------------------------------
if (Test-Path $ComfyCtl) {
    Write-Host ''
    Write-Host '--- comfyctl health ---' -ForegroundColor Cyan
    & node $ComfyCtl health
}
else {
    Write-Warning "comfyctl.mjs not found at $ComfyCtl"
}
