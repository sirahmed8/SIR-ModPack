"""
Aetheris Ultimate - Complete Name, Icon & Title Fix
- Renames ZIPs to proper Aetheris names
- Converts all JPEGs to real PNGs
- Fixes title screen minecraft.png with proper Aetheris banner
- Fixes legacy pack name, icon, description
- Syncs all renamed ZIPs to all profiles
"""

from PIL import Image
import os, json, zipfile, shutil

PACK_SOURCE_MODERN = r"D:\resource pack\MyCustomPack_Modern_32x"
PACK_SOURCE_LEGACY = r"D:\resource pack\MyCustomPack_1.8.9_32x"
BRAIN = r"C:\Users\a7med\.gemini\antigravity\brain\a311e7e5-c0b6-47b7-bcf7-7dcc1dba5d4c"
PROFILES_BASE = r"C:\Users\a7med\.lunarclient\profiles"
MC_PACKS = r"C:\Users\a7med\AppData\Roaming\.minecraft\resourcepacks"

print("=" * 60)
print("AETHERIS - NAME / ICON / TITLE FIXER")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# STEP 1: Convert title banner JPEG to proper PNG
# ─────────────────────────────────────────────────────────────
print("\n[1] Converting title banner to proper PNG...")

# Find the newly generated banner
banner_src = None
for f in os.listdir(BRAIN):
    if 'title_minecraft_banner' in f.lower() and f.endswith('.jpg'):
        banner_src = os.path.join(BRAIN, f)
        print(f"  Found: {f}")
        break

if banner_src:
    img = Image.open(banner_src).convert("RGBA")
    # Minecraft title texture: 256x44 OR we can use a larger custom texture
    # The game actually accepts any resolution for this texture
    # Use 512x230 for modern quality
    img = img.resize((512, 230), Image.LANCZOS)
    
    title_dest = os.path.join(PACK_SOURCE_MODERN,
        r"assets\minecraft\textures\gui\title\minecraft.png")
    os.makedirs(os.path.dirname(title_dest), exist_ok=True)
    img.save(title_dest, "PNG", optimize=True)
    
    # Verify
    with open(title_dest, 'rb') as f:
        m = f.read(4)
    is_png = m == bytes([0x89,0x50,0x4E,0x47])
    print(f"  ✅ Saved title/minecraft.png: PNG={is_png} ({os.path.getsize(title_dest)} bytes)")
else:
    print("  [SKIP] Banner image not found")

# ─────────────────────────────────────────────────────────────
# STEP 2: Update pack icons - find artwork files
# ─────────────────────────────────────────────────────────────
print("\n[2] Finding and converting all artwork to proper PNG...")

artworks = {}
for f in os.listdir(BRAIN):
    if not f.endswith('.jpg'):
        continue
    fl = f.lower()
    if 'balanced' in fl:
        artworks['balanced'] = os.path.join(BRAIN, f)
    elif 'performance' in fl:
        artworks['performance'] = os.path.join(BRAIN, f)
    elif 'visual' in fl:
        artworks['visual'] = os.path.join(BRAIN, f)
    elif 'legacy' in fl:
        artworks['legacy'] = os.path.join(BRAIN, f)
    elif 'pack_icon' in fl or ('icon' in fl and 'banner' not in fl 
                               and 'title' not in fl and 'cover' not in fl
                               and 'balanced' not in fl and 'performance' not in fl
                               and 'visual' not in fl and 'legacy' not in fl):
        artworks.setdefault('main', os.path.join(BRAIN, f))

print(f"  Found: {[k for k in artworks]}")

def save_png(src, dest, size):
    img = Image.open(src).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)
    img.save(dest, "PNG", optimize=True)
    with open(dest, 'rb') as f:
        m = f.read(4)
    ok = m == bytes([0x89,0x50,0x4E,0x47])
    print(f"    ✅ {os.path.basename(dest)}: PNG={ok} ({os.path.getsize(dest)} bytes)")
    return ok

