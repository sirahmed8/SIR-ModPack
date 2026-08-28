#!/usr/bin/env python3
"""Automated Package & Release Archive Builder for SIR Ecosystem.
Generates:
1. Modular compressed payloads for Cloud Self-Healing
2. Clean Offline SIR Package distribution
3. Standalone compressed 'SIR_Package_v1.0.0.zip' for GitHub Releases
"""
import os
import sys
import zipfile
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(ROOT, 'SIR Package')
PAYLOADS_DIR = os.path.join(ROOT, 'dist_payloads')
RELEASE_ZIP = os.path.join(ROOT, 'SIR_Package_v1.0.0.zip')

def zip_directory(src_dir, zip_path, arc_prefix=""):
    """Compresses directory tree into a high-compression zip archive."""
    if not os.path.isdir(src_dir):
        print(f"[-] Warning: source directory {src_dir} does not exist.")
        return 0
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    total_files = 0
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, src_dir)
                arc_name = os.path.join(arc_prefix, rel) if arc_prefix else rel
                zf.write(fp, arc_name)
                total_files += 1
    sz = os.path.getsize(zip_path)
    print(f"  -> Created {os.path.basename(zip_path):<30} : {sz / (1024*1024):8.2f} MB ({total_files} files)")
    return sz

def main():
    print("=== SIR ECOSYSTEM RELEASE PACKAGING PIPELINE ===")
    os.makedirs(PAYLOADS_DIR, exist_ok=True)
    os.makedirs(PKG_DIR, exist_ok=True)

    # 1. Build Modular Cloud Payloads
    print("[*] Generating modular compressed cloud payloads...")
    zip_directory(os.path.join(ROOT, 'instances', '26.2', 'minecraft', 'mods'), os.path.join(PAYLOADS_DIR, 'payload_mods_26.2.zip'))
    zip_directory(os.path.join(ROOT, 'instances', '1.8.9', 'minecraft', 'mods'), os.path.join(PAYLOADS_DIR, 'payload_mods_1.8.9.zip'))
    zip_directory(os.path.join(ROOT, 'resourcepacks'), os.path.join(PAYLOADS_DIR, 'payload_packs.zip'))
    zip_directory(os.path.join(ROOT, 'shaderpacks'), os.path.join(PAYLOADS_DIR, 'payload_shaders.zip'))
    zip_directory(os.path.join(ROOT, 'config'), os.path.join(PAYLOADS_DIR, 'payload_configs.zip'))

    # 2. Synchronize EXEs to SIR Package
    print("[*] Synchronizing standalone executables to SIR Package...")
    exes = ['SIR Launcher.exe', 'SIR Server Manager.exe', 'SIR Installer.exe', 'SIR_Icon.ico']
    for e in exes:
        src = os.path.join(ROOT, 'dist_apps', e) if e.endswith('.exe') else os.path.join(ROOT, e)
        if not os.path.exists(src):
            src = os.path.join(ROOT, e)
        if os.path.exists(src):
            dst = os.path.join(PKG_DIR, e)
            try:
                shutil.copy2(src, dst)
                print(f"  -> Synced {e} to SIR Package")
            except Exception as ex:
                print(f"  -> Warning copying {e}: {ex}")

    # 3. Create full standalone distribution zip
    print(f"[*] Packaging full offline release bundle -> {RELEASE_ZIP}...")
    zip_directory(PKG_DIR, RELEASE_ZIP)
    total_sz = os.path.getsize(RELEASE_ZIP)
    print(f"[+] Successfully built {os.path.basename(RELEASE_ZIP)}: {total_sz / (1024*1024):.2f} MB ({total_sz / (1024*1024*1024):.2f} GB)")
    print("=== PACKAGING COMPLETE ===")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
