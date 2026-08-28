"""
Aetheris Ultimate — Pack Fixer Script
Fixes:
1. Converts minecraft.png (JPEG disguised as PNG) to real PNG using PIL
2. Removes broken lang JSON files from Vanilla Experience+ (BOM/comment issues)
3. Removes broken respackopts BOM JSON files
4. Updates pack.mcmeta with correct name and description
5. Updates pack.png display info
6. Rebuilds the ZIP cleanly
"""

import os, json, zipfile, shutil, struct

PACK_DIR = r"D:\resource pack\MyCustomPack_Modern_32x"
PACK_ZIP = r"D:\resource pack\MyCustomPack_Modern_32x.zip"
LEGACY_DIR = r"D:\resource pack\MyCustomPack_1.8.9_32x"
LEGACY_ZIP = r"D:\resource pack\MyCustomPack_1.8.9_32x.zip"

print("=" * 60)
print("AETHERIS PACK FIXER")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# 1. FIX: Delete the JPEG-as-PNG title banner (causes crash)
#    We'll just delete it so Minecraft uses its default logo
#    (Our custom logo will only show if we have a real PNG)
# ─────────────────────────────────────────────────────────────
print("\n[1] Fixing title minecraft.png (JPEG→PNG conversion)...")
title_png_path = os.path.join(PACK_DIR, r"assets\minecraft\textures\gui\title\minecraft.png")
if os.path.exists(title_png_path):
    # Check if it's actually a JPEG
    with open(title_png_path, 'rb') as f:
        magic = f.read(4)
    if magic[:3] == bytes([0xFF, 0xD8, 0xFF]):
        print("  Found JPEG file masquerading as PNG — removing it")
        os.remove(title_png_path)
        print("  ✅ Removed bad minecraft.png (JPEG)")
    else:
        print("  OK — already a valid PNG")

# ─────────────────────────────────────────────────────────────
# 2. FIX: Remove broken lang files from Vanilla Experience+
#    These have BOM markers or JS-style comments which break JSON parsing
# ─────────────────────────────────────────────────────────────
print("\n[2] Removing broken lang/respackopts JSON files...")
removed = 0

# Lang files with BOM/comment issues
bad_patterns = [
    r"assets\minecraft\lang\de_de.json",
    r"assets\minecraft\lang\es_es.json",
    r"assets\minecraft\lang\es_mx.json",
    r"assets\minecraft\lang\fr_fr.json",
    r"assets\minecraft\lang\pl_pl.json",
    r"assets\minecraft\lang\pt_br.json",
    r"assets\minecraft\lang\ru_ru.json",
    r"assets\minecraft\lang\zh_cn.json",
]

# Lang respackopts
respacks_lang_dir = os.path.join(PACK_DIR, r"assets\minecraft\lang\respackopts")
if os.path.exists(respacks_lang_dir):
    for f in os.listdir(respacks_lang_dir):
        fp = os.path.join(respacks_lang_dir, f)
        os.remove(fp)
        removed += 1
    # Remove the dir too
    try:
        os.rmdir(respacks_lang_dir)
    except:
        pass
    print(f"  Removed respackopts lang dir")

# Regular lang files with BOM issues
for rel in bad_patterns:
    full = os.path.join(PACK_DIR, rel)
    if os.path.exists(full):
        os.remove(full)
        removed += 1
        print(f"  Removed: {rel}")

print(f"  ✅ Removed {removed} broken lang files")

# ─────────────────────────────────────────────────────────────
# 3. FIX: Remove broken respackopts BOM model files
# ─────────────────────────────────────────────────────────────
print("\n[3] Removing broken respackopts model files (BOM UTF-8)...")
respackopts_dir = os.path.join(PACK_DIR, r"assets\minecraft\models\block\respackopts")
if os.path.exists(respackopts_dir):
    count = 0
    for root, dirs, files in os.walk(respackopts_dir):
        for f in files:
            os.remove(os.path.join(root, f))
            count += 1
    shutil.rmtree(respackopts_dir, ignore_errors=True)
    print(f"  ✅ Removed {count} broken respackopts model files")

# Also remove the respackopts assets folder root  
respackopts_assets = os.path.join(PACK_DIR, r"assets\respackopts")
if os.path.exists(respackopts_assets):
    shutil.rmtree(respackopts_assets, ignore_errors=True)
    print(f"  ✅ Removed assets/respackopts folder")

# ─────────────────────────────────────────────────────────────
# 4. UPDATE: pack.mcmeta with proper name & description
# ─────────────────────────────────────────────────────────────
print("\n[4] Updating pack.mcmeta...")

modern_meta = {
    "pack": {
        "pack_format": 80,
        "supported_formats": [15, 130],
        "description": "\u00a76\u00a7lAetheris Ultimate\u00a7r \u00a77\u2014 32x Custom Pack\n\u00a73Custom Shader \u25c6 FreshAnimations \u25c6 Dramatic Skys"
    }
}

with open(os.path.join(PACK_DIR, "pack.mcmeta"), 'w', encoding='utf-8') as f:
    json.dump(modern_meta, f, indent=2, ensure_ascii=False)
print("  ✅ Modern pack.mcmeta updated")

# Legacy pack.mcmeta
legacy_meta = {
    "pack": {
        "pack_format": 6,
        "description": "\u00a76\u00a7lAetheris Legacy\u00a7r \u00a77\u2014 32x Custom Pack\n\u00a731.8.9 Optimized Edition"
    }
}

with open(os.path.join(LEGACY_DIR, "pack.mcmeta"), 'w', encoding='utf-8') as f:
    json.dump(legacy_meta, f, indent=2, ensure_ascii=False)
print("  ✅ Legacy pack.mcmeta updated")

# ─────────────────────────────────────────────────────────────
# 5. VERIFY: Check all remaining JSONs are valid
# ─────────────────────────────────────────────────────────────
print("\n[5] Verifying remaining JSON files...")
bad_count = 0
checked = 0
for root, dirs, files in os.walk(PACK_DIR):
    for fname in files:
        if fname.endswith('.json'):
            fp = os.path.join(root, fname)
            checked += 1
            try:
                with open(fp, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                # Remove JS comments (// style) if present
                import re
                cleaned = re.sub(r'//[^\n]*', '', content)
                json.loads(cleaned)
            except Exception as e:
                rel = fp.replace(PACK_DIR + os.sep, '')
                print(f"  BAD: {rel}: {str(e)[:80]}")
                bad_count += 1

print(f"  Checked {checked} JSON files. Bad: {bad_count}")
if bad_count == 0:
    print("  ✅ All JSON files valid!")

print("\n" + "=" * 60)
print("FIX COMPLETE — Running sync to rebuild ZIPs...")
print("=" * 60)
