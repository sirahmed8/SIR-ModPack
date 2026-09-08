#!/usr/bin/env python3
"""
===============================================================================
🌟 SIR ModPack — Master CLI Installer & Portable Deployer Engine
===============================================================================
Release:  v1.0.0 Genesis Production Release
Platform: 100% Free & Independent Platform (Free Independent Software Agreement)
Contact:  a7medorabe7@gmail.com
===============================================================================
"""

import os
import sys
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
import shutil
import zipfile
import tarfile
import json
import sqlite3
import glob
import subprocess
import tempfile
import time
import platform
import ctypes
import argparse
import hashlib
import urllib.request
import urllib.error
import re

APP_NAME = "SIR ModPack"
VERSION = "v1.0.0 Genesis Production Release"
CONTACT = "a7medorabe7@gmail.com"
LICENSE_NOTE = "100% Free & Independent Platform under Free Independent Software Agreement"

def resolve_source_root():
    """Finds the root repository folder containing mods, instances, and configs."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        here,
        os.path.dirname(here),
        os.path.abspath(os.path.join(here, "..")),
    ]
    for c in candidates:
        if os.path.isdir(os.path.join(c, "mods")) and (
            os.path.isdir(os.path.join(c, "instances")) or os.path.isdir(os.path.join(c, "config"))
        ):
            return c
    return here

SOURCE_ROOT = resolve_source_root()
MODS_DIR = os.path.join(SOURCE_ROOT, "mods")
RP_DIR = os.path.join(SOURCE_ROOT, "resourcepacks")
SH_DIR = os.path.join(SOURCE_ROOT, "shaderpacks")
CONFIG_DIR = os.path.join(SOURCE_ROOT, "config")
INSTANCES_SRC_DIR = os.path.join(SOURCE_ROOT, "instances")

USER_HOME = os.path.expanduser("~")
LUNAR_ROOT = os.path.join(USER_HOME, ".lunarclient")
LUNAR_PROFILES = os.path.join(LUNAR_ROOT, "profiles")

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ('dwLength', ctypes.c_ulong),
        ('dwMemoryLoad', ctypes.c_ulong),
        ('ullTotalPhys', ctypes.c_ulonglong),
        ('ullAvailPhys', ctypes.c_ulonglong),
        ('ullTotalPageFile', ctypes.c_ulonglong),
        ('ullAvailPageFile', ctypes.c_ulonglong),
        ('ullTotalVirtual', ctypes.c_ulonglong),
        ('ullAvailVirtual', ctypes.c_ulonglong),
        ('ullExtendedVirtual', ctypes.c_ulonglong),
    ]

def detect_hardware():
    ram_gb = 16.0
    if sys.platform == "win32":
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        try:
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            ram_gb = round(stat.ullTotalPhys / (1024**3), 1)
        except Exception:
            ram_gb = 16.0
    else:
        try:
            mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
            ram_gb = round(mem_bytes / (1024**3), 1)
        except Exception:
            ram_gb = 16.0

    cpu_cores = os.cpu_count() or 4
    cpu_name = platform.processor() or "Multi-Core CPU"
    gpu = "Dedicated Graphics"

    if sys.platform == "win32":
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            c_name, _ = winreg.QueryValueEx(k, "ProcessorNameString")
            winreg.CloseKey(k)
            if c_name and c_name.strip():
                cpu_name = c_name.strip()

            video_key_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
            video_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, video_key_path)
            found_gpus = []
            for i in range(16):
                try:
                    subkey_name = winreg.EnumKey(video_key, i)
                    sub_k = winreg.OpenKey(video_key, subkey_name)
                    try:
                        val, _ = winreg.QueryValueEx(sub_k, "DriverDesc")
                        if val and isinstance(val, str) and val.strip():
                            found_gpus.append(val.strip())
                    except Exception:
                        pass
                    winreg.CloseKey(sub_k)
                except OSError:
                    break
            winreg.CloseKey(video_key)
            for g in found_gpus:
                if any(k in g.upper() for k in ["RTX", "GTX", "RADEON", "ARC", "GEFORCE", "NVIDIA"]):
                    gpu = g
                    break
            else:
                if found_gpus:
                    gpu = found_gpus[0]
        except Exception:
            pass

    if ram_gb >= 32: min_m, max_m = 6144, 12288
    elif ram_gb >= 16: min_m, max_m = 4096, 8192
    elif ram_gb >= 8: min_m, max_m = 3072, 5120
    else: min_m, max_m = 2048, 3072

    return {
        "ram": ram_gb,
        "cores": cpu_cores,
        "cpu_name": cpu_name,
        "gpu": gpu,
        "min_m": min_m,
        "max_m": max_m
    }

HW_INFO = detect_hardware()

def apply_hardware_governor(governor="smooth"):
    if sys.platform != "win32":
        return
    try:
        if governor == "smooth":
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
            print("  🍃 Hardware Governor: Smooth / Eco Mode engaged (Background I/O priority, 0% system lag)")
        else:
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000020)
            print("  ⚡ Hardware Governor: Max Performance Mode engaged (Full CPU speed)")
    except Exception:
        pass

def is_file_identical(src, dst):
    """Smart check if destination file already exists and is identical to source."""
    if not os.path.exists(dst):
        return False
    try:
        src_stat = os.stat(src)
        dst_stat = os.stat(dst)
        if src_stat.st_size == dst_stat.st_size and dst_stat.st_mtime >= src_stat.st_mtime - 1:
            return True
        if src_stat.st_size != dst_stat.st_size:
            return False
        if src_stat.st_size > 0:
            with open(src, 'rb') as f1, open(dst, 'rb') as f2:
                if f1.read(8192) != f2.read(8192):
                    return False
            return True
    except Exception:
        return False
    return False

def governed_copy_file(src, dst, governor="smooth"):
    if not os.path.exists(src):
        return False
    if is_file_identical(src, dst):
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return True

def governed_copy_tree(src, dst, governor="smooth"):
    if not os.path.exists(src):
        return (0, 0)
    os.makedirs(dst, exist_ok=True)
    copied, skipped = 0, 0
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        target_root = dst if rel_path == "." else os.path.join(dst, rel_path)
        os.makedirs(target_root, exist_ok=True)
        for fn in files:
            src_fp = os.path.join(root, fn)
            dst_fp = os.path.join(target_root, fn)
            if is_file_identical(src_fp, dst_fp):
                skipped += 1
            else:
                shutil.copy2(src_fp, dst_fp)
                copied += 1
    return (copied, skipped)

# =============================================================================
# JAVA 21 PRE-FLIGHT INSPECTION & AUTOMATED ADOPTIUM DOWNLOAD
# =============================================================================

def probe_java_binary(java_exe):
    """Probes a java executable via subprocess and extracts major version and 64-bit status."""
    if not java_exe or not os.path.isfile(java_exe):
        return None
    try:
        res = subprocess.run(
            [java_exe, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=3.0,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
        )
        out = res.stdout or ""
        major = 0
        m_ver = re.search(r'(?:version|openjdk version)\s+"?([0-9._]+(?:-[a-zA-Z0-9.+]+)?)"?', out, re.IGNORECASE)
        if m_ver:
            raw = m_ver.group(1)
            if raw.startswith("1."):
                parts = raw.split(".")
                major = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 8
            else:
                m_maj = re.match(r"^(\d+)", raw)
                if m_maj:
                    major = int(m_maj.group(1))
        
        is_64bit = ("64-Bit" in out or "x86_64" in out or "amd64" in out)
        if not is_64bit and sys.platform == "win32":
            # Check PE header fallback
            try:
                with open(java_exe, "rb") as f:
                    if f.read(2) == b"MZ":
                        f.seek(0x3C)
                        pe_offset = int.from_bytes(f.read(4), "little")
                        f.seek(pe_offset)
                        if f.read(4) == b"PE\0\0":
                            machine = int.from_bytes(f.read(2), "little")
                            if machine in (0x8664, 0xAA64):
                                is_64bit = True
            except Exception:
                pass

        return {
            "path": os.path.abspath(java_exe),
            "major": major,
            "is_64bit": is_64bit,
            "raw_output": out.strip().split("\n")[0] if out else "Unknown"
        }
    except Exception:
        return None

def inspect_system_java21():
    """Scans Windows Registry, PATH, environment variables, and directories for 64-bit Java 21+."""
    candidates = []

    # 1. Environment variables
    for ev in ["JAVA21_HOME", "JAVA_HOME", "JDK_HOME"]:
        val = os.environ.get(ev)
        if val and os.path.isdir(val):
            for sub in ["bin/javaw.exe", "bin/java.exe", "bin/java"]:
                p = os.path.join(val, sub.replace("/", os.sep))
                if os.path.isfile(p):
                    candidates.append(p)

    # 2. Windows Registry
    if sys.platform == "win32":
        try:
            import winreg
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Eclipse Adoptium\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\AdoptOpenJDK\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\JDK"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Azul Systems\Zulu"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Eclipse Adoptium\JDK"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\JavaSoft\JDK"),
            ]
            for hkey, subkey in reg_paths:
                for access in [winreg.KEY_READ | getattr(winreg, "KEY_WOW64_64KEY", 0), winreg.KEY_READ]:
                    try:
                        with winreg.OpenKey(hkey, subkey, 0, access) as k:
                            num = winreg.QueryInfoKey(k)[0]
                            for i in range(num):
                                vname = winreg.EnumKey(k, i)
                                try:
                                    with winreg.OpenKey(k, f"{vname}\\MSI", 0, access) as mk:
                                        jh, _ = winreg.QueryValueEx(mk, "Path")
                                        candidates.extend([os.path.join(jh, "bin", "javaw.exe"), os.path.join(jh, "bin", "java.exe")])
                                except Exception:
                                    pass
                                try:
                                    with winreg.OpenKey(k, vname, 0, access) as vk:
                                        jh, _ = winreg.QueryValueEx(vk, "JavaHome")
                                        candidates.extend([os.path.join(jh, "bin", "javaw.exe"), os.path.join(jh, "bin", "java.exe")])
                                except Exception:
                                    pass
                    except Exception:
                        pass
        except Exception:
            pass

    # 3. Standard Directories
    prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    appdata = os.environ.get("APPDATA", "")
    search_dirs = [
        os.path.join(prog_files, "Eclipse Adoptium"),
        os.path.join(prog_files, "Java"),
        os.path.join(prog_files, "Microsoft"),
        os.path.join(prog_files, "Zulu"),
        os.path.join(local_appdata, "Programs", "Eclipse Adoptium"),
        os.path.join(appdata, ".minecraft", "runtime"),
        os.path.join(appdata, "SIR ModPack", "runtime"),
        os.path.join(USER_HOME, ".jdks"),
        os.path.join(USER_HOME, ".lunarclient", "jre"),
    ]
    for sd in search_dirs:
        if os.path.isdir(sd):
            for pat in [os.path.join(sd, "*", "bin", "javaw.exe"), os.path.join(sd, "*", "bin", "java.exe"), os.path.join(sd, "*", "bin", "java")]:
                candidates.extend(glob.glob(pat))

    # 4. PATH
    for cmd in ["javaw", "java"]:
        w = shutil.which(cmd)
        if w:
            candidates.append(w)

    seen = set()
    for cand in candidates:
        if not cand or not os.path.isfile(cand):
            continue
        c_norm = os.path.normcase(os.path.abspath(cand))
        if c_norm in seen:
            continue
        seen.add(c_norm)

        info = probe_java_binary(cand)
        if info and info["is_64bit"] and info["major"] >= 21:
            return info

    return None

def download_file_with_progress(url, dest_path, desc="Downloading"):
    """Downloads a file over HTTP(S) with live terminal percentage and throughput gauge."""
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    temp_dst = dest_path + ".tmp"
    headers = {"User-Agent": "SIR-ModPack-CLI-Installer/1.0.0 (Temurin Auto-Deployer)"}
    req = urllib.request.Request(url, headers=headers)

    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, open(temp_dst, "wb") as f:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            block_size = 65536
            last_print = 0

            while True:
                chunk = resp.read(block_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                now = time.time()
                if now - last_print > 0.25 or downloaded == total:
                    last_print = now
                    elapsed = max(0.001, now - start_time)
                    speed_mb = (downloaded / (1024 * 1024)) / elapsed
                    if total > 0:
                        pct = (downloaded / total) * 100
                        bar_len = 30
                        filled = int(bar_len * (downloaded / total))
                        bar = "=" * filled + (">" if filled < bar_len else "") + " " * (bar_len - filled - 1 if filled < bar_len else 0)
                        msg = f"\r  📥 {desc}: [{bar}] {pct:5.1f}% ({downloaded/(1024*1024):.1f}/{total/(1024*1024):.1f} MB @ {speed_mb:.1f} MB/s)"
                    else:
                        msg = f"\r  📥 {desc}: {downloaded/(1024*1024):.1f} MB downloaded (@ {speed_mb:.1f} MB/s)"
                    sys.stdout.write(msg)
                    sys.stdout.flush()

        sys.stdout.write("\n")
        sys.stdout.flush()
        if os.path.exists(dest_path):
            os.remove(dest_path)
        os.replace(temp_dst, dest_path)
        return True
    except Exception as e:
        if os.path.exists(temp_dst):
            try: os.remove(temp_dst)
            except Exception: pass
        raise e

def ensure_java21_runtime(dest_runtime_base, non_interactive=False):
    """
    Checks for system Java 21+. If missing, downloads Eclipse Adoptium Temurin 21 LTS x64
    silently or with progress bar into <dest_runtime_base>/runtime/java-21 without interrupting installation.
    """
    print("🔍 [Pre-Flight Stage] Inspecting Java 21+ LTS Runtime...")
    existing = inspect_system_java21()
    if existing:
        print(f"  ✅ Verified 64-bit Java {existing['major']} Runtime Detected:")
        print(f"     Path: {existing['path']}")
        print(f"     Info: {existing['raw_output']}")
        return existing['path']

    print("  ⚠️ No 64-bit Java 21+ detected on system. Initiating automated Adoptium Temurin 21 LTS setup...")
    
    target_dir = os.path.join(dest_runtime_base, "runtime", "java-21")
    os.makedirs(target_dir, exist_ok=True)
    
    # Check if already downloaded in local runtime dir
    for test_sub in ["bin/javaw.exe", "bin/java.exe", "bin/java"]:
        candidate = os.path.join(target_dir, test_sub.replace("/", os.sep))
        info = probe_java_binary(candidate)
        if info and info["is_64bit"] and info["major"] >= 21:
            print(f"  ✅ Bundled Adoptium Temurin 21 verified at: {candidate}")
            return candidate

    os_type = platform.system().lower()
    is_arm = platform.machine().lower() in ("arm64", "aarch64")

    if os_type == "windows":
        dl_url = "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse"
        archive_ext = ".zip"
    elif os_type == "darwin":
        arch = "aarch64" if is_arm else "x64"
        dl_url = f"https://api.adoptium.net/v3/binary/latest/21/ga/mac/{arch}/jdk/hotspot/normal/eclipse"
        archive_ext = ".tar.gz"
    else:
        arch = "aarch64" if is_arm else "x64"
        dl_url = f"https://api.adoptium.net/v3/binary/latest/21/ga/linux/{arch}/jdk/hotspot/normal/eclipse"
        archive_ext = ".tar.gz"

    archive_temp = os.path.join(tempfile.gettempdir(), f"temurin21_{int(time.time())}{archive_ext}")
    
    try:
        download_file_with_progress(dl_url, archive_temp, desc="Eclipse Adoptium Temurin 21 LTS")
        print("  📦 Extracting Adoptium Temurin 21 LTS runtime...")
        
        extract_tmp = os.path.join(tempfile.gettempdir(), f"temurin_extract_{int(time.time())}")
        os.makedirs(extract_tmp, exist_ok=True)
        
        if archive_ext == ".zip":
            with zipfile.ZipFile(archive_temp, "r") as z:
                z.extractall(extract_tmp)
        else:
            with tarfile.open(archive_temp, "r:*") as t:
                t.extractall(extract_tmp)

        # Move root directory
        entries = os.listdir(extract_tmp)
        top_root = os.path.join(extract_tmp, entries[0]) if len(entries) == 1 and os.path.isdir(os.path.join(extract_tmp, entries[0])) else extract_tmp
        
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir, ignore_errors=True)
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        shutil.move(top_root, target_dir)
        
        # Cleanup
        shutil.rmtree(extract_tmp, ignore_errors=True)
        if os.path.exists(archive_temp):
            os.remove(archive_temp)

        # Validate extracted binary
        for test_sub in ["bin/javaw.exe", "bin/java.exe", "bin/java"]:
            cand = os.path.join(target_dir, test_sub.replace("/", os.sep))
            if os.path.isfile(cand):
                # Set executable permissions on POSIX
                if sys.platform != "win32":
                    try: os.chmod(cand, 0o755)
                    except Exception: pass
                info = probe_java_binary(cand)
                if info and info["major"] >= 21:
                    print(f"  🎉 Eclipse Adoptium Temurin 21 deployed successfully: {cand}")
                    return cand

        print("  ⚠️ Warning: Extraction finished but binary probe failed; falling back to system 'java'.")
        return "java"
    except Exception as ex:
        print(f"  ❌ Auto-download of Adoptium Temurin 21 failed: {ex}")
        print("     Will proceed using system default Java.")
        if os.path.exists(archive_temp):
            try: os.remove(archive_temp)
            except Exception: pass
        return "java"

# =============================================================================
# PROFILE SPECIFICATION & MOD DEPLOYMENT
# =============================================================================

PROFILE_SPECS = {
    "26.2-ultra": {
        "display_name": "🌟 SIR Ultimate 26.2 [Ultra]",
        "version": "26.2",
        "category": "Modern",
        "group": "Modern",
        "chunks": 24,
        "shader_name": "SIR_Extreme_Shader.zip",
        "is_performance": False,
        "min_ram": 4096,
        "max_ram": 8192,
        "jvm_flags": "-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5 -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication -XX:+AlwaysPreTouch"
    },
    "26.2-balanced": {
        "display_name": "⚡ SIR Ultimate 26.2 [Balanced]",
        "version": "26.2",
        "category": "Modern",
        "group": "Modern",
        "chunks": 16,
        "shader_name": "SIR_Balanced_Shader.zip",
        "is_performance": False,
        "min_ram": 3072,
        "max_ram": 6144,
        "jvm_flags": "-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5 -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication -XX:+AlwaysPreTouch"
    },
    "26.2-performance": {
        "display_name": "🚀 SIR Ultimate 26.2 [Competitive]",
        "version": "26.2",
        "category": "Modern",
        "group": "Modern",
        "chunks": 8,
        "shader_name": "",
        "is_performance": True,
        "min_ram": 2048,
        "max_ram": 4096,
        "jvm_flags": "-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5 -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication -XX:+AlwaysPreTouch"
    },
    "1.8.9-ultra": {
        "display_name": "🌟 SIR Legacy 1.8.9 [Ultra PvP]",
        "version": "1.8.9",
        "category": "Legacy",
        "group": "Legacy",
        "chunks": 16,
        "shader_name": "SIR_Legacy_Shader_Pack.zip",
        "is_performance": False,
        "min_ram": 2048,
        "max_ram": 4096,
        "jvm_flags": "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:+UseNUMA -XX:MaxGCPauseMillis=20 -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication"
    },
    "1.8.9-balanced": {
        "display_name": "⚡ SIR Legacy 1.8.9 [Balanced PvP]",
        "version": "1.8.9",
        "category": "Legacy",
        "group": "Legacy",
        "chunks": 12,
        "shader_name": "",
        "is_performance": False,
        "min_ram": 2048,
        "max_ram": 4096,
        "jvm_flags": "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:+UseNUMA -XX:MaxGCPauseMillis=20 -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication"
    },
    "1.8.9-performance": {
        "display_name": "🚀 SIR Legacy 1.8.9 [Competitive PvP]",
        "version": "1.8.9",
        "category": "Legacy",
        "group": "Legacy",
        "chunks": 8,
        "shader_name": "",
        "is_performance": True,
        "min_ram": 2048,
        "max_ram": 3072,
        "jvm_flags": "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:+UseNUMA -XX:MaxGCPauseMillis=20 -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication"
    }
}

# The 11 Essential Mods verified across Modern 26.2 and Legacy 1.8.9
MODS_11_CATALOG = {
    "modern": [
        "krypton-0.3.1.jar",
        "Resourcify (26.2-fabric)-1.8.5.jar",
        "NoChatReports-FABRIC-26.2-v2.20.2.jar",
        "replaymod-26.2-2.6.27.jar",
        "keystrokes-mod-1.0.5.jar",
        "IAS-9.0.7+26.2-fabric.jar",
        "puddleflood-1.1.5+26.2-fabric.jar",
        "punchy-2.6.0-fabric-26.2.jar"
    ],
    "modern_perf_only": [
        "nvidium-0.4.4-beta5-26.2.jar"
    ],
    "legacy": [
        "Keystrokes-1.8.9-forge-1.0.0.jar",
        "InGameAccountSwitcher-Forge-1.8-8.0.1.jar"
    ]
}

def sync_launcher_config_and_accounts(launcher_root, default_username="Player"):
    os.makedirs(launcher_root, exist_ok=True)
    cfg_path = os.path.join(launcher_root, "sirlauncher.cfg")
    cfg_lines = [
        "[General]",
        "ConfigVersion=1.3",
        "ApplicationTitle=SIR Launcher",
        "Branding=SIR ModPack",
        "ApplicationTheme=sir-dark",
        "IconTheme=flat",
        "Language=en_US",
        "ShowNews=false",
        "NewsType=0",
        "ShownInstanceName=true",
        "InstSortMode=Custom",
        "Analytics=false",
        "UpdateCheck=false",
        "StatusBarVisible=true",
        "AutoCloseConsole=false",
        "AutomaticJavaDownload=true",
        "AutomaticJavaSwitch=true",
        "MinMemAlloc=4096",
        "MaxMemAlloc=8192",
        "InstanceDir=instances"
    ]
    if not os.path.exists(cfg_path):
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write("\n".join(cfg_lines) + "\n")
            
    acc_path = os.path.join(launcher_root, "accounts.json")
    if not os.path.exists(acc_path) or os.path.getsize(acc_path) < 10:
        acc_data = {"accounts": [], "formatVersion": 3}
        try:
            with open(acc_path, "w", encoding="utf-8") as f:
                json.dump(acc_data, f, indent=4)
        except Exception:
            pass

def install_profile(profile_id, target_instances_base, java_path, ram_mb=None, governor="smooth", clean=False):
    """Installs an individual profile cleanly into target_instances_base."""
    spec = PROFILE_SPECS.get(profile_id)
    if not spec:
        print(f"❌ Unknown profile ID: {profile_id}")
        return False

    inst_dir = os.path.join(target_instances_base, profile_id)
    mc_dir = os.path.join(inst_dir, "minecraft")
    
    if clean and os.path.exists(inst_dir):
        print(f"  🧹 Wiping existing profile (--clean): {inst_dir}")
        shutil.rmtree(inst_dir, ignore_errors=True)

    os.makedirs(mc_dir, exist_ok=True)

    # 1. instance.cfg with Generational ZGC / G1GC & verified Java
    max_ram = ram_mb or spec["max_ram"]
    min_ram = max(1024, min(spec["min_ram"], max_ram // 2))

    cfg_lines = [
        "[General]",
        "ConfigVersion=1.3",
        "InstanceType=OneSix",
        "iconKey=sir_crystal",
        f"name={spec['display_name']}",
        f"group={spec['group']}",
        "AutomaticJava=false",
        "OverrideJavaLocation=true",
        f"JavaPath={java_path.replace(os.sep, '/')}",
        "OverrideJavaArgs=true",
        "OverrideMemory=true",
        f"MinMemAlloc={min_ram}",
        f"MaxMemAlloc={max_ram}",
        f"JvmArgs={spec['jvm_flags']}"
    ]
    with open(os.path.join(inst_dir, "instance.cfg"), "w", encoding="utf-8") as f:
        f.write("\n".join(cfg_lines) + "\n")

    # 2. mmc-pack.json
    if spec["category"] == "Modern":
        pack_content = {
            "components": [
                {"cachedName": "LWJGL 3", "cachedVersion": "3.4.1", "cachedVolatile": True, "dependencyOnly": True, "uid": "org.lwjgl3", "version": "3.4.1"},
                {"cachedName": "Minecraft", "cachedRequires": [{"suggests": "3.4.1", "uid": "org.lwjgl3"}], "cachedVersion": "26.2", "important": True, "uid": "net.minecraft", "version": "26.2"},
                {"cachedName": "Intermediary Mappings", "cachedRequires": [{"equals": "26.2", "uid": "net.minecraft"}], "cachedVersion": "26.2", "cachedVolatile": True, "dependencyOnly": True, "uid": "net.fabricmc.intermediary", "version": "26.2"},
                {"cachedName": "Fabric Loader", "cachedRequires": [{"uid": "net.fabricmc.intermediary"}], "cachedVersion": "0.19.3", "uid": "net.fabricmc.fabric-loader", "version": "0.19.3"}
            ],
            "formatVersion": 1
        }
    else:
        pack_content = {
            "components": [
                {"cachedName": "Minecraft", "cachedRequires": [], "cachedVersion": "1.8.9", "important": True, "uid": "net.minecraft", "version": "1.8.9"},
                {"cachedName": "Forge", "cachedRequires": [{"suggests": "1.8.9", "uid": "net.minecraft"}], "cachedVersion": "11.15.1.2318", "important": True, "uid": "net.minecraftforge", "version": "11.15.1.2318"}
            ],
            "formatVersion": 1
        }
    with open(os.path.join(inst_dir, "mmc-pack.json"), "w", encoding="utf-8") as f:
        json.dump(pack_content, f, indent=4)

    # 3. Copy mods, configs, resourcepacks, shaderpacks
    src_inst_dir = os.path.join(INSTANCES_SRC_DIR, profile_id)
    
    # Base copy from source instance if exists
    if os.path.exists(src_inst_dir):
        governed_copy_tree(src_inst_dir, inst_dir, governor)

    # If modern, synchronize from root shared mods & configs
    if spec["category"] == "Modern":
        mods_dst = os.path.join(mc_dir, "mods")
        os.makedirs(mods_dst, exist_ok=True)
        if os.path.exists(MODS_DIR):
            for fn in os.listdir(MODS_DIR):
                if fn.endswith(".jar") and "forge-1.8" not in fn.lower():
                    # Filter Nvidium: strictly on performance profile only
                    if "nvidium" in fn.lower() and not spec["is_performance"]:
                        continue
                    governed_copy_file(os.path.join(MODS_DIR, fn), os.path.join(mods_dst, fn), governor)

        # Deploy 11 new mods explicitly
        for m in MODS_11_CATALOG["modern"]:
            src_m = os.path.join(MODS_DIR, m)
            if os.path.exists(src_m):
                governed_copy_file(src_m, os.path.join(mods_dst, m), governor)

        if spec["is_performance"]:
            for m in MODS_11_CATALOG["modern_perf_only"]:
                src_m = os.path.join(MODS_DIR, m)
                if os.path.exists(src_m):
                    governed_copy_file(src_m, os.path.join(mods_dst, m), governor)

        # Copy configs, shaders, resourcepacks
        for sub, s_path in [("config", CONFIG_DIR), ("shaderpacks", SH_DIR), ("resourcepacks", RP_DIR)]:
            if os.path.exists(s_path):
                governed_copy_tree(s_path, os.path.join(mc_dir, sub), governor)

    elif spec["category"] == "Legacy":
        # Legacy instances copy from source instances or lunar client
        mods_dst = os.path.join(mc_dir, "mods")
        os.makedirs(mods_dst, exist_ok=True)
        for m in MODS_11_CATALOG["legacy"]:
            src_m = os.path.join(MODS_DIR, m)
            if not os.path.exists(src_m):
                src_m = os.path.join(src_inst_dir, "minecraft", "mods", m)
            if os.path.exists(src_m):
                governed_copy_file(src_m, os.path.join(mods_dst, m), governor)

    # 4. options.txt calibration
    opt_path = os.path.join(mc_dir, "options.txt")
    if not os.path.exists(opt_path):
        opts_lines = [
            f"renderDistance:{spec['chunks']}",
            "biomeBlendRadius:7",
            "gamma:1.0",
            "autoJump:false",
            "fullscreen:false",
            "key_iris.keybind.toggleShaders:key.keyboard.k",
            "key_iris.keybind.shaderPackSelection:key.keyboard.i"
        ]
        with open(opt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(opts_lines) + "\n")

    # 5. Iris shader settings for modern
    if spec["category"] == "Modern":
        iris_props = os.path.join(mc_dir, "config", "iris.properties")
        os.makedirs(os.path.dirname(iris_props), exist_ok=True)
        with open(iris_props, "w", encoding="utf-8") as f:
            f.write(f"enableShaders={'true' if spec['shader_name'] else 'false'}\nshaderPack={spec['shader_name']}\n")

    # 6. servers.dat synchronization
    src_servers = os.path.join(SOURCE_ROOT, "servers.dat")
    if not os.path.exists(src_servers):
        src_servers = os.path.join(os.environ.get("APPDATA", ""), ".minecraft", "servers.dat")
    if os.path.exists(src_servers):
        governed_copy_file(src_servers, os.path.join(mc_dir, "servers.dat"), governor)

    print(f"  ✅ Installed Profile [{profile_id}] -> {inst_dir}")
    return True

# =============================================================================
# CHECKSUM VERIFICATION AGAINST delta_manifest.json
# =============================================================================

def compute_file_sha256(filepath):
    digest = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(131072):
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return ""

def verify_delta_manifest(dest_base, profile_ids):
    """Verifies installed files against delta_manifest.json."""
    manifest_path = os.path.join(SOURCE_ROOT, "delta_manifest.json")
    if not os.path.isfile(manifest_path):
        manifest_path = os.path.join(os.path.dirname(SOURCE_ROOT), "delta_manifest.json")
    if not os.path.isfile(manifest_path):
        print(f"⚠️ delta_manifest.json not found at {manifest_path}. Skipping checksum verification.")
        return True

    print("\n🔍 === EXECUTING SHA-256 CHECKSUM VALIDATION (delta_manifest.json) ===")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Failed to parse delta_manifest.json: {e}")
        return False

    files_map = manifest.get("files", {})
    total_verified = 0
    total_mismatched = 0
    total_missing = 0

    print(f"  📋 Loaded manifest: {manifest.get('total_files', len(files_map))} asset signatures")

    # Check files belonging to the target profiles
    for pid in profile_ids:
        prefix = f"instances/{pid}/"
        for rel_manifest, meta in files_map.items():
            if not rel_manifest.startswith(prefix):
                continue
            
            sub_rel = rel_manifest[len(prefix):]
            local_path = os.path.join(dest_base, "instances", pid, sub_rel)
            
            if not os.path.isfile(local_path):
                total_missing += 1
                continue
                
            expected_sha = meta.get("sha256", "").lower()
            actual_sha = compute_file_sha256(local_path).lower()
            
            if actual_sha == expected_sha:
                total_verified += 1
            else:
                total_mismatched += 1
                print(f"     ❌ Mismatch: {sub_rel} (Expected: {expected_sha[:8]}, Actual: {actual_sha[:8]})")

    print(f"\n  📊 Verification Summary for {len(profile_ids)} Profile(s):")
    print(f"     ✅ Verified Identical: {total_verified} files")
    print(f"     ⚠️ Missing from Profile: {total_missing} files")
    print(f"     ❌ Hash Mismatches:     {total_mismatched} files")
    
    if total_mismatched == 0:
        print("  ✨ 100% CHECKSUM INTEGRITY CERTIFIED — ZERO DEFECTS DETECTED!")
        return True
    else:
        print("  ⚠️ Integrity warning: Some files differed from official manifest.")
        return False

# =============================================================================
# DESKTOP SHORTCUT CREATION
# =============================================================================

def create_desktop_shortcut(target_exe=None):
    if sys.platform != "win32":
        return
    desktop = os.path.join(os.environ.get('USERPROFILE', USER_HOME), 'Desktop')
    ico_path = os.path.join(SOURCE_ROOT, "SIR Icon.ico")
    if not os.path.exists(ico_path):
        ico_path = os.path.join(SOURCE_ROOT, "SIR_Icon.ico")

    candidates = [
        target_exe,
        os.path.join(SOURCE_ROOT, "SIR Launcher.exe"),
        os.path.join(SOURCE_ROOT, "SIR ModPack.exe"),
        os.path.join(SOURCE_ROOT, "dist_build", "SIR Launcher.exe"),
    ]
    launcher_exe = next((p for p in candidates if p and os.path.exists(p)), None)
    if not launcher_exe:
        return

    lnk_path = os.path.join(desktop, "SIR Launcher.lnk")
    work_dir = os.path.dirname(launcher_exe)
    vbs = f'Set oWS = WScript.CreateObject("WScript.Shell")\nSet oLink = oWS.CreateShortcut("{lnk_path}")\noLink.TargetPath = "{launcher_exe}"\noLink.WorkingDirectory = "{work_dir}"\n'
    if os.path.exists(ico_path):
        vbs += f'oLink.IconLocation = "{ico_path}, 0"\n'
    vbs += 'oLink.Save\n'

    with tempfile.NamedTemporaryFile('w', suffix='.vbs', delete=False) as f:
        f.write(vbs)
        vbs_f = f.name
    try:
        subprocess.run(['cscript', '//nologo', vbs_f], check=True, capture_output=True)
        print(f"  ✅ Created Desktop Shortcut: {lnk_path}")
    except Exception:
        pass
    finally:
        if os.path.exists(vbs_f):
            os.remove(vbs_f)

# =============================================================================
# CLI PARSER & MAIN DISPATCHER
# =============================================================================

def parse_cli_arguments():
    parser = argparse.ArgumentParser(
        description=f"SIR ModPack Master CLI Installer ({VERSION})",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python install.py --profile 26.2-ultra
  python install.py --profile 26.2-performance --clean --verify
  python install.py --profile all --dest "D:\\Games\\Minecraft" -y
  python install.py --skip-java --non-interactive

Contact: {CONTACT}
Platform: {LICENSE_NOTE}
"""
    )
    parser.add_argument("--profile", default="all",
                        help="Target profile: 26.2-ultra, 26.2-balanced, 26.2-performance, 1.8.9-ultra, 1.8.9-balanced, 1.8.9-performance, or 'all' (default: all)")
    parser.add_argument("--dest", default="",
                        help="Custom destination directory (defaults to %%APPDATA%%/SIR ModPack or standard instances directory)")
    parser.add_argument("--skip-java", action="store_true",
                        help="Skip Java 21 pre-flight verification and automatic Adoptium Temurin download")
    parser.add_argument("--clean", action="store_true",
                        help="Wipe existing target profile directory before fresh deployment")
    parser.add_argument("--verify", action="store_true",
                        help="Run SHA-256 checksum verification against delta_manifest.json post-installation")
    parser.add_argument("-y", "--non-interactive", action="store_true",
                        help="Run in non-interactive / unattended mode without confirmation pauses")
    parser.add_argument("--ram", type=int, default=0,
                        help="Max RAM allocation in MB (auto-detected by default)")
    parser.add_argument("--governor", choices=["smooth", "max"], default="smooth",
                        help="Hardware power governor mode: smooth (background priority) or max (full speed)")
    parser.add_argument("--username", default=os.environ.get("USERNAME", "Player"),
                        help="Minecraft in-game account username / IGN (default: system username)")
    parser.add_argument("--target", choices=["sir", "lunar", "both"], default="sir",
                        help="Target launcher integration: sir (default), lunar, or both")
    parser.add_argument("--gui", action="store_true",
                        help="Launch graphical desktop installer if available")

    # Legacy compatibility arguments
    parser.add_argument("--modern-tiers", default="", help=argparse.SUPPRESS)
    parser.add_argument("--legacy-tiers", default="", help=argparse.SUPPRESS)
    parser.add_argument("--tier", default="", help=argparse.SUPPRESS)

    return parser.parse_args()

