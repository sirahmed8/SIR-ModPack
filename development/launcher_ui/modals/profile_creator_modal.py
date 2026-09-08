import os
import zipfile
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog
from sir_core.config import THEMES, INSTANCES_DIR
from sir_core.launcher.instance_manager import create_instance

def open_create_profile_choice_modal(parent):
    theme_name = getattr(parent, "current_theme", "cyber_dark")
    c = THEMES.get(theme_name, {
        "modal_bg": "#06090e",
        "card_bg": "#101624",
        "card_border": "#1e293b",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "accent_cyan": "#00e5ff",
        "accent_green": "#38ef7d",
        "accent_purple": "#a855f7",
        "btn_bg": "#1e293b",
        "btn_hover": "#334155"
    })

    modal = tk.Toplevel(parent)
    modal.title("Create or Import Profile — SIR Launcher")
    modal.geometry("820x440")
    modal.minsize(720, 400)
    modal.configure(bg=c["modal_bg"])
    modal.transient(parent)

    m_head = tk.Frame(modal, bg=c["card_bg"], padx=18, pady=12, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
    m_head.pack(fill="x")

    btn_close = tk.Button(m_head, text="✖ Close", font=("Segoe UI", 9, "bold"), bg=c["btn_bg"], fg=c["text_primary"], activebackground=c["btn_hover"], bd=0, padx=12, pady=4, cursor="hand2", command=modal.destroy)
    btn_close.pack(side="right", padx=(8, 0))

    lbl_t = tk.Label(m_head, text="➕ Create or Import Minecraft Profile", font=("Segoe UI", 12, "bold"), bg=c["card_bg"], fg=c["accent_cyan"], anchor="w")
    lbl_t.pack(side="left", fill="x", expand=True)

    body = tk.Frame(modal, bg=c["modal_bg"], padx=20, pady=20)
    body.pack(fill="both", expand=True)

    def on_create_new():
        modal.destroy()
        if hasattr(parent, "open_create_instance_modal"):
            parent.open_create_instance_modal()

    def on_import_archive():
        filepath = filedialog.askopenfilename(
            parent=modal,
            title="Select Instance Archive or Modpack (.zip, .mrpack)",
            filetypes=[("Minecraft Archive or Modpack", "*.zip;*.mrpack"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        try:
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            clean_name = "".join(ch for ch in base_name if ch.isalnum() or ch in "._- ")
            dest_dir = os.path.join(INSTANCES_DIR, clean_name)
            os.makedirs(dest_dir, exist_ok=True)
            with zipfile.ZipFile(filepath, 'r') as zf:
                zf.extractall(dest_dir)
            modal.destroy()
            if hasattr(parent, "load_instances"):
                parent.load_instances()
            messagebox.showinfo("Import Complete", f"Successfully imported instance: {clean_name}")
        except Exception as e:
            messagebox.showerror("Import Failed", f"Could not extract archive:\n{e}")

    def on_migrate_launchers():
        # Scan for existing launcher profile directories
        found_sources = []
        prism_dir = os.path.expandvars(r"%APPDATA%\PrismLauncher\instances")
        if os.path.exists(prism_dir):
            for d in os.listdir(prism_dir):
                full_p = os.path.join(prism_dir, d)
                if os.path.isdir(full_p):
                    found_sources.append(("PrismLauncher", d, full_p))

        lunar_dir = os.path.expanduser(r"~/.lunarclient/offline/multiver")
        if os.path.exists(lunar_dir):
            for d in os.listdir(lunar_dir):
                full_p = os.path.join(lunar_dir, d)
                if os.path.isdir(full_p):
                    found_sources.append(("Lunar Client", d, full_p))

        vanilla_dir = os.path.expandvars(r"%APPDATA%\.minecraft\versions")
        if os.path.exists(vanilla_dir):
            for d in os.listdir(vanilla_dir):
                full_p = os.path.join(vanilla_dir, d)
                if os.path.isdir(full_p):
                    found_sources.append(("Vanilla .minecraft", d, full_p))

        if not found_sources:
            messagebox.showinfo("Migration Scanner", "No existing third-party launcher profiles detected in standard directories.")
            return

        # Migration selection sub-dialog
        sub = tk.Toplevel(modal)
        sub.title("Migrate Profiles from Other Launchers")
        sub.geometry("560x420")
        sub.configure(bg=c["modal_bg"])
        sub.transient(modal)

        tk.Label(sub, text="Detected Launcher Profiles on this PC:", font=("Segoe UI", 10, "bold"), bg=c["modal_bg"], fg=c["accent_cyan"]).pack(anchor="w", padx=16, pady=(14, 8))

        sub_list = tk.Frame(sub, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
        sub_list.pack(fill="both", expand=True, padx=16, pady=4)

        canvas = tk.Canvas(sub_list, bg=c["card_bg"], bd=0, highlightthickness=0)
        scroll = tk.Scrollbar(sub_list, orient="vertical", command=canvas.yview)
        sub_box = tk.Frame(canvas, bg=c["card_bg"])

        sub_box.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sub_box, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for l_name, p_name, p_path in found_sources:
            row = tk.Frame(sub_box, bg=c["card_bg"], padx=10, pady=8, bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"])
            row.pack(fill="x", padx=6, pady=4)

            tk.Label(row, text=f"{p_name}", font=("Segoe UI", 9, "bold"), bg=c["card_bg"], fg=c["text_primary"], anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(row, text=f"Source: {l_name}", font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_secondary"]).pack(side="left", padx=8)

            def do_copy(src=p_path, name=p_name):
                dest = os.path.join(INSTANCES_DIR, f"imported_{name}")
                try:
                    if os.path.exists(dest):
                        messagebox.showwarning("Exists", f"Instance 'imported_{name}' already exists.")
                        return
                    shutil.copytree(src, dest)
                    sub.destroy()
                    modal.destroy()
                    if hasattr(parent, "load_instances"):
                        parent.load_instances()
                    messagebox.showinfo("Migration Complete", f"Successfully migrated {name} into SIR Launcher!")
                except Exception as ex:
                    messagebox.showerror("Error", f"Failed to migrate profile:\n{ex}")

            tk.Button(row, text="Import ➔", font=("Segoe UI", 8, "bold"), bg=c["accent_green"], fg="#06090e", bd=0, padx=10, pady=3, cursor="hand2", command=do_copy).pack(side="right")

    cards = [
        ("✨", "Create New Profile", "Configure a custom Minecraft version with loader presets.", c["accent_cyan"], on_create_new),
        ("📦", "Import from Archive", "Import an instance zip, folder, or Modrinth .mrpack archive.", c["accent_green"], on_import_archive),
        ("🔄", "From other Launchers", "Migrate existing profiles from Prism, Lunar, and Vanilla.", c["accent_purple"], on_migrate_launchers)
    ]

    for icon_sym, title, desc, col, cmd in cards:
        card = tk.Frame(body, bg=c["card_bg"], bd=1, relief="solid", highlightthickness=1, highlightbackground=c["card_border"], padx=16, pady=16, cursor="hand2")
        card.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(card, text=icon_sym, font=("Segoe UI Emoji", 26), bg=c["card_bg"], fg=col).pack(anchor="w")
        tk.Label(card, text=title, font=("Segoe UI", 11, "bold"), bg=c["card_bg"], fg=c["text_primary"]).pack(anchor="w", pady=(8, 4))
        tk.Label(card, text=desc, font=("Segoe UI", 8), bg=c["card_bg"], fg=c["text_secondary"], wraplength=190, justify="left").pack(anchor="w", fill="both", expand=True)
        tk.Button(card, text="Select ➔", font=("Segoe UI", 8, "bold"), bg=col, fg="#06090e", bd=0, padx=14, pady=6, cursor="hand2", command=cmd).pack(anchor="w", pady=(10, 0))

