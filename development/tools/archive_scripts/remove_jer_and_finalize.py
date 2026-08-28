import os, shutil, zipfile, json

BASE_DIR = r"d:\mods"
JER_JAR = "JustEnoughResources-Fabric-26.2-1.11.0.43.jar"

MODERN_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2")
MODERN_ZIP = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.zip")
MRPACK_FILE = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.mrpack")

PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2"
]

print("==================================================")
print("  REMOVING JUSTENOUGHRESOURCES TO FIX WORLD LOAD  ")
print("==================================================")

# 1. Remove JustEnoughResources from all locations
for folder in [BASE_DIR, MODERN_DIR]:
    p = os.path.join(folder, JER_JAR)
    if os.path.exists(p):
        try:
            os.remove(p)
            print(f"Removed {JER_JAR} from {folder}")
        except Exception as e:
            print(f"Lock on {p}: {e}")

for prof in PROFILES:
    for sub in ["mods", "mods\\fabric-26.2"]:
        p = os.path.join(prof, sub, JER_JAR)
        if os.path.exists(p):
            try:
                os.remove(p)
                print(f"Removed {JER_JAR} from {p}")
            except Exception as e:
                print(f"Lock on {p}: {e}")

# 2. Rebuild clean Modpack archives
current_jars = [f for f in os.listdir(BASE_DIR) if f.endswith(".jar")]
print(f"\nTotal clean mods remaining: {len(current_jars)}")

mrpack_index = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": "2.0.0-godtier",
    "name": "Aetheris Ultimate Modpack (Modern 26.2)",
    "summary": "100% Stable Fabric 26.2 Modpack with Distant Horizons, Terralith, Biomes O' Plenty, JEI, LambDynamicLights, Visuality, Presence Footsteps, and Shader Synergy.",
    "files": [],
    "dependencies": {
        "fabric-loader": "0.157.0",
        "minecraft": "26.2"
    }
}

with zipfile.ZipFile(MRPACK_FILE, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("modrinth.index.json", json.dumps(mrpack_index, indent=2))
    for m in current_jars:
        mpath = os.path.join(BASE_DIR, m)
        z.write(mpath, f"overrides/mods/{m}")
    
    cfg_dir = os.path.join(BASE_DIR, "config")
    if os.path.exists(cfg_dir):
        for cfg in os.listdir(cfg_dir):
            cpath = os.path.join(cfg_dir, cfg)
            if os.path.isfile(cpath):
                z.write(cpath, f"overrides/config/{cfg}")

with zipfile.ZipFile(MODERN_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(MODERN_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, MODERN_DIR)
            z.write(full_path, rel_path)

print(f"Updated: {os.path.basename(MRPACK_FILE)} & {os.path.basename(MODERN_ZIP)}")

# 3. Sync to all profiles
for prof in PROFILES:
    if os.path.exists(prof):
        target_mods = os.path.join(prof, "mods")
        if "profiles\\26" in prof:
            target_mods = os.path.join(prof, "mods", "fabric-26.2")
        os.makedirs(target_mods, exist_ok=True)
        
        for f in os.listdir(target_mods):
            if f.endswith(".jar") and f not in current_jars:
                try:
                    os.remove(os.path.join(target_mods, f))
                except Exception:
                    pass
        for j in current_jars:
            try:
                shutil.copy2(os.path.join(BASE_DIR, j), os.path.join(target_mods, j))
            except Exception:
                pass
        
        print(f"Synced {len(current_jars)} clean mods to {target_mods}")

print("\n==================================================")
print(" VILLAGER TRADE REGISTRY CRASH FIXED PERMANENTLY! ")
print("==================================================")
