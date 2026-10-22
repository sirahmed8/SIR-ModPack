#!/usr/bin/env python3
"""Convert generated high-resolution app icon images to multi-resolution Windows .ico and .png formats."""
import os
from PIL import Image

BRAIN_DIR = r"C:\Users\a7med\.gemini\antigravity\brain\c3ee15b0-52dd-4de0-ac08-fa5eb2c02120"
PROJECT_DIR = r"D:\Projects\SIR ModPack"
ICONS_DIR = os.path.join(PROJECT_DIR, "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

# Also ensure directories in public_repo, website-next, etc. exist
PUBLIC_REPO_ICONS = os.path.join(PROJECT_DIR, "public_repo", "icons")
WEBSITE_ICONS = os.path.join(PROJECT_DIR, "website-next", "public", "icons")
os.makedirs(PUBLIC_REPO_ICONS, exist_ok=True)
os.makedirs(WEBSITE_ICONS, exist_ok=True)

ICON_MAPPINGS = [
    {
        "src": os.path.join(BRAIN_DIR, "sir_launcher_icon_1790892349114.jpg"),
        "base_name": "SIR_Launcher_Icon",
        "description": "SIR Launcher (Game Launcher & PvP Client)"
    },
    {
        "src": os.path.join(BRAIN_DIR, "sir_server_icon_1790892398909.jpg"),
        "base_name": "SIR_Server_Manager_Icon",
        "description": "SIR Server Manager (Server Orchestration & Hosting)"
    },
    {
        "src": os.path.join(BRAIN_DIR, "sir_web_icon_1790892453814.jpg"),
        "base_name": "SIR_Web_Portal_Icon",
        "description": "SIR ModPack Web Portal (Cloud & Web Hub)"
    },
    {
        "src": os.path.join(BRAIN_DIR, "sir_stop_icon_1790892532517.jpg"),
        "base_name": "SIR_Stop_Portal_Icon",
        "description": "Stop SIR ModPack Web Portal (Process Shutdown Utility)"
    }
]

ICON_SIZES = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

def convert_all():
    print("=== SIR ECOSYSTEM APP ICON GENERATOR ===")
    for item in ICON_MAPPINGS:
        src = item["src"]
        base = item["base_name"]
        desc = item["description"]
        if not os.path.isfile(src):
            print(f"ERROR: Source file missing: {src}")
            continue

        print(f"[*] Processing {base} ({desc})...")
        with Image.open(src) as img:
            rgba_img = img.convert("RGBA")
            
            # Save master PNG
            master_png = os.path.join(ICONS_DIR, f"{base}.png")
            rgba_img.save(master_png, format="PNG")
            
            # Save multi-size .ico
            master_ico = os.path.join(ICONS_DIR, f"{base}.ico")
            rgba_img.save(master_ico, format="ICO", sizes=ICON_SIZES)
            print(f"  -> Generated {master_ico} ({os.path.getsize(master_ico)} bytes)")

            # Copy to public_repo/icons and website-next/public/icons
            import shutil
            shutil.copy2(master_ico, os.path.join(PUBLIC_REPO_ICONS, f"{base}.ico"))
            shutil.copy2(master_png, os.path.join(PUBLIC_REPO_ICONS, f"{base}.png"))
            shutil.copy2(master_ico, os.path.join(WEBSITE_ICONS, f"{base}.ico"))
            shutil.copy2(master_png, os.path.join(WEBSITE_ICONS, f"{base}.png"))

    # Also copy SIR_Launcher_Icon.ico into SIR Launcher folder
    launcher_dir = os.path.join(PROJECT_DIR, "SIR Launcher")
    if os.path.isdir(launcher_dir):
        import shutil
        shutil.copy2(os.path.join(ICONS_DIR, "SIR_Launcher_Icon.ico"), os.path.join(launcher_dir, "SIR_Launcher_Icon.ico"))

    print("[+] All ecosystem app icons generated and synchronized successfully!")

if __name__ == "__main__":
    convert_all()
