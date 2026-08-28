import os
import sys
import zipfile
import json
import sqlite3
import hashlib
import subprocess

print("=" * 70)
print("  AETHERIS COMPLETE SYNCHRONIZATION & INSTALLER VERIFICATION SUITE")
print("=" * 70)

failures = []

def record_failure(msg):
    print(f"  [FAIL] {msg}")
    failures.append(msg)

# ----------------------------------------------------------------------
# TEST 1: D:\AetherisShare Directory & Distribution Completeness
# ----------------------------------------------------------------------
print("\n[TEST 1] Verifying D:\\AetherisShare Distribution Structure...")
share_dir = r"D:\AetherisShare"

required_subdirs = [
    "shaders",
    "resourcepacks",
    "modpacks",
    "lunar_huds",
    "lunar_profiles",
    "profiles",
    "lunar-settings",
    "docs"
]

for sd in required_subdirs:
    p = os.path.join(share_dir, sd)
    if not os.path.exists(p) or not os.path.isdir(p):
        record_failure(f"Missing required subdirectory: {p}")

required_root_files = [
    "install.bat",
    "install.ps1"
]

for rf in required_root_files:
    p = os.path.join(share_dir, rf)
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        record_failure(f"Missing or empty root installer file: {p}")

if not failures:
    print("  -> Distribution root structure and required folders verified. (Failures: 0)")

# ----------------------------------------------------------------------
# TEST 2: Standalone Shaders & Companion Configs
# ----------------------------------------------------------------------
print("\n[TEST 2] Auditing Standalone Shaders in D:\\AetherisShare\\shaders...")
required_shaders = [
    "Aetheris_Visual_Shader.zip",
    "Aetheris_Visual_Shader.zip.txt",
    "Aetheris_Balanced_Shader.zip",
    "Aetheris_Balanced_Shader.zip.txt",
    "Aetheris_Extreme_Shader.zip",
    "Aetheris_Extreme_Shader.zip.txt",
    "Aetheris_Shader_Pack.zip",
    "Aetheris_Shader_Pack.zip.txt",
    "Aetheris_Legacy_Shader_Pack.zip",
    "Aetheris_Legacy_Shader_Pack.zip.txt"
]

shader_dir = os.path.join(share_dir, "shaders")
for sf in required_shaders:
    sp = os.path.join(shader_dir, sf)
    if not os.path.exists(sp):
        record_failure(f"Missing shader file: {sp}")
    elif sf.endswith(".zip"):
        try:
            with zipfile.ZipFile(sp, "r") as z:
                if z.testzip() is not None:
                    record_failure(f"Corrupted shader zip: {sp}")
                nl = z.namelist()
                has_root_shaders = any(n.startswith("shaders/") for n in nl)
                if not has_root_shaders:
                    record_failure(f"Shaderpack fails Java NIO root compliance (no shaders/ at root): {sp}")
        except Exception as e:
            record_failure(f"Error reading shader zip {sp}: {e}")

print(f"  -> Verified {len(required_shaders)} shader files and companion configs.")

# ----------------------------------------------------------------------
# TEST 3: Master Resource Packs & Formats
# ----------------------------------------------------------------------
print("\n[TEST 3] Auditing Master Resource Packs in D:\\AetherisShare\\resourcepacks...")
rp_dir = os.path.join(share_dir, "resourcepacks")

modern_packs = [
    "Aetheris_Ultimate_32x.zip",
    "Aetheris_Ultimate_Pack.zip",
    "MyCustomPack_Modern_32x.zip"
]

legacy_packs = [
    "Aetheris_Legacy_32x.zip",
    "MyCustomPack_1.8.9_32x.zip",
    "Private Default.zip",
    "[1.8.9] Aetheris Legacy 32x.zip"
]

for mp in modern_packs:
    mpp = os.path.join(rp_dir, mp)
    if not os.path.exists(mpp):
        record_failure(f"Missing modern resource pack: {mpp}")
    else:
        with zipfile.ZipFile(mpp, "r") as z:
            if z.testzip() is not None:
                record_failure(f"Corrupted resource pack zip: {mpp}")
            if "pack.mcmeta" not in z.namelist():
                record_failure(f"Missing pack.mcmeta in {mpp}")
            else:
                meta = json.loads(z.read("pack.mcmeta").decode("utf-8"))
                pformat = meta.get("pack", {}).get("pack_format")
                if pformat != 88:
                    record_failure(f"Invalid pack_format in {mpp}: {pformat}, expected 88")

for lp in legacy_packs:
    lpp = os.path.join(rp_dir, lp)
    if not os.path.exists(lpp):
        record_failure(f"Missing legacy resource pack: {lpp}")
    else:
        with zipfile.ZipFile(lpp, "r") as z:
            if z.testzip() is not None:
                record_failure(f"Corrupted resource pack zip: {lpp}")
            if "pack.mcmeta" not in z.namelist():
                record_failure(f"Missing pack.mcmeta in {lpp}")
            else:
                meta = json.loads(z.read("pack.mcmeta").decode("utf-8"))
                pformat = meta.get("pack", {}).get("pack_format")
                if pformat != 1:
                    record_failure(f"Invalid pack_format in {lpp}: {pformat}, expected 1")

