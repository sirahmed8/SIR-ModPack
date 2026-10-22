@echo off
setlocal EnableDelayedExpansion

REM ===========================================================================
REM SIR ModPack - Master All-In-One Unified Installer and Deployer
REM Release:  v1.0.0 Official Release
REM Platform: Independent Gaming Platform
REM Contact:  a7medorabe7@gmail.com
REM ===========================================================================

title SIR ModPack - Master CLI and Desktop Deployer (v1.0.0)
cd /d "%~dp0"

REM Setup ANSI Colors using prompt escape
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"
set "C_RESET=%ESC%[0m"
set "C_BOLD=%ESC%[1m"
set "C_CYAN=%ESC%[1;36m"
set "C_GREEN=%ESC%[1;32m"
set "C_YELLOW=%ESC%[1;33m"
set "C_BLUE=%ESC%[1;34m"
set "C_RED=%ESC%[1;31m"
set "C_WHITE=%ESC%[1;37m"

echo.
echo %C_CYAN%===============================================================================%C_RESET%
echo %C_BOLD%%C_WHITE%  SIR MODPACK - MASTER UNIFIED INSTALLER AND DEPLOYER PIPELINE%C_RESET%
echo %C_CYAN%  v1.0.0 Official Release - Independent Ecosystem%C_RESET%
echo %C_CYAN%===============================================================================%C_RESET%
echo.

REM ---------------------------------------------------------------------------
REM [STAGE 1/4] Checking System and Privilege Level
REM ---------------------------------------------------------------------------
echo %C_BLUE%[STAGE 1/4]%C_RESET% %C_BOLD%Checking System Environment and Privilege Level...%C_RESET%
net session >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   %C_GREEN%[OK]%C_RESET% Running with Administrator Privileges.
) else (
    echo   %C_GREEN%[OK]%C_RESET% Running in User Mode: Standard APPDATA and Profile Deployment.
)

REM ---------------------------------------------------------------------------
REM [STAGE 2/4] Runtime Detection
REM ---------------------------------------------------------------------------
echo.
echo %C_BLUE%[STAGE 2/4]%C_RESET% %C_BOLD%Detecting Available Execution Runtimes...%C_RESET%

set "PYTHON_CMD="
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
    goto :EXEC_PYTHON
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py -3"
    goto :EXEC_PYTHON
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :EXEC_PYTHON
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :EXEC_PYTHON
)

REM Fallback to standalone desktop binaries if Python is missing
echo   %C_YELLOW%[NOTICE]%C_RESET% Python runtime not found on PATH. Checking Standalone Binaries...

if exist "%~dp0SIR Installer.exe" (
    echo   %C_GREEN%[FOUND]%C_RESET% Found standalone: SIR Installer.exe
    goto :EXEC_STANDALONE_INSTALLER
)

if exist "%~dp0SIR ModPack.exe" (
    echo   %C_GREEN%[FOUND]%C_RESET% Found standalone dispatcher: SIR ModPack.exe
    goto :EXEC_STANDALONE_DISPATCHER
)

if exist "%~dp0dist_build\SIR Installer.exe" (
    echo   %C_GREEN%[FOUND]%C_RESET% Found pre-compiled: dist_build\SIR Installer.exe
    start "" "%~dp0dist_build\SIR Installer.exe" %*
    exit /b 0
)

echo.
echo %C_RED%[ERROR] Neither Python 3 nor Standalone SIR Executables were located!%C_RESET%
echo   Please install Python 3.10+ from https://www.python.org/
echo.
exit /b 1

REM ---------------------------------------------------------------------------
REM [STAGE 3/4] & [STAGE 4/4] Python Execution Pipeline
REM ---------------------------------------------------------------------------
:EXEC_PYTHON
echo   %C_GREEN%[OK]%C_RESET% Active Python Engine: %C_WHITE%%PYTHON_CMD%%C_RESET%
echo.
echo %C_BLUE%[STAGE 3/4]%C_RESET% %C_BOLD%Executing Master Installer Engine: install.py...%C_RESET%
echo.

%PYTHON_CMD% "%~dp0install.py" %*
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo %C_BLUE%[STAGE 4/4]%C_RESET% %C_BOLD%Finalizing and Verifying Deployment...%C_RESET%
if %EXIT_CODE% EQU 0 (
    echo %C_GREEN%===============================================================================%C_RESET%
    echo %C_GREEN%  INSTALLATION PIPELINE COMPLETED SUCCESSFULLY [EXIT CODE 0]%C_RESET%
    echo %C_GREEN%===============================================================================%C_RESET%
) else (
    echo %C_RED%===============================================================================%C_RESET%
    echo %C_RED%  INSTALLATION COMPLETED WITH EXIT CODE %EXIT_CODE%%C_RESET%
    echo %C_RED%===============================================================================%C_RESET%
)
exit /b %EXIT_CODE%

REM ---------------------------------------------------------------------------
REM Standalone Binary Handlers
REM ---------------------------------------------------------------------------
:EXEC_STANDALONE_INSTALLER
echo.
echo %C_BLUE%[STAGE 3/4]%C_RESET% %C_BOLD%Launching Standalone SIR Installer.exe...%C_RESET%
start "" "%~dp0SIR Installer.exe" %*
exit /b 0

:EXEC_STANDALONE_DISPATCHER
echo.
echo %C_BLUE%[STAGE 3/4]%C_RESET% %C_BOLD%Launching Standalone SIR ModPack.exe [--mode installer]...%C_RESET%
start "" "%~dp0SIR ModPack.exe" --mode installer %*
exit /b 0
