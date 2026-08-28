"""
Aetheris Master Pack Builder & Multi-Version Deployer
Builds and deploys:
  - [26.2] Aetheris Ultimate 32x.zip (Modern 26.2 / 1.21+)
  - [1.8.9] Aetheris Legacy 32x.zip (Legacy 1.8.9)
"""

import os, json, zipfile, shutil
from PIL import Image

BRAIN = r"C:\Users\a7med\.gemini\antigravity\brain\a311e7e5-c0b6-47b7-bcf7-7dcc1dba5d4c"
MODERN_DIR = r"D:\resource pack\MyCustomPack_Modern_32x"
LEGACY_DIR = r"D:\resource pack\MyCustomPack_1.8.9_32x"
OUTPUT_DIR = r"D:\resource pack"

print("=" * 70)
print("🌌 AETHERIS VERSION-TAGGED PACK BUILDER")
print("=" * 70)

# 1. Update Modern pack.mcmeta
modern_meta = {
    "pack": {
        "pack_format": 80,
        "supported_formats": [15, 130],
        "description": "§b[For Modern 26.2] §6§lAetheris Ultimate 32x§r\n§3Custom Shaders ◆ FreshAnimations ◆ HD Sky"
    }
}
with open(os.path.join(MODERN_DIR, "pack.mcmeta"), "w", encoding="utf-8") as f:
    json.dump(modern_meta, f, indent=2, ensure_ascii=False)
print("✅ Modern pack.mcmeta: §b[For Modern 26.2] §6§lAetheris Ultimate 32x§r")

# 2. Update Legacy pack.mcmeta
legacy_meta = {
    "pack": {
        "pack_format": 1,
        "description": "§e[For Legacy 1.8.9] §6§lAetheris Legacy 32x§r\n§31.8.9 Optimized ◆ High-FPS PvP"
    }
}
with open(os.path.join(LEGACY_DIR, "pack.mcmeta"), "w", encoding="utf-8") as f:
    json.dump(legacy_meta, f, indent=2, ensure_ascii=False)
print("✅ Legacy pack.mcmeta: §e[For Legacy 1.8.9] §6§lAetheris Legacy 32x§r")

# 3. Zip Builder Function
def build_zip(source_dir, dest_path):
    if os.path.exists(dest_path):
        os.remove(dest_path)
    count = 0
    with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "_temp"]
            for f in files:
                if f.startswith("."):
                    continue
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, source_dir).replace(os.sep, "/")
                zf.write(full_p, rel_p)
                count += 1
    size_mb = os.path.getsize(dest_path) / (1024 * 1024)
    print(f"  📦 Built {os.path.basename(dest_path)} ({count} files, {size_mb:.2f} MB)")
    return dest_path

print("\nBuilding Modern Packs...")
modern_primary = os.path.join(OUTPUT_DIR, "[26.2] Aetheris Ultimate 32x.zip")
build_zip(MODERN_DIR, modern_primary)
# Create alias copies
for alias in ["Aetheris_Ultimate_32x.zip", "MyCustomPack_Modern_32x.zip"]:
    shutil.copy2(modern_primary, os.path.join(OUTPUT_DIR, alias))

print("\nBuilding Legacy Packs...")
legacy_primary = os.path.join(OUTPUT_DIR, "[1.8.9] Aetheris Legacy 32x.zip")
build_zip(LEGACY_DIR, legacy_primary)
# Create alias copies
for alias in ["Aetheris_Legacy_32x.zip", "MyCustomPack_1.8.9_32x.zip"]:
    shutil.copy2(legacy_primary, os.path.join(OUTPUT_DIR, alias))

# 4. Sync to all profile directories
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

print("\nDeploying Modern packs...")
for t in modern_targets:
    os.makedirs(t, exist_ok=True)
    shutil.copy2(modern_primary, os.path.join(t, "[26.2] Aetheris Ultimate 32x.zip"))
    shutil.copy2(modern_primary, os.path.join(t, "Aetheris_Ultimate_32x.zip"))
    shutil.copy2(modern_primary, os.path.join(t, "MyCustomPack_Modern_32x.zip"))
    print(f"  🚀 Modern Synced -> {t}")

print("\nDeploying Legacy packs...")
for t in legacy_targets:
    os.makedirs(t, exist_ok=True)
    shutil.copy2(legacy_primary, os.path.join(t, "[1.8.9] Aetheris Legacy 32x.zip"))
    shutil.copy2(legacy_primary, os.path.join(t, "Aetheris_Legacy_32x.zip"))
    shutil.copy2(legacy_primary, os.path.join(t, "MyCustomPack_1.8.9_32x.zip"))
    print(f"  🚀 Legacy Synced -> {t}")

print("\n" + "=" * 70)
print("✨ ALL VERSION-TAGGED PACKS BUILT & DEPLOYED SUCCESSFULLY!")
print("=" * 70)
