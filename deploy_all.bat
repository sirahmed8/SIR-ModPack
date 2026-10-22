@echo off
setlocal EnableDelayedExpansion

REM ===========================================================================
REM SIR Ecosystem - Master 1-Click Unified Production Deployment Engine
REM Release:  v1.0.0 Production Release
REM Platform: 100%% Free and Independent Platform
REM Contact:  a7medorabe7@gmail.com
REM ===========================================================================

title SIR Ecosystem - Master All-In-One Deployment Pipeline (v1.0.0)
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
echo %C_BOLD%%C_WHITE%  SIR ECOSYSTEM - MASTER ALL-IN-ONE PRODUCTION DEPLOYMENT PIPELINE%C_RESET%
echo %C_CYAN%  v1.0.0 Production Release - 24 Instances, Binaries, OTA and Web%C_RESET%
echo %C_CYAN%===============================================================================%C_RESET%
echo.

REM ---------------------------------------------------------------------------
REM [STAGE 1/4] Checking System and Privilege Level
REM ---------------------------------------------------------------------------
echo %C_BLUE%[STAGE 1/4]%C_RESET% %C_BOLD%Checking Administrator Privileges...%C_RESET%
net session >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   %C_GREEN%[OK]%C_RESET% Running with Administrator Privileges.
) else (
    echo   %C_GREEN%[OK]%C_RESET% Running in Standard Developer Mode.
)

REM ---------------------------------------------------------------------------
REM [STAGE 2/4] Runtime Detection
REM ---------------------------------------------------------------------------
echo.
echo %C_BLUE%[STAGE 2/4]%C_RESET% %C_BOLD%Detecting Python Environment...%C_RESET%

set "PYTHON_CMD="
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
    goto :EXEC_DEPLOY
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py -3"
    goto :EXEC_DEPLOY
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :EXEC_DEPLOY
)

echo.
echo %C_RED%[ERROR] Python 3 was not found on system PATH!%C_RESET%
echo   Please install Python 3.10+ from https://www.python.org/
echo.
exit /b 1

REM ---------------------------------------------------------------------------
REM [STAGE 3/4] & [STAGE 4/4] Executing Master Pipeline
REM ---------------------------------------------------------------------------
:EXEC_DEPLOY
echo   %C_GREEN%[OK]%C_RESET% Active Python Engine: %C_WHITE%%PYTHON_CMD%%C_RESET%
echo.
echo %C_BLUE%[STAGE 3/4]%C_RESET% %C_BOLD%Executing Unified Ecosystem Deployment Engine: deploy_all.py...%C_RESET%
echo.

%PYTHON_CMD% "%~dp0deploy_all.py" %*
set "DEPLOY_EXIT=%ERRORLEVEL%"

echo.
echo %C_BLUE%[STAGE 4/4]%C_RESET% %C_BOLD%Pipeline Execution Results...%C_RESET%
if %DEPLOY_EXIT% EQU 0 (
    echo %C_GREEN%===============================================================================%C_RESET%
    echo %C_GREEN%  MASTER DEPLOYMENT PIPELINE COMPLETED SUCCESSFULLY [EXIT CODE 0]%C_RESET%
    echo %C_GREEN%===============================================================================%C_RESET%
) else (
    echo %C_RED%===============================================================================%C_RESET%
    echo %C_RED%  MASTER DEPLOYMENT FAILED WITH EXIT CODE %DEPLOY_EXIT%%C_RESET%
    echo %C_RED%===============================================================================%C_RESET%
)
exit /b %DEPLOY_EXIT%
