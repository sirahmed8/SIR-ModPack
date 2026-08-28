import tkinter as tk
from tkinter import ttk
import ctypes
from sir_core.config import THEMES
from sir_core.launcher.java_locator import locate_java_runtimes

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

def get_system_ram_gb():
    try:
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        total_gb = round(stat.ullTotalPhys / (1024**3), 1)
        avail_gb = round(stat.ullAvailPhys / (1024**3), 1)
        return total_gb, avail_gb
    except Exception:
        return 16.0, 10.0

def open_game_settings_modal(parent):
    c = THEMES[parent.current_theme]
    modal = tk.Toplevel(parent)
    modal.title("Minecraft & Launcher Settings")
    modal.geometry("780x560")
    modal.minsize(700, 500)
    modal.configure(bg=c["modal_bg"])
    modal.transient(parent)

    m_head = tk.Frame(modal, bg=c["card_bg"], padx=18, pady=12, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    m_head.pack(fill="x")

    btn_close = tk.Button(m_head, text="✖ Close", font=("Segoe UI", 9, "bold"), bg=c["btn_bg"], fg=c["text_primary"], activebackground=c["btn_hover"], bd=0, padx=12, pady=4, cursor="hand2", command=modal.destroy)
    btn_close.pack(side="right", padx=(8, 0))

    lbl_t = tk.Label(m_head, text="⚙️ Game & Launcher Settings", font=("Segoe UI", 12, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], anchor="w")
    lbl_t.pack(side="left", fill="x", expand=True)

    body = tk.Frame(modal, bg=c["modal_bg"])
    body.pack(fill="both", expand=True)

    f_nav = tk.Frame(body, bg=c["sidebar_bg"], width=180, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=8, pady=10)
    f_nav.pack(side="left", fill="y")
    f_nav.pack_propagate(False)

    f_content = tk.Frame(body, bg=c["modal_bg"], padx=20, pady=14)
    f_content.pack(side="right", fill="both", expand=True)

    cats = ["⚡ Memory & Java", "🎮 Resolution"]
    cat_frames = {}
    for cat in cats:
        cat_frames[cat] = tk.Frame(f_content, bg=c["modal_bg"])

    def show_cat(target):
        for k, fr in cat_frames.items(): fr.pack_forget()
        for k, btn in nav_btns.items():
            if k == target: btn.config(bg=c["accent_cyan"], fg="#06090e")
            else: btn.config(bg=c["card_bg"], fg=c["text_primary"])
        cat_frames[target].pack(fill="both", expand=True)

    nav_btns = {}
    for cat in cats:
        btn = tk.Button(f_nav, text=cat, font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"], bd=0, padx=10, pady=8, anchor="w", cursor="hand2", command=lambda t=cat: show_cat(t))
        btn.pack(fill="x", pady=2)
        nav_btns[cat] = btn

    mem_fr = cat_frames["⚡ Memory & Java"]
    total_ram_gb, avail_ram_gb = get_system_ram_gb()

    lbl_ram_h = tk.Label(mem_fr, text="Allocated RAM (Memory)", font=("Segoe UI", 10, "bold"), bg=c["modal_bg"], fg=c["text_primary"])
    lbl_ram_h.pack(anchor="w")

    ram_info_r = tk.Frame(mem_fr, bg=c["modal_bg"])
    ram_info_r.pack(fill="x", pady=(4, 8))
    tk.Label(ram_info_r, text=f"Total System RAM: {total_ram_gb} GB  | ", font=("Segoe UI", 8), bg=c["modal_bg"], fg=c["text_secondary"]).pack(side="left")
    tk.Label(ram_info_r, text=f"● Free Available: {avail_ram_gb} GB", font=("Segoe UI", 8, "bold"), bg="#064e3b", fg=c["accent_green"], padx=6, pady=2).pack(side="left")

    cur_ram = parent.settings.get("ram_mb", 6144)
    lbl_cur_val = tk.Label(mem_fr, text=f"{cur_ram // 1024} GB ({cur_ram} MB)", font=("Segoe UI", 12, "bold"), bg=c["modal_bg"], fg=c["accent_cyan"])
    lbl_cur_val.pack(anchor="w", pady=(0, 4))

    def on_slider_change(v):
        val = int(float(v))
        lbl_cur_val.config(text=f"{val // 1024} GB ({val} MB)")
        parent.settings["ram_mb"] = val
        parent.save_settings()

    max_slider = int(total_ram_gb * 1024)
    ram_scale = ttk.Scale(mem_fr, from_=2048, to=max(8192, max_slider), orient="horizontal", command=on_slider_change)
    ram_scale.set(cur_ram)
    ram_scale.pack(fill="x", pady=(0, 16))

    show_cat("⚡ Memory & Java")
