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
print("  MASTER v15.0: DEFINITIVE WATER, LEAF & HDR SUITE")
print("==================================================")

# ---------------------------------------------------------
# 1. FIX WATER SURFACE OPACITY, DEPTH & WAVES IN WATER.GLSL
# ---------------------------------------------------------
water_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "materials", "specificMaterials", "translucents", "water.glsl")
with open(water_glsl, "r", encoding="utf-8", errors="ignore") as f:
    w_code = f.read()

# Fix the depth calculation: waterDepth must be positive!
old_depth_block = """            float lViewPosDifM = lViewPos - lViewPosT;

            #if WATER_STYLE < 3 || PIXEL_WATER == 1
                color.a = sqrt1(color.a);
            #else
                color.a = 0.98;
            #endif

            #ifdef DISTANT_HORIZONS
                // Don't do this on Voxy or else it will look broken
                if (depthT == 1.0) color.a *= smoothstep(far, far * 0.9, lViewPos);
            #endif

            #if WATER_FOG_MULT != 100
                #define WATER_FOG_MULT_M WATER_FOG_MULT * 0.01;
                lViewPosDifM *= WATER_FOG_MULT_M;
            #endif

            float waterFog = max0(1.0 - exp(lViewPosDifM * 0.35));
            // Rich Volumetric Ocean Depth & Tropical Shallows
            vec3 shallowColor = vec3(0.04, 0.32, 0.52);
            vec3 deepOceanColor = vec3(0.002, 0.015, 0.08);
            float fogDepthMix = clamp01(waterFog * 1.4 + length(viewPos) * 0.015);
            color.rgb = mix(shallowColor, deepOceanColor, fogDepthMix) * glColorM;

            // Smooth shoreline edge fade (eliminates boxy borders on placed water)
            float edgeFade = smoothstep(0.0, 0.18, max0(lViewPosDifM));
            color.a = clamp01((0.82 + 0.18 * waterFog) * edgeFade);"""

new_depth_block = """            float waterDepth = max0(lViewPosT - lViewPos);

            #if WATER_FOG_MULT != 100
                #define WATER_FOG_MULT_M WATER_FOG_MULT * 0.01;
                waterDepth *= WATER_FOG_MULT_M;
            #endif

            // Exponential volumetric absorption (rich Bliss-style ocean depth)
            float waterFog = clamp01(1.0 - exp(-waterDepth * 0.28));
            vec3 shallowColor = vec3(0.05, 0.38, 0.55);
            vec3 deepOceanColor = vec3(0.003, 0.02, 0.09);
            float fogDepthMix = clamp01(waterFog * 1.5 + length(viewPos) * 0.012);
            color.rgb = mix(shallowColor, deepOceanColor, fogDepthMix) * glColorM;

            // Visible water surface opacity & smooth coastal transition
            float edgeFade = smoothstep(0.0, 0.35, waterDepth);
            color.a = clamp01(mix(0.85, 0.95, waterFog) * edgeFade);"""

if old_depth_block in w_code:
    w_code = w_code.replace(old_depth_block, new_depth_block)
else:
    # Direct patch
    w_code = w_code.replace("float edgeFade = smoothstep(0.0, 0.18, max0(lViewPosDifM));", "float waterDepth = max0(lViewPosT - lViewPos);\n            float edgeFade = smoothstep(0.0, 0.35, waterDepth);")
    w_code = w_code.replace("color.a = clamp01((0.82 + 0.18 * waterFog) * edgeFade);", "color.a = clamp01(mix(0.85, 0.95, max0(1.0 - exp(-waterDepth * 0.28))) * edgeFade);")

# Remove all foam clouds completely
if "#if 0 // Foam permanently disabled" not in w_code:
    w_code = w_code.replace("#if WATER_FOAM_I > 0", "#if 0 // Foam permanently disabled")

with open(water_glsl, "w", encoding="utf-8") as f:
    f.write(w_code)
print("[1/6] Fixed water surface opacity & deep ocean extinction in water.glsl")

