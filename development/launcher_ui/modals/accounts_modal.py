import tkinter as tk
from tkinter import messagebox
import threading
from sir_core.config import THEMES
from sir_core.auth.offline_manager import load_accounts, save_accounts, add_offline_account
from sir_core.auth.microsoft_oauth import start_microsoft_login_flow

def open_accounts_manager_modal(parent):
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

    modal = tk.Toplevel(parent)
    modal.title("Account & Identity Studio — SIR Launcher")
    modal.geometry("640x560")
    modal.minsize(560, 480)
    modal.configure(bg=c["modal_bg"])
    modal.transient(parent)

    # Top Header
    m_head = tk.Frame(modal, bg=c["card_bg"], padx=18, pady=12, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    m_head.pack(fill="x")

    btn_close = tk.Button(m_head, text="✖ Close", font=("Segoe UI", 9, "bold"), bg=c["btn_bg"], fg=c["text_primary"], activebackground=c["btn_hover"], bd=0, padx=12, pady=4, cursor="hand2", command=modal.destroy)
    btn_close.pack(side="right", padx=(8, 0))

    lbl_t = tk.Label(m_head, text="👤 Account & Profile Studio", font=("Segoe UI", 12, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], anchor="w")
    lbl_t.pack(side="left", fill="x", expand=True)

    body = tk.Frame(modal, bg=c["modal_bg"], padx=18, pady=14)
    body.pack(fill="both", expand=True)

    # Subtitle
    tk.Label(body, text="Manage official Microsoft accounts, offline profiles, and cloud-synced identities.", font=("Segoe UI", 8), bg=c["modal_bg"], fg=c["text_secondary"]).pack(anchor="w", pady=(0, 10))

    # Accounts List Container
    list_frame = tk.Frame(body, bg=c["modal_bg"])
    list_frame.pack(fill="both", expand=True, pady=(0, 12))

    canvas = tk.Canvas(list_frame, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    scroll_content = tk.Frame(canvas, bg=c["card_bg"])

    scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=scroll_content, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def render_accounts_list():
        for widget in scroll_content.winfo_children():
            widget.destroy()

        accounts = load_accounts()
        if not accounts:
            accounts = [{"name": "Player", "type": "Offline", "active": True}]

        for acc in accounts:
            acc_name = acc.get("name", "Player")
            acc_type = acc.get("type", "Offline")
            is_active = acc.get("active", False)

            row = tk.Frame(scroll_content, bg=c["sidebar_bg"] if not is_active else "#0e1e2d", padx=12, pady=10, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["accent_cyan"] if is_active else c["card_border"])
            row.pack(fill="x", padx=6, pady=4)

            # Avatar Icon
            icon_char = "🟢" if is_active else "⚪"
            tk.Label(row, text=icon_char, font=("Segoe UI", 10), bg=row["bg"]).pack(side="left", padx=(0, 8))

            # Name & Type
            col = tk.Frame(row, bg=row["bg"])
            col.pack(side="left", fill="x", expand=True)

            name_lbl = tk.Label(col, text=acc_name, font=("Segoe UI", 10, "bold"), bg=row["bg"], fg=c["accent_cyan"] if is_active else c["text_primary"], anchor="w")
            name_lbl.pack(fill="x")

            type_desc = f"{acc_type} Profile" + (" • Active Selected" if is_active else "")
            tk.Label(col, text=type_desc, font=("Segoe UI", 8), bg=row["bg"], fg=c["accent_green"] if is_active else c["text_secondary"], anchor="w").pack(fill="x")

            # Actions
            btn_box = tk.Frame(row, bg=row["bg"])
            btn_box.pack(side="right")

            if not is_active:
                def make_active(name=acc_name):
                    save_accounts(load_accounts(), active_account_name=name)
                    if hasattr(parent, "active_account"):
                        parent.active_account = name
                    if hasattr(parent, "update_active_account_ui"):
                        parent.update_active_account_ui()
                    render_accounts_list()

                btn_select = tk.Button(btn_box, text="Activate", font=("Segoe UI", 8, "bold"), bg=c["accent_cyan"], fg="#06090e", bd=0, padx=10, pady=3, cursor="hand2", command=make_active)
                btn_select.pack(side="left", padx=4)

            if len(accounts) > 1:
                def delete_acc(name=acc_name):
                    curr = [a for a in load_accounts() if a.get("name") != name]
                    save_accounts(curr, active_account_name=curr[0]["name"] if curr else "Player")
                    if hasattr(parent, "update_active_account_ui"):
                        parent.update_active_account_ui()
                    render_accounts_list()

                btn_del = tk.Button(btn_box, text="🗑", font=("Segoe UI", 9), bg="#451a1a", fg="#f87171", bd=0, padx=8, pady=2, cursor="hand2", command=delete_acc)
                btn_del.pack(side="left", padx=2)

    render_accounts_list()

    # Add Account Controls Bar
    control_box = tk.Frame(body, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=14, pady=12)
    control_box.pack(fill="x")

    tk.Label(control_box, text="Add New Profile:", font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"]).pack(anchor="w", pady=(0, 6))

    add_row = tk.Frame(control_box, bg=c["card_bg"])
    add_row.pack(fill="x", pady=(0, 8))

    ent_new_name = tk.Entry(add_row, font=("Segoe UI", 9), bg=c["entry_bg"], fg=c["text_primary"], insertbackground=c["accent_cyan"], bd=1, relief="solid")
    ent_new_name.insert(0, "NewPlayer")
    ent_new_name.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def on_add_offline():
        val = ent_new_name.get().strip()
        if not val:
            messagebox.showwarning("Validation", "Please enter a valid player username.")
            return
        if len(val) < 3 or len(val) > 16:
            messagebox.showwarning("Validation", "Username must be between 3 and 16 characters.")
            return
        add_offline_account(val)
        if hasattr(parent, "update_active_account_ui"):
            parent.update_active_account_ui()
        ent_new_name.delete(0, tk.END)
        ent_new_name.insert(0, "")
        render_accounts_list()

    btn_add_offline = tk.Button(add_row, text="➕ Add Offline Profile", font=("Segoe UI", 9, "bold"), bg=c["accent_cyan"], fg="#06090e", bd=0, padx=12, pady=5, cursor="hand2", command=on_add_offline)
    btn_add_offline.pack(side="right")

    # Bottom Actions Bar (Microsoft & Web Sync)
    bot_row = tk.Frame(control_box, bg=c["card_bg"])
    bot_row.pack(fill="x")

    def on_ms_login():
        def _flow():
            res, err = start_microsoft_login_flow()
            if res:
                save_accounts(load_accounts(), active_account_name=res.get("name", "Player"))
                modal.after(0, lambda: [render_accounts_list(), messagebox.showinfo("Success", f"Signed in as {res.get('name')}!")])
            elif err:
                modal.after(0, lambda: messagebox.showerror("Microsoft Auth Error", str(err)))
        threading.Thread(target=_flow, daemon=True).start()

    btn_ms = tk.Button(bot_row, text="🛡️ Sign in with Microsoft (Official)", font=("Segoe UI", 8, "bold"), bg="#065f46", fg="#a7f3d0", bd=0, padx=12, pady=5, cursor="hand2", command=on_ms_login)
    btn_ms.pack(side="left", padx=(0, 8))

    def on_web_sync():
        try:
            from .web_sync_modal import open_sir_web_account_sync_modal
            open_sir_web_account_sync_modal(parent)
        except Exception:
            pass

    btn_sync = tk.Button(bot_row, text="🌐 Cloud Web Sync", font=("Segoe UI", 8, "bold"), bg="#1e1b4b", fg="#c7d2fe", bd=0, padx=12, pady=5, cursor="hand2", command=on_web_sync)
    btn_sync.pack(side="left")
