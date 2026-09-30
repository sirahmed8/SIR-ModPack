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
DEV_DIR = os.path.join(ROOT, "development")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from shared_core.delta_patcher import DeltaPatcher

PKG_DIR = os.path.join(ROOT, 'SIR Package')
PAYLOADS_DIR = os.path.join(ROOT, 'dist_payloads')
RELEASE_ZIP = os.path.join(ROOT, 'SIR_Package_v1.0.0.zip')

def zip_directory(src_dir, zip_path, arc_prefix="", exclude_exts=None):
    """Compresses directory tree into a high-compression zip archive."""
    if not os.path.isdir(src_dir):
        print(f"[-] Warning: source directory {src_dir} does not exist.")
        return 0
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    total_files = 0
    exclude_exts = set(exclude_exts or [])
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                if exclude_exts and any(f.endswith(ext) for ext in exclude_exts):
                    continue
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, src_dir)
                arc_name = os.path.join(arc_prefix, rel) if arc_prefix else rel
                zf.write(fp, arc_name)
                total_files += 1
    sz = os.path.getsize(zip_path)
    print(f"  -> Created {os.path.basename(zip_path):<30} : {sz / (1024*1024):8.2f} MB ({total_files} files)")
    return sz

def link_or_copy_tree(src, dst):
    """Recursively synchronizes directory tree using NTFS hardlinks when possible, falling back to copy."""
    os.makedirs(dst, exist_ok=True)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        dest_root = os.path.join(dst, rel) if rel != '.' else dst
        for d in dirs:
            os.makedirs(os.path.join(dest_root, d), exist_ok=True)
        for f in files:
            s_f = os.path.join(root, f)
            d_f = os.path.join(dest_root, f)
            if os.path.exists(d_f):
                try:
                    if os.stat(s_f).st_ino == os.stat(d_f).st_ino:
                        continue
                    os.remove(d_f)
                except Exception:
                    pass
            try:
                os.link(s_f, d_f)
            except Exception:
                shutil.copy2(s_f, d_f)

