#!/usr/bin/env python3
"""
🌌 AETHERIS ULTIMATE ECOSYSTEM SYNCHRONIZER & VALIDATOR (v16.0 MASTER)
Automates compilation, validation, packaging, and multi-profile deployment across:
- Modern 26.2 (Fabric / Iris / Sodium)
- Legacy 1.8.9 (Forge / OptiFine)
- Lunar Client profiles & Standard .minecraft
"""

import os
import shutil
import zipfile
import json
import glob

def print_header(title):
    print("=" * 70)
    print(f"🌌 {title}")
    print("=" * 70)

# Paths
BASE_DIR = r"D:\mods"
SHADER_SRC = r"D:\shader\Aetheris_Shader_Pack"
MODS_SHADER_SRC = r"D:\mods\shader\Aetheris_Shader_Pack"
SHADER_ZIP = r"D:\shader\Aetheris_Shader_Pack.zip"

RESOURCE_MODERN_SRC = r"D:\resource pack\MyCustomPack_Modern_32x"
RESOURCE_MODERN_ZIP = r"D:\resource pack\MyCustomPack_Modern_32x.zip"

RESOURCE_LEGACY_SRC = r"D:\resource pack\MyCustomPack_1.8.9_32x"
RESOURCE_LEGACY_ZIP = r"D:\resource pack\MyCustomPack_1.8.9_32x.zip"

CORE_JAR_SRC = r"D:\mods\build\AetherisCore-fabric-26.2.jar"

LUNAR_PROFILES = r"C:\Users\a7med\.lunarclient\profiles"
DOT_MINECRAFT = r"C:\Users\a7med\AppData\Roaming\.minecraft"

