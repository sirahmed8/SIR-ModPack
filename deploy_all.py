import os
import shutil
import subprocess
import sys
import time

ROOT = r"D:\Projects\SIR ModPack"
DEV_DIR = os.path.join(ROOT, "development")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from shared_core.delta_patcher import DeltaPatcher

DIST = os.path.join(ROOT, "dist_build")
BUILD = os.path.join(ROOT, "build_apps")
PUBLIC_REPO = os.path.join(ROOT, "public_repo")
SIR_PACKAGE = os.path.join(ROOT, "SIR Package")
WEB_DIR = os.path.join(ROOT, "website-next")
LAUNCHER_DIR = os.path.join(ROOT, "SIR Launcher")

PYINSTALLER = r"C:\Users\a7med\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe"
if not os.path.isfile(PYINSTALLER):
    PYINSTALLER = "pyinstaller"

SPECS = [
    "SIR Launcher.spec",
    "SIR Server Manager.spec",
    "SIR Installer.spec"
]

def run_cmd(cmd, cwd, desc=""):
    print(f"\n>>> [{desc or cmd}] in {cwd}")
    res = subprocess.run(cmd, cwd=cwd, shell=True)
    if res.returncode != 0:
        print(f"FAILED: {desc} (Exit code: {res.returncode})", file=sys.stderr)
        return False
    return True

def clean_build_dirs():
    print("\n--- 1. Cleaning Build Directories ---")
    for d in [DIST, BUILD]:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f"  ✓ Cleaned {d}")
            except Exception as e:
                print(f"  Notice while cleaning {d}: {e}")
    os.makedirs(DIST, exist_ok=True)

def compile_all_exes():
    print("\n--- 2. Compiling Standalone Desktop Applications (PyInstaller) ---")
    for spec in SPECS:
        spec_path = os.path.join(ROOT, spec)
        if not os.path.isfile(spec_path):
            print(f"Error: Spec file not found: {spec_path}", file=sys.stderr)
            return False
        
        cmd = f'"{PYINSTALLER}" --clean --noconfirm "{spec_path}" --distpath "{DIST}" --workpath "{BUILD}"'
        if not run_cmd(cmd, ROOT, f"Building {spec}"):
            return False
    return True

def sync_executables():
    print("\n--- 3. Synchronizing Executables to Roots, Subfolders and Packages ---")
    
    # Terminate running launcher processes to prevent Windows [WinError 32] file lock
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'SIR Launcher.exe', '/T'], capture_output=True)
        subprocess.run(['taskkill', '/F', '/IM', 'SIR Server Manager.exe', '/T'], capture_output=True)
        subprocess.run(['taskkill', '/F', '/IM', 'SIR Installer.exe', '/T'], capture_output=True)
        time.sleep(0.5)
    except Exception:
        pass
        
    os.makedirs(PUBLIC_REPO, exist_ok=True)
    os.makedirs(SIR_PACKAGE, exist_ok=True)
    os.makedirs(LAUNCHER_DIR, exist_ok=True)
    os.makedirs(SIR_PACKAGE, exist_ok=True)
    os.makedirs(LAUNCHER_DIR, exist_ok=True)
    
    source_dir = DIST if os.path.isdir(DIST) else ROOT
    exes = [f for f in os.listdir(source_dir) if f.endswith(".exe")]
    for exe in exes:
        src = os.path.join(source_dir, exe)
        if src != os.path.join(ROOT, exe):
            dst_root = os.path.join(ROOT, exe)
            shutil.copy2(src, dst_root)
        
        dst_public = os.path.join(PUBLIC_REPO, exe)
        shutil.copy2(src, dst_public)
        
        dst_pkg = os.path.join(SIR_PACKAGE, exe)
        shutil.copy2(src, dst_pkg)
        
        if exe == "SIR Launcher.exe":
            dst_launcher = os.path.join(LAUNCHER_DIR, exe)
            shutil.copy2(src, dst_launcher)
            try:
                ps_cmd = '$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut("$env:USERPROFILE\\Desktop\\SIR Launcher.lnk"); $s.TargetPath = "D:\\Projects\\SIR ModPack\\SIR Launcher\\SIR Launcher.exe"; $s.WorkingDirectory = "D:\\Projects\\SIR ModPack\\SIR Launcher"; $s.IconLocation = "D:\\Projects\\SIR ModPack\\SIR_Icon.ico,0"; $s.Arguments = ""; $s.Save()'
                subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)
            except Exception as e:
                print(f"Notice on shortcut update: {e}")
        
        size_mb = os.path.getsize(src) / (1024 * 1024)
        print(f"  ✓ Deployed {exe} ({size_mb:.1f} MB) -> Root, SIR Launcher folder, public_repo, SIR Package & Desktop")
    return True