# Modern pack icon (crystal/main)
if 'main' in artworks:
    save_png(artworks['main'], os.path.join(PACK_SOURCE_MODERN, "pack.png"), (128, 128))

# Legacy pack icon (use legacy artwork)  
if 'legacy' in artworks:
    save_png(artworks['legacy'], os.path.join(PACK_SOURCE_LEGACY, "pack.png"), (128, 128))
elif 'main' in artworks:
    # Fallback: use main icon for legacy too
    save_png(artworks['main'], os.path.join(PACK_SOURCE_LEGACY, "pack.png"), (128, 128))

# ─────────────────────────────────────────────────────────────
# STEP 3: Update BOTH pack.mcmeta files properly
# ─────────────────────────────────────────────────────────────
print("\n[3] Updating pack.mcmeta files...")

modern_meta = {
    "pack": {
        "pack_format": 80,
        "supported_formats": [15, 130],
        "description": "\u00a76\u00a7lAetheris Ultimate\u00a7r \u00a77\u2014 Modern 32x\n\u00a73Shaders \u25c6 FreshAnims \u25c6 DramaticSkys"
    }
}
with open(os.path.join(PACK_SOURCE_MODERN, "pack.mcmeta"), 'w', encoding='utf-8') as f:
    json.dump(modern_meta, f, indent=2, ensure_ascii=False)
print("  ✅ Modern pack.mcmeta: §6§lAetheris Ultimate§r §7— Modern 32x")

legacy_meta = {
    "pack": {
        "pack_format": 6,
        "description": "\u00a76\u00a7lAetheris Legacy\u00a7r \u00a77\u2014 1.8.9 32x\n\u00a731.8.9 Optimized \u25c6 High Contrast PvP"
    }
}
with open(os.path.join(PACK_SOURCE_LEGACY, "pack.mcmeta"), 'w', encoding='utf-8') as f:
    json.dump(legacy_meta, f, indent=2, ensure_ascii=False)
print("  ✅ Legacy pack.mcmeta: §6§lAetheris Legacy§r §7— 1.8.9 32x")

# ─────────────────────────────────────────────────────────────
# STEP 4: Build ZIPs with PROPER NAMES (Aetheris branded)
# ─────────────────────────────────────────────────────────────
print("\n[4] Building properly-named Aetheris ZIPs...")

def build_zip(source_dir, zip_path):
    """Build a clean ZIP from source directory"""
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    file_count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(source_dir):
            # Skip temp/hidden folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '_temp']
            for file in files:
                if file.startswith('.'):
                    continue
                full = os.path.join(root, file)
                arc = os.path.relpath(full, source_dir).replace(os.sep, '/')
                zf.write(full, arc)
                file_count += 1
    
    size = os.path.getsize(zip_path)
    print(f"  ✅ Built {os.path.basename(zip_path)}: {file_count} files, {size:,} bytes")
    return zip_path

# Build modern pack with Aetheris name
modern_zip_new = r"D:\resource pack\Aetheris_Ultimate_32x.zip"
build_zip(PACK_SOURCE_MODERN, modern_zip_new)

# Build legacy pack with Aetheris name  
legacy_zip_new = r"D:\resource pack\Aetheris_Legacy_32x.zip"
build_zip(PACK_SOURCE_LEGACY, legacy_zip_new)

# Also keep the old names updated (for compatibility)
old_modern = r"D:\resource pack\MyCustomPack_Modern_32x.zip"
old_legacy = r"D:\resource pack\MyCustomPack_1.8.9_32x.zip"
build_zip(PACK_SOURCE_MODERN, old_modern)
build_zip(PACK_SOURCE_LEGACY, old_legacy)

# ─────────────────────────────────────────────────────────────
# STEP 5: Deploy new named ZIPs to all profile resourcepacks
# ─────────────────────────────────────────────────────────────
print("\n[5] Deploying Aetheris-named ZIPs to all profiles...")

