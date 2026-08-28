import tkinter as tk
from tkinter import messagebox
from sir_core.config import THEMES
from sir_core.launcher.instance_manager import create_instance

def open_create_profile_choice_modal(parent):
    c = THEMES[parent.current_theme]
    modal = tk.Toplevel(parent)
    modal.title("Create or Import Profile")
    modal.geometry("780x420")
    modal.minsize(700, 380)
    modal.configure(bg=c["modal_bg"])
    modal.transient(parent)

    m_head = tk.Frame(modal, bg=c["card_bg"], padx=16, pady=10, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    m_head.pack(fill="x")

    btn_close = tk.Button(m_head, text="✖ Close", font=("Segoe UI", 9, "bold"), bg=c["btn_bg"], fg=c["text_primary"], activebackground=c["btn_hover"], bd=0, padx=12, pady=4, cursor="hand2", command=modal.destroy)
    btn_close.pack(side="right", padx=(8, 0))

    lbl_t = tk.Label(m_head, text="➕ Create or Import Minecraft Profile", font=("Segoe UI", 11, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], anchor="w")
    lbl_t.pack(side="left", fill="x", expand=True)

    body = tk.Frame(modal, bg=c["modal_bg"], padx=20, pady=20)
    body.pack(fill="both", expand=True)

    cards = [
        ("✨", "Create New Profile", "Configure a custom Minecraft version.", c["accent_cyan"], lambda: [modal.destroy(), parent.open_create_instance_modal()]),
        ("📦", "Import from Archive", "Import an instance zip, folder, or Modrinth pack.", c["accent_green"], lambda: [modal.destroy(), messagebox.showinfo("Import Profile", "Select any .zip or folder to import into SIR Launcher.")]),
        ("🔄", "From other Launchers", "Migrate existing profiles from Prism, Lunar, CurseForge, Vanilla, & Badlion!", c["accent_purple"], lambda: [modal.destroy(), messagebox.showinfo("Migration Wizard", "Scanning system for existing launcher instances...")])
    ]

    for icon_sym, title, desc, col, cmd in cards:
        card = tk.Frame(body, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=16, pady=16, cursor="hand2")
        card.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(card, text=icon_sym, font=("Segoe UI Emoji", 26), bg=c["card_bg"], fg=col).pack(anchor="w")
        tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), bg=c["card_bg"], fg=c["text_primary"]).pack(anchor="w", pady=(8, 4))
        tk.Label(card, text=desc, font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_secondary"], wraplength=180, justify="left").pack(anchor="w", fill="both", expand=True)
        tk.Button(card, text="Select ➔", font=("Segoe UI", 8, "bold"), bg=col, fg="#06090e", bd=0, padx=12, pady=5, cursor="hand2", command=cmd).pack(anchor="w", pady=(10, 0))
