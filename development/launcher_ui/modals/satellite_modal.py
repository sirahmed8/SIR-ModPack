import tkinter as tk
from tkinter import messagebox
from sir_core.config import THEMES
from sir_core.social.satellite_hub import get_friends_list, get_chat_history

def open_satellite_modal(parent):
    theme_name = getattr(parent, "current_theme", "cyber_dark")
    c = THEMES.get(theme_name, {
        "modal_bg": "#06090e",
        "card_bg": "#101624",
        "card_border": "#1e293b",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "accent_cyan": "#00e5ff",
        "accent_green": "#38ef7d",
        "btn_bg": "#1e293b",
        "btn_hover": "#334155",
        "sidebar_bg": "#0b0f19",
        "entry_bg": "#0b101b"
    })

    sat = tk.Toplevel(parent)
    sat.title("Satellite — Friends & Social Telemetry Hub")
    sat.geometry("860x580")
    sat.minsize(760, 500)
    sat.configure(bg=c["modal_bg"])
    sat.transient(parent)

    # Top Header
    m_head = tk.Frame(sat, bg=c["card_bg"], padx=18, pady=12, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    m_head.pack(fill="x")

    btn_close = tk.Button(m_head, text="✖ Close", font=("Segoe UI", 9, "bold"), bg=c["btn_bg"], fg=c["text_primary"], activebackground=c["btn_hover"], bd=0, padx=12, pady=4, cursor="hand2", command=sat.destroy)
    btn_close.pack(side="right", padx=(8, 0))

    lbl_t = tk.Label(m_head, text="🛰️ Satellite Social & Telemetry Hub", font=("Segoe UI", 12, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], anchor="w")
    lbl_t.pack(side="left", fill="x", expand=True)

    # Main Body with Left Friends List & Right Chat/Telemetry Pane
    body = tk.Frame(sat, bg=c["modal_bg"])
    body.pack(fill="both", expand=True)

    # Left Friends Sidebar (260px)
    f_side = tk.Frame(body, bg=c["sidebar_bg"], width=260, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=10, pady=10)
    f_side.pack(side="left", fill="y")
    f_side.pack_propagate(False)

    lbl_f_t = tk.Label(f_side, text="👥 Online & Friends", font=("Segoe UI", 9, "bold"), bg=c["sidebar_bg"], fg=c["text_primary"])
    lbl_f_t.pack(anchor="w", pady=(0, 8))

    friends_canvas = tk.Canvas(f_side, bg=c["sidebar_bg"], bd=0, highlightthickness=0)
    friends_scroll = tk.Scrollbar(f_side, orient="vertical", command=friends_canvas.yview)
    friends_box = tk.Frame(friends_canvas, bg=c["sidebar_bg"])

    friends_box.bind("<Configure>", lambda e: friends_canvas.configure(scrollregion=friends_canvas.bbox("all")))
    friends_win = friends_canvas.create_window((0, 0), window=friends_box, anchor="nw")
    friends_canvas.bind("<Configure>", lambda e: friends_canvas.itemconfig(friends_win, width=e.width))
    friends_canvas.configure(yscrollcommand=friends_scroll.set)

    friends_canvas.pack(side="left", fill="both", expand=True)
    friends_scroll.pack(side="right", fill="y")

    # Right Chat & Telemetry Pane
    f_chat = tk.Frame(body, bg=c["modal_bg"], padx=16, pady=12)
    f_chat.pack(side="right", fill="both", expand=True)

    # Active Friend Header
    chat_header = tk.Frame(f_chat, bg=c["card_bg"], padx=14, pady=10, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    chat_header.pack(fill="x", pady=(0, 10))

    lbl_active_friend = tk.Label(chat_header, text="Select a friend to begin messaging", font=("Segoe UI", 11, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], anchor="w")
    lbl_active_friend.pack(side="left", fill="x", expand=True)

    btn_invite = tk.Button(chat_header, text="🎮 Invite to Game", font=("Segoe UI", 8, "bold"), bg=c["accent_green"], fg="#06090e", bd=0, padx=10, pady=4, cursor="hand2", command=lambda: messagebox.showinfo("Game Invite", "Dispatched in-game party invitation link!"))
    btn_invite.pack(side="right")

    # Message Stream History
    msg_box = tk.Frame(f_chat, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=10, pady=10)
    msg_box.pack(fill="both", expand=True, pady=(0, 10))

    txt_messages = tk.Text(msg_box, bg=c["card_bg"], fg=c["text_primary"], font=("Segoe UI", 9), bd=0, wrap="word", state="disabled")
    txt_scroll = tk.Scrollbar(msg_box, orient="vertical", command=txt_messages.yview)
    txt_messages.configure(yscrollcommand=txt_scroll.set)
    txt_messages.pack(side="left", fill="both", expand=True)
    txt_scroll.pack(side="right", fill="y")

    # Bottom Input Bar
    in_bar = tk.Frame(f_chat, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=10, pady=8)
    in_bar.pack(fill="x")

    ent_msg = tk.Entry(in_bar, font=("Segoe UI", 10), bg=c["entry_bg"], fg=c["text_primary"], insertbackground=c["accent_cyan"], bd=1, relief="solid")
    ent_msg.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def append_message(sender, text, color=None):
        txt_messages.configure(state="normal")
        tag_name = f"tag_{sender}"
        txt_messages.tag_config(tag_name, foreground=color or c["accent_cyan"], font=("Segoe UI", 9, "bold"))
        txt_messages.insert(tk.END, f"[{sender}]: ", tag_name)
        txt_messages.insert(tk.END, f"{text}\n")
        txt_messages.see(tk.END)
        txt_messages.configure(state="disabled")

    def send_current_msg():
        t = ent_msg.get().strip()
        if not t: return
        append_message("You", t, c["accent_green"])
        ent_msg.delete(0, tk.END)
        # Simulated friendly auto-reply after 1.2s
        sat.after(1200, lambda: append_message("Satellite Bot", "Transmission routed via mesh network with 22ms latency."))

    ent_msg.bind("<Return>", lambda e: send_current_msg())

    btn_send = tk.Button(in_bar, text="Send ➔", font=("Segoe UI", 9, "bold"), bg=c["accent_cyan"], fg="#06090e", bd=0, padx=14, pady=5, cursor="hand2", command=send_current_msg)
    btn_send.pack(side="right")

    # Populate Friends List
    friends = get_friends_list()
    for f_info in friends:
        f_name = f_info.get("name", "Friend")
        f_flag = f_info.get("flag", "🌐")
        f_seen = f_info.get("last_seen", "Online")

        f_row = tk.Frame(friends_box, bg=c["card_bg"], padx=8, pady=8, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], cursor="hand2")
        f_row.pack(fill="x", padx=4, pady=3)

        tk.Label(f_row, text="👤", font=("Segoe UI", 11), bg=c["card_bg"], fg=c["accent_cyan"]).pack(side="left", padx=(0, 6))
        col = tk.Frame(f_row, bg=c["card_bg"])
        col.pack(side="left", fill="x", expand=True)

        tk.Label(col, text=f"{f_name} {f_flag}", font=("Segoe UI", 8, "bold"), bg=c["card_bg"], fg=c["text_primary"], anchor="w").pack(fill="x")
        tk.Label(col, text=f_seen, font=("Segoe UI", 7), bg=c["card_bg"], fg=c["text_secondary"], anchor="w").pack(fill="x")

        def select_friend(name=f_name, seen=f_seen):
            lbl_active_friend.config(text=f"💬 Chatting with {name} • {seen}")
            txt_messages.configure(state="normal")
            txt_messages.delete("1.0", tk.END)
            txt_messages.configure(state="disabled")
            append_message("System", f"Established peer encrypted channel with {name} (Satellite Node: EU-Central).", c["accent_cyan"])

        f_row.bind("<Button-1>", lambda e, n=f_name, s=f_seen: select_friend(n, s))
        for child in f_row.winfo_children():
            child.bind("<Button-1>", lambda e, n=f_name, s=f_seen: select_friend(n, s))

    if friends:
        select_friend(friends[0]["name"], friends[0]["last_seen"])
