import os, zipfile, shutil

SHADER_DIR = r"d:\shader"
RP_DIR = r"d:\resource pack"

TARGET_PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2"
]

print("==================================================")
print(" PACKAGING & SYNCING ALL SHADERPACKS & RESOURCES  ")
print("==================================================")

# 1. Zip any unzipped shader folders in d:\shader
for item in os.listdir(SHADER_DIR):
    item_path = os.path.join(SHADER_DIR, item)
    if os.path.isdir(item_path):
        out_zip = os.path.join(SHADER_DIR, f"{item}.zip")
        if not os.path.exists(out_zip):
            print(f"Zipping shader folder: {item} -> {item}.zip")
            with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:
                for root, dirs, files in os.walk(item_path):
                    for f in files:
                        fp = os.path.join(root, f)
                        rel = os.path.relpath(fp, item_path)
                        z.write(fp, rel)
            print(f"  -> Created {os.path.basename(out_zip)}")

# 2. Get all shader zips & txt presets
shader_files = [f for f in os.listdir(SHADER_DIR) if f.endswith(".zip") or f.endswith(".txt")]
print(f"\nFound {len(shader_files)} shader files/presets in {SHADER_DIR}")

# 3. Sync to all target directories
for target in TARGET_PROFILES:
    if os.path.exists(target):
        sp_dir = os.path.join(target, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        for sf in shader_files:
            src = os.path.join(SHADER_DIR, sf)
            dst = os.path.join(sp_dir, sf)
            shutil.copy2(src, dst)
        print(f"Synced all shaderpacks into: {sp_dir}")

        rp_dir = os.path.join(target, "resourcepacks")
        os.makedirs(rp_dir, exist_ok=True)
        for rpf in ["MyCustomPack_Modern_32x.zip", "MyCustomPack_1.8.9_32x.zip"]:
            rp_src = os.path.join(RP_DIR, rpf)
            if os.path.exists(rp_src):
                shutil.copy2(rp_src, os.path.join(rp_dir, rpf))
        print(f"Synced resource packs into: {rp_dir}")

print("\n==================================================")
print(" ALL SHADERPACKS (INCLUDING COMPLEMENTARY R5.8.1) ")
print("          ARE NOW FULLY PACKAGED & SYNCED!        ")
print("==================================================")
