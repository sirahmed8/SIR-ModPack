import os
import sys

APP_TITLE = "SIR Launcher — The Ultimate Minecraft Experience"
APP_VERSION = "1.0.0"
MSA_CLIENT_ID = "c36a9fb6-4f2a-41ff-90bd-ae7cc92031eb"
FIREBASE_RTDB_BASE = "https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app"

# Base Paths
SOURCE_ROOT = r"D:\Projects\SIR ModPack"
LAUNCHER_DIR = os.path.join(SOURCE_ROOT, "SIR Launcher")
INSTANCES_DIR = os.path.join(LAUNCHER_DIR, "instances")
SETTINGS_FILE = os.path.join(LAUNCHER_DIR, "settings.json")
ACCOUNTS_FILE = os.path.join(LAUNCHER_DIR, "accounts.json")
CACHE_DIR = os.path.join(LAUNCHER_DIR, "cache")
SERVER_HOST_EXE = os.path.join(SOURCE_ROOT, "SIR Package", "SIR Server Host.exe")

os.makedirs(INSTANCES_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

THEMES = {
    "dark": {
        "bg": "#0a0d14",
        "sidebar_bg": "#0c0e16",
        "sidebar_btn": "#141926",
        "sidebar_btn_hover": "#1c2336",
        "sidebar_active": "#00e5ff",
        "header_bg": "#0d101a",
        "card_bg": "#121622",
        "card_border": "#1c2336",
        "card_hover": "#181f30",
        "card_selected": "#14253d",
        "accent_cyan": "#00e5ff",
        "accent_green": "#10b981",
        "accent_green_hover": "#059669",
        "accent_gold": "#fbbf24",
        "accent_red": "#ff3b5c",
        "accent_purple": "#a855f7",
        "accent_indigo": "#6366f1",
        "text_primary": "#ffffff",
        "text_secondary": "#cbd5e1",
        "text_muted": "#818cf8",
        "btn_bg": "#182030",
        "btn_hover": "#222d42",
        "entry_bg": "#0e131f",
        "modal_bg": "#0c0f17",
        "ribbon_bg": "#1e1b4b"
    },
    "light": {
        "bg": "#f8fafc",
        "sidebar_bg": "#f1f5f9",
        "sidebar_btn": "#e2e8f0",
        "sidebar_btn_hover": "#cbd5e1",
        "sidebar_active": "#0284c7",
        "header_bg": "#ffffff",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "card_hover": "#f1f5f9",
        "card_selected": "#e0f2fe",
        "accent_cyan": "#0284c7",
        "accent_green": "#10b981",
        "accent_green_hover": "#059669",
        "accent_gold": "#d97706",
        "accent_red": "#dc2626",
        "accent_purple": "#7c3aed",
        "accent_indigo": "#4f46e5",
        "text_primary": "#0f172a",
        "text_secondary": "#475569",
        "text_muted": "#6366f1",
        "btn_bg": "#e2e8f0",
        "btn_hover": "#cbd5e1",
        "entry_bg": "#f8fafc",
        "modal_bg": "#ffffff",
        "ribbon_bg": "#e0e7ff"
    }
}

LANGS = {
    "en": {
        "play": "LAUNCH GAME",
        "settings": "Settings",
        "accounts": "Accounts",
        "online_status": "ONLINE (SYNC ACTIVE)"
    },
    "ar": {
        "play": "تشغيل اللعبة",
        "settings": "الإعدادات",
        "accounts": "الحسابات",
        "online_status": "متصل (المزامنة نشطة)"
    }
}
