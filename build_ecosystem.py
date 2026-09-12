#!/usr/bin/env python3
"""Centralized Release Build Orchestrator for SIR Ecosystem.
Compiles the 3 standalone applications:
1. SIR Launcher.exe
2. SIR Server Manager.exe
3. SIR Installer.exe
"""
import os, sys, shutil, subprocess, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist_apps')
BUILD = os.path.join(ROOT, 'build_apps')

SPECS = ['SIR Launcher.spec', 'SIR Server Manager.spec', 'SIR Installer.spec']

def link_or_copy(src, dst):
    if os.path.abspath(src) == os.path.abspath(dst):
        return
    if os.path.splitdrive(src)[0].upper() == os.path.splitdrive(dst)[0].upper():
        try:
            if os.path.exists(dst):
                if os.stat(src).st_ino == os.stat(dst).st_ino:
                    return
                os.remove(dst)
            os.link(src, dst)
            return
        except Exception:
            pass
    shutil.copy2(src, dst)


def main():
    print('=== SIR ECOSYSTEM MASTER BUILD PIPELINE ===')
    os.makedirs(DIST, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)

    pyinstaller_exe = r"C:\Users\a7med\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe"
    if not os.path.isfile(pyinstaller_exe):
        pyinstaller_exe = "pyinstaller"

    sync_only = "--sync-only" in sys.argv

    if not sync_only:
        for spec in SPECS:
            spec_path = os.path.join(ROOT, spec)
            if not os.path.isfile(spec_path):
                print(f'ERROR: Missing {spec_path}', file=sys.stderr)
                continue
            print(f'[*] Compiling {spec}...')
            cmd = ["py", "-3.13", "-m", "PyInstaller", "--clean", "--noconfirm", spec_path, "--distpath", DIST, "--workpath", BUILD]
            res = subprocess.run(cmd, cwd=ROOT)
            if res.returncode != 0:
                print(f'[-] Build failed for {spec}', file=sys.stderr)
                return res.returncode
            print(f'[+] Successfully built {spec}')

    exes = ['SIR Launcher.exe', 'SIR Server Manager.exe', 'SIR Installer.exe', 'SIR_Icon.ico']
    targets = [
        ROOT,
        os.path.join(ROOT, 'public_repo'),
        os.path.join(ROOT, 'SIR Package'),
        os.path.join(ROOT, 'SIR Launcher'),
        os.path.expandvars(r'%APPDATA%\SIR ModPack'),
        os.path.expandvars(r'%APPDATA%\SIR ModPack\SIR Launcher'),
        os.path.join(ROOT, 'website-next', 'public', 'share'),
        os.path.join(ROOT, 'website-next', 'out', 'share')
    ]

    for item in exes:
        src = os.path.join(DIST, item) if item.endswith('.exe') else os.path.join(ROOT, item)
        if not os.path.exists(src) and item.endswith('.exe'):
            src = os.path.join(ROOT, item)
        if os.path.exists(src):
            for t in targets:
                if os.path.isdir(t):
                    dst = os.path.join(t, item)
                    try:
                        link_or_copy(src, dst)
                        print(f'  -> Synchronized {item} to {t}')
                    except Exception as e:
                        print(f'  -> Warning on copy to {dst}: {e}')

    # Build SIR_Apps_Suite.zip containing all 3 apps and icon
    zip_name = "SIR_Apps_Suite.zip"
    zip_dist_path = os.path.join(DIST, zip_name)
    print(f"[*] Packaging {zip_name}...")
    with zipfile.ZipFile(zip_dist_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in exes:
            item_path = os.path.join(DIST, item) if item.endswith('.exe') else os.path.join(ROOT, item)
            if not os.path.exists(item_path):
                item_path = os.path.join(ROOT, item)
            if os.path.isfile(item_path):
                zf.write(item_path, arcname=item)
    print(f"[+] Created {zip_name} ({os.path.getsize(zip_dist_path) / 1024 / 1024:.2f} MB)")

    suite_targets = [
        ROOT,
        os.path.expandvars(r'%APPDATA%\SIR ModPack')
    ]
    for st in suite_targets:
        if os.path.isdir(st):
            dst = os.path.join(st, zip_name)
            if os.path.abspath(zip_dist_path) != os.path.abspath(dst):
                try:
                    shutil.copy2(zip_dist_path, dst)
                    print(f'  -> Synchronized {zip_name} to {st}')
                except Exception as e:
                    print(f'  -> Warning on copy {zip_name} to {dst}: {e}')

    if os.path.exists(BUILD):
        shutil.rmtree(BUILD, ignore_errors=True)

    print('=== ALL 3 APPS & SUITE ZIP COMPILED & SYNCHRONIZED ===')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
