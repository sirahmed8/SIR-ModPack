import os
import sys
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
import shutil
import zipfile
import json
import sqlite3
import glob
import subprocess
import tempfile
import time
import platform
import ctypes
import webbrowser

# Historical compatibility shim. The supported installer is the Installer &
# Repair mode of SIR ModPack.exe. The legacy direct deployment functions below
# are bypassed whenever the dispatcher build is available.
SOURCE_ROOT = os.path.dirname(os.path.abspath(__file__))
MODS_DIR = os.path.join(SOURCE_ROOT, "mods")
RP_DIR = os.path.join(SOURCE_ROOT, "resourcepacks")
SH_DIR = os.path.join(SOURCE_ROOT, "shaderpacks")
CONFIG_DIR = os.path.join(SOURCE_ROOT, "config")

USER_HOME = os.path.expanduser("~")
LUNAR_ROOT = os.path.join(USER_HOME, ".lunarclient")
LUNAR_DB = os.path.join(LUNAR_ROOT, "db", "profiles.db")
LUNAR_PROFILES = os.path.join(LUNAR_ROOT, "profiles")

PRISM_ROOT = os.path.join(os.environ.get("APPDATA", os.path.join(USER_HOME, "AppData", "Roaming")), "PrismLauncher")
PRISM_INSTANCES = os.path.join(PRISM_ROOT, "instances")

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
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    try:
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        ram_gb = round(stat.ullTotalPhys / (1024**3), 1)
    except Exception:
        ram_gb = 16.0
    cpu_cores = os.cpu_count() or 4
    gpu = "Dedicated Graphics"
    try:
        cmd = ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_VideoController).Name"]
        out = subprocess.check_output(cmd, text=True, timeout=2).strip().split('\n')
        gpu = out[0].strip() if out else "NVIDIA GeForce RTX 4050 Laptop GPU"
    except Exception:
        gpu = "NVIDIA GeForce RTX 4050 Laptop GPU"
    if ram_gb >= 32: min_m, max_m = 6144, 12288
    elif ram_gb >= 16: min_m, max_m = 4096, 8192
    elif ram_gb >= 8: min_m, max_m = 3072, 5120
    else: min_m, max_m = 2048, 3072
    return {"ram": ram_gb, "cores": cpu_cores, "gpu": gpu, "min_m": min_m, "max_m": max_m}


HW_INFO = detect_hardware()

def apply_hardware_governor(governor="smooth"):
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



def parse_args():
    target = "both"
    ram = HW_INFO["max_m"]
    modern_tiers = ["ultra", "balanced", "performance"]
    legacy_tiers = ["ultra", "balanced", "performance"]
    governor = "smooth"
    username = os.environ.get("USERNAME", "Player")
    
    for i in range(len(sys.argv)):
        arg = sys.argv[i]
        if arg == "--target" and i + 1 < len(sys.argv):
            target = sys.argv[i+1].lower()
        elif arg == "--ram" and i + 1 < len(sys.argv):
            try: ram = int(sys.argv[i+1])
            except: pass
        elif arg == "--modern-tiers" and i + 1 < len(sys.argv):
            modern_tiers = [t.strip().lower() for t in sys.argv[i+1].split(",") if t.strip()]
        elif arg == "--legacy-tiers" and i + 1 < len(sys.argv):
            legacy_tiers = [t.strip().lower() for t in sys.argv[i+1].split(",") if t.strip()]
        elif arg == "--tier" and i + 1 < len(sys.argv):
            t = sys.argv[i+1].lower()
            modern_tiers = [t]
            legacy_tiers = [t]
        elif arg == "--governor" and i + 1 < len(sys.argv):
            governor = sys.argv[i+1].lower()
        elif arg == "--username" and i + 1 < len(sys.argv):
            username = sys.argv[i+1].strip()
            
    return target, ram, modern_tiers, legacy_tiers, governor, username

def get_launcher_roots():
    """Returns exclusively the official SIR Launcher roaming root."""
    sir_roaming = os.path.join(USER_HOME, "AppData", "Roaming", "SIR Launcher")
    return [sir_roaming]



