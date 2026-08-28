"""
SIR LAUNCHER STUDIO — MODULAR DESKTOP ENGINE v1.0.0
Professional Multi-Tier Architecture (Separation of Concerns)
Designed by SIR Ahmed & DeepMind Team
"""
import sys
import os

DEV_DIR = os.path.dirname(os.path.abspath(__file__))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
import subprocess
import json

# Import Modular Core Subsystems
from sir_core.config import APP_TITLE, APP_VERSION, THEMES, LANGS, SETTINGS_FILE, ACCOUNTS_FILE, INSTANCES_DIR
from sir_core.auth import load_accounts, save_accounts, add_offline_account, start_microsoft_login_flow, sync_profile_by_ign_or_email, sync_profile_by_code, start_loopback_sync_bridge
from sir_core.launcher import scan_instances, create_instance, locate_java_runtimes, get_recommended_java_path, launch_instance, build_aikar_flags
from sir_core.store import query_modrinth_mods, query_curseforge_mods, download_and_install_mod, MODRINTH_CATEGORIES
from sir_core.servers import fetch_remote_servers, query_minecraft_server_live_status
from sir_core.social import get_friends_list, get_chat_history
from sir_core.server_host import start_dedicated_server
from sir_core.updater import check_for_launcher_updates

# Import Modular Modals
from launcher_ui.modals.custom_ping_modal import open_custom_server_ping_modal
from launcher_ui.modals.web_sync_modal import open_sir_web_account_sync_modal
from launcher_ui.modals.game_settings_modal import open_game_settings_modal
from launcher_ui.modals.satellite_modal import open_satellite_modal
from launcher_ui.modals.profile_creator_modal import open_create_profile_choice_modal
from launcher_ui.components.mousewheel import attach_mousewheel

# Import Launcher Application Studio Engine
from launcher_source.SIR_Launcher_Studio import SIRLauncherApp

def main():
    app = SIRLauncherApp()
    app.mainloop()

if __name__ == "__main__":
    main()