def main():
    print("=== SIR ECOSYSTEM RELEASE PACKAGING PIPELINE ===", flush=True)
    os.makedirs(PAYLOADS_DIR, exist_ok=True)
    os.makedirs(PKG_DIR, exist_ok=True)

    # 1. Sync Live Ecosystem Components to Offline SIR Package
    print("[*] Synchronizing live ecosystem folders to SIR Package...", flush=True)
    
    # Sync core folders
    for d in ['shaderpacks', 'resourcepacks', 'config', 'capes', 'mods']:
        src = os.path.join(ROOT, d)
        dst = os.path.join(PKG_DIR, d)
        if os.path.isdir(src):
            link_or_copy_tree(src, dst)
            print(f"  -> Synced {d}/ to SIR Package (Hardlinked)", flush=True)

    # Sync only SIR ModPack instances (skip heavy third-party packs like ATM10/RLCraft)
    sir_inst_src = os.path.join(ROOT, 'instances')
    sir_inst_dst = os.path.join(PKG_DIR, 'instances')
    os.makedirs(sir_inst_dst, exist_ok=True)
    allowed_instances = ['26.2', '26.2-ultra', '26.2-balanced', '26.2-performance', '1.8.9', '1.8.9-ultra', '1.8.9-balanced', '1.8.9-performance']
    for inst_name in allowed_instances:
        s_p = os.path.join(sir_inst_src, inst_name)
        d_p = os.path.join(sir_inst_dst, inst_name)
        if os.path.isdir(s_p):
            link_or_copy_tree(s_p, d_p)
            print(f"  -> Synced instance {inst_name} to SIR Package (Hardlinked)", flush=True)

    # 2. Build Modular Cloud Payloads for Online Installer & Self-Healing
    print("[*] Generating modular compressed cloud payloads...", flush=True)
    zip_directory(os.path.join(ROOT, 'instances', '26.2-ultra', 'minecraft', 'mods'), os.path.join(PAYLOADS_DIR, 'payload_mods_26.2.zip'))
    zip_directory(os.path.join(ROOT, 'instances', '1.8.9-ultra', 'minecraft', 'mods'), os.path.join(PAYLOADS_DIR, 'payload_mods_1.8.9.zip'))
    zip_directory(os.path.join(ROOT, 'resourcepacks'), os.path.join(PAYLOADS_DIR, 'payload_packs.zip'))
    zip_directory(os.path.join(ROOT, 'shaderpacks'), os.path.join(PAYLOADS_DIR, 'payload_shaders.zip'))
    zip_directory(os.path.join(ROOT, 'config'), os.path.join(PAYLOADS_DIR, 'payload_configs.zip'))
    zip_directory(sir_inst_dst, os.path.join(PAYLOADS_DIR, 'payload_instances.zip'), exclude_exts=['.jar', '.zip'])

    # 3. Generate Binary Delta Manifest for Fast Differential OTA Updates
    print("[*] Generating SHA-256 binary delta manifest...", flush=True)
    patcher = DeltaPatcher(ROOT)
    manifest_path = os.path.join(ROOT, 'delta_manifest.json')
    manifest = patcher.generate_manifest(
        base_dir=ROOT,
        include_rel_dirs=[
            'mods', 'config', 'shaderpacks', 'resourcepacks', 'capes',
            'instances/26.2', 'instances/26.2-ultra', 'instances/26.2-balanced', 'instances/26.2-performance',
            'instances/1.8.9', 'instances/1.8.9-ultra', 'instances/1.8.9-balanced', 'instances/1.8.9-performance'
        ],
        output_file=manifest_path
    )
    print(f"  -> Generated delta_manifest.json ({manifest['total_files']} files, {manifest['total_size_bytes'] / (1024*1024):.1f} MB)", flush=True)

    # Distribute delta manifest to dist_payloads, SIR Package, public_repo, and website-next/public
    manifest_dests = [
        os.path.join(PAYLOADS_DIR, 'delta_manifest.json'),
        os.path.join(PKG_DIR, 'delta_manifest.json'),
        os.path.join(ROOT, 'public_repo', 'delta_manifest.json'),
        os.path.join(ROOT, 'website-next', 'public', 'delta_manifest.json')
    ]
    for m_dst in manifest_dests:
        try:
            os.makedirs(os.path.dirname(m_dst), exist_ok=True)
            shutil.copy2(manifest_path, m_dst)
            print(f"  -> Synced delta_manifest.json to {os.path.relpath(m_dst, ROOT)}", flush=True)
        except Exception as ex:
            print(f"  -> Warning syncing manifest to {m_dst}: {ex}")

    # 4. Build Portable SIR Apps Suite Zip
    print("[*] Packaging portable SIR Apps Suite...", flush=True)
    apps_zip = os.path.join(PAYLOADS_DIR, 'SIR_Apps_Suite.zip')
    with zipfile.ZipFile(apps_zip, 'w', zipfile.ZIP_DEFLATED) as z_apps:
        for app_f in ['SIR Launcher.exe', 'SIR Server Manager.exe', 'SIR Installer.exe', 'SIR_Icon.ico', 'README.md', 'delta_manifest.json']:
            ap_src = os.path.join(ROOT, 'dist_apps', app_f) if app_f.endswith('.exe') else os.path.join(ROOT, app_f)
            if not os.path.exists(ap_src):
                ap_src = os.path.join(ROOT, app_f)
            if os.path.exists(ap_src):
                z_apps.write(ap_src, app_f)
    print(f"  -> Created SIR_Apps_Suite.zip ({os.path.getsize(apps_zip)/(1024*1024):.2f} MB)", flush=True)

    # 4. Synchronize EXEs to SIR Package & public_repo
    print("[*] Synchronizing standalone executables to SIR Package & public_repo...")
    exes = ['SIR Launcher.exe', 'SIR Server Manager.exe', 'SIR Installer.exe', 'SIR_Icon.ico']
    pub_dir = os.path.join(ROOT, 'public_repo')
    for e in exes:
        src = os.path.join(ROOT, 'dist_apps', e) if e.endswith('.exe') else os.path.join(ROOT, e)
        if not os.path.exists(src):
            src = os.path.join(ROOT, e)
        if os.path.exists(src):
            for dest in [PKG_DIR, pub_dir]:
                if os.path.isdir(dest):
                    try:
                        shutil.copy2(src, os.path.join(dest, e))
                    except Exception:
                        pass
            print(f"  -> Synced {e} to SIR Package and public_repo")

    # 4. Standalone distribution zip (Only when requested via --make-zip)
    make_zip = '--make-zip' in sys.argv
    if make_zip:
        print(f"[*] Packaging full offline release bundle -> {RELEASE_ZIP}...")
        zip_directory(PKG_DIR, RELEASE_ZIP)
        total_sz = os.path.getsize(RELEASE_ZIP)
        print(f"[+] Successfully built {os.path.basename(RELEASE_ZIP)}: {total_sz / (1024*1024):.2f} MB ({total_sz / (1024*1024*1024):.2f} GB)")

        if os.path.isdir(pub_dir):
            pub_zip = os.path.join(pub_dir, 'SIR_Package_v1.0.0.zip')
            try:
                shutil.copy2(RELEASE_ZIP, pub_zip)
                print(f"[+] Synced {os.path.basename(RELEASE_ZIP)} to public_repo/")
            except Exception as ex:
                print(f"  -> Warning copying zip to public_repo: {ex}")
    else:
        print("[*] Skipped full zip creation (SIR Package folder is 100% updated and ready). Pass --make-zip when ready to build the release archive.")

    print("=== PACKAGING COMPLETE ===")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
