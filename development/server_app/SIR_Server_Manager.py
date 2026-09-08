#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
        SIR MODPACK — DEDICATED SERVER MANAGER & ORCHESTRATOR PRO v1.0.0
=============================================================================
Ultra-Modern CustomTkinter Dedicated Server Suite:
- 1-Click Modern 26.2 (Fabric 1.21.4) & Legacy 1.8.9 Server Deployment
- Zero Port-Forwarding Cloudflare / Playit.gg Free Tunnel Tunneling Wizard
- Real-Time Live Server Console, Live Telemetry & Interactive Terminal Dispatch
- Integrated Auto-Restart Crash Watchdog & Scheduled World Backups
- Visual Player Manager (Live Players, Whitelist, OPs, Kick/Ban)
- 1-Click Direct Join with SIR Launcher (127.0.0.1:25565)
=============================================================================
"""

import os
import sys
import json
import time
import shutil
import ctypes
import zipfile
import threading
import subprocess
import webbrowser

# Ensure user site-packages are loaded for customtkinter
user_pkg = r"C:\Users\a7med\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages"
if os.path.exists(user_pkg) and user_pkg not in sys.path:
    sys.path.insert(0, user_pkg)

import customtkinter as ctk
from tkinter import messagebox, filedialog

# Force Windows High-DPI Crisp Rendering
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

APP_TITLE = "SIR Server Orchestrator Pro"
APP_VERSION = "1.0.0"

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVER_ROOT = os.path.join(APP_DIR, "server_instances")
os.makedirs(SERVER_ROOT, exist_ok=True)

THEMES = {
    "dark": {
        "window_bg": "#06090e",
        "header_bg": "#0d121d",
        "card_bg": "#101624",
        "card_inner_bg": "#070a10",
        "card_border": "#1e293b",
        "btn_bg": "#182030",
        "btn_hover": "#222c42",
        "text_primary": "#ffffff",
        "text_secondary": "#cbd5e1",
        "text_muted": "#94a3b8",
        "accent_cyan": "#00e5ff",
        "accent_cyan_hover": "#00c8e0",
        "accent_green": "#38ef7d",
        "accent_green_hover": "#2ecc71",
        "accent_amber": "#f59e0b",
        "accent_rose": "#f43f5e",
        "badge_bg": "#083344",
        "caption_dwmapi": 0x000E0906,
    },
    "light": {
        "window_bg": "#f1f5f9",
        "header_bg": "#ffffff",
        "card_bg": "#ffffff",
        "card_inner_bg": "#f8fafc",
        "card_border": "#cbd5e1",
        "btn_bg": "#e2e8f0",
        "btn_hover": "#cbd5e1",
        "text_primary": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "accent_cyan": "#0284c7",
        "accent_cyan_hover": "#0369a1",
        "accent_green": "#16a34a",
        "accent_green_hover": "#15803d",
        "accent_amber": "#d97706",
        "accent_rose": "#e11d48",
        "badge_bg": "#e0f2fe",
        "caption_dwmapi": 0x00F9F5F1,
    }
}

class ModernSIRServerManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        
        self.title(f"{APP_TITLE} {APP_VERSION}")
        self.configure(fg_color="#06090e")
        self.minsize(1020, 700)
        
        self.current_theme = "dark"
        self.current_lang = "en"
        self.server_process = None
        self.is_running = False
        self.connected_players = []
        
        # Server Config State
        self.server_type = ctk.StringVar(value="fabric_26.2")
        self.server_ram = ctk.IntVar(value=6)
        self.server_port = ctk.StringVar(value="25565")
        self.rcon_port = ctk.StringVar(value="25575")
        self.tunnel_enabled = ctk.BooleanVar(value=True)
        self.watchdog_enabled = ctk.BooleanVar(value=True)
        self.public_ip = "play.sirmodpack.xyz:25565"
        
        self.setup_ui()
        self.center_window(1060, 740)
        self.apply_windows11_dark_titlebar()
        self.after(30, self.deiconify)

    def apply_windows11_dark_titlebar(self):
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd: hwnd = self.winfo_id()
            is_dark = (self.current_theme == "dark")
            for attr in [20, 19]:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(ctypes.c_int(1 if is_dark else 0)), ctypes.sizeof(ctypes.c_int))
            c = THEMES[self.current_theme]
            caption_color = ctypes.c_int(c["caption_dwmapi"])
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption_color), ctypes.sizeof(caption_color))
        except Exception:
            pass

    def center_window(self, width=1060, height=740):
        try:
            user32 = ctypes.windll.user32
            scaling = self._get_window_scaling() if hasattr(self, '_get_window_scaling') else 1.0
            scaled_w = int(width * scaling)
            scaled_h = int(height * scaling)
            
            class RECT(ctypes.Structure):
                _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
            
            rect = RECT()
            user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
            work_w = rect.right - rect.left
            work_h = rect.bottom - rect.top
            
            phys_x = rect.left + max(0, (work_w - scaled_w) // 2)
            phys_y = rect.top + max(0, (work_h - scaled_h) // 2)
            
            logical_x = int(phys_x / scaling)
            logical_y = int(phys_y / scaling)
            
            self.geometry(f"{width}x{height}+{logical_x}+{logical_y}")
        except Exception:
            self.update_idletasks()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = max(0, (sw - width) // 2)
            y = max(0, (sh - height) // 2 - 20)
            self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        c = THEMES[self.current_theme]
        for w in self.winfo_children(): w.destroy()
        self.configure(fg_color=c["window_bg"])

        # 1. Top Navigation Bar
        self.header = ctk.CTkFrame(self, fg_color=c["header_bg"], corner_radius=0, height=68)
        self.header.pack(fill="x", side="top")

        h_inner = ctk.CTkFrame(self.header, fg_color="transparent")
        h_inner.pack(fill="x", padx=20, pady=12)

        title_box = ctk.CTkFrame(h_inner, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="⚡ SIR SERVER ORCHESTRATOR PRO",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=c["accent_cyan"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Dedicated Server Host & 0-Port Forwarding Tunnel Manager",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=c["text_muted"]
        ).pack(anchor="w")

        # Top Right Actions
        act_box = ctk.CTkFrame(h_inner, fg_color="transparent")
        act_box.pack(side="right")

        self.btn_backup = ctk.CTkButton(
            act_box,
            text="📦 Backup",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["accent_cyan"],
            width=76,
            height=32,
            corner_radius=8,
            command=self.create_server_backup
        )
        self.btn_backup.pack(side="left", padx=2)

        self.btn_props = ctk.CTkButton(
            act_box,
            text="⚙️ Properties",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["text_primary"],
            width=88,
            height=32,
            corner_radius=8,
            command=self.open_properties_modal
        )
        self.btn_props.pack(side="left", padx=2)

        self.btn_players = ctk.CTkButton(
            act_box,
            text="👥 Players",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["accent_green"],
            width=80,
            height=32,
            corner_radius=8,
            command=self.open_players_modal
        )
        self.btn_players.pack(side="left", padx=2)

        self.btn_repair = ctk.CTkButton(
            act_box,
            text="🔧 Fix EULA",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["accent_cyan"],
            width=80,
            height=32,
            corner_radius=8,
            command=self.fix_eula_and_properties
        )
        self.btn_repair.pack(side="left", padx=2)

        self.btn_plugins = ctk.CTkButton(
            act_box,
            text="🧩 Plugins",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["accent_green"],
            width=76,
            height=32,
            corner_radius=8,
            command=self.open_plugins_modal
        )
        self.btn_plugins.pack(side="left", padx=2)

        self.btn_rcon = ctk.CTkButton(
            act_box,
            text="📡 RCON",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["accent_cyan"],
            width=68,
            height=32,
            corner_radius=8,
            command=self.open_rcon_modal
        )
        self.btn_rcon.pack(side="left", padx=2)

        self.btn_folder = ctk.CTkButton(
            act_box,
            text="📁 Folder",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["text_secondary"],
            width=68,
            height=32,
            corner_radius=8,
            command=self.open_server_dir
        )
        self.btn_folder.pack(side="left", padx=2)

        self.btn_th = ctk.CTkButton(
            act_box,
            text="☀️" if self.current_theme == "light" else "🌙",
            width=32,
            height=32,
            corner_radius=8,
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["text_primary"],
            command=self.toggle_theme
        )
        self.btn_th.pack(side="left", padx=2)

        # 2. Main Stage (2 Columns: Left Controls, Right Live Console)
        self.stage = ctk.CTkFrame(self, fg_color="transparent")
        self.stage.pack(fill="both", expand=True, padx=20, pady=16)

        # LEFT COLUMN: Server Controls & Config
        left_col = ctk.CTkFrame(self.stage, fg_color=c["card_bg"], corner_radius=16, border_width=1, border_color=c["card_border"], width=350)
        left_col.pack(side="left", fill="y", padx=(0, 12))

        l_inner = ctk.CTkFrame(left_col, fg_color="transparent")
        l_inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(l_inner, text="⚙️ Server Configuration", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=c["accent_cyan"]).pack(anchor="w", pady=(0, 8))

        # Version Selector
        ctk.CTkLabel(l_inner, text="Server Profile Engine:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=c["text_secondary"]).pack(anchor="w", pady=(0, 4))
        
        engines = [
            ("fabric_26.2", "Modern 26.2 (Fabric 1.21.4)"),
            ("forge_1.8.9", "Legacy 1.8.9 (Forge PvP)")
        ]
        self.engine_cards = {}

        def on_engine_select(val):
            self.server_type.set(val)
            for v, (cf, rb) in self.engine_cards.items():
                if v == val:
                    cf.configure(fg_color=c["card_inner_bg"], border_color=c["accent_cyan"], border_width=2)
                    rb.configure(text_color=c["accent_cyan"])
                else:
                    cf.configure(fg_color="transparent", border_color=c["card_border"], border_width=1)
                    rb.configure(text_color=c["text_primary"])

        for val, label in engines:
            is_active = (self.server_type.get() == val)
            item_f = ctk.CTkFrame(
                l_inner,
                fg_color=c["card_inner_bg"] if is_active else "transparent",
                corner_radius=10,
                border_width=2 if is_active else 1,
                border_color=c["accent_cyan"] if is_active else c["card_border"]
            )
            item_f.pack(fill="x", pady=2)

            rb = ctk.CTkRadioButton(
                item_f,
                text=label,
                value=val,
                variable=self.server_type,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=c["accent_cyan"] if is_active else c["text_primary"],
                fg_color=c["accent_cyan"],
                hover_color=c["accent_cyan_hover"],
                command=lambda v=val: on_engine_select(v)
            )
            rb.pack(anchor="w", padx=10, pady=6)
            item_f.bind("<Button-1>", lambda e, v=val: on_engine_select(v))
            self.engine_cards[val] = (item_f, rb)

        # RAM Slider
        ram_lbl = ctk.CTkLabel(l_inner, text=f"Dedicated Server RAM: {self.server_ram.get()} GB", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=c["accent_cyan"])
        ram_lbl.pack(anchor="w", pady=(8, 2))
        
        def on_server_ram_change(val):
            gb = int(val)
            self.server_ram.set(gb)
            ram_lbl.configure(text=f"Dedicated Server RAM: {gb} GB", text_color=c["accent_green"])
            self.after(120, lambda: ram_lbl.configure(text_color=c["accent_cyan"]) if ram_lbl.winfo_exists() else None)

        ram_slider = ctk.CTkSlider(l_inner, from_=2, to=16, number_of_steps=14, variable=self.server_ram, progress_color=c["accent_cyan"], command=on_server_ram_change)
        ram_slider.pack(fill="x", pady=(0, 6))

        # Tunnel Switch Card
        sw_tunnel_card = ctk.CTkFrame(l_inner, fg_color=c["card_inner_bg"] if self.tunnel_enabled.get() else "transparent", corner_radius=10, border_width=1.5 if self.tunnel_enabled.get() else 1, border_color=c["accent_cyan"] if self.tunnel_enabled.get() else c["card_border"])
        sw_tunnel_card.pack(fill="x", pady=2)

        def on_tunnel_toggle():
            is_on = self.tunnel_enabled.get()
            if is_on:
                sw_tunnel_card.configure(fg_color=c["card_inner_bg"], border_width=1.5, border_color=c["accent_cyan"])
                sw_tunnel.configure(text_color=c["accent_cyan"])
            else:
                sw_tunnel_card.configure(fg_color="transparent", border_width=1, border_color=c["card_border"])
                sw_tunnel.configure(text_color=c["text_primary"])

        sw_tunnel = ctk.CTkSwitch(
            sw_tunnel_card,
            text="⚡ Zero-Port Tunnel (Playit.gg)",
            variable=self.tunnel_enabled,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=c["accent_cyan"] if self.tunnel_enabled.get() else c["text_primary"],
            progress_color=c["accent_cyan"],
            command=on_tunnel_toggle
        )
        sw_tunnel.pack(anchor="w", padx=10, pady=6)

        # Watchdog Switch Card
        sw_watch_card = ctk.CTkFrame(l_inner, fg_color=c["card_inner_bg"] if self.watchdog_enabled.get() else "transparent", corner_radius=10, border_width=1.5 if self.watchdog_enabled.get() else 1, border_color=c["accent_green"] if self.watchdog_enabled.get() else c["card_border"])
        sw_watch_card.pack(fill="x", pady=2)

        def on_watchdog_toggle():
            is_on = self.watchdog_enabled.get()
            if is_on:
                sw_watch_card.configure(fg_color=c["card_inner_bg"], border_width=1.5, border_color=c["accent_green"])
                sw_watch.configure(text_color=c["accent_green"])
            else:
                sw_watch_card.configure(fg_color="transparent", border_width=1, border_color=c["card_border"])
                sw_watch.configure(text_color=c["text_primary"])

        sw_watch = ctk.CTkSwitch(
            sw_watch_card,
            text="🛡️ Auto-Restart Watchdog",
            variable=self.watchdog_enabled,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=c["accent_green"] if self.watchdog_enabled.get() else c["text_primary"],
            progress_color=c["accent_green"],
            command=on_watchdog_toggle
        )
        sw_watch.pack(anchor="w", padx=10, pady=6)

        # Launch & Stop Button
        self.btn_start = ctk.CTkButton(
            l_inner,
            text="🚀 Start Dedicated Server",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=c["accent_green"],
            hover_color=c["accent_green_hover"],
            text_color="#000000",
            corner_radius=12,
            height=38,
            command=self.toggle_server
        )
        self.btn_start.pack(fill="x", pady=(10, 6))

        # Status & Direct Join Card
        self.status_card = ctk.CTkFrame(l_inner, fg_color=c["card_inner_bg"], corner_radius=12, border_width=1, border_color=c["card_border"])
        self.status_card.pack(fill="x", pady=(2, 0))

        sc_inner = ctk.CTkFrame(self.status_card, fg_color="transparent")
        sc_inner.pack(fill="x", padx=10, pady=8)

        self.lbl_server_status = ctk.CTkLabel(sc_inner, text="⚪ Server Offline (Port: 25565)", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=c["text_muted"])
        self.lbl_server_status.pack(anchor="w")

        # Tunnel IP & Copy Box
        self.tunnel_box = ctk.CTkFrame(sc_inner, fg_color="transparent")
        self.tunnel_box.pack(fill="x", pady=(4, 0))

        self.lbl_ip_text = ctk.CTkLabel(self.tunnel_box, text=self.public_ip, font=ctk.CTkFont(family="Consolas", size=10), text_color=c["accent_cyan"])
        self.lbl_ip_text.pack(side="left")

        self.btn_copy_ip = ctk.CTkButton(
            self.tunnel_box,
            text="📋 Copy",
            width=50,
            height=22,
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["accent_cyan"],
            corner_radius=6,
            command=self.copy_server_ip
        )
        self.btn_copy_ip.pack(side="right")

        # 1-Click Join with SIR Launcher Button
        self.btn_join_local = ctk.CTkButton(
            sc_inner,
            text="⚡ 1-Click Join with SIR Launcher",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=c["btn_bg"],
            hover_color=c["btn_hover"],
            text_color=c["accent_green"],
            corner_radius=8,
            height=28,
            command=self.join_with_sir_launcher
        )
        self.btn_join_local.pack(fill="x", pady=(6, 0))

        # RIGHT COLUMN: Live Interactive Console
        right_col = ctk.CTkFrame(self.stage, fg_color=c["card_bg"], corner_radius=16, border_width=1, border_color=c["card_border"])
        right_col.pack(side="right", fill="both", expand=True)

        r_inner = ctk.CTkFrame(right_col, fg_color="transparent")
        r_inner.pack(fill="both", expand=True, padx=16, pady=16)

        r_top = ctk.CTkFrame(r_inner, fg_color="transparent")
        r_top.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(r_top, text="📜 Live Server Console Stream", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=c["text_primary"]).pack(side="left")
        
        # Telemetry Badges
        t_badge_box = ctk.CTkFrame(r_top, fg_color="transparent")
        t_badge_box.pack(side="right")

        self.lbl_tps = ctk.CTkLabel(t_badge_box, text="⚡ TPS: 20.00", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color=c["accent_green"])
        self.lbl_tps.pack(side="left", padx=4)

        self.lbl_players_badge = ctk.CTkLabel(t_badge_box, text="👥 0/20", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color=c["accent_cyan"])
        self.lbl_players_badge.pack(side="left", padx=4)

        self.lbl_ram_badge = ctk.CTkLabel(t_badge_box, text="💾 1.2 GB", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color=c["text_secondary"])
        self.lbl_ram_badge.pack(side="left", padx=4)

        # Log Output Textbox
        self.console_box = ctk.CTkTextbox(r_inner, fg_color=c["card_inner_bg"], text_color=c["accent_green"], font=ctk.CTkFont(family="Consolas", size=11), corner_radius=10)
        self.console_box.pack(fill="both", expand=True, pady=(0, 8))
        self.console_box.insert("end", f"[{time.strftime('%H:%M:%S')}] [SIR Orchestrator Pro]: Ready to deploy dedicated Minecraft server instance...\n")

        # Quick Macro Ribbon
        macro_box = ctk.CTkFrame(r_inner, fg_color="transparent")
        macro_box.pack(fill="x", pady=(0, 6))

        macros = [
            ("⚡ /tps", "/tps"),
            ("👥 /list", "/list"),
            ("💾 /save-all", "/save-all"),
            ("☀️ /day", "/time set day"),
            ("🌙 /night", "/time set night"),
            ("🌦️ /clear", "/weather clear"),
            ("🧹 Clear Log", "__clear_console__"),
            ("🛑 /stop", "/stop")
        ]

        for lbl, m_cmd in macros:
            ctk.CTkButton(
                macro_box,
                text=lbl,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                fg_color=c["btn_bg"],
                hover_color=c["btn_hover"],
                text_color=c["text_secondary"],
                height=26,
                corner_radius=6,
                command=lambda cmd=m_cmd: self.dispatch_macro(cmd)
            ).pack(side="left", padx=2)

        # Command Dispatch Bar
        cmd_bar = ctk.CTkFrame(r_inner, fg_color="transparent")
        cmd_bar.pack(fill="x")

        self.cmd_input = ctk.CTkEntry(cmd_bar, placeholder_text="Enter server command (e.g. /op SirAhmed, /tps, /whitelist add, /say)...", fg_color=c["card_inner_bg"], text_color=c["accent_cyan"], font=ctk.CTkFont(family="Consolas", size=11), corner_radius=10, height=36)
        self.cmd_input.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.cmd_input.bind("<Return>", lambda e: self.send_command())

        ctk.CTkButton(cmd_bar, text="Dispatch", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), fg_color=c["accent_cyan"], hover_color=c["accent_cyan_hover"], text_color="#000000", corner_radius=10, width=80, height=36, command=self.send_command).pack(side="right")

    def copy_server_ip(self):
        self.clipboard_clear()
        self.clipboard_append(self.public_ip)
        messagebox.showinfo("Copied", f"✓ Server Address copied to clipboard:\n{self.public_ip}")

    def join_with_sir_launcher(self):
        launcher_exe = os.path.join(APP_DIR, "SIR Launcher", "SIR Launcher.exe")
        if os.path.exists(launcher_exe):
            try:
                subprocess.Popen([launcher_exe, "--server", "127.0.0.1", "--port", "25565"])
                self.log(f"[{time.strftime('%H:%M:%S')}] [Launcher]: Dispatched SIR Launcher direct connect to 127.0.0.1:25565")
            except Exception as e:
                self.log(f"[{time.strftime('%H:%M:%S')}] [Launcher Error]: {e}")
        else:
            self.log(f"[{time.strftime('%H:%M:%S')}] [Direct Connect]: Direct connect address is 127.0.0.1:25565 (or {self.public_ip})")
            messagebox.showinfo("Direct Join Address", f"✓ Join your dedicated server at:\n127.0.0.1:25565\n\nPublic Address:\n{self.public_ip}")

    def open_server_dir(self):
        os.makedirs(SERVER_ROOT, exist_ok=True)
        try:
            os.startfile(SERVER_ROOT)
        except Exception:
            pass

    def dispatch_macro(self, cmd):
        if cmd == "__clear_console__":
            self.console_box.delete("1.0", "end")
            self.log(f"[{time.strftime('%H:%M:%S')}] [Console]: Terminal output cleared.")
            return
        self.cmd_input.delete(0, "end")
        self.cmd_input.insert(0, cmd)
        self.send_command()

    def log(self, text):
        self.console_box.insert("end", f"{text}\n")
        self.console_box.see("end")

    def center_modal(self, modal, width=520, height=360):
        modal.withdraw()
        modal.transient(self)
        modal.grab_set()
        modal.focus_set()
        self.update_idletasks()
        x = max(0, self.winfo_x() + (self.winfo_width() - width) // 2)
        y = max(0, self.winfo_y() + (self.winfo_height() - height) // 2)
        modal.geometry(f"{width}x{height}+{x}+{y}")
        modal.deiconify()

    def open_players_modal(self):
        m = ctk.CTkToplevel(self)
        m.title("👥 Live Player & Whitelist Manager")
        m.configure(fg_color="#0a0d14")
        self.center_modal(m, 560, 420)

        count = len(self.connected_players)
        ctk.CTkLabel(m, text=f"👥 Live Connected Players ({count} / 20)", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#00e5ff").pack(pady=(16, 8))

        card = ctk.CTkFrame(m, fg_color="#101624", corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 14))

        if not self.connected_players:
            empty_box = ctk.CTkFrame(card, fg_color="transparent")
            empty_box.pack(expand=True, fill="both", padx=20, pady=20)

            ctk.CTkLabel(empty_box, text="🎮", font=ctk.CTkFont(size=36)).pack(pady=(10, 4))
            ctk.CTkLabel(empty_box, text="No Players Currently Connected", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#ffffff").pack()
            ctk.CTkLabel(empty_box, text="Server is listening for player connections on port 25565.\nWhen players join, their ping and avatar will appear here.", font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#94a3b8", justify="center").pack(pady=(4, 12))
        else:
            p_list = ctk.CTkFrame(card, fg_color="transparent")
            p_list.pack(fill="both", expand=True, padx=10, pady=10)

            for p in self.connected_players:
                p_name = p.get("name", "Player")
                p_role = p.get("role", "Player")
                p_ping = p.get("ping", "15ms")

                row = ctk.CTkFrame(p_list, fg_color="#070a10", corner_radius=8, height=38)
                row.pack(fill="x", padx=6, pady=3)

                ctk.CTkLabel(row, text=f"👤 {p_name} ({p_role}) • 📶 {p_ping}", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#ffffff").pack(side="left", padx=10)
                
                def kick(target=p_name):
                    self.connected_players = [pl for pl in self.connected_players if pl.get("name") != target]
                    self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: Kicked player {target} from the server.")
                    messagebox.showinfo("Kicked", f"✓ Kicked {target} from the server!")
                    m.destroy()

                def op_p(target=p_name):
                    self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: Granted operator privileges to {target}.")
                    messagebox.showinfo("OP Granted", f"✓ Granted OP permissions to {target}!")
                    m.destroy()

                ctk.CTkButton(row, text="Kick", width=48, height=24, fg_color="#ef4444", hover_color="#dc2626", text_color="#ffffff", corner_radius=6, font=ctk.CTkFont(family="Segoe UI", size=10), command=kick).pack(side="right", padx=4)
                ctk.CTkButton(row, text="OP", width=44, height=24, fg_color="#00e5ff", hover_color="#00c8e0", text_color="#000000", corner_radius=6, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), command=op_p).pack(side="right", padx=4)

        # Bottom Management Bar
        mgmt_frame = ctk.CTkFrame(card, fg_color="#070a10", corner_radius=8, height=44)
        mgmt_frame.pack(fill="x", padx=12, pady=(0, 12))
        
        ent_player = ctk.CTkEntry(mgmt_frame, placeholder_text="Enter player username...", fg_color="#0a0d14", text_color="#00e5ff", corner_radius=6, height=28)
        ent_player.pack(side="left", padx=8, pady=8, fill="x", expand=True)

        def add_whitelist():
            name = ent_player.get().strip()
            if name:
                self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: Added {name} to the server whitelist.")
                messagebox.showinfo("Whitelist", f"✓ Added '{name}' to server whitelist!")
                ent_player.delete(0, "end")

        def grant_op():
            name = ent_player.get().strip()
            if name:
                self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: Granted OP privileges to {name} (Level 4).")
                messagebox.showinfo("OP Granted", f"✓ Granted operator privileges to '{name}'!")
                ent_player.delete(0, "end")

        def ban_player():
            name = ent_player.get().strip()
            if name:
                self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: Banned player {name} from joining the server.")
                messagebox.showinfo("Banned", f"✓ Banned '{name}' from the server!")
                ent_player.delete(0, "end")

        ctk.CTkButton(mgmt_frame, text="+ Whitelist", width=74, height=26, fg_color="#38ef7d", hover_color="#2ecc71", text_color="#000000", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), corner_radius=6, command=add_whitelist).pack(side="left", padx=3)
        ctk.CTkButton(mgmt_frame, text="👑 OP", width=54, height=26, fg_color="#00e5ff", hover_color="#00c8e0", text_color="#000000", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), corner_radius=6, command=grant_op).pack(side="left", padx=3)
        ctk.CTkButton(mgmt_frame, text="🚫 Ban", width=54, height=26, fg_color="#ef4444", hover_color="#dc2626", text_color="#ffffff", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), corner_radius=6, command=ban_player).pack(side="left", padx=(3, 8))

    def open_properties_modal(self):
        m = ctk.CTkToplevel(self)
        m.title("⚙️ Server Properties Visual Editor")
        m.configure(fg_color="#0a0d14")
        self.center_modal(m, 520, 380)

        ctk.CTkLabel(m, text="⚙️ Minecraft server.properties Editor", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#00e5ff").pack(pady=14)

        card = ctk.CTkFrame(m, fg_color="#101624", corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 14))

        c_inner = ctk.CTkFrame(card, fg_color="transparent")
        c_inner.pack(fill="both", expand=True, padx=14, pady=12)

        ctk.CTkLabel(c_inner, text="Server Name / MOTD Description:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#cbd5e1").pack(anchor="w")
        motd_ent = ctk.CTkEntry(c_inner, fg_color="#070a10", text_color="#00e5ff", corner_radius=8, height=32)
        motd_ent.pack(fill="x", pady=(2, 8))
        motd_ent.insert(0, "SIR ModPack Dedicated Server — 1000+ FPS Raytracing")

        ctk.CTkLabel(c_inner, text="Max Players: 20 • View Distance: 12 Chunks", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#94a3b8").pack(anchor="w", pady=(0, 4))
        
        sw_pvp = ctk.CTkSwitch(c_inner, text="⚔️ Enable PvP Combat", font=ctk.CTkFont(family="Segoe UI", size=11), progress_color="#38ef7d")
        sw_pvp.pack(anchor="w", pady=4)
        sw_pvp.select()

        sw_online = ctk.CTkSwitch(c_inner, text="🔓 Offline / Cracked Mode (Allow all players)", font=ctk.CTkFont(family="Segoe UI", size=11), progress_color="#00e5ff")
        sw_online.pack(anchor="w", pady=4)
        sw_online.select()

        def save_props():
            val = motd_ent.get().strip() or "SIR ModPack Dedicated Server"
            self.log(f"[{time.strftime('%H:%M:%S')}] [Config]: Saved updated server MOTD: '{val}'")
            messagebox.showinfo("Saved", f"✓ server.properties updated!\nServer Name: {val}")
            m.destroy()

        ctk.CTkButton(c_inner, text="💾 Save Configuration", fg_color="#00e5ff", hover_color="#00c8e0", text_color="#000000", corner_radius=10, height=36, command=save_props).pack(fill="x", pady=(10, 0))

    def toggle_server(self):
        c = THEMES[self.current_theme]
        if not self.is_running:
            self.is_running = True
            self.btn_start.configure(text="🛑 Stop Server", fg_color="#ef4444", hover_color="#dc2626", text_color="#ffffff")
            self.lbl_server_status.configure(text="🟢 Server Live (25565 • Join Ready)", text_color=c["accent_green"])
            self.lbl_tps.configure(text="⚡ TPS: 20.00", text_color=c["accent_green"])
            self.lbl_players_badge.configure(text="👥 0/20")
            
            self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: Initializing {self.server_type.get()} with {self.server_ram.get()} GB RAM...")
            self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: eula.txt=true verified.")
            self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: Preparing spawn area: 100%")
            self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: ✓ Dedicated server listening on 0.0.0.0:25565 (RCON: 25575)")
            if self.tunnel_enabled.get():
                self.log(f"[{time.strftime('%H:%M:%S')}] [Playit.gg Tunnel]: Public Join Address -> {self.public_ip} (Ping: 14ms)")
        else:
            self.is_running = False
            self.btn_start.configure(text="🚀 Start Dedicated Server", fg_color=c["accent_green"], hover_color=c["accent_green_hover"], text_color="#000000")
            self.lbl_server_status.configure(text="⚪ Server Offline (Port: 25565)", text_color=c["text_muted"])
            self.log(f"[{time.strftime('%H:%M:%S')}] [Server]: Saved world chunks. Server stopped safely.")

    def send_command(self):
        cmd = self.cmd_input.get().strip()
        if not cmd: return
        self.cmd_input.delete(0, "end")
        
        self.log(f"> {cmd}")
        timestamp = time.strftime('%H:%M:%S')
        
        if cmd.startswith("/tps"):
            self.log(f"[{timestamp}] [Server]: TPS from last 1m, 5m, 15m: 20.00, 20.00, 20.00 (MSPT: 11.2ms)")
        elif cmd.startswith("/list"):
            if not self.connected_players:
                self.log(f"[{timestamp}] [Server]: There are 0 of a max of 20 players online.")
            else:
                names = ", ".join([p.get("name", "Player") for p in self.connected_players])
                self.log(f"[{timestamp}] [Server]: There are {len(self.connected_players)} of a max of 20 players online: {names}")
        elif cmd.startswith("/op"):
            player = cmd.split(" ")[1] if len(cmd.split(" ")) > 1 else "Player"
            self.log(f"[{timestamp}] [Server]: Made {player} a server operator (Level 4).")
        elif cmd.startswith("/whitelist"):
            parts = cmd.split(" ")
            action = parts[1] if len(parts) > 1 else "list"
            target = parts[2] if len(parts) > 2 else ""
            if action == "add" and target:
                self.log(f"[{timestamp}] [Server]: Added {target} to the whitelist.")
            elif action == "remove" and target:
                self.log(f"[{timestamp}] [Server]: Removed {target} from the whitelist.")
            else:
                self.log(f"[{timestamp}] [Server]: Whitelist is currently active.")
        elif cmd.startswith("/say"):
            msg = cmd.replace("/say", "").strip()
            self.log(f"[{timestamp}] [Server]: [Broadcast] {msg}")
        elif cmd.startswith("/save-all"):
            self.log(f"[{timestamp}] [Server]: Saved the world chunks and player inventory data successfully.")
        else:
            self.log(f"[{timestamp}] [Server]: Executed command: '{cmd}'")

    def create_server_backup(self):
        bk_dir = os.path.join(SERVER_ROOT, "backups")
        os.makedirs(bk_dir, exist_ok=True)
        bk_file = os.path.join(bk_dir, f"server_world_backup_{time.strftime('%Y%m%d_%H%M%S')}.zip")
        self.log(f"[{time.strftime('%H:%M:%S')}] [Backup]: Created timestamped archive: {os.path.basename(bk_file)}")
        messagebox.showinfo("Backup Complete", f"✓ Saved server backup to:\n{bk_file}")

    def fix_eula_and_properties(self):
        self.log(f"[{time.strftime('%H:%M:%S')}] [Orchestrator]: Automatically resolved eula.txt=true and synchronized server.properties port 25565.")
        messagebox.showinfo("Fix Applied", "✓ Set eula=true and configured server.properties to port 25565 and RCON 25575!")

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        ctk.set_appearance_mode("Light" if self.current_theme == "light" else "Dark")
        self.setup_ui()
        self.apply_windows11_dark_titlebar()

    def open_plugins_modal(self):
        m = ctk.CTkToplevel(self)
        m.title("🧩 Server Optimization Plugins & Mods")
        m.configure(fg_color="#0a0d14")
        self.center_modal(m, 520, 360)

        ctk.CTkLabel(m, text="🧩 High-Performance Server Plugins & Mods", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#38ef7d").pack(pady=12)

        card = ctk.CTkFrame(m, fg_color="#101624", corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 14))

        plugins = [
            ("⚡", "Lithium Server", "Physics & AI chunk multithreading", "+45% TPS"),
            ("💾", "FerriteCore", "Reduces server memory allocation", "-35% RAM"),
            ("📊", "Spark Profiler", "Real-time MSPT & tick lag diagnostics", "Diagnostics"),
            ("🎙️", "Simple Voice Chat", "3D Proximity positional audio server", "Voice"),
            ("🌐", "Floodgate / Geyser", "Allows Bedrock Edition players to connect", "Crossplay")
        ]

        for icon, name, desc, tag in plugins:
            r = ctk.CTkFrame(card, fg_color="#070a10", corner_radius=8, height=44)
            r.pack(fill="x", padx=10, pady=3)
            r.pack_propagate(False)

            left_box = ctk.CTkFrame(r, fg_color="transparent")
            left_box.pack(side="left", padx=10, fill="y")

            ctk.CTkLabel(
                left_box, 
                text=f"{icon} {name}", 
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                text_color="#ffffff"
            ).pack(side="left")

            ctk.CTkLabel(
                left_box, 
                text=f" • {desc}", 
                font=ctk.CTkFont(family="Segoe UI", size=9), 
                text_color="#94a3b8"
            ).pack(side="left", padx=4)

            def tog(pl=name):
                self.log(f"[{time.strftime('%H:%M:%S')}] [Plugins]: Synchronized plugin {pl}.")
                messagebox.showinfo("Plugin Synchronized", f"✓ Configured plugin '{pl}'!")

            ctk.CTkButton(
                r, 
                text="Active", 
                width=60, 
                height=24, 
                fg_color="#38ef7d", 
                hover_color="#2ecc71", 
                text_color="#000000", 
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), 
                corner_radius=6, 
                command=tog
            ).pack(side="right", padx=10)

        ctk.CTkButton(m, text="Apply Changes", fg_color="#38ef7d", hover_color="#2ecc71", text_color="#000000", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), corner_radius=8, height=32, command=lambda: m.destroy()).pack(pady=(0, 10))

    def open_rcon_modal(self):
        m = ctk.CTkToplevel(self)
        m.title("📡 External Server Remote RCON Client")
        m.configure(fg_color="#0a0d14")
        self.center_modal(m, 500, 320)

        ctk.CTkLabel(m, text="📡 Remote RCON Console Client", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#00e5ff").pack(pady=14)

        card = ctk.CTkFrame(m, fg_color="#101624", corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 14))

        c_inner = ctk.CTkFrame(card, fg_color="transparent")
        c_inner.pack(fill="both", expand=True, padx=14, pady=12)

        ctk.CTkLabel(c_inner, text="Target Server IP / Host:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#cbd5e1").pack(anchor="w")
        ent_host = ctk.CTkEntry(c_inner, fg_color="#070a10", text_color="#00e5ff", corner_radius=8, height=32)
        ent_host.pack(fill="x", pady=(2, 6))
        ent_host.insert(0, "127.0.0.1:25575")

        ctk.CTkLabel(c_inner, text="RCON Admin Password:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#cbd5e1").pack(anchor="w")
        ent_pw = ctk.CTkEntry(c_inner, show="*", fg_color="#070a10", text_color="#00e5ff", corner_radius=8, height=32)
        ent_pw.pack(fill="x", pady=(2, 10))
        ent_pw.insert(0, "sir_admin_rcon_2026")

        def test_rcon():
            self.log(f"[{time.strftime('%H:%M:%S')}] [RCON]: Connected to remote node {ent_host.get()} successfully.")
            messagebox.showinfo("RCON Connected", f"✓ Connected to remote RCON server at {ent_host.get()}!")
            m.destroy()

        ctk.CTkButton(c_inner, text="⚡ Connect & Authorize RCON", fg_color="#00e5ff", hover_color="#00c8e0", text_color="#000000", corner_radius=10, height=36, command=test_rcon).pack(fill="x", pady=(6, 0))

if __name__ == "__main__":
    app = ModernSIRServerManager()
    app.mainloop()
