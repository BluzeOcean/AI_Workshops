@echo off
REM ---------------------------------------------------------------------------
REM comfy-boot.cmd - start ComfyUI as a DETACHED, HEADLESS background process.
REM
REM Pattern proven on this machine (same shape as
REM D:\ComfyUI\comfyui-mcp-server\run-server-detached.cmd):
REM
REM     start "" /B <exe> <args> > log 2>&1
REM
REM   /B        => no new console window; nothing pops up on the user's desktop
REM   redirect  => the child never writes to the parent's console
REM   detached  => the process outlives the shell that launched it
REM
REM NEVER use "start" WITHOUT /B here: that opens a visible console window,
REM which is exactly the "a terminal keeps opening" failure recorded in
REM D:\ComfyUI\.claude\mistakes\harness-launch-comfyui-outside-sandbox.md
REM
REM DESTINATION IS A SERVER-LEVEL SETTING.
REM ComfyUI's folder_paths.get_save_image_path() refuses to write outside
REM --output-directory ("Saving image outside the output folder is not
REM allowed"), so the folder a task's assets land in is fixed here, at boot.
REM That is why the caller must know the destination BEFORE launching.
REM
REM Overridable via environment variables (see boot-comfyui.ps1).
REM ---------------------------------------------------------------------------
setlocal

if "%COMFY_ROOT%"=="" set "COMFY_ROOT=D:\ComfyUI"
if "%COMFY_PORT%"=="" set "COMFY_PORT=8188"
if "%COMFY_OUT%"==""  set "COMFY_OUT=V:\05_Media\Comfy_output"
if "%COMFY_IN%"==""   set "COMFY_IN=%COMFY_ROOT%\ComfyUI\input"
if "%COMFY_LOG%"==""  set "COMFY_LOG=%COMFY_ROOT%\harness\comfyui-headless.log"

cd /D "%COMFY_ROOT%"

start "" /B "%COMFY_ROOT%\python_embeded\python.exe" -I -W ignore::FutureWarning ComfyUI\main.py ^
  --windows-standalone-build ^
  --disable-auto-launch ^
  --listen 127.0.0.1 ^
  --port %COMFY_PORT% ^
  --vram-headroom 3 ^
  --input-directory "%COMFY_IN%" ^
  --output-directory "%COMFY_OUT%" ^
  > "%COMFY_LOG%" 2>&1

echo [comfy-boot] launch requested (out=%COMFY_OUT%) log: %COMFY_LOG%
endlocal
