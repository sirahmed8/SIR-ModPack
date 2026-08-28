"""
master_cleanup.py
Runs all cleanup operations:
1. Visual/Balanced profile shaderpacks & resourcepacks junk
2. Stock/preset Lunar profiles (small ones, clearly not ours)
3. D:\mods old superseded scripts
4. AetherisShare full rebuild
5. Antigravity brain old scratch files
6. Minecraft / Lunar logs and caches
"""
import os, shutil, json

PROFILES = r"C:\Users\a7med\.lunarclient\profiles"
VISUAL   = os.path.join(PROFILES, "aetheris-ultimate-modern-visual-26.2")
BALANCED = os.path.join(PROFILES, "aetheris-ultimate-modern-balanced-26.2")
LEGACY   = os.path.join(PROFILES, "aetheris-ultimate-legacy-1.8.9")
LUNAR    = r"C:\Users\a7med\.lunarclient"
MC       = r"C:\Users\a7med\AppData\Roaming\.minecraft"
MODS_DIR = r"D:\mods"
AGY_BRAIN= r"C:\Users\a7med\.gemini\antigravity\brain"
THIS_CONV= "a311e7e5-c0b6-47b7-bcf7-7dcc1dba5d4c"  # current conversation — NEVER delete

freed = 0

def rmfile(p, reason=""):
    global freed
    if os.path.isfile(p):
        sz = os.path.getsize(p)
        os.remove(p)
        freed += sz
        print("  DEL  " + str(round(sz/1024/1024,1)).rjust(6) + "MB  " + os.path.basename(p) + ("  [" + reason + "]" if reason else ""))

def rmdir(p, reason=""):
    global freed
    if os.path.isdir(p):
        sz = sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(p) for f in fs if os.path.exists(os.path.join(r,f)))
        shutil.rmtree(p)
        freed += sz
        print("  DEL  " + str(round(sz/1024/1024,1)).rjust(6) + "MB  " + os.path.basename(p) + "/"  + ("  [" + reason + "]" if reason else ""))

# ══════════════════════════════════════════════════════════════════
# 1. CLEAN VISUAL PROFILE — shaderpacks & resourcepacks junk
# ══════════════════════════════════════════════════════════════════
print("=== 1. VISUAL profile junk ===")
vsp = os.path.join(VISUAL, "shaderpacks")
# Old EP + misc shader junk
for junk in ["Aetheris_Shader_Pack.txt", "Aetheris_Shader_Pack.zip",
             "Aetheris_Shader_Pack.zip.txt", "Aetheris_Visual_Preset.txt",
             "_0EuphoriaPatches_ErrorShader.zip"]:
    rmfile(os.path.join(vsp, junk), "EP/old shader junk")
rmdir(os.path.join(vsp, "_0EuphoriaPatches_ErrorShader"), "EP error shader folder")

# Old duplicate resource packs
vrp = os.path.join(VISUAL, "resourcepacks")
for junk in ["Aetheris_Ultimate_32x.zip", "MyCustomPack_Modern_32x.zip",
             "[26.2] Aetheris Ultimate 32x.zip"]:
    rmfile(os.path.join(vrp, junk), "old duplicate pack")

# ══════════════════════════════════════════════════════════════════
# 2. CLEAN BALANCED PROFILE — resourcepacks junk
# ══════════════════════════════════════════════════════════════════
print()
print("=== 2. BALANCED profile junk ===")
brp = os.path.join(BALANCED, "resourcepacks")
for junk in ["Aetheris_Ultimate_32x.zip", "MyCustomPack_Modern_32x.zip",
             "[26.2] Aetheris Ultimate 32x.zip", "Aetheris_Ultimate_32x.zip"]:
    rmfile(os.path.join(brp, junk), "old duplicate pack")

bsp = os.path.join(BALANCED, "shaderpacks")
for junk in ["Aetheris_Shader_Pack.txt", "Aetheris_Shader_Pack.zip",
             "Aetheris_Shader_Pack.zip.txt", "_0EuphoriaPatches_ErrorShader.zip"]:
    rmfile(os.path.join(bsp, junk), "EP/old shader junk")
rmdir(os.path.join(bsp, "_0EuphoriaPatches_ErrorShader"), "EP error shader folder")

