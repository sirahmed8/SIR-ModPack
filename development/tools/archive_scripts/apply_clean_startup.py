import os, shutil

BASE_DIR = r"d:\mods"
SHADER_DIR = r"d:\shader"
RP_DIR = r"d:\resource pack"

PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2"
]

print("==================================================")
print("  APPLYING CLEAN STARTUP CONFIGS & SYNCING ALL    ")
print("==================================================")

# 1. Update options.txt to permanently skip narrator & onboarding popups
for prof in PROFILES:
    if os.path.exists(prof):
        for opt_name in ["options.txt", "optionsLC.txt"]:
            opt_path = os.path.join(prof, opt_name)
            if os.path.exists(opt_path):
                with open(opt_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                
                new_lines = []
                keys_seen = set()
                for line in lines:
                    if line.startswith("onboardingFinished:"):
                        new_lines.append("onboardingFinished:true\n")
                        keys_seen.add("onboardingFinished")
                    elif line.startswith("joinedFirstServer:"):
                        new_lines.append("joinedFirstServer:true\n")
                        keys_seen.add("joinedFirstServer")
                    elif line.startswith("narrator:"):
                        new_lines.append("narrator:0\n")
                        keys_seen.add("narrator")
                    else:
                        new_lines.append(line)
                
                if "onboardingFinished" not in keys_seen:
                    new_lines.append("onboardingFinished:true\n")
                if "joinedFirstServer" not in keys_seen:
                    new_lines.append("joinedFirstServer:true\n")
                    
                with open(opt_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                print(f"Updated {opt_path} (Narrator & onboarding popup permanently suppressed)")

# 2. Suppress WorldWeaver / BetterX popup
ww_config = """{
  "showWelcomeScreen": false,
  "hideExperimentalWarning": true,
  "versionChecker": false
}"""

for prof in PROFILES:
    cfg_dir = os.path.join(prof, "config")
    if os.path.exists(cfg_dir):
        with open(os.path.join(cfg_dir, "worldweaver.json"), "w", encoding="utf-8") as f:
            f.write(ww_config)
        with open(os.path.join(cfg_dir, "betterx.json"), "w", encoding="utf-8") as f:
            f.write(ww_config)

# 3. Sync Resource Pack & Shaders to all profiles
for prof in PROFILES:
    if os.path.exists(prof):
        # Sync RP
        rp_dir = os.path.join(prof, "resourcepacks")
        os.makedirs(rp_dir, exist_ok=True)
        shutil.copy2(os.path.join(RP_DIR, "MyCustomPack_Modern_32x.zip"), os.path.join(rp_dir, "MyCustomPack_Modern_32x.zip"))
        print(f"Synced fixed MyCustomPack_Modern_32x.zip to {rp_dir}")
        
        # Sync Shader
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip"), os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip.txt"), os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        print(f"Synced Aetheris_Shader_Pack to {sp_dir}")

print("\nAll profiles updated with zero popups and fixed assets!")
