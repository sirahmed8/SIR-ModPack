import os, shutil

# 1. Sync Lunar HUDs
source_huds = r"C:\Users\a7med\.lunarclient\settings\game"
huds_dirs = [r"D:\AetherisShare\lunar_huds", r"D:\AetherisShare\lunar-settings"]
for hdir in huds_dirs:
    os.makedirs(hdir, exist_ok=True)
    for item in ["Aetheris Balanced", "Aetheris BedWars", "Aetheris Main", "Aetheris Performance", "Aetheris PvP", "Aetheris Visual Stream"]:
        sp = os.path.join(source_huds, item)
        dp = os.path.join(hdir, item)
        if os.path.exists(sp):
            if os.path.exists(dp):
                shutil.rmtree(dp)
            shutil.copytree(sp, dp)
            print(f"Synced HUD preset {item} -> {hdir}")
            
    # profile_manager.json
    spm = os.path.join(source_huds, "profile_manager.json")
    dpm = os.path.join(hdir, "profile_manager.json")
    if os.path.exists(spm):
        shutil.copy2(spm, dpm)
        print(f"Synced profile_manager.json -> {hdir}")

# 2. Sync Profile Bundles
lunar_base = r"C:\Users\a7med\.lunarclient\profiles"
target_full = r"D:\AetherisShare\lunar_profiles"
target_alias = r"D:\AetherisShare\profiles"
os.makedirs(target_full, exist_ok=True)
os.makedirs(target_alias, exist_ok=True)

profile_map = [
    ("visual", "aetheris-ultimate-modern-visual-26.2"),
    ("balanced", "aetheris-ultimate-modern-balanced-26.2"),
    ("performance", "aetheris-ultimate-modern-performance-26.2"),
    ("modpack", "aetheris-ultimate-modpack-modern-26.2"),
    ("legacy", "aetheris-ultimate-legacy-1.8.9"),
    ("legacy-visual", "aetheris-ultimate-legacy-visual-1.8.9"),
    ("legacy-balanced", "aetheris-ultimate-legacy-balanced-1.8.9"),
    ("legacy-performance", "aetheris-ultimate-legacy-performance-1.8.9")
]

for alias, canonical in profile_map:
    src_profile = os.path.join(lunar_base, canonical)
    dst_full = os.path.join(target_full, canonical)
    dst_alias = os.path.join(target_alias, alias)
    
    if not os.path.exists(src_profile):
        print(f"ERROR: Source profile missing: {src_profile}")
        continue
        
    print(f"Syncing profile: {canonical}...")
    # Sync canonical full folder
    if os.path.exists(dst_full):
        shutil.rmtree(dst_full)
    shutil.copytree(src_profile, dst_full)
    
    # Sync alias folder
    if os.path.exists(dst_alias):
        shutil.rmtree(dst_alias)
    shutil.copytree(src_profile, dst_alias)
    
    # Ensure canonical folder also in target_alias for full backwards compatibility
    dst_canonical_in_alias = os.path.join(target_alias, canonical)
    if not os.path.exists(dst_canonical_in_alias):
        shutil.copytree(src_profile, dst_canonical_in_alias)

print("Profile bundles sync complete.")
