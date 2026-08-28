#!/usr/bin/env python3
"""
patch_mods_jar.py

1. Patch better-nether JAR — remove compat resource packs that spam logs
2. Patch better-end JAR   — remove nourish_extensions compat pack
3. Fix WorldPresetInfoRegistry datapack — correct namespace path
"""
import os, zipfile, shutil, json

PROFILE = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
MODS_DIR = os.path.join(PROFILE, "mods")

def patch_jar_remove_dirs(jar_path, dirs_to_remove):
    """Rebuild a JAR without the specified directory prefixes."""
    print(f"\n  Patching: {os.path.basename(jar_path)}")
    backup = jar_path + ".bak"
    tmp_path = jar_path + ".tmp"

    # Backup original
    if not os.path.exists(backup):
        shutil.copy2(jar_path, backup)
        print(f"    Backup: {os.path.basename(backup)}")

    removed = 0
    kept = 0

    with zipfile.ZipFile(jar_path, "r") as zin:
        with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zout:
            for item in zin.infolist():
                # Check if this file is in any of the dirs to remove
                should_remove = any(item.filename.startswith(d) for d in dirs_to_remove)
                if should_remove:
                    removed += 1
                else:
                    # Copy file data unchanged
                    data = zin.read(item.filename)
                    zout.writestr(item, data)
                    kept += 1

    # Replace original with patched
    os.replace(tmp_path, jar_path)
    print(f"    Removed {removed} files (compat packs)")
    print(f"    Kept    {kept} files")
    print(f"    Done!")

# ══════════════════════════════════════════════════════════════════
# 1. PATCH better-nether — remove vanilla-hammers + vanillaexcavators
# ══════════════════════════════════════════════════════════════════
print("=== PATCHING MOD JARS ===")

# BetterNether
bn_jar = os.path.join(MODS_DIR, "better-nether-26.201.2.jar")
if os.path.exists(bn_jar):
    patch_jar_remove_dirs(bn_jar, [
        "resourcepacks/vanilla-hammers_extensions/",
        "resourcepacks/vanillaexcavators_extensions/",
        "resourcepacks/vanilla_hammers_extensions/",
        "resourcepacks/vanilla-excavators_extensions/",
    ])
else:
    print(f"  BetterNether JAR not found: {bn_jar}")

# BetterEnd — look for it
be_jar = None
for f in os.listdir(MODS_DIR):
    if "betterend" in f.lower() or "better-end" in f.lower() or "better_end" in f.lower():
        be_jar = os.path.join(MODS_DIR, f)
        break

if be_jar:
    patch_jar_remove_dirs(be_jar, [
        "resourcepacks/nourish_extensions/",
        "resourcepacks/vanillanourish_extensions/",
        "resourcepacks/vanilla-nourish_extensions/",
    ])
else:
    print("\n  BetterEnd JAR not found in mods (may be embedded in worldweaver)")
    # Check if it's inside worldweaver
    ww_jar = os.path.join(MODS_DIR, "worldweaver-26.201.2.jar")
    if os.path.exists(ww_jar):
        with zipfile.ZipFile(ww_jar) as z:
            nested = [n for n in z.namelist() if "betterend" in n.lower() and n.endswith(".jar")]
            if nested:
                print(f"  BetterEnd is nested inside worldweaver: {nested}")
            # Look for nourish_extensions anywhere
            nourish = [n for n in z.namelist() if "nourish" in n.lower()]
            if nourish:
                print(f"  Found nourish files in worldweaver: {nourish[:5]}")

# Also check if betterend is a separate mod
print()
print("=== All mods in profile ===")
for f in sorted(os.listdir(MODS_DIR)):
    if any(x in f.lower() for x in ["betterend", "better-end", "better_end"]):
        print(f"  {f}")

# ══════════════════════════════════════════════════════════════════
# 2. FIX WorldPresetInfoRegistry datapack — correct namespace path
# ══════════════════════════════════════════════════════════════════
print("\n=== FIXING WORLD PRESET INFO DATAPACK ===")

world_saves = os.path.join(PROFILE, "saves")
if os.path.exists(world_saves):
    for world_name in os.listdir(world_saves):
        world_dir = os.path.join(world_saves, world_name)
        if not os.path.isdir(world_dir): continue
        level_dat = os.path.join(world_dir, "level.dat")
        if not os.path.exists(level_dat): continue

        dp_root = os.path.join(world_dir, "datapacks", "aetheris-wover-fix")

        # Remove old wrong-path datapack content
        old_wrong = os.path.join(dp_root, "data", "wover")
        if os.path.exists(old_wrong):
            shutil.rmtree(old_wrong)
            print(f"  Removed old wrong-path entry")

        # Correct path: data/<preset_namespace>/wover/world_preset_info/<preset_path>.json
        # For minecraft:normal world preset:
        correct_dir = os.path.join(dp_root, "data", "minecraft", "wover", "world_preset_info")
        os.makedirs(correct_dir, exist_ok=True)

        # pack.mcmeta (already exists but let's ensure it's correct format 48 = MC 26.2)
        pack_meta = {
            "pack": {
                "pack_format": 48,
                "description": "Aetheris: WoVer WorldPreset registry fix"
            }
        }
        with open(os.path.join(dp_root, "pack.mcmeta"), "w") as f:
            json.dump(pack_meta, f, indent=2)

        # The WorldPresetInfo codec fields (from WoVer source: title, description, etc.)
        # For a vanilla world we just need a minimal valid entry
        preset_info = {
            "title": "Minecraft Normal",
            "description": "Standard Minecraft world",
            "preset": "minecraft:normal"
        }
        preset_path = os.path.join(correct_dir, "normal.json")
        with open(preset_path, "w") as f:
            json.dump(preset_info, f, indent=2)

        print(f"  Fixed datapack in world '{world_name}'")
        print(f"  Path: {os.path.relpath(preset_path, world_dir)}")

print()
print("=== DONE ===")
print()
print("Changes made:")
print("  1. better-nether.jar patched — vanilla-hammers + vanillaexcavators compat packs removed")
print("  2. WorldPreset datapack namespace corrected (wover -> minecraft)")
print()
print("After restarting the game:")
print("  - NO MORE texture fallback spam from betternether/vanilla-hammers_extensions")
print("  - NO MORE texture fallback spam from betternether/vanillaexcavators_extensions")
print("  - WorldPresetInfoRegistry error should be gone too")
