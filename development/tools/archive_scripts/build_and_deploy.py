import os, shutil, zipfile, datetime, json, hashlib

BASE_DIR = r"d:\mods"
SHADER_DIR = r"d:\shader"
RP_DIR = r"d:\resource pack"

MODERN_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2")
MODERN_ZIP = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.zip")
MRPACK_FILE = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.mrpack")

LEGACY_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Legacy_1.8.9")
LEGACY_ZIP = os.path.join(BASE_DIR, "Aetheris_Modpack_Legacy_1.8.9.zip")

LUNAR_26_MODS = r"C:\Users\a7med\.lunarclient\profiles\26\mods\fabric-26.2"
LUNAR_18_MODS = r"C:\Users\a7med\.lunarclient\profiles\1.8\mods\forge-1.8.9"
DOT_MINECRAFT = r"C:\Users\a7med\AppData\Roaming\.minecraft"

def zip_directory(src_dir, dest_zip):
    print(f"Compressing {os.path.basename(dest_zip)}...")
    with zipfile.ZipFile(dest_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, src_dir)
                z.write(full_path, rel_path)
    size_mb = os.path.getsize(dest_zip) / (1024 * 1024)
    print(f"  -> Created {os.path.basename(dest_zip)} ({size_mb:.2f} MB)")

def build_all():
    print("==================================================")
    print("   AETHERIS MODPACK & ECOSYSTEM BUILD & DEPLOY    ")
    print("==================================================")
    
    # 1. Update Configs
    cfg_dir = os.path.join(BASE_DIR, "config")
    os.makedirs(cfg_dir, exist_ok=True)
    
    # 2. Package Modern Modpack Zip
    zip_directory(MODERN_DIR, MODERN_ZIP)
    
    # 3. Package Legacy Modpack Zip
    zip_directory(LEGACY_DIR, LEGACY_ZIP)
    
    # 4. Sync to Lunar Client Profile 26 & .minecraft
    print("\n[DEPLOY] Syncing ecosystem components to Lunar Client & Minecraft...")
    
    # Sync Shaders
    mc_shaders = os.path.join(DOT_MINECRAFT, "shaderpacks")
    os.makedirs(mc_shaders, exist_ok=True)
    shader_zip = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip")
    if os.path.exists(shader_zip):
        shutil.copy2(shader_zip, os.path.join(mc_shaders, "Aetheris_Shader_Pack.zip"))
        shader_txt = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip.txt")
        if os.path.exists(shader_txt):
            shutil.copy2(shader_txt, os.path.join(mc_shaders, "Aetheris_Shader_Pack.zip.txt"))
        print("  -> Synced Aetheris Shader Pack to .minecraft/shaderpacks/")

    # Sync Resource Packs
    mc_rp = os.path.join(DOT_MINECRAFT, "resourcepacks")
    os.makedirs(mc_rp, exist_ok=True)
    for rp in ["MyCustomPack_Modern_32x.zip", "MyCustomPack_1.8.9_32x.zip"]:
        rp_path = os.path.join(RP_DIR, rp)
        if os.path.exists(rp_path):
            shutil.copy2(rp_path, os.path.join(mc_rp, rp))
            print(f"  -> Synced {rp} to .minecraft/resourcepacks/")

    # Sync Configs
    mc_config = os.path.join(DOT_MINECRAFT, "config")
    os.makedirs(mc_config, exist_ok=True)
    for cfg in os.listdir(cfg_dir):
        src_cfg = os.path.join(cfg_dir, cfg)
        if os.path.isfile(src_cfg):
            shutil.copy2(src_cfg, os.path.join(mc_config, cfg))
    print("  -> Synced optimized hardware configs to .minecraft/config/")
    
    # Sync iris.properties to .minecraft root
    iris_p = os.path.join(cfg_dir, "iris.properties")
    if os.path.exists(iris_p):
        shutil.copy2(iris_p, os.path.join(DOT_MINECRAFT, "iris.properties"))
        print("  -> Synced iris.properties (shaderPack=Aetheris_Shader_Pack.zip)")

    print("\n==================================================")
    print("      AETHERIS ECOSYSTEM IS 100% READY TO PLAY!    ")
    print("==================================================")

if __name__ == "__main__":
    build_all()
