import os, shutil, zipfile, json

BASE_DIR = r"d:\mods"
EP_JAR = "EuphoriaPatcher-1.9.3-r5.8.1-fabric.jar"

TARGET_DIRS = [
    BASE_DIR,
    os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2"),
    r"C:\Users\a7med\.lunarclient\profiles\26\mods\fabric-26.2",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2\mods",
    r"C:\Users\a7med\AppData\Roaming\.minecraft\mods"
]

print("==================================================")
print(" REMOVING EUPHORIAPATCHER TO ELIMINATE TOAST SPAM ")
print("==================================================")

for t in TARGET_DIRS:
    jar_path = os.path.join(t, EP_JAR)
    if os.path.exists(jar_path):
        os.remove(jar_path)
        print(f"Removed {EP_JAR} from {t}")

# Rebuild .mrpack and .zip without euphoria patcher
all_valid_jars = [f for f in os.listdir(BASE_DIR) if f.endswith(".jar")]
print(f"\nRemaining clean mods: {len(all_valid_jars)}")

# Rebuild Modrinth mrpack
MRPACK_FILE = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.mrpack")
mrpack_index = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": "2.0.0-godtier",
    "name": "Aetheris Ultimate Modpack (Modern 26.2)",
    "summary": "100% Clean Lunar Client & Fabric Modpack with Aetheris Core, Shader & Resource Pack Synergy.",
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

print(f"Updated: {os.path.basename(MRPACK_FILE)}")

# Rebuild Zip
MODERN_ZIP = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.zip")
MODERN_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2")
with zipfile.ZipFile(MODERN_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(MODERN_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, MODERN_DIR)
            z.write(full_path, rel_path)

print(f"Updated: {os.path.basename(MODERN_ZIP)}")
print("\nEuphoriaPatcher red toast spam permanently eliminated!")
