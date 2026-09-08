import tkinter as tk
from tkinter import messagebox
import threading
from sir_core.config import THEMES
from sir_core.servers.live_pinger import query_minecraft_server_live_status

def open_custom_server_ping_modal(parent):
    c = THEMES[parent.current_theme]
    modal = tk.Toplevel(parent)
    modal.title("Ping Custom Minecraft Server")
    modal.geometry("540x420")
    modal.minsize(480, 360)
    modal.configure(bg=c["modal_bg"])
    modal.transient(parent)

    m_head = tk.Frame(modal, bg=c["card_bg"], padx=16, pady=10, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    m_head.pack(fill="x")

    btn_close = tk.Button(m_head, text="✖ Close", font=("Segoe UI", 9, "bold"), bg=c["btn_bg"], fg=c["text_primary"], activebackground=c["btn_hover"], bd=0, padx=12, pady=4, cursor="hand2", command=modal.destroy)
    btn_close.pack(side="right", padx=(8, 0))

    lbl_t = tk.Label(m_head, text="➕ Real-Time Custom Server Ping", font=("Segoe UI", 11, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], anchor="w")
    lbl_t.pack(side="left", fill="x", expand=True)

    body = tk.Frame(modal, bg=c["modal_bg"], padx=20, pady=16)
    body.pack(fill="both", expand=True)

    lbl_prompt = tk.Label(body, text="Enter any Minecraft Java Server address / domain / IP:", font=("Segoe UI", 9, "bold"), bg=c["modal_bg"], fg=c["text_primary"])
    lbl_prompt.pack(anchor="w", pady=(0, 6))

    in_f = tk.Frame(body, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=10, pady=6)
    in_f.pack(fill="x", pady=(0, 12))

    ent_host = tk.Entry(in_f, font=("Segoe UI", 10), bg=c["card_bg"], fg=c["text_primary"], insertbackground=c["accent_cyan"], bd=0)
    ent_host.insert(0, "play.hypixel.net")
    ent_host.pack(side="left", fill="x", expand=True)

    res_box = tk.Frame(body, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=12)
    res_box.pack(fill="both", expand=True, pady=(0, 12))

    lbl_res_status = tk.Label(res_box, text="⚡ Click 'Ping Server' below to query live stats", font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_secondary"])
    lbl_res_status.pack(anchor="w")

    lbl_res_players = tk.Label(res_box, text="👥 Players: --", font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_primary"])
    lbl_res_players.pack(anchor="w", pady=(4, 0))

    lbl_res_ver = tk.Label(res_box, text="🎮 Version: --", font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_primary"])
    lbl_res_ver.pack(anchor="w", pady=(2, 0))

    lbl_res_motd = tk.Label(res_box, text="📜 MOTD: --", font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_secondary"], wraplength=440, justify="left")
    lbl_res_motd.pack(anchor="w", pady=(4, 0))

    def do_ping():
        host = ent_host.get().strip()
        if not host: return
        lbl_res_status.config(text="⏳ Querying live API...", fg=c["accent_cyan"])
        def _p():
            data, err = query_minecraft_server_live_status(host)
            def update():
                if data and data.get("online"):
                    lbl_res_status.config(text=f"🟢 ONLINE — {host}", fg=c["accent_green"])
                    lbl_res_players.config(text=f"👥 Players: {data.get('players_str')}")
                    lbl_res_ver.config(text=f"🎮 Supported Version: {data.get('version')}")
                    lbl_res_motd.config(text=f"📜 MOTD: {data.get('motd') or 'Active'}")
                else:
                    lbl_res_status.config(text=f"🔴 OFFLINE / UNREACHABLE — {host}", fg="#ef4444")
                    lbl_res_players.config(text="👥 Players: 0")
                    lbl_res_ver.config(text="🎮 Version: Unknown")
                    lbl_res_motd.config(text="📜 MOTD: Unable to establish handshake")
            modal.after(0, update)
        threading.Thread(target=_p, daemon=True).start()

    btn_row = tk.Frame(body, bg=c["modal_bg"])
    btn_row.pack(fill="x")

    btn_ping = tk.Button(btn_row, text="⚡ Ping Server", font=("Segoe UI", 9, "bold"), bg=c["accent_cyan"], fg="#06090e", activebackground=c["accent_green"], bd=0, padx=16, pady=6, cursor="hand2", command=do_ping)
    btn_ping.pack(side="left", padx=(0, 8))

    def quick_join_custom():
        h = ent_host.get().strip()
        if h:
            parent.clipboard_clear()
            parent.clipboard_append(h)
            messagebox.showinfo("Quick Join", f"✓ Server address '{h}' copied! Launching active SIR profile ({parent.selected_instance_id})...")
            parent.launch_active_instance()

    btn_join_cust = tk.Button(btn_row, text="▶ Quick Join", font=("Segoe UI", 9, "bold"), bg=c["accent_green"], fg="#06090e", activebackground=c["accent_green_hover"], bd=0, padx=16, pady=6, cursor="hand2", command=quick_join_custom)
    btn_join_cust.pack(side="left")