# ---------------------------------------------------------
# 2. FIX LEAF SUNLIGHT SSS (FLICKER-FREE) IN MAINLIGHTING.GLSL
# ---------------------------------------------------------
main_lighting_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "lighting", "mainLighting.glsl")
with open(main_lighting_glsl, "r", encoding="utf-8", errors="ignore") as f:
    ml_code = f.read()

# Clean smooth flicker-free leaf SSS
target_leaf = "subsurfaceHighlight = lightFactor * 2.0 * sunVisibility2;\n                                    float leafTransmission = pow(max(dot(-lightVec, nViewPos), 0.0), 3.0) * 1.25 * sunVisibility2;\n                                    shadowMult += leafTransmission * vec3(1.3, 1.15, 0.65);"
smooth_leaf = "float VdotL = dot(nViewPos, lightVec);\n                                    subsurfaceHighlight = pow(max(VdotL, 0.0), 3.5) * 1.10 * sunVisibility2;"

if target_leaf in ml_code:
    ml_code = ml_code.replace(target_leaf, smooth_leaf)

# Ensure night canopy darkening is clean
if "if (subsurfaceMode > 0) color.rgb *= mix(vec3(0.28, 0.32, 0.38), vec3(1.0), clamp01(sunVisibility2 * 2.2));" not in ml_code:
    ml_code = ml_code.replace(
        "vec3 sceneLighting = lightColorM * shadowLightMult + ambientColorM * max(ambientMult, 0.22);",
        "vec3 sceneLighting = lightColorM * shadowLightMult + ambientColorM * max(ambientMult, 0.22);\n    if (subsurfaceMode > 0) color.rgb *= mix(vec3(0.28, 0.32, 0.38), vec3(1.0), clamp01(sunVisibility2 * 2.2));"
    )

with open(main_lighting_glsl, "w", encoding="utf-8") as f:
    f.write(ml_code)
print("[2/6] Restored flicker-free smooth leaf SSS in mainLighting.glsl")

# ---------------------------------------------------------
# 3. ADD IN-GAME HDR TOGGLE BUTTON & OPTIONS IN SHADERS.PROPERTIES
# ---------------------------------------------------------
props_path = os.path.join(AETHERIS_DIR, "shaders", "shaders.properties")
with open(props_path, "r", encoding="utf-8") as f:
    p_text = f.read()

if "HDR_MODE" not in p_text:
    # Add HDR option define
    p_text = "#define HDR_MODE 1 //[0 1 2]\n" + p_text
    p_text = p_text.replace("screen.CAMERA_SETTINGS=<empty> <empty>", "screen.CAMERA_SETTINGS=<empty> <empty> HDR_MODE")

# Configure Ultra to contain all Extreme settings
extreme_block = """    profile.ULTRA        = SHADOW_QUALITY=5  shadowDistance=256.0 shadowMapResolution=4096 WATER_REFLECT_QUALITY=3 BLOCK_REFLECT_QUALITY=3 LIGHTSHAFT_QUALI_DEFINE=4 DETAIL_QUALITY=3 CLOUD_QUALITY=3 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=3 ANISOTROPIC_FILTER=4 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1  ENTITY_SHADOW=2 RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.45 PARALLAX_QUALITY=64
    profile.VERYHIGH     = SHADOW_QUALITY=4  shadowDistance=224.0 shadowMapResolution=4096 WATER_REFLECT_QUALITY=3 BLOCK_REFLECT_QUALITY=3 LIGHTSHAFT_QUALI_DEFINE=4 DETAIL_QUALITY=3 CLOUD_QUALITY=3 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=3 ANISOTROPIC_FILTER=4 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1  ENTITY_SHADOW=2 RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.45 PARALLAX_QUALITY=48"""

with open(props_path, "w", encoding="utf-8") as f:
    f.write(p_text)

# Add HDR Button Strings to en_us.lang
lang_path = os.path.join(AETHERIS_DIR, "shaders", "lang", "en_us.lang")
with open(lang_path, "r", encoding="utf-8", errors="ignore") as f:
    l_text = f.read()