print(f"  -> Verified {len(modern_packs) + len(legacy_packs)} master resource packs.")

# ----------------------------------------------------------------------
# TEST 4: Modpack Archives & mods/ Layout
# ----------------------------------------------------------------------
print("\n[TEST 4] Auditing Modpack Archives in D:\\AetherisShare\\modpacks...")
modpack_dir = os.path.join(share_dir, "modpacks")

legacy_mp = os.path.join(modpack_dir, "Aetheris_Modpack_Legacy_1.8.9.zip")
modern_mp = os.path.join(modpack_dir, "Aetheris_Modpack_Modern_26.2.zip")

if not os.path.exists(legacy_mp):
    record_failure(f"Missing legacy modpack zip: {legacy_mp}")
else:
    with zipfile.ZipFile(legacy_mp, "r") as z:
        if z.testzip() is not None:
            record_failure(f"Corrupted legacy modpack: {legacy_mp}")
        nl = z.namelist()
        mods = [n for n in nl if n.startswith("mods/") and n.endswith(".jar")]
        if len(mods) < 55:
            record_failure(f"Legacy modpack mod count mismatch: got {len(mods)}, expected >= 55")
        root_jars = [n for n in nl if "/" not in n and n.endswith(".jar")]
        if root_jars:
            record_failure(f"Found loose root jars in legacy modpack: {root_jars}")

if not os.path.exists(modern_mp):
    record_failure(f"Missing modern modpack zip: {modern_mp}")
else:
    with zipfile.ZipFile(modern_mp, "r") as z:
        if z.testzip() is not None:
            record_failure(f"Corrupted modern modpack: {modern_mp}")
        nl = z.namelist()
        mods = [n for n in nl if n.startswith("mods/") and n.endswith(".jar")]
        if len(mods) < 250:
            record_failure(f"Modern modpack mod count too low: got {len(mods)}, expected >= 250")
        root_jars = [n for n in nl if "/" not in n and n.endswith(".jar")]
        if root_jars:
            record_failure(f"Found loose root jars in modern modpack: {root_jars}")

print("  -> Verified modpack archives layout and jar containment.")

# ----------------------------------------------------------------------
# TEST 5: Lunar HUD Presets & JSON Schemas
# ----------------------------------------------------------------------
print("\n[TEST 5] Auditing Lunar HUD Presets in D:\\AetherisShare\\lunar_huds...")
huds_dir = os.path.join(share_dir, "lunar_huds")

required_huds = [
    "Aetheris Balanced",
    "Aetheris BedWars",
    "Aetheris Main",
    "Aetheris Performance",
    "Aetheris PvP",
    "Aetheris Visual Stream"
]

for hud in required_huds:
    hp = os.path.join(huds_dir, hud)
    if not os.path.exists(hp) or not os.path.isdir(hp):
        record_failure(f"Missing HUD preset directory: {hp}")
    else:
        for jf in ["controls.json", "general.json", "mods.json", "performance.json"]:
            jfp = os.path.join(hp, jf)
            if not os.path.exists(jfp):
                record_failure(f"Missing HUD file {jf} in {hp}")
            else:
                try:
                    with open(jfp, "r", encoding="utf-8") as f:
                        json.load(f)
                except Exception as e:
                    record_failure(f"Invalid JSON syntax in {jfp}: {e}")

pm_file = os.path.join(huds_dir, "profile_manager.json")
if not os.path.exists(pm_file):
    record_failure(f"Missing profile_manager.json in {huds_dir}")
else:
    with open(pm_file, "r", encoding="utf-8") as f:
        json.load(f)

print(f"  -> Verified {len(required_huds)} Lunar HUD presets and JSON schemas.")

# ----------------------------------------------------------------------
# TEST 6: Complete Lunar Profile Bundles (8 Profiles)
# ----------------------------------------------------------------------
print("\n[TEST 6] Auditing 8 Complete Lunar Profile Bundles in D:\\AetherisShare\\lunar_profiles...")
lp_dir = os.path.join(share_dir, "lunar_profiles")

expected_profiles = [
    ("aetheris-ultimate-modern-visual-26.2", 198, "Modern"),
    ("aetheris-ultimate-modern-balanced-26.2", 198, "Modern"),
    ("aetheris-ultimate-modern-performance-26.2", 181, "Modern"),
    ("aetheris-ultimate-modpack-modern-26.2", 249, "Modern"),
    ("aetheris-ultimate-legacy-1.8.9", 57, "Legacy"),
    ("aetheris-ultimate-legacy-visual-1.8.9", 57, "Legacy"),
    ("aetheris-ultimate-legacy-balanced-1.8.9", 57, "Legacy"),
    ("aetheris-ultimate-legacy-performance-1.8.9", 57, "Legacy")
]

