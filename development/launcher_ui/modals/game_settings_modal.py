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

    cats = [
        "⚡ Memory & JVM",
        "🎮 Display & Window",
        "🚀 Hardware & GPU",
        "🌐 Network & Satellite",
        "🎨 Visuals & Shaders",
        "🛡️ Diagnostics & Privacy"
    ]
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

    # Ensure parent settings dict exists
    if not hasattr(parent, "settings"):
        parent.settings = {}

    def get_setting(k, default):
        return parent.settings.get(k, default)

    def set_setting(k, v):
        parent.settings[k] = v
        if hasattr(parent, "save_settings"):
            parent.save_settings()

    # --- TAB 1: MEMORY & JVM ---
    mem_fr = cat_frames["⚡ Memory & JVM"]
    total_ram_gb, avail_ram_gb = get_system_ram_gb()

    tk.Label(mem_fr, text="RAM Allocation & JVM Execution", font=("Segoe UI", 11, "bold"), bg=c["modal_bg"], fg=c["accent_cyan"]).pack(anchor="w", pady=(0, 4))
    tk.Label(mem_fr, text="Configure memory headroom and garbage collector flags for maximum stutter-free 144Hz FPS.", font=("Segoe UI", 8), bg=c["modal_bg"], fg=c["text_secondary"]).pack(anchor="w", pady=(0, 10))

    ram_card = tk.Frame(mem_fr, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=12)
    ram_card.pack(fill="x", pady=(0, 10))

    ram_info_r = tk.Frame(ram_card, bg=c["card_bg"])
    ram_info_r.pack(fill="x", pady=(0, 8))
    tk.Label(ram_info_r, text=f"Total System RAM: {total_ram_gb} GB  | ", font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_secondary"]).pack(side="left")
    tk.Label(ram_info_r, text=f"● Available Free: {avail_ram_gb} GB", font=("Segoe UI", 8, "bold"), bg="#064e3b", fg=c["accent_green"], padx=6, pady=2).pack(side="left")

    cur_ram = get_setting("ram_mb", 6144)
    lbl_cur_val = tk.Label(ram_card, text=f"{cur_ram // 1024} GB ({cur_ram} MB)", font=("Segoe UI", 12, "bold"), bg=c["card_bg"], fg=c["accent_cyan"])
    lbl_cur_val.pack(anchor="w", pady=(0, 4))

    def on_slider_change(v):
        val = int(float(v))
        lbl_cur_val.config(text=f"{val // 1024} GB ({val} MB)")
        set_setting("ram_mb", val)

    max_slider = int(total_ram_gb * 1024)
    ram_scale = ttk.Scale(ram_card, from_=2048, to=max(8192, max_slider), orient="horizontal", command=on_slider_change)
    ram_scale.set(cur_ram)
    ram_scale.pack(fill="x", pady=(0, 8))

    flags_card = tk.Frame(mem_fr, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=10)
    flags_card.pack(fill="x", pady=(0, 10))

    zgc_var = tk.BooleanVar(value=get_setting("enable_zgc", True))
    def on_zgc_toggle():
        set_setting("enable_zgc", zgc_var.get())
    chk_zgc = tk.Checkbutton(flags_card, text="Enable Generational ZGC (-XX:+UseZGC -XX:+ZGenerational) [Zero Stutter GC]", variable=zgc_var, font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["accent_green"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_zgc_toggle)
    chk_zgc.pack(anchor="w")

    aikar_var = tk.BooleanVar(value=get_setting("enable_aikar", True))
    def on_aikar_toggle():
        set_setting("enable_aikar", aikar_var.get())
    chk_aikar = tk.Checkbutton(flags_card, text="Apply Aikar's Enterprise Low-Latency JVM Flags", variable=aikar_var, font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_secondary"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_aikar_toggle)
    chk_aikar.pack(anchor="w", pady=(4, 0))

    # --- TAB 2: DISPLAY & WINDOW ---
    disp_fr = cat_frames["🎮 Display & Window"]
    tk.Label(disp_fr, text="Display & Resolution Geometry", font=("Segoe UI", 11, "bold"), bg=c["modal_bg"], fg=c["accent_cyan"]).pack(anchor="w", pady=(0, 4))

    disp_card = tk.Frame(disp_fr, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=12)
    disp_card.pack(fill="x", pady=(0, 10))

    fs_var = tk.BooleanVar(value=get_setting("fullscreen", False))
    def on_fs_toggle(): set_setting("fullscreen", fs_var.get())
    tk.Checkbutton(disp_card, text="Launch Game in Exclusive Fullscreen", variable=fs_var, font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_fs_toggle).pack(anchor="w")

    borderless_var = tk.BooleanVar(value=get_setting("borderless_window", True))
    def on_borderless_toggle(): set_setting("borderless_window", borderless_var.get())
    tk.Checkbutton(disp_card, text="Enable Seamless Borderless Windowed Mode (Cubes Without Borders)", variable=borderless_var, font=("Segoe UI", 9), bg=c["card_bg"], fg=c["accent_cyan"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_borderless_toggle).pack(anchor="w", pady=(6, 0))

    res_card = tk.Frame(disp_fr, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=12)
    res_card.pack(fill="x", pady=(0, 10))

    tk.Label(res_card, text="Window Dimensions (Width x Height):", font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"]).pack(anchor="w", pady=(0, 6))
    res_r = tk.Frame(res_card, bg=c["card_bg"])
    res_r.pack(fill="x")

    ent_w = tk.Entry(res_r, width=8, font=("Segoe UI", 10), bg=c["entry_bg"], fg=c["text_primary"], bd=1, relief="solid")
    ent_w.insert(0, str(get_setting("window_width", 1280)))
    ent_w.pack(side="left", padx=(0, 4))
    tk.Label(res_r, text="✕", font=("Segoe UI", 9), bg=c["card_bg"], fg=c["text_secondary"]).pack(side="left", padx=4)
    ent_h = tk.Entry(res_r, width=8, font=("Segoe UI", 10), bg=c["entry_bg"], fg=c["text_primary"], bd=1, relief="solid")
    ent_h.insert(0, str(get_setting("window_height", 720)))
    ent_h.pack(side="left", padx=(0, 8))

    def save_res():
        try:
            set_setting("window_width", int(ent_w.get()))
            set_setting("window_height", int(ent_h.get()))
            messagebox.showinfo("Saved", "Resolution geometry updated.")
        except Exception:
            pass
    tk.Button(res_r, text="Apply Resolution", font=("Segoe UI", 8, "bold"), bg=c["accent_cyan"], fg="#06090e", bd=0, padx=10, pady=3, cursor="hand2", command=save_res).pack(side="left")

    # --- TAB 3: HARDWARE & GPU ---
    hw_fr = cat_frames["🚀 Hardware & GPU"]
    tk.Label(hw_fr, text="GPU Preference & Memory Compaction", font=("Segoe UI", 11, "bold"), bg=c["modal_bg"], fg=c["accent_cyan"]).pack(anchor="w", pady=(0, 4))

    hw_card = tk.Frame(hw_fr, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=12)
    hw_card.pack(fill="x", pady=(0, 10))

    gpu_var = tk.BooleanVar(value=get_setting("prefer_discrete_gpu", True))
    def on_gpu_toggle(): set_setting("prefer_discrete_gpu", gpu_var.get())
    tk.Checkbutton(hw_card, text="Force High-Performance Dedicated GPU (NVIDIA / AMD) for Java Runtime", variable=gpu_var, font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_gpu_toggle).pack(anchor="w")

    ram_comp_var = tk.BooleanVar(value=get_setting("auto_compact_ram", True))
    def on_comp_toggle(): set_setting("auto_compact_ram", ram_comp_var.get())
    tk.Checkbutton(hw_card, text="Enable Background RAM Compactor (psapi.dll EmptyWorkingSet every 10 min)", variable=ram_comp_var, font=("Segoe UI", 9), bg=c["card_bg"], fg=c["accent_green"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_comp_toggle).pack(anchor="w", pady=(6, 0))

    # --- TAB 4: NETWORK & SATELLITE ---
    net_fr = cat_frames["🌐 Network & Satellite"]
    tk.Label(net_fr, text="Low-Latency CDN Mesh & Telemetry", font=("Segoe UI", 11, "bold"), bg=c["modal_bg"], fg=c["accent_cyan"]).pack(anchor="w", pady=(0, 4))

    net_card = tk.Frame(net_fr, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=12)
    net_card.pack(fill="x", pady=(0, 10))

    tk.Label(net_card, text="Preferred Satellite Routing Region:", font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"]).pack(anchor="w", pady=(0, 6))
    region_box = tk.Frame(net_card, bg=c["card_bg"])
    region_box.pack(fill="x")

    for reg_name in ["Auto-Mesh (Lowest Ping)", "EU-Frankfurt", "US-East", "AP-Tokyo"]:
        tk.Radiobutton(region_box, text=reg_name, value=reg_name, font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_secondary"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"]).pack(side="left", padx=(0, 10))

    # --- TAB 5: VISUALS & SHADERS ---
    vis_fr = cat_frames["🎨 Visuals & Shaders"]
    tk.Label(vis_fr, text="Iris Shaders Engine & Raytracing Defaults", font=("Segoe UI", 11, "bold"), bg=c["modal_bg"], fg=c["accent_cyan"]).pack(anchor="w", pady=(0, 4))

    vis_card = tk.Frame(vis_fr, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=12)
    vis_card.pack(fill="x", pady=(0, 10))

    sh_var = tk.BooleanVar(value=get_setting("enable_shaders_default", True))
    def on_sh_toggle(): set_setting("enable_shaders_default", sh_var.get())
    tk.Checkbutton(vis_card, text="Enable SIR Modern 2.0 Shaders on Profile Launch (Toggle Key: 'K')", variable=sh_var, font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_sh_toggle).pack(anchor="w")

    pom_var = tk.BooleanVar(value=get_setting("enable_pom_relief", True))
    def on_pom_toggle(): set_setting("enable_pom_relief", pom_var.get())
    tk.Checkbutton(vis_card, text="Enable 3D Parallax Occlusion Mapping (POM) Relief Depth", variable=pom_var, font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_secondary"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_pom_toggle).pack(anchor="w", pady=(4, 0))

    # --- TAB 6: DIAGNOSTICS & PRIVACY ---
    diag_fr = cat_frames["🛡️ Diagnostics & Privacy"]
    tk.Label(diag_fr, text="Diagnostics & Incident Telemetry", font=("Segoe UI", 11, "bold"), bg=c["modal_bg"], fg=c["accent_cyan"]).pack(anchor="w", pady=(0, 4))

    diag_card = tk.Frame(diag_fr, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=12)
    diag_card.pack(fill="x", pady=(0, 10))

    crash_var = tk.BooleanVar(value=get_setting("auto_report_crashes", True))
    def on_crash_toggle(): set_setting("auto_report_crashes", crash_var.get())
    tk.Checkbutton(diag_card, text="Auto-Report Game Crash Logs to Firebase Firestore for Instant AI Fixes", variable=crash_var, font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["accent_green"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_crash_toggle).pack(anchor="w")

    rpc_var = tk.BooleanVar(value=get_setting("enable_discord_rpc", True))
    def on_rpc_toggle(): set_setting("enable_discord_rpc", rpc_var.get())
    tk.Checkbutton(diag_card, text="Enable Discord Rich Presence (Display Current Minecraft Instance & Server)", variable=rpc_var, font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_secondary"], selectcolor=c["sidebar_bg"], activebackground=c["card_bg"], command=on_rpc_toggle).pack(anchor="w", pady=(4, 0))

    show_cat("⚡ Memory & JVM")
