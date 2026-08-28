import tkinter as tk
from sir_core.config import THEMES
from sir_core.social.satellite_hub import get_friends_list

def open_satellite_modal(parent):
    c = THEMES[parent.current_theme]
    sat = tk.Toplevel(parent)
    sat.title("Satellite — Friends & Social Hub")
    sat.geometry("780x540")
    sat.minsize(700, 480)
    sat.configure(bg=c["modal_bg"])
    sat.transient(parent)

    m_head = tk.Frame(sat, bg=c["card_bg"], padx=16, pady=10, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    m_head.pack(fill="x")

    btn_close = tk.Button(m_head, text="✖ Close", font=("Segoe UI", 9, "bold"), bg=c["btn_bg"], fg=c["text_primary"], activebackground=c["btn_hover"], bd=0, padx=12, pady=4, cursor="hand2", command=sat.destroy)
    btn_close.pack(side="right", padx=(8, 0))

    lbl_t = tk.Label(m_head, text="🛰️ Satellite Social Hub", font=("Segoe UI", 11, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], anchor="w")
    lbl_t.pack(side="left", fill="x", expand=True)

    body = tk.Frame(sat, bg=c["modal_bg"])
    body.pack(fill="both", expand=True)

    f_side = tk.Frame(body, bg=c["sidebar_bg"], width=260, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=10, pady=10)
    f_side.pack(side="left", fill="y")
    f_side.pack_propagate(False)

    lbl_f_t = tk.Label(f_side, text="👥 Online & Friends", font=("Segoe UI", 9, "bold"), bg=c["sidebar_bg"], fg=c["text_primary"])
    lbl_f_t.pack(anchor="w", pady=(0, 6))

    friends = get_friends_list()
    for f_info in friends:
        f_row = tk.Frame(f_side, bg=c["card_bg"], padx=8, pady=6, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], cursor="hand2")
        f_row.pack(fill="x", pady=2)
        tk.Label(f_row, text="👤", font=("Segoe UI", 11), bg=c["card_bg"], fg=c["accent_cyan"]).pack(side="left", padx=(0, 6))
        col = tk.Frame(f_row, bg=c["card_bg"])
        col.pack(side="left", fill="x", expand=True)
        tk.Label(col, text=f"{f_info['name']} {f_info['flag']}", font=("Segoe UI", 8, "bold"), bg=c["card_bg"], fg=c["text_primary"], anchor="w").pack(fill="x")
        tk.Label(col, text=f_info["last_seen"], font=("Segoe UI", 7), bg=c["card_bg"], fg=c["text_secondary"], anchor="w").pack(fill="x")
