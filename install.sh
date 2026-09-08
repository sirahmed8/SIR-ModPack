#!/usr/bin/env bash
# =============================================================================
# 🌟 SIR ModPack — Master CLI Installer & Portable Deployer (POSIX / Linux / macOS)
# Release:  v1.0.0 Genesis Production Release
# Platform: 100% Free & Independent Platform (Free Independent Software Agreement)
# Contact:  a7medorabe7@gmail.com
# =============================================================================

set -e

C_RESET="\033[0m"
C_BOLD="\033[1m"
C_CYAN="\033[1;36m"
C_GREEN="\033[1;32m"
C_YELLOW="\033[1;33m"
C_BLUE="\033[1;34m"
C_RED="\033[1;31m"
C_WHITE="\033[1;37m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "\n${C_CYAN}===============================================================================${C_RESET}"
echo -e "${C_BOLD}${C_WHITE}  🌟 SIR MODPACK — MASTER UNIFIED POSIX INSTALLER & DEPLOYER PIPELINE${C_RESET}"
echo -e "${C_CYAN}  v1.0.0 Genesis Production Release • Free & Independent Ecosystem${C_RESET}"
echo -e "${C_CYAN}===============================================================================${C_RESET}\n"

# -----------------------------------------------------------------------------
# [STAGE 1/4] Checking System & Permissions
# -----------------------------------------------------------------------------
echo -e "${C_BLUE}[STAGE 1/4]${C_RESET} ${C_BOLD}Checking Operating System & User Privileges...${C_RESET}"
OS="$(uname -s)"
ARCH="$(uname -m)"
echo -e "  ${C_GREEN}[OK]${C_RESET} Detected OS: ${C_WHITE}${OS} (${ARCH})${C_RESET}"
if [ "$EUID" -eq 0 ]; then
    echo -e "  ${C_YELLOW}[NOTICE]${C_RESET} Running as root/superuser."
else
    echo -e "  ${C_GREEN}[OK]${C_RESET} Running as regular user (${USER})."
fi

# -----------------------------------------------------------------------------
# [STAGE 2/4] Runtime Detection (Python 3.x)
# -----------------------------------------------------------------------------
echo -e "\n${C_BLUE}[STAGE 2/4]${C_RESET} ${C_BOLD}Detecting Python 3 Environment...${C_RESET}"
PYTHON_BIN=""

if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo -e "  ${C_RED}[ERROR] Python 3 is not installed or not in PATH!${C_RESET}"
    echo -e "  Please install Python 3 via your package manager:"
    echo -e "    - Ubuntu/Debian:  sudo apt-get install python3"
    echo -e "    - Arch Linux:     sudo pacman -S python"
    echo -e "    - Fedora:         sudo dnf install python3"
    echo -e "    - macOS (Brew):   brew install python3"
    exit 1
fi

PY_VER=$($PYTHON_BIN --version 2>&1)
echo -e "  ${C_GREEN}[OK]${C_RESET} Active Python Engine: ${C_WHITE}${PY_VER}${C_RESET} (${PYTHON_BIN})"

# -----------------------------------------------------------------------------
# [STAGE 3/4] & [STAGE 4/4] Executing Installer Engine
# -----------------------------------------------------------------------------
echo -e "\n${C_BLUE}[STAGE 3/4]${C_RESET} ${C_BOLD}Executing Master Installer Engine (install.py)...${C_RESET}\n"

set +e
"$PYTHON_BIN" "$SCRIPT_DIR/install.py" "$@"
EXIT_CODE=$?
set -e

echo -e "\n${C_BLUE}[STAGE 4/4]${C_RESET} ${C_BOLD}Finalizing and Verifying Deployment...${C_RESET}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${C_GREEN}===============================================================================${C_RESET}"
    echo -e "${C_GREEN}  🎉 POSIX INSTALLATION COMPLETED SUCCESSFULLY [EXIT CODE 0]${C_RESET}"
    echo -e "${C_GREEN}===============================================================================${C_RESET}"
else
    echo -e "${C_RED}===============================================================================${C_RESET}"
    echo -e "${C_RED}  ❌ INSTALLATION COMPLETED WITH EXIT CODE ${EXIT_CODE}${C_RESET}"
    echo -e "${C_RED}===============================================================================${C_RESET}"
fi

exit $EXIT_CODE