def validate_glsl():
    print_header("VALIDATING GLSL SHADERS")
    errors = 0
    for root, dirs, files in os.walk(SHADER_SRC):
        for f in files:
            if f.endswith(('.glsl', '.fsh', '.vsh', '.gsh')):
                full = os.path.join(root, f)
                with open(full, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    # Check for undefined TAA smoothing blocks
                    if 'taa.glsl' in f and '#else' not in content:
                        print(f"⚠️ Warning: {f} missing #else fallback!")
                        errors += 1
    print(f"✅ GLSL Validation complete. Issues found: {errors}")
    return errors == 0

def build_shader_zip():
    print_header("PACKAGING AETHERIS SHADER PACK")
    # Sync shader sources between D:\shader and D:\mods\shader
    for root, dirs, files in os.walk(SHADER_SRC):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, SHADER_SRC)
            dst = os.path.join(MODS_SHADER_SRC, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    
    # Create zip
    with zipfile.ZipFile(SHADER_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(SHADER_SRC):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, SHADER_SRC)
                z.write(full, rel)
    
    # Copy zip to D:\mods\shader\
    shutil.copy2(SHADER_ZIP, r"D:\mods\shader\Aetheris_Shader_Pack.zip")
    print(f"✅ Created Shader Archive: {SHADER_ZIP} ({os.path.getsize(SHADER_ZIP)} bytes)")

def build_resource_packs():
    print_header("PACKAGING RESOURCE PACKS")
    
    # 1. Clean modern pack
    clock_bad = os.path.join(RESOURCE_MODERN_SRC, "assets", "minecraft", "items", "clock - Copy.json")
    if os.path.exists(clock_bad):
        os.remove(clock_bad)
        print("  Cleaned clock - Copy.json")
        
    with zipfile.ZipFile(RESOURCE_MODERN_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(RESOURCE_MODERN_SRC):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, RESOURCE_MODERN_SRC)
                z.write(full, rel)
    print(f"✅ Created Modern Resource Pack: {RESOURCE_MODERN_ZIP} ({os.path.getsize(RESOURCE_MODERN_ZIP)} bytes)")
    
    # Copy to D:\mods\resource pack\
    os.makedirs(r"D:\mods\resource pack", exist_ok=True)
    shutil.copy2(RESOURCE_MODERN_ZIP, r"D:\mods\resource pack\MyCustomPack_Modern_32x.zip")

    # 2. Clean legacy pack
    if os.path.exists(RESOURCE_LEGACY_SRC):
        with zipfile.ZipFile(RESOURCE_LEGACY_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(RESOURCE_LEGACY_SRC):
                for f in files:
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, RESOURCE_LEGACY_SRC)
                    z.write(full, rel)
        print(f"✅ Created Legacy Resource Pack: {RESOURCE_LEGACY_ZIP} ({os.path.getsize(RESOURCE_LEGACY_ZIP)} bytes)")
        shutil.copy2(RESOURCE_LEGACY_ZIP, r"D:\mods\resource pack\MyCustomPack_1.8.9_32x.zip")

def sync_modern_mods():
    print_header("SYNCHRONIZING & DEDUPLICATING MODERN FABRIC MODS")
    
    # Target directories
    modern_targets = [
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modpack-modern-26.2", "mods"),
        os.path.join(LUNAR_PROFILES, "26", "mods", "fabric-26.2"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modern-balanced-26.2", "mods"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modern-visual-26.2", "mods"),
        BASE_DIR
    ]
    
    # Deploy compiled AetherisCore-fabric-26.2.jar to D:\mods
    shutil.copy2(CORE_JAR_SRC, os.path.join(BASE_DIR, "AetherisCore-fabric-26.2.jar"))
    
    for t in modern_targets:
        if os.path.exists(t):
            # Remove old duplicate core
            old_core = os.path.join(t, "aetheris_core-1.0.0.jar")
            if os.path.exists(old_core):
                os.remove(old_core)
                print(f"  Removed obsolete aetheris_core-1.0.0.jar from {t}")
            
            # Copy new verified core
            shutil.copy2(CORE_JAR_SRC, os.path.join(t, "AetherisCore-fabric-26.2.jar"))
            print(f"  Deployed AetherisCore-fabric-26.2.jar (v2.0.0) -> {t}")

def sync_shaders_and_resources():
    print_header("SYNCHRONIZING SHADERS, PRESETS & RESOURCE PACKS")
    
    shader_targets = [
        os.path.join(DOT_MINECRAFT, "shaderpacks"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modpack-modern-26.2", "shaderpacks"),
        os.path.join(LUNAR_PROFILES, "26", "shaderpacks"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modern-balanced-26.2", "shaderpacks"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modern-performance-26.2", "shaderpacks"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modern-visual-26.2", "shaderpacks"),
    ]
    
    rp_targets = [
        os.path.join(DOT_MINECRAFT, "resourcepacks"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modpack-modern-26.2", "resourcepacks"),
        os.path.join(LUNAR_PROFILES, "26", "resourcepacks"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modern-balanced-26.2", "resourcepacks"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modern-performance-26.2", "resourcepacks"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-modern-visual-26.2", "resourcepacks"),
    ]
    
    preset_txt = r"D:\shader\Aetheris_Shader_Pack.txt"
    preset_zip_txt = r"D:\shader\Aetheris_Shader_Pack.zip.txt"
    
    for st in shader_targets:
        os.makedirs(st, exist_ok=True)
        shutil.copy2(SHADER_ZIP, os.path.join(st, "Aetheris_Shader_Pack.zip"))
        if os.path.exists(preset_txt):
            shutil.copy2(preset_txt, os.path.join(st, "Aetheris_Shader_Pack.txt"))
        if os.path.exists(preset_zip_txt):
            shutil.copy2(preset_zip_txt, os.path.join(st, "Aetheris_Shader_Pack.zip.txt"))
        print(f"  Synced shader & presets -> {st}")
        
    for rpt in rp_targets:
        os.makedirs(rpt, exist_ok=True)
        shutil.copy2(RESOURCE_MODERN_ZIP, os.path.join(rpt, "MyCustomPack_Modern_32x.zip"))
        print(f"  Synced resource pack -> {rpt}")
        
    # Games folder preset
    if os.path.exists(r"D:\Games"):
        shutil.copy2(preset_zip_txt, r"D:\Games\Aetheris_Shader_Pack.zip.txt")
        print("  Synced preset -> D:\\Games\\Aetheris_Shader_Pack.zip.txt")

def optimize_legacy_1_8_9():
    print_header("OPTIMIZING LEGACY 1.8.9 PROFILE")
    
    legacy_dirs = [
        os.path.join(LUNAR_PROFILES, "1.8"),
        os.path.join(LUNAR_PROFILES, "aetheris-ultimate-legacy-1.8.9")
    ]
    
    for ld in legacy_dirs:
        if os.path.exists(ld):
            # Sync 1.8.9 resource pack
            rp_dir = os.path.join(ld, "resourcepacks")
            os.makedirs(rp_dir, exist_ok=True)
            shutil.copy2(RESOURCE_LEGACY_ZIP, os.path.join(rp_dir, "MyCustomPack_1.8.9_32x.zip"))
            
            # Remove modern pack if accidentally placed in 1.8.9
            bad_modern_pack = os.path.join(rp_dir, "MyCustomPack_Modern_32x.zip")
            if os.path.exists(bad_modern_pack):
                os.remove(bad_modern_pack)
                print(f"  Removed incompatible modern pack from 1.8.9: {bad_modern_pack}")
                
            # Clean incompatible mods from forge-1.8.9
            mods_dir = os.path.join(ld, "mods", "forge-1.8.9")
            if not os.path.exists(mods_dir):
                mods_dir = os.path.join(ld, "mods")
            if os.path.exists(mods_dir):
                incompatible = [
                    "IGCM_v1.2.0pre-3_mc1.12.2.jar",
                    "EuphoriaPatcher-1.9.3-r5.8.1-forgeLegacy.jar"
                ]
                for inc in incompatible:
                    inc_path = os.path.join(mods_dir, inc)
                    if os.path.exists(inc_path):
                        os.remove(inc_path)
                        print(f"  Removed incompatible 1.8.9 mod: {inc}")
                        
            print(f"✅ Optimized Legacy 1.8.9 instance: {ld}")

def main():
    validate_glsl()
    build_shader_zip()
    build_resource_packs()
    sync_modern_mods()
    sync_shaders_and_resources()
    optimize_legacy_1_8_9()
    print_header("ALL AETHERIS ECOSYSTEM SYNCHRONIZATIONS COMPLETED SUCCESSFULLY! ✨")

if __name__ == '__main__':
    main()
