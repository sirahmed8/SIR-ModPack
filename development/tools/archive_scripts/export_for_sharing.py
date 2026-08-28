#!/usr/bin/env python3
"""
export_for_sharing.py

Creates a clean shareable package of the Aetheris modpack for your friend.
Outputs to D:\mods\AetherisShare\

The package contains:
- 3 profile folders (Visual, Balanced, Legacy)
- The Aetheris shader (already in shaderpacks as .zip)
- The resource pack ZIPs
- A README with install instructions
- An auto-install script for Windows
"""
import os, shutil, zipfile, json, time

OUT_DIR = r"D:\AetherisShare"
LC_PROFILES = r"C:\Users\a7med\.lunarclient\profiles"
RP_DIR = r"D:\resource pack"
SHADER_SRC = r"D:\shader\Aetheris_Shader_Pack"

PROFILES = {
    "aetheris-ultimate-modern-visual-26.2": "Visual (26.2) — Maximum quality",
    "aetheris-ultimate-modern-balanced-26.2": "Balanced (26.2) — Best FPS/quality ratio",
    "aetheris-ultimate-legacy-1.8.9": "Legacy PvP (1.8.9) — Max FPS for PvP",
}

# Skip files that are user-specific or world saves
SKIP_PATTERNS = [
    "saves", "logs", "crash-reports", ".bak",
    "screenshots", "replay_recordings",
    "mods-optional-disabled",  # user's own disabled mods folder
]

def should_skip(path):
    for pat in SKIP_PATTERNS:
        if pat in path.replace("\\", "/").lower():
            return True
    return False

def copy_tree_filtered(src, dst):
    """Copy directory tree skipping saves/logs/etc."""
    total = 0
    for root, dirs, files in os.walk(src):
        rel_root = os.path.relpath(root, src)
        if should_skip(rel_root):
            dirs.clear()
            continue
        dst_root = os.path.join(dst, rel_root)
        os.makedirs(dst_root, exist_ok=True)
        for f in files:
            if should_skip(f):
                continue
            src_f = os.path.join(root, f)
            dst_f = os.path.join(dst_root, f)
            shutil.copy2(src_f, dst_f)
            total += os.path.getsize(src_f)
    return total

print("=" * 60)
print("  AETHERIS MODPACK — SHARE PACKAGE BUILDER")
print("=" * 60)

# Clean output
if os.path.exists(OUT_DIR):
    shutil.rmtree(OUT_DIR)
os.makedirs(OUT_DIR)

# ── 1. COPY PROFILES ────────────────────────────────────────────
print("\n[1/5] Copying profiles...")
profiles_out = os.path.join(OUT_DIR, "profiles")
os.makedirs(profiles_out)

for folder, desc in PROFILES.items():
    src = os.path.join(LC_PROFILES, folder)
    dst = os.path.join(profiles_out, folder)
    if not os.path.exists(src):
        print(f"  SKIP (not found): {folder}")
        continue
    print(f"  Copying: {folder}")
    size = copy_tree_filtered(src, dst)
    print(f"    → {size/1024/1024:.1f} MB (saves/logs excluded)")

# ── 2. COPY RESOURCE PACKS ──────────────────────────────────────
print("\n[2/5] Copying resource packs...")
rp_out = os.path.join(OUT_DIR, "resourcepacks")
os.makedirs(rp_out)

for rp_name in ["[26.2] Aetheris Ultimate 32x.zip", "[1.8.9] Aetheris Legacy 32x.zip"]:
    rp_path = os.path.join(RP_DIR, rp_name)
    if os.path.exists(rp_path):
        shutil.copy2(rp_path, os.path.join(rp_out, rp_name))
        size = os.path.getsize(rp_path)
        print(f"  Copied: {rp_name} ({size/1024/1024:.1f} MB)")
    else:
        print(f"  NOT FOUND: {rp_name}")

# ── 3. COPY SHADER ──────────────────────────────────────────────
print("\n[3/5] Copying shader...")
# The shader is already a .zip in the profile shaderpacks folder
# Just copy the source dir as a zip
shader_out = os.path.join(OUT_DIR, "shaderpacks")
os.makedirs(shader_out)

shader_zip_src = os.path.join(LC_PROFILES,
    "aetheris-ultimate-modern-visual-26.2", "shaderpacks", "Aetheris_Shader_Pack.zip")