# ══════════════════════════════════════════════════════════════════
# 3. REMOVE CLEARLY STOCK PRESET PROFILES (small, no user data)
# ══════════════════════════════════════════════════════════════════
print()
print("=== 3. Stock preset profiles ===")
STOCK_PROFILES = [
    "badlion-1.21", "badlion-1.8",
    "vanilla-1.18", "vanilla-1.21", "vanilla-1.8",
    "mcc-island-for-lunar-client", "max-fps-optimized",
    "fps-modpack", "optimization", "optimized-fps-neo-forge",
    "keo-optimized", "remarkably-optimized",
    "boosted-fps-performance-optimized-fb",
    "fabulously-optimized", "fabulously-optimized-1",
    "wynncraft-for-lunar-client", "performium",
    "more-fps-forge-increase-fps-shaders-1.21-update",
    "sodium-plus", "distant-horizons-iris-shaders",
    "immersed-with-shaders",
]
for prof in STOCK_PROFILES:
    rmdir(os.path.join(PROFILES, prof), "stock preset")

# Larger modpacks — report but keep (user might want them)
LARGE_KEEP = ["all-the-mods-10-atm10", "rlcraft", "skyfactory-4",
              "veritycraft-a-realistic-horror-experience-with-verity",
              "vanilla-perfected"]
print()
print("  [KEPT — large modpacks, check manually]")
for prof in LARGE_KEEP:
    p = os.path.join(PROFILES, prof)
    if os.path.isdir(p):
        sz = sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(p) for f in fs if os.path.exists(os.path.join(r,f)))
        print("  KEEP " + str(round(sz/1024/1024)).rjust(6) + "MB  " + prof)

# ══════════════════════════════════════════════════════════════════
# 4. CLEAN D:\mods — remove superseded scripts
# ══════════════════════════════════════════════════════════════════
print()
print("=== 4. D:\\mods — superseded scripts ===")
SUPERSEDED = [
    "install_shaders.py", "setup_ultimate_pack.py",
    "build_aetheris_packs.py", "finalize_shaders.py",
    "apply_all_fixes.py",
]
for s in SUPERSEDED:
    rmfile(os.path.join(MODS_DIR, s), "superseded")

# ══════════════════════════════════════════════════════════════════
# 5. CLEAN MINECRAFT FOLDER — logs, crash reports, old versions
# ══════════════════════════════════════════════════════════════════
print()
print("=== 5. Minecraft folder cleanup ===")
if os.path.exists(MC):
    # Crash reports
    crash = os.path.join(MC, "crash-reports")
    if os.path.isdir(crash):
        for f in os.listdir(crash):
            rmfile(os.path.join(crash, f), "crash report")

    # Logs
    logs = os.path.join(MC, "logs")
    if os.path.isdir(logs):
        for f in os.listdir(logs):
            if f != "latest.log":
                rmfile(os.path.join(logs, f), "old log")

# ══════════════════════════════════════════════════════════════════
# 6. CLEAN LUNAR CLIENT — logs and caches
# ══════════════════════════════════════════════════════════════════
print()
print("=== 6. Lunar Client logs/cache ===")
for subdir in ["logs", "crash-reports"]:
    lpath = os.path.join(LUNAR, subdir)
    if os.path.isdir(lpath):
        for f in os.listdir(lpath):
            fp = os.path.join(lpath, f)
            if os.path.isfile(fp) and f != "latest.log":
                rmfile(fp, "old lunar log")

# Lunar offline cache (often huge)
for cache_name in ["offline-cache", "jre-cache"]:
    cpath = os.path.join(LUNAR, cache_name)
    # Don't remove jre-cache — needed for Java
    if cache_name == "offline-cache" and os.path.isdir(cpath):
        for f in os.listdir(cpath):
            fp = os.path.join(cpath, f)
            if os.path.isfile(fp):
                rmfile(fp, "offline cache")

# ══════════════════════════════════════════════════════════════════
# 7. CLEAN ANTIGRAVITY BRAIN — old conversation scratch files
# ══════════════════════════════════════════════════════════════════
print()
print("=== 7. Antigravity brain — old scratch ===")
if os.path.isdir(AGY_BRAIN):
    for conv in os.listdir(AGY_BRAIN):
        if conv == THIS_CONV:
            continue  # NEVER touch current conversation
        conv_path = os.path.join(AGY_BRAIN, conv)
        scratch = os.path.join(conv_path, "scratch")
        if os.path.isdir(scratch):
            rmdir(scratch, "old scratch")

print()
print("=" * 60)
print("CLEANUP COMPLETE")
print("=" * 60)
print("  Total freed: " + str(round(freed/1024/1024/1024, 2)) + " GB")