for pname, min_mods, category in expected_profiles:
    pdir = os.path.join(lp_dir, pname)
    if not os.path.exists(pdir):
        record_failure(f"Missing Lunar profile bundle: {pdir}")
    else:
        # Check mods/
        mdir = os.path.join(pdir, "mods")
        if not os.path.exists(mdir):
            record_failure(f"Missing mods directory in {pdir}")
        else:
            jars = [f for f in os.listdir(mdir) if f.endswith(".jar")]
            if len(jars) < min_mods:
                record_failure(f"Mod count low in {pdir}: got {len(jars)}, expected at least {min_mods}")
                
        # Check config/
        cdir = os.path.join(pdir, "config")
        if not os.path.exists(cdir):
            record_failure(f"Missing config directory in {pdir}")
            
        # Check shaderpacks/
        sdir = os.path.join(pdir, "shaderpacks")
        if not os.path.exists(sdir):
            record_failure(f"Missing shaderpacks in {pdir}")
            
        # Check resourcepacks/
        rdir = os.path.join(pdir, "resourcepacks")
        if not os.path.exists(rdir):
            record_failure(f"Missing resourcepacks in {pdir}")
            
        # Check options.txt & jvm-options.txt
        for rf in ["options.txt", "jvm-options.txt", "icon.png", "featured_image.png"]:
            rfp = os.path.join(pdir, rf)
            if not os.path.exists(rfp):
                record_failure(f"Missing required file {rf} in {pdir}")

print(f"  -> Verified all 8 profile bundles in D:\\AetherisShare\\lunar_profiles.")

# ----------------------------------------------------------------------
# TEST 7: Documentation Completeness
# ----------------------------------------------------------------------
print("\n[TEST 7] Auditing Documentation in D:\\AetherisShare\\docs...")
docs_dir = os.path.join(share_dir, "docs")
required_docs = [
    "INSTALLATION_GUIDE.md",
    "PROFILES_OVERVIEW.md",
    "SHADERS_AND_TEXTURES.md",
    "TROUBLESHOOTING.md"
]

for doc in required_docs:
    dp = os.path.join(docs_dir, doc)
    if not os.path.exists(dp) or os.path.getsize(dp) == 0:
        record_failure(f"Missing or empty documentation file: {dp}")

print(f"  -> Verified {len(required_docs)} documentation files.")

# ----------------------------------------------------------------------
# TEST 8: SQLite profiles.db Registration & Schema Validation
# ----------------------------------------------------------------------
print("\n[TEST 8] Validating Lunar Client SQLite profiles.db Registration...")
db_path = os.path.expandvars(r"%USERPROFILE%\.lunarclient\db\profiles.db")
if not os.path.exists(db_path):
    record_failure(f"profiles.db does not exist at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT path, name, allocated_memory, jvm_arguments, loaders, type FROM profiles;")
    rows = cur.fetchall()
    db_paths = {r[0]: r for r in rows}
    
    for pname, min_mods, category in expected_profiles:
        if pname not in db_paths:
            record_failure(f"Profile {pname} not registered in profiles.db")
        else:
            r = db_paths[pname]
            alloc_mem = r[2]
            jvm_args = r[3]
            loaders = r[4]
            if alloc_mem != 8192:
                record_failure(f"Profile {pname} has allocated_memory={alloc_mem}, expected 8192")
            if not jvm_args or "-XX:+UseG1GC" not in jvm_args or "-XX:MaxGCPauseMillis=200" not in jvm_args:
                record_failure(f"Profile {pname} missing tuned G1GC jvm_arguments")
            if category == "Modern" and "fabric" not in loaders:
                record_failure(f"Profile {pname} loaders mismatch: {loaders}, expected fabric")
            if category == "Legacy" and "forge" not in loaders:
                record_failure(f"Profile {pname} loaders mismatch: {loaders}, expected forge")
    conn.close()

print(f"  -> Verified 8 Lunar profiles registered in SQLite profiles.db with 8GB memory & G1GC flags.")

# ----------------------------------------------------------------------
# TEST 9: Headless Installer Execution (Selective & Dry-Run Modes)
# ----------------------------------------------------------------------
print("\n[TEST 9] Testing Headless Execution of install.ps1...")
test_modes = [
    ["-Mode", "Selective", "-ProfileNames", "visual,legacy", "-NonInteractive", "-SkipBackup"],
    ["-Mode", "HUDs", "-NonInteractive", "-SkipBackup"]
]

for targs in test_modes:
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(share_dir, "install.ps1")] + targs
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        record_failure(f"Installer failed with args {' '.join(targs)}: {res.stderr}")
    else:
        print(f"  -> Installer succeeded for mode args: {' '.join(targs)}")

# ----------------------------------------------------------------------
# FINAL SUMMARY
# ----------------------------------------------------------------------
print("\n" + "=" * 70)
if len(failures) == 0:
    print("  ALL 9 VERIFICATION TEST SUITES PASSED (0 FAILURES)!")
    print("  D:\\AetherisShare is 100% SYNCHRONIZED, HARDENED & PRODUCTION READY!")
    print("=" * 70)
    sys.exit(0)
else:
    print(f"  VERIFICATION FAILED: {len(failures)} issues detected!")
    for f in failures:
        print(f"    - {f}")
    print("=" * 70)
    sys.exit(1)
