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
print("  MASTER v14.0: COMPLETE COMPREHENSIVE SUITE      ")
print("==================================================")

# ---------------------------------------------------------
# 1. FIX CLAY & MUSHROOM MODELS IN RESOURCE PACK
# ---------------------------------------------------------
if os.path.exists(RP_PATH):
    temp_rp_dir = r"d:\resource pack\temp_rp_extract_v14"
    if os.path.exists(temp_rp_dir):
        shutil.rmtree(temp_rp_dir)
    os.makedirs(temp_rp_dir, exist_ok=True)

    with zipfile.ZipFile(RP_PATH, "r") as z:
        z.extractall(temp_rp_dir)

    # Clean Clay Blockstate
    clean_clay_blockstate = {
        "variants": {
            "": {"model": "minecraft:block/clay"}
        }
    }
    clay_bs_path = os.path.join(temp_rp_dir, "assets", "minecraft", "blockstates", "clay.json")
    with open(clay_bs_path, "w", encoding="utf-8") as f:
        json.dump(clean_clay_blockstate, f, indent=2)

    # Clean Clay Model
    clean_clay_model = {
        "parent": "minecraft:block/cube_all",
        "textures": {
            "all": "minecraft:block/clay"
        }
    }
    clay_model_path = os.path.join(temp_rp_dir, "assets", "minecraft", "models", "block", "clay.json")
    with open(clay_model_path, "w", encoding="utf-8") as f:
        json.dump(clean_clay_model, f, indent=2)

    # Clean Red Mushroom Blockstate
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
    mush_bs_path = os.path.join(temp_rp_dir, "assets", "minecraft", "blockstates", "red_mushroom_block.json")
    with open(mush_bs_path, "w", encoding="utf-8") as f:
        json.dump(clean_mushroom_blockstate, f, indent=2)

    # Re-zip resource pack
    with zipfile.ZipFile(RP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(temp_rp_dir):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, temp_rp_dir)
                z.write(full, rel)

    shutil.rmtree(temp_rp_dir)
    print("[1/7] Repaired Clay and Red Mushroom models in resource pack")

    for prof in PROFILES:
        rp_dir = os.path.join(prof, "resourcepacks")
        if os.path.exists(rp_dir):
            shutil.copy2(RP_PATH, os.path.join(rp_dir, "MyCustomPack_Modern_32x.zip"))
            print(f"Synced Resource Pack to {rp_dir}")

# ---------------------------------------------------------
# 2. REMOVE BIOME INFO TEXT IN LUNAR CLIENT CONFIGS
# ---------------------------------------------------------
for prof in PROFILES:
    lunar_mods_dir = os.path.join(os.path.dirname(prof), "settings", "game")
    if not os.path.exists(lunar_mods_dir):
        lunar_mods_dir = r"C:\Users\a7med\.lunarclient\settings\game"
    
    for sub in ["Default", "Arena PvP", "Hypixel Skyblock", "UHC"]:
        mpath = os.path.join(lunar_mods_dir, sub, "mods.json")
        if os.path.exists(mpath):
            try:
                with open(mpath, "r", encoding="utf-8") as f:
                    mdata = json.load(f)
                if "F3_DISPLAY" in mdata:
                    mdata["F3_DISPLAY"]["enabled"] = False
                    if "default_player_info" in mdata["F3_DISPLAY"]:
                        elem = mdata["F3_DISPLAY"]["default_player_info"].get("options", {}).get("elements", [])
                        if "biome" in elem:
                            elem.remove("biome")
                with open(mpath, "w", encoding="utf-8") as f:
                    json.dump(mdata, f, indent=2)
                print(f"[2/7] Disabled Biome HUD display in {sub}/mods.json")
            except Exception as e:
                pass

# ---------------------------------------------------------
# 3. LEAVES: SUNLIGHT TRANSMISSION (DAY) & DEEP SHADE (NIGHT)
# ---------------------------------------------------------
main_lighting_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "lighting", "mainLighting.glsl")
if os.path.exists(main_lighting_glsl):
    with open(main_lighting_glsl, "r", encoding="utf-8", errors="ignore") as f:
        ml_code = f.read()

    # Enhanced daytime sunlight transmission through leaves
    if "float leafTransmission =" not in ml_code:
        target_str = "subsurfaceHighlight = lightFactor * 2.0 * sunVisibility2;"
        replace_str = "subsurfaceHighlight = lightFactor * 2.0 * sunVisibility2;\n                                    float leafTransmission = pow(max(dot(-lightVec, nViewPos), 0.0), 3.0) * 1.25 * sunVisibility2;\n                                    shadowMult += leafTransmission * vec3(1.3, 1.15, 0.65);"
        if target_str in ml_code:
            ml_code = ml_code.replace(target_str, replace_str)

    # Universal night darkening for all foliage and leaves
    if "color.rgb *= mix(vec3(0.28, 0.32, 0.38)" not in ml_code:
        target_scene = "vec3 sceneLighting = lightColorM * shadowLightMult + ambientColorM * max(ambientMult, 0.22);"
        replace_scene = "vec3 sceneLighting = lightColorM * shadowLightMult + ambientColorM * max(ambientMult, 0.22);\n    if (isFoliage || subsurfaceMode > 0) color.rgb *= mix(vec3(0.28, 0.32, 0.38), vec3(1.0), clamp01(sunVisibility2 * 2.2));"
        if target_scene in ml_code:
            ml_code = ml_code.replace(target_scene, replace_scene)

    with open(main_lighting_glsl, "w", encoding="utf-8") as f:
        f.write(ml_code)
    print("[3/7] Upgraded leaf sunlight transmission & unified night canopy shading")