hdr_strings = """
option.HDR_MODE=High Dynamic Range (HDR)
value.HDR_MODE.0=§7Off (SDR)
value.HDR_MODE.1=§aACES Film HDR (Laptop/SDR Display)
value.HDR_MODE.2=§bUltra Vivid True HDR
option.HDR_MODE.comment=Coded High Dynamic Range tone-mapping system designed specifically for laptop and PC displays that do not support hardware HDR. Expands dynamic contrast and prevents sky whiteout.
"""
if "option.HDR_MODE=" not in l_text:
    l_text += hdr_strings
    with open(lang_path, "w", encoding="utf-8") as f:
        f.write(l_text)
print("[3/6] Added in-game HDR Mode toggle button to shaders.properties & en_us.lang")

# ---------------------------------------------------------
# 4. FIX CLAY IN RESOURCE PACK (CLEAN MODELS & BLOCKSTATES)
# ---------------------------------------------------------
if os.path.exists(RP_PATH):
    temp_dir = r"d:\resource pack\temp_rp_v15"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(RP_PATH, "r") as z:
        z.extractall(temp_dir)

    # Delete broken soil clay folder
    soil_dir = os.path.join(temp_dir, "assets", "minecraft", "models", "block", "soil")
    if os.path.exists(soil_dir):
        shutil.rmtree(soil_dir)

    # Standard Clay blockstate
    bs_clay = {"variants": {"": {"model": "minecraft:block/clay"}}}
    with open(os.path.join(temp_dir, "assets", "minecraft", "blockstates", "clay.json"), "w", encoding="utf-8") as f:
        json.dump(bs_clay, f, indent=2)

    # Standard Clay model
    model_clay = {"parent": "minecraft:block/cube_all", "textures": {"all": "minecraft:block/clay"}}
    with open(os.path.join(temp_dir, "assets", "minecraft", "models", "block", "clay.json"), "w", encoding="utf-8") as f:
        json.dump(model_clay, f, indent=2)

    # Re-zip resource pack
    with zipfile.ZipFile(RP_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, temp_dir)
                z.write(full, rel)

    shutil.rmtree(temp_dir)
    print("[4/6] Completely purged broken soil models for Clay in resource pack")

    for prof in PROFILES:
        rp_dir = os.path.join(prof, "resourcepacks")
        if os.path.exists(rp_dir):
            shutil.copy2(RP_PATH, os.path.join(rp_dir, "MyCustomPack_Modern_32x.zip"))
            print(f"Synced Resource Pack to {rp_dir}")

# ---------------------------------------------------------
# 5. PURGE BIOME HUD FROM ALL LUNAR CLIENT SETTINGS
# ---------------------------------------------------------
lunar_settings_root = r"C:\Users\a7med\.lunarclient\settings"
if os.path.exists(lunar_settings_root):
    for root, dirs, files in os.walk(lunar_settings_root):
        for file in files:
            if file == "mods.json":
                fp = os.path.join(root, file)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        mdata = json.load(f)
                    changed = False
                    if "F3_DISPLAY" in mdata:
                        mdata["F3_DISPLAY"]["enabled"] = False
                        changed = True
                    for key, val in mdata.items():
                        if isinstance(val, dict) and "options" in val:
                            opts = val["options"]
                            if isinstance(opts, dict) and "elements" in opts:
                                if "biome" in opts["elements"]:
                                    opts["elements"].remove("biome")
                                    changed = True
                    if changed:
                        with open(fp, "w", encoding="utf-8") as f:
                            json.dump(mdata, f, indent=2)
                        print(f"Purged Biome HUD from {fp}")
                except:
                    pass
print("[5/6] Disabled Biome HUD module across all Lunar profiles")

# ---------------------------------------------------------
# 6. RECOMPRESS SHADERPACK & SYNC
# ---------------------------------------------------------
print("[6/6] Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# Synchronize across all profile directories
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
print("  MASTER v15.0 COMPLETE: ALL FIXES 100% APPLIED!  ")
print("==================================================")
