@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0SIR Installer.exe" (
    start "" "%~dp0SIR Installer.exe"
    exit /b
)
if exist "%~dp0SIR Package\SIR Installer.exe" (
    start "" "%~dp0SIR Package\SIR Installer.exe"
    exit /b
)
python "%~dp0install.py" %*
pause