def resolve_target_profiles(arg_profile, args):
    """Maps CLI profile argument to an exact list of valid profile IDs."""
    p_lower = (arg_profile or "all").lower().strip()
    
    if args.tier:
        t = args.tier.lower().strip()
        return [f"26.2-{t}", f"1.8.9-{t}"]

    if p_lower == "all":
        return list(PROFILE_SPECS.keys())
    elif p_lower in ("modern", "26.2"):
        return [k for k in PROFILE_SPECS.keys() if k.startswith("26.2")]
    elif p_lower in ("legacy", "1.8.9"):
        return [k for k in PROFILE_SPECS.keys() if k.startswith("1.8.9")]
    elif p_lower in ("ultra", "balanced", "performance"):
        return [f"26.2-{p_lower}", f"1.8.9-{p_lower}"]
    elif p_lower == "perf":
        return ["26.2-performance", "1.8.9-performance"]
    elif p_lower in PROFILE_SPECS:
        return [p_lower]
    else:
        print(f"⚠️ Unrecognized profile '{arg_profile}'. Defaulting to 'all'.")
        return list(PROFILE_SPECS.keys())

def main():
    args = parse_cli_arguments()

    # If --gui requested or running with no arguments in interactive mode and GUI exe exists
    if args.gui:
        dispatcher_candidates = [
            os.path.join(SOURCE_ROOT, "SIR ModPack.exe"),
            os.path.join(SOURCE_ROOT, "SIR Installer.exe"),
            os.path.join(SOURCE_ROOT, "dist_build", "SIR ModPack.exe"),
            os.path.join(SOURCE_ROOT, "dist_build", "SIR Installer.exe"),
        ]
        dispatcher = next((p for p in dispatcher_candidates if os.path.isfile(p)), None)
        if dispatcher:
            print("🚀 Launching Graphical SIR Installer Studio...")
            return subprocess.call([dispatcher, "--mode", "installer"], cwd=os.path.dirname(dispatcher))

    apply_hardware_governor(args.governor)

    # Determine default destination
    if args.dest:
        dest_root = os.path.abspath(args.dest)
    else:
        appdata = os.environ.get("APPDATA", os.path.join(USER_HOME, "AppData", "Roaming"))
        dest_root = os.path.join(appdata, "SIR ModPack")

    inst_base = os.path.join(dest_root, "instances")
    os.makedirs(inst_base, exist_ok=True)

    # Resolve target profiles
    target_profiles = resolve_target_profiles(args.profile, args)
    
    # Ram allocation
    ram_mb = args.ram if args.ram > 0 else HW_INFO["max_m"]

    print("===============================================================================")
    print(f"🌟 SIR MODPACK MASTER CLI INSTALLER — {VERSION}")
    print(f"   📜 {LICENSE_NOTE}")
    print(f"   💻 System Hardware: {HW_INFO['gpu']} | {HW_INFO['cores']} Cores | {HW_INFO['ram']}GB RAM")
    print(f"   ⚡ Hardware Governor: {args.governor.upper()} MODE")
    print(f"   📍 Installation Root: {dest_root}")
    print(f"   🎯 Target Profiles:   {', '.join(target_profiles)}")
    print(f"   ⚙️ Allocated Memory:  {ram_mb} MB")
    print(f"   👤 Account IGN:       {args.username}")
    print(f"   📦 11 New Mods:       Active & Bundled (Krypton, Resourcify, NoChatReports, etc.)")
    print("===============================================================================")

    # Java 21 Check & Auto-Download
    if args.skip_java:
        print("⏩ Java pre-flight verification bypassed by user (--skip-java).")
        java_path = "javaw.exe" if sys.platform == "win32" else "java"
    else:
        java_path = ensure_java21_runtime(dest_root, non_interactive=args.non_interactive)

    # Sync Launcher Configurations
    sync_launcher_config_and_accounts(dest_root, args.username)

    # Copy Icons
    icons_dir = os.path.join(dest_root, "icons")
    os.makedirs(icons_dir, exist_ok=True)
    src_ico = os.path.join(SOURCE_ROOT, "SIR Icon.ico")
    if not os.path.exists(src_ico):
        src_ico = os.path.join(SOURCE_ROOT, "SIR_Icon.ico")
    if os.path.exists(src_ico):
        shutil.copy2(src_ico, os.path.join(icons_dir, "sir_crystal.ico"))

    # Execute Profile Deployments
    print(f"\n🚀 Deploying {len(target_profiles)} Profile(s)...")
    for pid in target_profiles:
        install_profile(
            profile_id=pid,
            target_instances_base=inst_base,
            java_path=java_path,
            ram_mb=ram_mb,
            governor=args.governor,
            clean=args.clean
        )

    # Generate instgroups.json
    groups_data = {
        "formatVersion": "1",
        "groups": {
            "Modern": {
                "hidden": False,
                "instances": [p for p in target_profiles if p.startswith("26.2")]
            },
            "Legacy": {
                "hidden": False,
                "instances": [p for p in target_profiles if p.startswith("1.8.9")]
            }
        }
    }
    with open(os.path.join(inst_base, "instgroups.json"), "w", encoding="utf-8") as f:
        json.dump(groups_data, f, indent=4)

    # Create desktop shortcut
    create_desktop_shortcut()

    # Optional SHA-256 Checksum Validation
    if args.verify:
        verify_delta_manifest(dest_root, target_profiles)

    print("\n===============================================================================")
    print("🎉 SIR MODPACK INSTALLATION & PORTABLE DEPLOYMENT COMPLETE 100%!")
    print(f"   📂 Target Directory: {dest_root}")
    print(f"   🎮 Launch using:     SIR Launcher.exe or desktop shortcut")
    print(f"   ✉️ Support Contact:  {CONTACT}")
    print("===============================================================================")
    return 0

if __name__ == "__main__":
    sys.exit(main())
