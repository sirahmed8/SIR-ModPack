#!/usr/bin/env python3
"""Centralized Production Build Orchestrator for SIR Ecosystem.
Compiles the 3 standalone applications:
1. SIR Launcher.exe
2. SIR Server Manager.exe
3. SIR Installer.exe
"""
import os, sys, shutil, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist_apps')
BUILD = os.path.join(ROOT, 'build_apps')

SPECS = ['SIR Launcher.spec', 'SIR Server Manager.spec', 'SIR Installer.spec']

def main():
    print('=== SIR ECOSYSTEM MASTER BUILD PIPELINE ===')
    os.makedirs(DIST, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)

    pyinstaller_exe = r"C:\Users\a7med\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\pyinstaller.exe"
    if not os.path.isfile(pyinstaller_exe):
        pyinstaller_exe = "pyinstaller"

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
        os.path.expandvars(r'%APPDATA%\SIR ModPack')
    ]

    for item in exes:
        src = os.path.join(DIST, item) if item.endswith('.exe') else os.path.join(ROOT, item)
        if os.path.exists(src):
            for t in targets:
                if os.path.isdir(t):
                    dst = os.path.join(t, item)
                    try:
                        shutil.copy2(src, dst)
                        print(f'  -> Synchronized {item} to {t}')
                    except Exception as e:
                        print(f'  -> Warning on copy to {dst}: {e}')

    print('=== ALL 3 APPS COMPILED & SYNCHRONIZED ===')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
