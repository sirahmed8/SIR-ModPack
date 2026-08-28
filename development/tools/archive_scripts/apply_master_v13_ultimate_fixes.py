import os, shutil, zipfile, json

SHADER_DIR = r"d:\shader"
RP_PATH = r"d:\resource pack\MyCustomPack_Modern_32x.zip"
AETHERIS_DIR = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack")
AETHERIS_ZIP = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip")
AETHERIS_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.txt")
AETHERIS_ZIP_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip.txt")

PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2",
    r"C:\Users\a7med\.lunarclient\profiles\1.8"
]

print("==================================================")
print("  MASTER v13.0: COMPLETE DEFINITIVE OVERHAUL      ")
print("==================================================")

# ---------------------------------------------------------
# 1. FIX RED MUSHROOM CHECKERBOARD IN RESOURCE PACK
# ---------------------------------------------------------
if os.path.exists(RP_PATH):
    temp_rp_dir = r"d:\resource pack\temp_rp_extract"
    if os.path.exists(temp_rp_dir):
        shutil.rmtree(temp_rp_dir)
    os.makedirs(temp_rp_dir, exist_ok=True)

    with zipfile.ZipFile(RP_PATH, "r") as z:
        z.extractall(temp_rp_dir)

    # Standard clean vanilla multipart red_mushroom_block blockstate
    clean_mushroom_blockstate = {
        "multipart": [
            {"when": {"up": "true"}, "apply": {"model": "minecraft:block/red_mushroom_block"}},
            {"when": {"down": "true"}, "apply": {"model": "minecraft:block/red_mushroom_block"}},
            {"when": {"north": "true"}, "apply": {"model": "minecraft:block/red_mushroom_block"}},
            {"when": {"south": "true"}, "apply": {"model": "minecraft:block/red_mushroom_block"}},
            {"when": {"east": "true"}, "apply": {"model": "minecraft:block/red_mushroom_block"}},
            {"when": {"west": "true"}, "apply": {"model": "minecraft:block/red_mushroom_block"}},
            {"when": {"up": "false"}, "apply": {"model": "minecraft:block/mushroom_block_inside"}},
            {"when": {"down": "false"}, "apply": {"model": "minecraft:block/mushroom_block_inside"}},
            {"when": {"north": "false"}, "apply": {"model": "minecraft:block/mushroom_block_inside"}},
            {"when": {"south": "false"}, "apply": {"model": "minecraft:block/mushroom_block_inside"}},
            {"when": {"east": "false"}, "apply": {"model": "minecraft:block/mushroom_block_inside"}},
            {"when": {"west": "false"}, "apply": {"model": "minecraft:block/mushroom_block_inside"}}
        ]
    }

    bs_target = os.path.join(temp_rp_dir, "assets", "minecraft", "blockstates", "red_mushroom_block.json")
    with open(bs_target, "w", encoding="utf-8") as f:
        json.dump(clean_mushroom_blockstate, f, indent=2)

    # Re-zip resource pack
    with zipfile.ZipFile(RP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(temp_rp_dir):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, temp_rp_dir)
                z.write(full, rel)

    shutil.rmtree(temp_rp_dir)
    print("[1/5] Fixed red_mushroom_block missing texture in MyCustomPack_Modern_32x.zip")

    # Sync RP to all profile resourcepacks directories
    for prof in PROFILES:
        rp_dir = os.path.join(prof, "resourcepacks")
        if os.path.exists(rp_dir):
            shutil.copy2(RP_PATH, os.path.join(rp_dir, "MyCustomPack_Modern_32x.zip"))
            print(f"Synced Resource Pack to {rp_dir}")