def sync_launcher_config_and_accounts(launcher_root, default_username=None):
    if not default_username:
        default_username = os.environ.get("USERNAME", "Player")
    os.makedirs(launcher_root, exist_ok=True)
    
    # 1. sirlauncher.cfg
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
    
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
                existing = f.read()
            if "ShowNews=true" in existing:
                existing = existing.replace("ShowNews=true", "ShowNews=false")
            if "ShowNews=false" not in existing:
                existing += "\nShowNews=false\nNewsType=0\n"
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(existing)
        except Exception:
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write("\n".join(cfg_lines) + "\n")
    else:
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write("\n".join(cfg_lines) + "\n")
            
    # 2. accounts.json (Clean default - no dummy/ghost accounts)
    acc_path = os.path.join(launcher_root, "accounts.json")
    if not os.path.exists(acc_path) or os.path.getsize(acc_path) < 10:
        acc_data = {
            "accounts": [],
            "formatVersion": 3
        }
        try:
            with open(acc_path, "w", encoding="utf-8") as f:
                json.dump(acc_data, f, indent=4)
        except Exception:
            pass


def deploy_sir_launcher(target, ram_mb, modern_tiers, legacy_tiers, governor="smooth", username="Player"):
    print("\n📦 === DEPLOYING & SYNCHRONIZING SIR LAUNCHER PROFILES ===")
    
    launcher_roots = get_launcher_roots()
    print(f"  📍 Detected Launcher Locations: {len(launcher_roots)}")
    for r in launcher_roots:
        print(f"     -> {r}")
        
    src_ico = os.path.join(SOURCE_ROOT, "SIR Icon.ico")
    
    tier_meta_modern = {
        "ultra": ("🌟 SIR Ultimate 26.2 [Ultra]", "SIR_Extreme_Shader.zip", 24, "extreme"),
        "balanced": ("⚡ SIR Ultimate 26.2 [Balanced]", "SIR_Balanced_Shader.zip", 16, "balanced"),
        "performance": ("🚀 SIR Ultimate 26.2 [Competitive]", "", 8, "performance")
    }
    
    tier_meta_legacy = {
        "ultra": ("🌟 SIR Legacy 1.8.9 [Ultra PvP]", "SIR_Legacy_Shader_Pack.zip", 16),
        "balanced": ("⚡ SIR Legacy 1.8.9 [Balanced PvP]", "", 12),
        "performance": ("🚀 SIR Legacy 1.8.9 [Competitive PvP]", "", 8)
    }
    
    lunar_189 = os.path.join(LUNAR_PROFILES, "sir-ultimate-legacy-1.8.9")

    for l_root in launcher_roots:
        inst_base = os.path.join(l_root, "instances")
        os.makedirs(inst_base, exist_ok=True)
        sync_launcher_config_and_accounts(l_root, username)
        
        os.makedirs(os.path.join(l_root, "icons"), exist_ok=True)
        if os.path.exists(src_ico):
            shutil.copy2(src_ico, os.path.join(l_root, "icons", "sir_crystal.ico"))
            
        modern_inst_ids = []
        legacy_inst_ids = []
        
        # Deploy Modern Instances
        for tier in modern_tiers:
            if tier not in tier_meta_modern: continue
            display_name, shader_name, chunks, tier_key = tier_meta_modern[tier]
            inst_id = f"26.2-{tier}"
            inst_dir = os.path.join(inst_base, inst_id)
            mc_dir = os.path.join(inst_dir, "minecraft")
            os.makedirs(mc_dir, exist_ok=True)
            modern_inst_ids.append(inst_id)
            
            cfg_lines = [
                "[General]",
                "ConfigVersion=1.3",
                "InstanceType=OneSix",
                "iconKey=sir_crystal",
                f"name={display_name}",
                "group=Modern",
                "AutomaticJava=true",
                "OverrideJavaArgs=true",
                "OverrideMemory=true",
                f"MinMemAlloc={max(2048, ram_mb // 2)}",
                f"MaxMemAlloc={ram_mb}",
                'JvmArgs="-XX:+UseZGC -XX:+UnlockExperimentalVMOptions -XX:+AlwaysPreTouch -XX:+UseStringDeduplication -XX:ParallelGCThreads=10"'
            ]
            with open(os.path.join(inst_dir, "instance.cfg"), "w", encoding="utf-8") as f:
                f.write("\n".join(cfg_lines) + "\n")
                
            pack_content = {
                "components": [
                    {"cachedName": "LWJGL 3", "cachedVersion": "3.4.1", "cachedVolatile": True, "dependencyOnly": True, "uid": "org.lwjgl3", "version": "3.4.1"},
                    {"cachedName": "Minecraft", "cachedRequires": [{"suggests": "3.4.1", "uid": "org.lwjgl3"}], "cachedVersion": "26.2", "important": True, "uid": "net.minecraft", "version": "26.2"},
                    {"cachedName": "Intermediary Mappings", "cachedRequires": [{"equals": "26.2", "uid": "net.minecraft"}], "cachedVersion": "26.2", "cachedVolatile": True, "dependencyOnly": True, "uid": "net.fabricmc.intermediary", "version": "26.2"},
                    {"cachedName": "Fabric Loader", "cachedRequires": [{"uid": "net.fabricmc.intermediary"}], "cachedVersion": "0.19.3", "uid": "net.fabricmc.fabric-loader", "version": "0.19.3"}
                ],
                "formatVersion": 1
            }
            with open(os.path.join(inst_dir, "mmc-pack.json"), "w", encoding="utf-8") as f:
                json.dump(pack_content, f, indent=4)
                
            for sub, src_path in [("mods", MODS_DIR), ("shaderpacks", SH_DIR), ("resourcepacks", RP_DIR), ("config", CONFIG_DIR)]:
                if os.path.exists(src_path):
                    dst = os.path.join(mc_dir, sub)
                    if sub == "mods":
                        for fn in os.listdir(src_path):
                            if fn.endswith(".jar") and "forge-1.8" not in fn.lower():
                                governed_copy_file(os.path.join(src_path, fn), os.path.join(dst, fn), governor)
                    else:
                        governed_copy_tree(src_path, dst, governor)
                        
            src_ias = os.path.join(MODS_DIR, "IAS-9.0.7+26.2-fabric.jar")
            if os.path.exists(src_ias):
                governed_copy_file(src_ias, os.path.join(mc_dir, "mods", "IAS-9.0.7+26.2-fabric.jar"), governor)
                
            opts_lines = [
                f"renderDistance:{chunks}",
                "biomeBlendRadius:7",
                "gamma:1.0",
                "autoJump:false",
                "fullscreen:false"
            ]
            with open(os.path.join(mc_dir, "options.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(opts_lines) + "\n")
                
            iris_props = os.path.join(mc_dir, "config", "iris.properties")
            os.makedirs(os.path.dirname(iris_props), exist_ok=True)
            with open(iris_props, "w", encoding="utf-8") as f:
                f.write(f"enableShaders={'true' if shader_name else 'false'}\nshaderPack={shader_name}\n")
                
            # Legacy redundant single folder removed

        # Deploy Legacy Instances
        for tier in legacy_tiers:
            if tier not in tier_meta_legacy: continue
            display_name, shader_name, chunks = tier_meta_legacy[tier]
            inst_id = f"1.8.9-{tier}"
            inst_dir = os.path.join(inst_base, inst_id)
            mc_dir = os.path.join(inst_dir, "minecraft")
            os.makedirs(mc_dir, exist_ok=True)
            legacy_inst_ids.append(inst_id)
            
            cfg_lines = [
                "[General]",
                "ConfigVersion=1.3",
                "InstanceType=OneSix",
                "iconKey=sir_crystal",
                f"name={display_name}",
                "group=Legacy",
                "AutomaticJava=true",
                "OverrideJavaArgs=true",
                "OverrideMemory=true",
                "MinMemAlloc=2048",
                f"MaxMemAlloc={min(4096, ram_mb)}",
                'JvmArgs="-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:+AlwaysPreTouch -XX:+UseStringDeduplication -XX:ParallelGCThreads=4"'
            ]
            with open(os.path.join(inst_dir, "instance.cfg"), "w", encoding="utf-8") as f:
                f.write("\n".join(cfg_lines) + "\n")
                
            pack_content = {
                "components": [
                    {"cachedName": "Minecraft", "cachedRequires": [], "cachedVersion": "1.8.9", "important": True, "uid": "net.minecraft", "version": "1.8.9"},
                    {"cachedName": "Forge", "cachedRequires": [{"suggests": "1.8.9", "uid": "net.minecraft"}], "cachedVersion": "11.15.1.2318", "important": True, "uid": "net.minecraftforge", "version": "11.15.1.2318"}
                ],
                "formatVersion": 1
            }
            with open(os.path.join(inst_dir, "mmc-pack.json"), "w", encoding="utf-8") as f:
                json.dump(pack_content, f, indent=4)
                
            if os.path.exists(lunar_189):
                for sub in ["mods", "config", "resourcepacks", "shaderpacks"]:
                    src_sub = os.path.join(lunar_189, sub)
                    dst_sub = os.path.join(mc_dir, sub)
                    governed_copy_tree(src_sub, dst_sub, governor)
                    
            src_ias_legacy = os.path.join(MODS_DIR, "InGameAccountSwitcher-Forge-1.8-8.0.1.jar")
            if os.path.exists(src_ias_legacy):
                governed_copy_file(src_ias_legacy, os.path.join(mc_dir, "mods", "InGameAccountSwitcher-Forge-1.8-8.0.1.jar"), governor)
                
            # Legacy redundant single folder removed

        groups_data = {
            "formatVersion": "1",
            "groups": {
                "Modern": {
                    "hidden": False,
                    "instances": list(set(modern_inst_ids))
                },
                "Legacy": {
                    "hidden": False,
                    "instances": list(set(legacy_inst_ids))
                }
            }
        }
        with open(os.path.join(inst_base, "instgroups.json"), "w", encoding="utf-8") as f:
            json.dump(groups_data, f, indent=4)
            
        print(f"  ✅ Synchronized {len(modern_inst_ids) + len(legacy_inst_ids)} Profiles in: {inst_base}")

def deploy_lunar_client(modern_tiers, legacy_tiers, governor="smooth"):
    if not os.path.exists(LUNAR_PROFILES):
        print("⚠️ Lunar Client profiles directory not detected. Skipping Lunar deployment.")
        return
        
    print("\n🌙 === CONFIGURING LUNAR CLIENT PROFILES ===")
    tier_meta_lunar = {
        "ultra": ("sir-ultimate-legacy-visual-1.8.9", 16),
        "balanced": ("sir-ultimate-legacy-balanced-1.8.9", 12),
        "performance": ("sir-ultimate-legacy-performance-1.8.9", 8)
    }
    
    src_189 = os.path.join(LUNAR_PROFILES, "sir-ultimate-legacy-1.8.9")
    for tier in legacy_tiers:
        if tier not in tier_meta_lunar: continue
        prof_name, chunks = tier_meta_lunar[tier]
        dst_prof = os.path.join(LUNAR_PROFILES, prof_name)
        os.makedirs(dst_prof, exist_ok=True)
        if os.path.exists(src_189):
            for sub in ["mods", "config", "resourcepacks", "shaderpacks"]:
                s = os.path.join(src_189, sub)
                d = os.path.join(dst_prof, sub)
                governed_copy_tree(s, d, governor)
        print(f"  ✅ Configured Lunar Profile: {prof_name}")

def create_desktop_shortcut():
    desktop = os.path.join(os.environ.get('USERPROFILE', USER_HOME), 'Desktop')
    ico_path = os.path.join(SOURCE_ROOT, "SIR Icon.ico")
    if not os.path.exists(ico_path):
        ico_path = os.path.join(SOURCE_ROOT, "SIR Launcher", "SIR Icon.ico")
        
    # 1. Launcher Shortcut
    launcher_candidates = [
        os.path.join(SOURCE_ROOT, "SIR ModPack.exe"),
        os.path.join(SOURCE_ROOT, "dist_build", "SIR ModPack.exe"),
    ]
    launcher_exe = next((p for p in launcher_candidates if os.path.exists(p)), None)
    if launcher_exe:
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
            print(f"  ✅ Created Launcher Shortcut: {lnk_path}")
        finally:
            if os.path.exists(vbs_f): os.remove(vbs_f)

    # 2. Server Host App Shortcut
    server_candidates = [
        os.path.join(SOURCE_ROOT, "SIR ModPack.exe"),
        os.path.join(SOURCE_ROOT, "dist_build", "SIR ModPack.exe"),
    ]
    server_exe = next((p for p in server_candidates if os.path.exists(p)), None)
    if server_exe:
        lnk_server = os.path.join(desktop, "SIR Server Host.lnk")
        work_dir_srv = os.path.dirname(server_exe)
        vbs_srv = f'Set oWS = WScript.CreateObject("WScript.Shell")\nSet oLink = oWS.CreateShortcut("{lnk_server}")\noLink.TargetPath = "{server_exe}"\noLink.WorkingDirectory = "{work_dir_srv}"\n'
        if os.path.exists(ico_path):
            vbs_srv += f'oLink.IconLocation = "{ico_path}, 0"\n'
        vbs_srv += 'oLink.Save\n'
        with tempfile.NamedTemporaryFile('w', suffix='.vbs', delete=False) as f:
            f.write(vbs_srv)
            vbs_sf = f.name
        try:
            subprocess.run(['cscript', '//nologo', vbs_sf], check=True, capture_output=True)
            print(f"  ✅ Created Server Host Shortcut: {lnk_server}")
        finally:
            if os.path.exists(vbs_sf): os.remove(vbs_sf)

def main():
    dispatcher_candidates = [
        os.path.join(SOURCE_ROOT, "SIR ModPack.exe"),
        os.path.join(SOURCE_ROOT, "dist_build", "SIR ModPack.exe"),
    ]
    dispatcher = next((path for path in dispatcher_candidates if os.path.isfile(path)), None)
    if dispatcher:
        print("Opening SIR ModPack Installer & Repair mode...")
        return subprocess.call([dispatcher, "--mode", "installer"], cwd=os.path.dirname(dispatcher))

    target, ram_mb, modern_tiers, legacy_tiers, governor, username = parse_args()
    apply_hardware_governor(governor)
    
    print("============================================================")
    print("🌟 SIR ULTIMATE INSTALLER v1.0.0")
    print(f"   💻 Hardware: {HW_INFO['gpu']} | {HW_INFO['cores']} Cores | {HW_INFO['ram']}GB RAM")
    print(f"   ⚡ Power Governor: {governor.upper()} MODE")
    print(f"   🎯 Target Platform: {target.upper()}")
    print(f"   👤 Account IGN: {username}")
    print(f"   ⚙️ Allocated Memory: {ram_mb} MB")
    print(f"   🌟 Modern Profiles (26.2): {', '.join(modern_tiers).upper()}")
    print(f"   🌙 Legacy Profiles (1.8.9): {', '.join(legacy_tiers).upper()}")
    print("============================================================")
    
    if target in ("sir", "both"):
        deploy_sir_launcher(target, ram_mb, modern_tiers, legacy_tiers, governor, username)
        create_desktop_shortcut()
        
    if target in ("lunar", "both"):
        deploy_lunar_client(modern_tiers, legacy_tiers, governor)
        
    print("\n🎉 SIR ULTIMATE v1.0.0 INSTALLATION COMPLETE 100%!")

if __name__ == "__main__":
    main()

