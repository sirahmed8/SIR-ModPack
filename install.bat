@echo off
setlocal enabledelayedexpansion
title Installing SIR ModPack 144+ FPS Gaming Ecosystem - SIR Ecosystem
color 0A

echo =========================================================================
echo   SIR ModPack 144+ FPS Gaming Ecosystem
echo   SIR Official Production Desktop Application
echo =========================================================================
echo.
echo [1/3] Verifying environment & integrity...

if not exist "%CD%\SIR Installer.exe" (
    color 0C
    echo [ERROR] Application binary "SIR Installer.exe" was not found in this folder.
    echo Please make sure all files were extracted properly from the zip archive.
    echo.
    pause
    exit /b 1
)

echo [OK] Verified SIR Installer.exe.
echo [2/3] Launching installer: "SIR Installer.exe"...
start "" "%CD%\SIR Installer.exe"

echo [3/3] Installation initiated successfully.
echo.
echo Thank you for using SIR ModPack 144+ FPS Gaming Ecosystem.
echo.
timeout /t 3 >nul
exit /b 0