profile_dirs = [
    os.path.join(PROFILES_BASE, "aetheris-ultimate-modpack-modern-26.2", "resourcepacks"),
    os.path.join(PROFILES_BASE, "aetheris-ultimate-modern-balanced-26.2", "resourcepacks"),
    os.path.join(PROFILES_BASE, "aetheris-ultimate-modern-performance-26.2", "resourcepacks"),
    os.path.join(PROFILES_BASE, "aetheris-ultimate-modern-visual-26.2", "resourcepacks"),
    os.path.join(PROFILES_BASE, "26", "resourcepacks"),
    MC_PACKS,
]

for profile_rp_dir in profile_dirs:
    if not os.path.exists(profile_rp_dir):
        os.makedirs(profile_rp_dir, exist_ok=True)
    
    # Deploy both the old name (backward compat) and new Aetheris name
    shutil.copy2(modern_zip_new, os.path.join(profile_rp_dir, "Aetheris_Ultimate_32x.zip"))
    shutil.copy2(modern_zip_new, os.path.join(profile_rp_dir, "MyCustomPack_Modern_32x.zip"))
    
    dirname = os.path.basename(os.path.dirname(profile_rp_dir))
    print(f"  ✅ Synced Modern pack → {dirname}")

# Legacy profile
legacy_profile_rp = os.path.join(PROFILES_BASE, "aetheris-ultimate-legacy-1.8.9", "resourcepacks")
os.makedirs(legacy_profile_rp, exist_ok=True)
shutil.copy2(legacy_zip_new, os.path.join(legacy_profile_rp, "Aetheris_Legacy_32x.zip"))
shutil.copy2(legacy_zip_new, os.path.join(legacy_profile_rp, "MyCustomPack_1.8.9_32x.zip"))
print(f"  ✅ Synced Legacy pack → aetheris-ultimate-legacy-1.8.9")

# ─────────────────────────────────────────────────────────────
# STEP 6: Profile icons - convert to proper PNG for all profiles
# ─────────────────────────────────────────────────────────────
print("\n[6] Converting profile icons to proper PNG...")

profile_icon_map = [
    ("aetheris-ultimate-modpack-modern-26.2",    artworks.get('main'),        (256,256), (512,288)),
    ("aetheris-ultimate-modern-balanced-26.2",   artworks.get('balanced'),    (256,256), (512,288)),
    ("aetheris-ultimate-modern-performance-26.2",artworks.get('performance'), (256,256), (512,288)),
    ("aetheris-ultimate-modern-visual-26.2",     artworks.get('visual'),      (256,256), (512,288)),
    ("aetheris-ultimate-legacy-1.8.9",           artworks.get('legacy'),      (256,256), (512,288)),
]

for profile, src, icon_size, feat_size in profile_icon_map:
    if not src or not os.path.exists(src):
        print(f"  [SKIP] No artwork for {profile}")
        continue
    profile_dir = os.path.join(PROFILES_BASE, profile)
    if not os.path.exists(profile_dir):
        print(f"  [SKIP] Profile dir not found: {profile}")
        continue
    save_png(src, os.path.join(profile_dir, "icon.png"), icon_size)
    save_png(src, os.path.join(profile_dir, "featured_image.png"), feat_size)
    print(f"  Profile done: {profile}")

# ─────────────────────────────────────────────────────────────
# FINAL VERIFICATION
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

for zip_path in [modern_zip_new, legacy_zip_new]:
    with zipfile.ZipFile(zip_path) as z:
        meta = json.loads(z.read("pack.mcmeta").decode("utf-8"))
        desc = meta["pack"]["description"]
        png = z.read("pack.png")
        is_png = png[:4] == bytes([0x89,0x50,0x4E,0x47])
        
        # Check bad JSONs
        bad = 0
        for n in z.namelist():
            if n.endswith('.json'):
                try:
                    json.loads(z.read(n).decode('utf-8', errors='replace'))
                except:
                    bad += 1
        
        print(f"\n{os.path.basename(zip_path)}:")
        print(f"  Description: {desc}")
        print(f"  pack.png: PNG={is_png}")
        print(f"  Bad JSONs: {bad}")
        print(f"  Files: {len(z.namelist())}")

print("\n✅ COMPLETE!")
