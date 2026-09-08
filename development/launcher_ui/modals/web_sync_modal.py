import tkinter as tk
from tkinter import messagebox
import webbrowser
import threading
from sir_core.config import THEMES
from sir_core.auth.firebase_web_sync import sync_profile_by_ign_or_email, sync_profile_by_code

def open_sir_web_account_sync_modal(parent):
    c = THEMES[parent.current_theme]
    modal = tk.Toplevel(parent)
    modal.title("Link Claimed SIR Web Account (Firebase)")
    modal.geometry("560x520")
    modal.minsize(500, 460)
    modal.configure(bg=c["modal_bg"])
    modal.transient(parent)

    m_head = tk.Frame(modal, bg=c["card_bg"], padx=16, pady=10, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    m_head.pack(fill="x")

    btn_close = tk.Button(m_head, text="✖ Close", font=("Segoe UI", 9, "bold"), bg=c["btn_bg"], fg=c["text_primary"], activebackground=c["btn_hover"], bd=0, padx=12, pady=4, cursor="hand2", command=modal.destroy)
    btn_close.pack(side="right", padx=(8, 0))

    lbl_t = tk.Label(m_head, text="🌐 Link Claimed SIR Web Account", font=("Segoe UI", 11, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], anchor="w")
    lbl_t.pack(side="left", fill="x", expand=True)

    body = tk.Frame(modal, bg=c["modal_bg"], padx=20, pady=16)
    body.pack(fill="both", expand=True)

    # Method 1
    m1_card = tk.Frame(body, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=16, pady=12)
    m1_card.pack(fill="x", pady=(0, 10))

    lbl_m1_t = tk.Label(m1_card, text="1. Search by Claimed In-Game Name or Email:", font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"])
    lbl_m1_t.pack(anchor="w")

    row_m1 = tk.Frame(m1_card, bg=c["card_bg"])
    row_m1.pack(fill="x", pady=(8, 4))
    ent_ign = tk.Entry(row_m1, font=("Segoe UI", 10), bg=c["entry_bg"], fg=c["text_primary"], insertbackground=c["accent_cyan"], bd=1, relief="solid")
    ent_ign.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def do_ign_sync():
        q = ent_ign.get().strip()
        if not q: return
        def _fetch():
            profile, err = sync_profile_by_ign_or_email(q)
            if profile:
                parent.add_and_activate_claimed_profile(profile["ign"], profile["skinUrl"], profile["type"], profile["model"])
                modal.destroy()
            else:
                modal.after(0, lambda: messagebox.showerror("Sync Failed", err))
        threading.Thread(target=_fetch, daemon=True).start()

    btn_m1 = tk.Button(row_m1, text="🔍 Sync Profile", font=("Segoe UI", 9, "bold"), bg=c["accent_cyan"], fg="#06090e", bd=0, padx=14, pady=5, cursor="hand2", command=do_ign_sync)
    btn_m1.pack(side="right")

    # Method 2
    m2_card = tk.Frame(body, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=16, pady=12)
    m2_card.pack(fill="x", pady=(0, 10))

    lbl_m2_t = tk.Label(m2_card, text="2. Enter 6-Digit Web Sync Code:", font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"])
    lbl_m2_t.pack(anchor="w")

    row_m2 = tk.Frame(m2_card, bg=c["card_bg"])
    row_m2.pack(fill="x", pady=(8, 4))
    ent_code = tk.Entry(row_m2, font=("Segoe UI", 10, "bold"), bg=c["entry_bg"], fg=c["accent_green"], insertbackground=c["accent_green"], bd=1, relief="solid", width=12)
    ent_code.pack(side="left", padx=(0, 8))

    def do_code_sync():
        code = ent_code.get().strip()
        if not code: return
        def _fetch():
            profile, err = sync_profile_by_code(code)
            if profile:
                parent.add_and_activate_claimed_profile(profile["ign"], profile["skinUrl"], profile["type"], profile["model"])
                modal.destroy()
            else:
                modal.after(0, lambda: messagebox.showerror("Code Sync Failed", err))
        threading.Thread(target=_fetch, daemon=True).start()

    btn_m2 = tk.Button(row_m2, text="🔑 Link Code", font=("Segoe UI", 9, "bold"), bg=c["accent_green"], fg="#06090e", bd=0, padx=14, pady=5, cursor="hand2", command=do_code_sync)
    btn_m2.pack(side="left")

    # Method 3
    m3_card = tk.Frame(body, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=16, pady=12)
    m3_card.pack(fill="x")

    lbl_m3_t = tk.Label(m3_card, text="3. 1-Click Instant Web Bridge:", font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"])
    lbl_m3_t.pack(anchor="w")

    def open_site_bridge():
        webbrowser.open("http://localhost:3000/#account")
        messagebox.showinfo("Web Bridge Active", "🌐 Browser opened to SIR Account Studio!\n\nClick '1-Click Send to Launcher' on the website to sync instantly.")

    btn_open_web = tk.Button(m3_card, text="🌐 Open SIR Web Studio (http://localhost:3000/#account)", font=("Segoe UI", 9, "bold"), bg=c["btn_bg"], fg=c["accent_cyan"], activebackground=c["btn_hover"], bd=0, padx=14, pady=6, cursor="hand2", command=open_site_bridge)
    btn_open_web.pack(fill="x", pady=(8, 0))
