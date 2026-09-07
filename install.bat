@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0SIR ModPack.exe" (
    start "" "%~dp0SIR ModPack.exe" --mode installer %*
    exit /b
)
if exist "%~dp0dist_build\SIR ModPack.exe" (
    start "" "%~dp0dist_build\SIR ModPack.exe" --mode installer %*
    exit /b
)
echo SIR ModPack.exe was not found. Build it with build_dispatcher.py first.
exit /b 2