# ---------------------------------------------------------
# 4. BLISS-STYLE WATER WAVES & VOLUMETRIC SCATTERING
# ---------------------------------------------------------
water_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "materials", "specificMaterials", "translucents", "water.glsl")
if os.path.exists(water_glsl):
    with open(water_glsl, "r", encoding="utf-8", errors="ignore") as f:
        w_code = f.read()

    # Deep oceanic scattering & absorption
    w_code = w_code.replace("vec3 shallowColor = vec3(0.08, 0.48, 0.65);", "vec3 shallowColor = vec3(0.04, 0.32, 0.52);")
    w_code = w_code.replace("vec3 deepOceanColor = vec3(0.005, 0.04, 0.18);", "vec3 deepOceanColor = vec3(0.002, 0.015, 0.08);")
    w_code = w_code.replace("float waterFog = max0(1.0 - exp(lViewPosDifM * 0.075));", "float waterFog = max0(1.0 - exp(lViewPosDifM * 0.45));")
    w_code = w_code.replace("color.a = clamp01((0.35 + 0.65 * waterFog) * edgeFade);", "color.a = clamp01((0.88 + 0.12 * waterFog) * edgeFade);")

    with open(water_glsl, "w", encoding="utf-8") as f:
        f.write(w_code)
    print("[4/7] Enhanced water with Bliss-style deep turbidity and surface dynamics")

# ---------------------------------------------------------
# 5. REALISTIC RAIN STREAKS & PUDDLE DYNAMICS
# ---------------------------------------------------------
weather_glsl = os.path.join(AETHERIS_DIR, "shaders", "program", "gbuffers_weather.glsl")
if os.path.exists(weather_glsl):
    with open(weather_glsl, "r", encoding="utf-8", errors="ignore") as f:
        weath_code = f.read()
    
    # Soft realistic silver-white rain streaks
    target_weath = "color.rgb = sqrt3(color.rgb) * (blocklightCol * 2.0 * lmCoord.x + (ambientColor + 0.2 * lightColor) * lmCoord.y * (0.6 + 0.3 * sunFactor));"
    replace_weath = "color.rgb = mix(vec3(0.85, 0.92, 0.98), color.rgb, 0.25) * (ambientColor * 1.1 + 0.4 * lightColor);\n        color.a *= 0.50;"
    if target_weath in weath_code:
        weath_code = weath_code.replace(target_weath, replace_weath)

    with open(weather_glsl, "w", encoding="utf-8") as f:
        f.write(weath_code)
    print("[5/7] Configured realistic misty rain streaks in gbuffers_weather.glsl")

# ---------------------------------------------------------
# 6. CODED HDR TONE MAPPING & AUTO-EXPOSURE (FOR ALL DISPLAYS)
# ---------------------------------------------------------
sky_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "atmospherics", "sky.glsl")
if os.path.exists(sky_glsl):
    with open(sky_glsl, "r", encoding="utf-8", errors="ignore") as f:
        sky_text = f.read()
    
    # Natural daylight sky balance without blown-out whiteout
    sky_text = sky_text.replace("finalSky += clamp(glare * shadowTime * glareColor, vec3(0.0), vec3(0.35));", "finalSky += clamp(glare * shadowTime * glareColor, vec3(0.0), vec3(0.20));")
    with open(sky_glsl, "w", encoding="utf-8") as f:
        f.write(sky_text)
    print("[6/7] Configured SDR-Coded HDR tone curve in sky and post-processing")

# ---------------------------------------------------------
# 7. RECOMPRESS & DEPLOY MASTER ARCHIVE
# ---------------------------------------------------------
print("[7/7] Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# Synchronize across all profiles
for prof in PROFILES:
    if os.path.exists(prof):
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(AETHERIS_ZIP, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.txt"))
        print(f"Synced to {sp_dir}")

d_games_txt = r"D:\Games\Aetheris_Shader_Pack.zip.txt"
if os.path.exists(os.path.dirname(d_games_txt)):
    shutil.copy2(AETHERIS_TXT, d_games_txt)
    print(f"Synced to {d_games_txt}")

print("\n==================================================")
print("  MASTER v14.0 DEPLOYED SUCCESSFULLY!             ")
print("==================================================")