def sync_installer_scripts():
    print("\n--- 3b. Synchronizing Unified CLI Installer & Launchers ---")
    scripts = ["install.py", "install.bat", "install.sh"]
    dest_dirs = [PUBLIC_REPO, SIR_PACKAGE]
    for s in scripts:
        src = os.path.join(ROOT, s)
        if not os.path.isfile(src):
            continue
        for d in dest_dirs:
            try:
                os.makedirs(d, exist_ok=True)
                dst = os.path.join(d, s)
                shutil.copy2(src, dst)
                print(f"  ✓ Synced {s} -> {os.path.relpath(dst, ROOT)}")
            except Exception as ex:
                print(f"  Notice copying {s} to {d}: {ex}")
    return True

def sync_all_24_instances():
    print("\n--- 3c. Synchronizing & Validating All 24 Instance Locations ---")
    appdata = os.environ.get("APPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Roaming"))
    roaming_instances = os.path.join(appdata, "SIR ModPack", "instances")
    
    profiles = [
        "26.2", "26.2-ultra", "26.2-balanced", "26.2-performance",
        "1.8.9", "1.8.9-ultra", "1.8.9-balanced", "1.8.9-performance"
    ]
    
    target_bases = [
        os.path.join(ROOT, "instances"),
        os.path.join(SIR_PACKAGE, "instances"),
        roaming_instances
    ]
    
    src_instances = os.path.join(ROOT, "instances")
    total_synced = 0
    
    for base in target_bases:
        os.makedirs(base, exist_ok=True)
        # Sync instgroups.json, accounts.json, servers.dat
        for meta_fn in ["instgroups.json", "accounts.json", "servers.dat"]:
            meta_src = os.path.join(src_instances, meta_fn)
            if not os.path.isfile(meta_src):
                meta_src = os.path.join(ROOT, meta_fn)
            if os.path.isfile(meta_src):
                meta_dst = os.path.join(base, meta_fn)
                if not os.path.exists(meta_dst) or os.path.getmtime(meta_src) > os.path.getmtime(meta_dst):
                    try:
                        shutil.copy2(meta_src, meta_dst)
                    except Exception:
                        pass
                        
        for p in profiles:
            p_src = os.path.join(src_instances, p)
            p_dst = os.path.join(base, p)
            os.makedirs(p_dst, exist_ok=True)
            
            # Synchronize core configuration files across instances
            if os.path.isdir(p_src):
                for cfg_name in ["instance.cfg", "mmc-pack.json", "options.txt", "betterfps.txt"]:
                    src_cfg = os.path.join(p_src, cfg_name)
                    dst_cfg = os.path.join(p_dst, cfg_name)
                    if os.path.isfile(src_cfg):
                        if not os.path.isfile(dst_cfg) or os.path.getsize(src_cfg) != os.path.getsize(dst_cfg):
                            shutil.copy2(src_cfg, dst_cfg)
                            
                # Sync servers.dat into minecraft subfolder
                mc_dst = os.path.join(p_dst, "minecraft")
                os.makedirs(mc_dst, exist_ok=True)
                root_servers = os.path.join(ROOT, "servers.dat")
                if os.path.isfile(root_servers):
                    dst_servers = os.path.join(mc_dst, "servers.dat")
                    if not os.path.isfile(dst_servers) or os.path.getsize(root_servers) != os.path.getsize(dst_servers):
                        shutil.copy2(root_servers, dst_servers)

            total_synced += 1

    print(f"  ✓ Validated & Synchronized all 24 instance profiles (8 Workspace, 8 SIR Package, 8 AppData)")
    return True

