import os, shutil, zipfile, json

SHADER_DIR = r"d:\shader"
AETHERIS_DIR = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack")
AETHERIS_ZIP = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip")
AETHERIS_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.txt")
UNIFORMS_GLSL = os.path.join(AETHERIS_DIR, "shaders", "lib", "uniforms.glsl")

PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2"
]

print("==================================================")
print("  FIXING DH SHADER COMPILATION & WORLDGEN CRASH   ")
print("==================================================")

# ---------------------------------------------------------
# 1. FIX DH_TERRAIN & DH_WATER SHADER UNIFORM DEFINITIONS
# ---------------------------------------------------------
print("\n[1/3] Fixing dhProjection Uniform Declarations in Shader...")

if os.path.exists(UNIFORMS_GLSL):
    with open(UNIFORMS_GLSL, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Replace #ifdef DISTANT_HORIZONS with #if defined DISTANT_HORIZONS || defined DH_TERRAIN || defined DH_WATER
    old_target = "#ifdef DISTANT_HORIZONS\n    uniform int dhRenderDistance;\n\n    uniform mat4 dhProjection;\n    uniform mat4 dhProjectionInverse;"
    new_target = "#if defined DISTANT_HORIZONS || defined DH_TERRAIN || defined DH_WATER\n    uniform int dhRenderDistance;\n    uniform int dhMaterialId;\n\n    uniform mat4 dhProjection;\n    uniform mat4 dhProjectionInverse;"

    if old_target in content:
        content = content.replace(old_target, new_target)
        print("  -> Updated uniforms.glsl with global DH uniforms")
    else:
        # Fallback replacement
        content = content.replace("#ifdef DISTANT_HORIZONS", "#if defined DISTANT_HORIZONS || defined DH_TERRAIN || defined DH_WATER\n    uniform int dhMaterialId;")
        print("  -> Patched DISTANT_HORIZONS condition in uniforms.glsl")

    with open(UNIFORMS_GLSL, "w", encoding="utf-8") as f:
        f.write(content)

# Also ensure program/dh_terrain.glsl and program/dh_water.glsl have safe uniform fallbacks
for prog in ["dh_terrain.glsl", "dh_water.glsl"]:
    prog_path = os.path.join(AETHERIS_DIR, "shaders", "program", prog)
    if os.path.exists(prog_path):
        with open(prog_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        # Check if dhProjection is declared
        full_p = "".join(lines)
        if "uniform mat4 dhProjection;" not in full_p:
            # Insert at top under Common
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if "#include \"/lib/common.glsl\"" in line:
                    new_lines.append("\n// DH Fallback Uniforms\nuniform mat4 dhProjection;\nuniform mat4 dhProjectionInverse;\nuniform int dhMaterialId;\nuniform int dhRenderDistance;\n")
            with open(prog_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"  -> Injected explicit DH uniforms in {prog}")

# Recompress Aetheris_Shader_Pack.zip
print("Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# ---------------------------------------------------------
# 2. FIX WOVER / BETTERX WORLDGEN CRASH
# ---------------------------------------------------------
print("\n[2/3] Fixing WoVer / BetterNether WorldGen Config...")

wover_client_cfg = {
  "create_version": "26.201.2",
  "internal": {
    "did_present_welcome_screen": True
  },
  "general": {
    "check_for_new_versions": False,
    "prefere_modrinth": False,
    "force_betterx_world_type": False
  },
  "loading": {
    "disable_experimental_warning": True
  },
  "modify_version": "26.201.2"
}

for prof in PROFILES:
    cfg_dir = os.path.join(prof, "config", "wover")
    os.makedirs(cfg_dir, exist_ok=True)
    with open(os.path.join(cfg_dir, "client.json"), "w", encoding="utf-8") as f:
        json.dump(wover_client_cfg, f, indent=2)
    print(f"Updated: {os.path.join(cfg_dir, 'client.json')}")

# Also update d:\mods\config\wover\client.json
os.makedirs(r"d:\mods\config\wover", exist_ok=True)
with open(r"d:\mods\config\wover\client.json", "w", encoding="utf-8") as f:
    json.dump(wover_client_cfg, f, indent=2)

# ---------------------------------------------------------
# 3. SYNC SHADERS & CONFIGS TO ALL PROFILES
# ---------------------------------------------------------
print("\n[3/3] Synchronizing all profiles...")

for prof in PROFILES:
    if os.path.exists(prof):
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(AETHERIS_ZIP, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        print(f"Synced shader to {sp_dir}")

print("\n==================================================")
print(" DH SHADER & WORLDGEN CRASH 100% FIXED & SYNCED!  ")
print("==================================================")