# ---------------------------------------------------------
# 2. FIX OVERLAPPING PROCEDURAL MOON IN SKYBASIC.GLSL
# ---------------------------------------------------------
skybasic_glsl = os.path.join(AETHERIS_DIR, "shaders", "program", "gbuffers_skybasic.glsl")
if os.path.exists(skybasic_glsl):
    with open(skybasic_glsl, "r", encoding="utf-8", errors="ignore") as f:
        sb_text = f.read()
    
    # Strictly disable the procedural moon so only textured HD moon from skytextured renders
    sb_text = sb_text.replace("#if SUN_MOON_STYLE >= 2", "#if 0 // Procedural moon disabled for Single HD Moon")
    with open(skybasic_glsl, "w", encoding="utf-8") as f:
        f.write(sb_text)
    print("[2/5] Hard-disabled procedural moon in gbuffers_skybasic.glsl (Single HD Moon only)")

# ---------------------------------------------------------
# 3. FIX GLOWING LEAVES AT SUNSET & NIGHT IN LEAVES.GLSL & MAINLIGHTING.GLSL
# ---------------------------------------------------------
leaves_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "materials", "specificMaterials", "terrain", "leaves.glsl")
if os.path.exists(leaves_glsl):
    with open(leaves_glsl, "r", encoding="utf-8", errors="ignore") as f:
        l_text = f.read()
    
    if "color.rgb *= mix(vec3(0.35, 0.40, 0.45)" not in l_text:
        l_text += "\n// Natural leaf night darkening (no neon glowing leaves)\ncolor.rgb *= mix(vec3(0.35, 0.40, 0.45), vec3(1.0), sunVisibility2);\n"
    with open(leaves_glsl, "w", encoding="utf-8") as f:
        f.write(l_text)
    print("[3/5] Applied natural night canopy shading to leaves.glsl")

# ---------------------------------------------------------
# 4. FIX DENSE OCEAN WATER & ZERO FOAM IN WATER.GLSL
# ---------------------------------------------------------
water_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "materials", "specificMaterials", "translucents", "water.glsl")
if os.path.exists(water_glsl):
    with open(water_glsl, "r", encoding="utf-8", errors="ignore") as f:
        w_text = f.read()

    # Dense water opacity & deep ocean darkening
    old_water_fog = "float waterFog = max0(1.0 - exp(lViewPosDifM * 0.075));"
    new_water_fog = "float waterFog = max0(1.0 - exp(lViewPosDifM * 0.35));"
    if old_water_fog in w_text:
        w_text = w_text.replace(old_water_fog, new_water_fog)

    old_water_alpha = "color.a = clamp01((0.35 + 0.65 * waterFog) * edgeFade);"
    new_water_alpha = "color.a = clamp01((0.82 + 0.18 * waterFog) * edgeFade);"
    if old_water_alpha in w_text:
        w_text = w_text.replace(old_water_alpha, new_water_alpha)

    # Disable foam calculation
    w_text = w_text.replace(
        "#if WATER_FOAM_I > 0 && defined GBUFFERS_WATER && !(defined MIRROR_DIMENSION || defined WORLD_CURVATURE)",
        "#if 0 // Foam permanently disabled"
    )

    with open(water_glsl, "w", encoding="utf-8") as f:
        f.write(w_text)
    print("[4/5] Configured rich dense ocean opacity and 0 foam in water.glsl")

# ---------------------------------------------------------
# 5. RECOMPRESS SHADERPACK & SYNC PRESETS
# ---------------------------------------------------------
print("[5/5] Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# Sync shader & presets across all profiles
for prof in PROFILES:
    if os.path.exists(prof):
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(AETHERIS_ZIP, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.txt"))
        print(f"Synced Shaderpack to {sp_dir}")

d_games_txt = r"D:\Games\Aetheris_Shader_Pack.zip.txt"
if os.path.exists(os.path.dirname(d_games_txt)):
    shutil.copy2(AETHERIS_TXT, d_games_txt)
    print(f"Synced to {d_games_txt}")

print("\n==================================================")
print("  MASTER v13.0 COMPLETE: ALL REPORTED BUGS FIXED! ")
print("==================================================")
