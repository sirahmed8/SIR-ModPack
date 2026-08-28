"""
AETHERIS ECOSYSTEM - MASTER PACK REBUILD & DEPLOYER
- Fixes Title Screen (minecraft.png + 3D edition.png + custom splashes)
- Fixes 1.8.9 Legacy Pack (pack_format = 1, custom retro pack.png, description)
- Fixes Modern Pack (pack_format = 80, custom crystal pack.png, description)
- Rebuilds clean ZIPs for both Modern and Legacy
- Deploys ZIPs to ALL Lunar Client profile folders + .minecraft/resourcepacks
"""

import os, sys, json, zipfile, shutil
from PIL import Image

BRAIN = r"C:\Users\a7med\.gemini\antigravity\brain\a311e7e5-c0b6-47b7-bcf7-7dcc1dba5d4c"
MODERN_DIR = r"D:\resource pack\MyCustomPack_Modern_32x"
LEGACY_DIR = r"D:\resource pack\MyCustomPack_1.8.9_32x"
OUTPUT_DIR = r"D:\resource pack"

print("=" * 70)
print("🌌 AETHERIS MASTER PACK REBUILD & DEPLOYMENT")
print("=" * 70)

# -------------------------------------------------------------
# 1. FIX TITLE SCREEN TEXTURES (MODERN)
# -------------------------------------------------------------
print("\n[1] Preparing title screen textures (clean 3D vector styling)...")
title_dir = os.path.join(MODERN_DIR, r"assets\minecraft\textures\gui\title")
os.makedirs(title_dir, exist_ok=True)

# Generate / verify 3D edition.png
sys.path.append(r"D:\mods")
from generate_3d_edition import create_aetheris_edition_texture
create_aetheris_edition_texture(os.path.join(title_dir, "edition.png"))

# Ensure clean minecraft.png is from Sapixcraft (1024x256 transparent stone logo)
sapix_zip = r"D:\resource pack\Sapixcraft 32x r1.5 26.2.zip"
if os.path.exists(sapix_zip):
    with zipfile.ZipFile(sapix_zip) as z:
        mc_data = z.read("assets/minecraft/textures/gui/title/minecraft.png")
    with open(os.path.join(title_dir, "minecraft.png"), "wb") as f:
        f.write(mc_data)
    print("  ✅ minecraft.png: Clean HD 3D stone logo applied")

# Clean splashes.txt
texts_dir = os.path.join(MODERN_DIR, r"assets\minecraft\texts")
os.makedirs(texts_dir, exist_ok=True)

# Remove any patron splashes file
patron_file = os.path.join(texts_dir, "patron splashes.txt")
if os.path.exists(patron_file):
    os.remove(patron_file)

splashes_content = """Aetheris Ultimate!
1000x Better!
Custom Shaders Enabled!
God-tier Performance!
RTX-Quality Shaders!
Smooth 999 FPS!
Crystal Clear Water!
Leaves in the Breeze!
Sun is Perfectly Round!
Dramatic Skies Await!
Fresh Animations Active!
32x Textures, Zero Lag!
Optimized. Perfected. Aetheris.
The Ultimate Experience!
"""
with open(os.path.join(texts_dir, "splashes.txt"), "w", encoding="utf-8") as f:
    f.write(splashes_content.strip())
print("  ✅ splashes.txt: Modpack-themed splash lines configured")

# -------------------------------------------------------------
# 2. FIX PACK ICONS (pack.png)
# -------------------------------------------------------------
print("\n[2] Converting custom pack icons to crisp RGBA PNG format...")

# Modern Icon (Crystal / Galaxy emblem)
modern_art = os.path.join(BRAIN, "aetheris_pack_icon_1787103828557.jpg")
if os.path.exists(modern_art):
    im_m = Image.open(modern_art).convert("RGBA").resize((128, 128), Image.LANCZOS)
    im_m.save(os.path.join(MODERN_DIR, "pack.png"), "PNG", optimize=True)
    print(f"  ✅ Modern pack.png: {im_m.size} RGBA PNG")

# Legacy Icon (Retro Creeper / CRT scanlines)
legacy_art = os.path.join(BRAIN, "aetheris_legacy_icon_1787104820456.jpg")
if os.path.exists(legacy_art):
    im_l = Image.open(legacy_art).convert("RGBA").resize((128, 128), Image.LANCZOS)
    im_l.save(os.path.join(LEGACY_DIR, "pack.png"), "PNG", optimize=True)
    print(f"  ✅ Legacy pack.png: {im_l.size} RGBA PNG")

