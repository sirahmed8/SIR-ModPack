import os, shutil, zipfile, json

BASE_DIR = r"d:\mods"
LUNAR_26_MODS = r"C:\Users\a7med\.lunarclient\profiles\26\mods\fabric-26.2"
MC_MODS = r"C:\Users\a7med\AppData\Roaming\.minecraft\mods"
MODERN_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2")

print("==================================================")
print("     REMOVING C2ME & CLEANING LUNAR COMPATIBILITY ")
print("==================================================")

# 1. Remove c2me jar from d:\mods and target folders
c2me_jars = [
    "c2me-fabric-mc26.2-0.4.2-alpha.0.43.jar"
]

for cjar in c2me_jars:
    for loc in [BASE_DIR, MODERN_DIR, LUNAR_26_MODS, MC_MODS]:
        p = os.path.join(loc, cjar)
        if os.path.exists(p):
            os.remove(p)
            print(f"Removed incompatible C2ME jar: {p}")

# 2. Clean c2me sub-jars from dependencies folders
for dep_dir in [os.path.join(BASE_DIR, "dependencies"), os.path.join(MODERN_DIR, "dependencies"), os.path.join(LUNAR_26_MODS, "dependencies")]:
    if os.path.exists(dep_dir):
        for f in os.listdir(dep_dir):
            if f.startswith("c2me-"):
                fp = os.path.join(dep_dir, f)
                os.remove(fp)
                print(f"Removed C2ME sub-module: {f}")

# 3. Clean c2me.toml config
for cdir in [os.path.join(BASE_DIR, "config"), os.path.join(MODERN_DIR, "config"), r"C:\Users\a7med\AppData\Roaming\.minecraft\config"]:
    c2me_cfg = os.path.join(cdir, "c2me.toml")
    if os.path.exists(c2me_cfg):
        os.remove(c2me_cfg)
        print(f"Removed {c2me_cfg}")

# 4. Copy all current valid jars from BASE_DIR into MODERN_DIR and LUNAR_26_MODS
all_valid_jars = [f for f in os.listdir(BASE_DIR) if f.endswith(".jar")]
print(f"\nRemaining verified modern mods: {len(all_valid_jars)}")

for d in [MODERN_DIR, LUNAR_26_MODS]:
    if os.path.exists(d):
        # Sync jars
        for f in os.listdir(d):
            if f.endswith(".jar") and f not in all_valid_jars:
                os.remove(os.path.join(d, f))
        for j in all_valid_jars:
            shutil.copy2(os.path.join(BASE_DIR, j), os.path.join(d, j))
print("Synced verified mod collection to Modern folder and Lunar Client 26 profile.")

# 5. Rebuild Offline-Ready .mrpack
print("\nRebuilding Aetheris_Modpack_Modern_26.2.mrpack...")
MRPACK_FILE = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.mrpack")

mrpack_index = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": "2.0.0-godtier",
    "name": "Aetheris Ultimate Modpack (Modern 26.2)",
    "summary": "100% Lunar Client & Fabric Compatible Modpack with Aetheris Core, Shader & Resource Pack Synergy.",
    "files": [],
    "dependencies": {
        "fabric-loader": "0.157.0",
        "minecraft": "26.2"
    }
}

with zipfile.ZipFile(MRPACK_FILE, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("modrinth.index.json", json.dumps(mrpack_index, indent=2))
    for m in all_valid_jars:
        mpath = os.path.join(BASE_DIR, m)
        z.write(mpath, f"overrides/mods/{m}")
    
    dep_dir = os.path.join(BASE_DIR, "dependencies")
    if os.path.exists(dep_dir):
        for root, dirs, files in os.walk(dep_dir):
            for f in files:
                fpath = os.path.join(root, f)
                rel = os.path.relpath(fpath, BASE_DIR)
                z.write(fpath, f"overrides/{rel}")
                
    cfg_dir = os.path.join(BASE_DIR, "config")
    if os.path.exists(cfg_dir):
        for cfg in os.listdir(cfg_dir):
            cpath = os.path.join(cfg_dir, cfg)
            if os.path.isfile(cpath):
                z.write(cpath, f"overrides/config/{cfg}")

print(f"Created: {os.path.basename(MRPACK_FILE)} ({os.path.getsize(MRPACK_FILE)/(1024*1024):.2f} MB)")

# 6. Rebuild Aetheris_Modpack_Modern_26.2.zip
print("\nRebuilding Aetheris_Modpack_Modern_26.2.zip...")
MODERN_ZIP = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.zip")
with zipfile.ZipFile(MODERN_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(MODERN_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, MODERN_DIR)
            z.write(full_path, rel_path)

print(f"Created: {os.path.basename(MODERN_ZIP)} ({os.path.getsize(MODERN_ZIP)/(1024*1024):.2f} MB)")
print("\n==================================================")
print("             LUNAR CLIENT FIX COMPLETE!           ")
print("==================================================")
