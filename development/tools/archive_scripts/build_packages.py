import os, shutil, zipfile, datetime, json

BASE_DIR = r"d:\mods"
MODERN_OUT_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2")
MODERN_ZIP = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.zip")

LEGACY_OUT_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Legacy_1.8.9")
LEGACY_ZIP = os.path.join(BASE_DIR, "Aetheris_Modpack_Legacy_1.8.9.zip")

LUNAR_26_MODS = r"C:\Users\a7med\.lunarclient\profiles\26\mods\fabric-26.2"
LUNAR_18_MODS = r"C:\Users\a7med\.lunarclient\profiles\1.8\mods\forge-1.8.9"
DOT_MINECRAFT = r"C:\Users\a7med\AppData\Roaming\.minecraft"

print("==================================================")
print("   AETHERIS MODPACK SUITE - PACKAGING & DEPLOY    ")
print("==================================================")

# Clean previous output dirs
for d in [MODERN_OUT_DIR, LEGACY_OUT_DIR]:
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)

# 1. Assemble Modern 26.2 Fabric Mods
print("\n[1/4] Assembling Modern 26.2 Fabric Mods...")
modern_jars = [f for f in os.listdir(BASE_DIR) if f.endswith(".jar")]
print(f"Found {len(modern_jars)} primary mod jars in {BASE_DIR}")

for j in modern_jars:
    src = os.path.join(BASE_DIR, j)
    dst = os.path.join(MODERN_OUT_DIR, j)
    shutil.copy2(src, dst)

# Also copy dependencies folder for complete offline runtime support
dep_src = os.path.join(BASE_DIR, "dependencies")
if os.path.exists(dep_src):
    dep_dst = os.path.join(MODERN_OUT_DIR, "dependencies")
    shutil.copytree(dep_src, dep_dst, dirs_exist_ok=True)
    print(f"Bundled {len(os.listdir(dep_src))} runtime sub-dependencies into dependencies/ folder.")

# 2. Assemble Legacy 1.8.9 Mods
print("\n[2/4] Assembling Legacy 1.8.9 OptiFine/Forge Mods...")
legacy_sources = []
if os.path.exists(LUNAR_18_MODS):
    for f in os.listdir(LUNAR_18_MODS):
        if f.endswith(".jar"):
            legacy_sources.append(os.path.join(LUNAR_18_MODS, f))

# Also check .minecraft/mods for any 1.8.9 jars
mc_mods = os.path.join(DOT_MINECRAFT, "mods")
if os.path.exists(mc_mods):
    for f in os.listdir(mc_mods):
        if f.endswith(".jar") and f not in [os.path.basename(x) for x in legacy_sources]:
            legacy_sources.append(os.path.join(mc_mods, f))

print(f"Found {len(legacy_sources)} Legacy 1.8.9 mod jars.")
for src in legacy_sources:
    dst = os.path.join(LEGACY_OUT_DIR, os.path.basename(src))
    shutil.copy2(src, dst)

# 3. Create Zip Archives
print("\n[3/4] Creating Optimized Zip Packages...")

def zip_folder(folder_path, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"Created: {os.path.basename(output_zip)} ({size_mb:.2f} MB)")

zip_folder(MODERN_OUT_DIR, MODERN_ZIP)
zip_folder(LEGACY_OUT_DIR, LEGACY_ZIP)

print("\n[4/4] Done assembling modpack packages!")