# -------------------------------------------------------------
# 3. FIX PACK.MCMETA FOR BOTH PACKS
# -------------------------------------------------------------
print("\n[3] Setting exact pack.mcmeta descriptions & pack_format...")

modern_mcmeta = {
    "pack": {
        "pack_format": 80,
        "supported_formats": [15, 130],
        "description": "§6§lAetheris Ultimate§r §7— Modern 32x\n§3Custom Shaders ◆ FreshAnimations ◆ HD Sky"
    }
}
with open(os.path.join(MODERN_DIR, "pack.mcmeta"), "w", encoding="utf-8") as f:
    json.dump(modern_mcmeta, f, indent=2, ensure_ascii=False)
print("  ✅ Modern pack.mcmeta: format=80 (1.20 - 1.21+ / 26.2)")

legacy_mcmeta = {
    "pack": {
        "pack_format": 1,
        "description": "§6§lAetheris Legacy§r §7— 1.8.9 32x\n§31.8.9 Optimized ◆ High-FPS PvP"
    }
}
with open(os.path.join(LEGACY_DIR, "pack.mcmeta"), "w", encoding="utf-8") as f:
    json.dump(legacy_mcmeta, f, indent=2, ensure_ascii=False)
print("  ✅ Legacy pack.mcmeta: format=1 (1.8.9 Native)")

# -------------------------------------------------------------
# 4. REBUILD ZIPS
# -------------------------------------------------------------
print("\n[4] Packaging ZIP files...")

def zip_folder(source_dir, zip_dest):
    if os.path.exists(zip_dest):
        os.remove(zip_dest)
    count = 0
    with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "_temp"]
            for f in files:
                if f.startswith("."):
                    continue
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, source_dir).replace(os.sep, "/")
                zf.write(full_p, rel_p)
                count += 1
    size_mb = os.path.getsize(zip_dest) / (1024 * 1024)
    print(f"  📦 Built {os.path.basename(zip_dest)} ({count} files, {size_mb:.2f} MB)")
    return zip_dest

# Build Modern
modern_primary = zip_folder(MODERN_DIR, os.path.join(OUTPUT_DIR, "Aetheris_Ultimate_32x.zip"))
zip_folder(MODERN_DIR, os.path.join(OUTPUT_DIR, "MyCustomPack_Modern_32x.zip"))

# Build Legacy
legacy_primary = zip_folder(LEGACY_DIR, os.path.join(OUTPUT_DIR, "Aetheris_Legacy_32x.zip"))
zip_folder(LEGACY_DIR, os.path.join(OUTPUT_DIR, "MyCustomPack_1.8.9_32x.zip"))

# -------------------------------------------------------------
# 5. DEPLOY TO ALL PROFILES & .MINECRAFT
# -------------------------------------------------------------
print("\n[5] Synchronizing all pack ZIPs across Lunar Client & .minecraft...")

modern_targets = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\26\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\1.21\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\vanilla-1.21\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\badlion-1.21\resourcepacks",
]

legacy_targets = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\1.8\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\vanilla-1.8\resourcepacks",
    r"C:\Users\a7med\.lunarclient\profiles\badlion-1.8\resourcepacks",
]

for t in modern_targets:
    os.makedirs(t, exist_ok=True)
    shutil.copy2(modern_primary, os.path.join(t, "Aetheris_Ultimate_32x.zip"))
    shutil.copy2(modern_primary, os.path.join(t, "MyCustomPack_Modern_32x.zip"))
    print(f"  🚀 Modern Synced -> {t}")

for t in legacy_targets:
    os.makedirs(t, exist_ok=True)
    shutil.copy2(legacy_primary, os.path.join(t, "Aetheris_Legacy_32x.zip"))
    shutil.copy2(legacy_primary, os.path.join(t, "MyCustomPack_1.8.9_32x.zip"))
    print(f"  🚀 Legacy Synced -> {t}")

print("\n" + "=" * 70)
print("✨ MASTER PACK REBUILD & DEPLOYMENT COMPLETED SUCCESSFULLY!")
print("=" * 70)