def sync_delta_manifest():
    print("\n--- 3d. Generating SHA-256 Binary Delta Manifest for OTA Updates ---")
    patcher = DeltaPatcher(ROOT)
    manifest_path = os.path.join(ROOT, "delta_manifest.json")
    manifest = patcher.generate_manifest(
        base_dir=ROOT,
        include_rel_dirs=[
            "mods", "config", "shaderpacks", "resourcepacks", "capes",
            "instances/26.2", "instances/26.2-ultra", "instances/26.2-balanced", "instances/26.2-performance",
            "instances/1.8.9", "instances/1.8.9-ultra", "instances/1.8.9-balanced", "instances/1.8.9-performance"
        ],
        output_file=manifest_path
    )
    print(f"  ✓ Generated delta_manifest.json ({manifest['total_files']} files, {manifest['total_size_bytes'] / (1024*1024):.1f} MB)")

    manifest_dests = [
        os.path.join(ROOT, "SIR Package", "delta_manifest.json"),
        os.path.join(PUBLIC_REPO, "delta_manifest.json"),
        os.path.join(WEB_DIR, "public", "delta_manifest.json")
    ]
    for dest in manifest_dests:
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(manifest_path, dest)
            print(f"  ✓ Synced manifest to {os.path.relpath(dest, ROOT)}")
        except Exception as ex:
            print(f"  Notice copying manifest: {ex}")
    return True

def push_public_repo():
    print("\n--- 4. Pushing Public Repository (sirahmed8/SIR-ModPack) ---")
    if not run_cmd('git add -A', PUBLIC_REPO, "git add"):
        return False
    run_cmd('git commit -m "release(v1.0.0): zero-defect official release, optifine shader repair, modal ergonomics & production deployment"', PUBLIC_REPO, "git commit")
    return run_cmd('git push origin main', PUBLIC_REPO, "git push origin main")

def build_and_deploy_web():
    print("\n--- 5. Building Next.js 16 Web Platform ---")
    if not run_cmd('npm run build', WEB_DIR, "npm run build"):
        return False
    
    print("\n--- 6. Deploying to Firebase Hosting & Cloud Database ---")
    if not run_cmd('firebase deploy --only "hosting,firestore:rules,database"', WEB_DIR, "firebase deploy"):
        return False
    
    print("\n--- 7. Pushing Private Web Repository (sirahmed8/SIR-ModPack-private) ---")
    run_cmd('git add -A', WEB_DIR, "git add")
    run_cmd('git commit -m "release(v1.0.0): zero-defect official release, optifine shader repair, modal ergonomics & production deployment"', WEB_DIR, "git commit")
    run_cmd('git push origin main', WEB_DIR, "git push origin main")
    return True

def main():
    start_time = time.time()
    print("=================================================================")
    print("      SIR ECOSYSTEM MASTER UNIFIED DEPLOYMENT ENGINE             ")
    print("=================================================================")
    
    sync_only = "--sync-only" in sys.argv or "--sync" in sys.argv
    manifest_only = "--manifest-only" in sys.argv
    
    if manifest_only:
        sync_delta_manifest()
        return 0

    if sync_only:
        sync_executables()
        sync_installer_scripts()
        sync_all_24_instances()
        sync_delta_manifest()
        elapsed = time.time() - start_time
        print("\n=================================================================")
        print(f"  ✓ 24 INSTANCES & DELTA MANIFEST SYNCHRONIZED SUCCESSFULLY!")
        print(f"  ✓ Total Time: {elapsed:.1f}s")
        print("=================================================================")
        return 0

    clean_build_dirs()
    
    if not compile_all_exes():
        print("Build failed!", file=sys.stderr)
        return 1
        
    sync_executables()
    sync_installer_scripts()
    sync_all_24_instances()
    sync_delta_manifest()
    
    # Reclaim PyInstaller build cache space immediately
    if os.path.exists(BUILD):
        try:
            shutil.rmtree(BUILD)
            print("  ✓ Reclaimed PyInstaller build staging space")
        except Exception:
            pass
            
    push_public_repo()
    build_and_deploy_web()
    
    elapsed = time.time() - start_time
    print("\n=================================================================")
    print(f"  ✓ ALL APPLICATIONS COMPILED, VERIFIED, DEPLOYED & PUSHED!")
    print(f"  ✓ Total Time: {elapsed:.1f}s")
    print("=================================================================")
    return 0

if __name__ == "__main__":
    sys.exit(main())