if os.path.exists(shader_zip_src):
    shutil.copy2(shader_zip_src, os.path.join(shader_out, "Aetheris_Shader_Pack.zip"))
    print(f"  Copied: Aetheris_Shader_Pack.zip ({os.path.getsize(shader_zip_src)/1024/1024:.1f} MB)")
elif os.path.exists(SHADER_SRC):
    # ZIP the shader source directory
    shader_zip_dst = os.path.join(shader_out, "Aetheris_Shader_Pack.zip")
    print(f"  Zipping shader source from {SHADER_SRC}...")
    with zipfile.ZipFile(shader_zip_dst, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(SHADER_SRC):
            for f in files:
                fp = os.path.join(root, f)
                arcname = os.path.join("Aetheris_Shader_Pack",
                                       os.path.relpath(fp, SHADER_SRC))
                zf.write(fp, arcname)
    print(f"  Zipped: {os.path.getsize(shader_zip_dst)/1024/1024:.1f} MB")

# ── 4. WRITE AUTO-INSTALL SCRIPT ────────────────────────────────
print("\n[4/5] Writing install script...")
install_bat = """\
@echo off
echo ╔══════════════════════════════════════════════════════╗
echo ║         AETHERIS MODPACK — AUTO INSTALLER            ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo This will install the Aetheris profiles into Lunar Client.
echo Make sure Lunar Client is CLOSED before continuing.
echo.
pause

set LC=%USERPROFILE%\\.lunarclient
set PROFILES=%LC%\\profiles
set APPDATA_MC=%APPDATA%\\.minecraft

echo.
echo [1/3] Installing profiles...

for /d %%P in (profiles\\*) do (
    echo   Installing: %%~nxP
    if not exist "%PROFILES%\\%%~nxP" mkdir "%PROFILES%\\%%~nxP"
    xcopy /E /Y /Q "%%P\\*" "%PROFILES%\\%%~nxP\\"
)
echo   Done!

echo.
echo [2/3] Installing resource packs...
if not exist "%PROFILES%\\aetheris-ultimate-modern-visual-26.2\\resourcepacks" mkdir "%PROFILES%\\aetheris-ultimate-modern-visual-26.2\\resourcepacks"
if not exist "%PROFILES%\\aetheris-ultimate-modern-balanced-26.2\\resourcepacks" mkdir "%PROFILES%\\aetheris-ultimate-modern-balanced-26.2\\resourcepacks"
if not exist "%PROFILES%\\aetheris-ultimate-legacy-1.8.9\\resourcepacks" mkdir "%PROFILES%\\aetheris-ultimate-legacy-1.8.9\\resourcepacks"

copy /Y "resourcepacks\\[26.2] Aetheris Ultimate 32x.zip" "%PROFILES%\\aetheris-ultimate-modern-visual-26.2\\resourcepacks\\"
copy /Y "resourcepacks\\[26.2] Aetheris Ultimate 32x.zip" "%PROFILES%\\aetheris-ultimate-modern-balanced-26.2\\resourcepacks\\"
copy /Y "resourcepacks\\[1.8.9] Aetheris Legacy 32x.zip" "%PROFILES%\\aetheris-ultimate-legacy-1.8.9\\resourcepacks\\"
echo   Done!

echo.
echo [3/3] Installing shader...
if not exist "%PROFILES%\\aetheris-ultimate-modern-visual-26.2\\shaderpacks" mkdir "%PROFILES%\\aetheris-ultimate-modern-visual-26.2\\shaderpacks"
if not exist "%PROFILES%\\aetheris-ultimate-modern-balanced-26.2\\shaderpacks" mkdir "%PROFILES%\\aetheris-ultimate-modern-balanced-26.2\\shaderpacks"
copy /Y "shaderpacks\\Aetheris_Shader_Pack.zip" "%PROFILES%\\aetheris-ultimate-modern-visual-26.2\\shaderpacks\\"
copy /Y "shaderpacks\\Aetheris_Shader_Pack.zip" "%PROFILES%\\aetheris-ultimate-modern-balanced-26.2\\shaderpacks\\"
echo   Done!

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║              INSTALLATION COMPLETE!                  ║
echo ║                                                      ║
echo ║  Open Lunar Client and you will see:                 ║
echo ║  • Aetheris Visual  (26.2) - Maximum quality         ║
echo ║  • Aetheris Balanced (26.2) - Best FPS/quality       ║
echo ║  • Aetheris Legacy PvP (1.8.9) - Max FPS PvP         ║
echo ║                                                      ║
echo ║  Recommended RAM: 8GB in Lunar Client settings       ║
echo ╚══════════════════════════════════════════════════════╝
echo.
pause
"""
with open(os.path.join(OUT_DIR, "INSTALL.bat"), "w") as f:
    f.write(install_bat)
print("  INSTALL.bat created")

# ── 5. WRITE README ─────────────────────────────────────────────
print("\n[5/5] Writing README...")
readme = """\
╔══════════════════════════════════════════════════════════════╗
║              🌌 AETHERIS MODPACK — SHARE PACKAGE            ║
╚══════════════════════════════════════════════════════════════╝

Created for: [Your Bro's Name Here]
Made by: Ahmed's custom Aetheris setup


════════════════ WHAT'S INSIDE ════════════════

  📁 profiles/
     ├── aetheris-ultimate-modern-visual-26.2/   → 🎨 Max quality
     ├── aetheris-ultimate-modern-balanced-26.2/ → ⚖️ Best mix
     └── aetheris-ultimate-legacy-1.8.9/         → 🗡️ PvP 1.8.9

  📁 resourcepacks/
     ├── [26.2] Aetheris Ultimate 32x.zip         → For 26.2 profiles
     └── [1.8.9] Aetheris Legacy 32x.zip          → For 1.8.9 profile

  📁 shaderpacks/
     └── Aetheris_Shader_Pack.zip                 → Custom shader

  📄 INSTALL.bat → Auto-installer (run this!)


════════════════ HOW TO INSTALL ════════════════

  REQUIREMENTS:
  ✓ Lunar Client installed
  ✓ At least 8 GB RAM available for Minecraft
  ✓ NVIDIA GPU (GTX 1060+ or RTX recommended)

  STEPS:
  1. Close Lunar Client completely
  2. Double-click INSTALL.bat
  3. Wait for "INSTALLATION COMPLETE"
  4. Open Lunar Client
  5. You'll see the 3 new profiles!

  In Lunar Client settings → set RAM to 8192 MB


════════════════ PROFILE GUIDE ════════════════

  🌌 VISUAL (26.2)
     Best: Screenshots, exploration, cinematics
     Needs: RTX 2070+ or equivalent
     Mods: 245 mods, full shader, 32x textures

  ⚖️ BALANCED (26.2)
     Best: Daily survival play, servers
     Needs: GTX 1060+
     Mods: 235 mods, optimized shader, 32x textures

  🗡️ LEGACY PvP (1.8.9)
     Best: PvP, competitive, Hypixel/Bedwars
     Target: 200+ FPS
     Mods: 62 mods, no shader, 32x clean textures


════════════════ FIRST LAUNCH TIPS ════════════

  • First time loading a world may be slow (mod init)
  • If shaders don't work → Iris settings → reload
  • If you get low FPS → switch to Balanced profile
  • DO NOT click "Open DH Settings" in-game (known LC bug)


════════════════ CREDITS ════════════════════════

  Shader: Complementary Reimagined + Euphoria Patches
  Built by: Antigravity AI + Ahmed's custom config
"""
with open(os.path.join(OUT_DIR, "README.txt"), "w", encoding="utf-8") as f:
    f.write(readme)
print("  README.txt created")

# ── FINAL SUMMARY ───────────────────────────────────────────────
total_size = sum(
    os.path.getsize(os.path.join(r, f))
    for r, d, files in os.walk(OUT_DIR) for f in files
)
print()
print("=" * 60)
print("  PACKAGE READY!")
print("=" * 60)
print(f"  Location: {OUT_DIR}")
print(f"  Total size: {total_size/1024/1024:.0f} MB")
print()
print("  WHAT TO SEND YOUR BRO:")
print("  → Upload entire D:\\AetherisShare\\ folder to Google Drive,")
print("    Discord, Mega, or any cloud storage")
print("  → Tell him to run INSTALL.bat after downloading")
print()
print("  Or ZIP the whole folder first:")
print("  Right-click AetherisShare → Send to → Compressed folder")
