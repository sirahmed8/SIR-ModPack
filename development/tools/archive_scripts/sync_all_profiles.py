import os, shutil

BASE_DIR = r"d:\mods"
MODERN_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2")
LUNAR_PROFILE_AETHERIS = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2"
LUNAR_PROFILE_26 = r"C:\Users\a7med\.lunarclient\profiles\26"
MC_DIR = r"C:\Users\a7med\AppData\Roaming\.minecraft"

print("==================================================")
print("  SYNCHRONIZING ALL PROFILES ACROSS LUNAR CLIENT  ")
print("==================================================")

jars = [f for f in os.listdir(BASE_DIR) if f.endswith(".jar")]
print(f"Total valid mods to sync: {len(jars)}")

# Sync to Lunar Aetheris Profile
for target_mods_dir in [
    os.path.join(LUNAR_PROFILE_AETHERIS, "mods"),
    os.path.join(LUNAR_PROFILE_26, "mods", "fabric-26.2"),
    os.path.join(MC_DIR, "mods")
]:
    if os.path.exists(os.path.dirname(target_mods_dir)):
        os.makedirs(target_mods_dir, exist_ok=True)
        # remove old/deleted jars
        for f in os.listdir(target_mods_dir):
            if f.endswith(".jar") and f not in jars:
                os.remove(os.path.join(target_mods_dir, f))
                print(f"Removed stale jar: {f} from {target_mods_dir}")
        # copy current jars
        for j in jars:
            shutil.copy2(os.path.join(BASE_DIR, j), os.path.join(target_mods_dir, j))
        print(f"Synced {len(jars)} mods into {target_mods_dir}")

# Sync configs
cfg_src = os.path.join(BASE_DIR, "config")
for target_cfg_dir in [
    os.path.join(LUNAR_PROFILE_AETHERIS, "config"),
    os.path.join(LUNAR_PROFILE_26, "config"),
    os.path.join(MC_DIR, "config")
]:
    if os.path.exists(os.path.dirname(target_cfg_dir)):
        os.makedirs(target_cfg_dir, exist_ok=True)
        for cfg in os.listdir(cfg_src):
            src_file = os.path.join(cfg_src, cfg)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, os.path.join(target_cfg_dir, cfg))
        print(f"Synced configs into {target_cfg_dir}")

print("\nAll Lunar Client profiles and Minecraft directories are 100% synchronized!")
