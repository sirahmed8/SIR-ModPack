import os, shutil, zipfile

SHADER_DIR = r"d:\shader"
BASE_EUPHORIA = os.path.join(SHADER_DIR, "ComplementaryUnbound_r5.8.1 + EuphoriaPatches_1.9.3")
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
print("  MASTER v11.0: SINGLE HD MOON, DARK LEAVES, ZERO FOAM, HDR SUN, NO CIRCLE")
print("==================================================")

# ---------------------------------------------------------
# 1. FIX DUAL MOONS IN GBUFFERS_SKYBASIC.GLSL
# ---------------------------------------------------------
skybasic_glsl = os.path.join(AETHERIS_DIR, "shaders", "program", "gbuffers_skybasic.glsl")
if os.path.exists(skybasic_glsl):
    with open(skybasic_glsl, "r", encoding="utf-8", errors="ignore") as f:
        sb_code = f.read()
    
    # Disable procedural moon drawing in skybasic so only textured HD moon from skytextured renders
    if "#if SUN_MOON_STYLE >= 2" in sb_code:
        idx_start = sb_code.find("#if SUN_MOON_STYLE >= 2")
        idx_end = sb_code.find("#endif\n        #endif", idx_start)
        if idx_start != -1 and idx_end != -1:
            sb_code = sb_code[:idx_start] + "// Procedural moon removed to prevent dual overlapping moons\n" + sb_code[idx_end+16:]
            print("[1/5] Eliminated procedural moon in gbuffers_skybasic.glsl (Single HD Moon only)")
            with open(skybasic_glsl, "w", encoding="utf-8") as f:
                f.write(sb_code)

# ---------------------------------------------------------
# 2. FIX LEAVES AT NIGHT IN MAINLIGHTING.GLSL
# ---------------------------------------------------------
main_lighting_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "lighting", "mainLighting.glsl")
if os.path.exists(main_lighting_glsl):
    with open(main_lighting_glsl, "r", encoding="utf-8", errors="ignore") as f:
        ml_code = f.read()
    
    # Strictly disable foliage SSS and boost night canopy shadows
    old_sss = "int oldSubsurfaceMode = subsurfaceMode;\n    if (subsurfaceMode == 2 && sunVisibility2 < 0.05) subsurfaceMode = 0;"
    new_sss = "int oldSubsurfaceMode = subsurfaceMode;\n    if (subsurfaceMode > 0 && sunVisibility2 < 0.08) subsurfaceMode = 0;"
    if old_sss in ml_code:
        ml_code = ml_code.replace(old_sss, new_sss)
    elif "int oldSubsurfaceMode = subsurfaceMode;" in ml_code:
        ml_code = ml_code.replace("int oldSubsurfaceMode = subsurfaceMode;", new_sss)

    with open(main_lighting_glsl, "w", encoding="utf-8") as f:
        f.write(ml_code)
    print("[2/5] Hardened leaf lighting against night glow in mainLighting.glsl")

# ---------------------------------------------------------
# 3. FIX BLINDING SUN WHITEOUT IN SKY.GLSL
# ---------------------------------------------------------
sky_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "atmospherics", "sky.glsl")
if os.path.exists(sky_glsl):
    with open(sky_glsl, "r", encoding="utf-8", errors="ignore") as f:
        sky_code = f.read()
    # Clamp sun glare so it never washes out the screen in pure white
    sky_code = sky_code.replace("finalSky += glare * shadowTime * glareColor;", "finalSky += clamp(glare * shadowTime * glareColor, vec3(0.0), vec3(0.35));")
    with open(sky_glsl, "w", encoding="utf-8") as f:
        f.write(sky_code)
    print("[3/5] Clamped sun glare in sky.glsl for balanced HDR contrast")

# ---------------------------------------------------------
# 4. FIX CIRCULAR FOG BUBBLE IN WATERFOG.GLSL
# ---------------------------------------------------------
waterfog_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "atmospherics", "fog", "waterFog.glsl")
if os.path.exists(waterfog_glsl):
    new_waterfog_code = """#ifndef INCLUDE_WATER_FOG
    #define INCLUDE_WATER_FOG

    float GetWaterFog(float lViewPos) {
        #if WATER_FOG_MULT != 100
            #define WATER_FOG_MULT_M WATER_FOG_MULT * 0.01;
            lViewPos *= WATER_FOG_MULT_M;
        #endif

        // Smooth linear exponential depth fog without quadratic radial bubble
        float fog = lViewPos * 0.035;
        return 1.0 - exp(-fog);
    }
#endif
"""
    with open(waterfog_glsl, "w", encoding="utf-8") as f:
        f.write(new_waterfog_code)
    print("[4/5] Replaced quadratic radial bubble with smooth exponential fog in waterFog.glsl")

# ---------------------------------------------------------
# 5. ELIMINATE 100% OF WHITE FOAM CLOUDS IN WATER.GLSL
# ---------------------------------------------------------
water_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "materials", "specificMaterials", "translucents", "water.glsl")
if os.path.exists(water_glsl):
    with open(water_glsl, "r", encoding="utf-8", errors="ignore") as f:
        w_code = f.read()
    
    # Completely eliminate foam calculation
    if "// Water Foam //" in w_code:
        f_start = w_code.find("// Water Foam //")
        f_end = w_code.find("////\n\n            // Reflections", f_start)
        if f_start != -1 and f_end != -1:
            w_code = w_code[:f_start] + "// White foam cloud calculations permanently disabled\n            " + w_code[f_end:]
            print("[5/5] Completely removed white foam clouds from water.glsl")
            with open(water_glsl, "w", encoding="utf-8") as f:
                f.write(w_code)

# ---------------------------------------------------------
# 6. MASTER PRESET DEPLOYMENT
# ---------------------------------------------------------
master_v11_preset = """# Aetheris Shader Pack v11.0 - Master Extreme Profile
profile=EXTREME
profile2=AETHERIS
tonemap=DoBSLTonemap
ANISOTROPIC_FILTER=4
ATM_COLOR_MULTS=true
AURORA_COLOR_PRESET=-1
AURORA_INFLUENCE=true
AURORA_STYLE_DEFINE=3
BIOME_COLORED_NETHER_PORTALS=true
BLOCKLIGHT_CAUSTICS=true
BLOOM_STRENGTH=0.016
CAVE_SMOKE=true
CELESTIAL_BOTH_HEMISPHERES=true
CLEAR_WATER_SPOTS=false
CLOUD_QUALITY=3
CLOUD_SHADOWS=true
CLOUD_STYLE_DEFINE=3
CLOUD_SUN_MOON_SHADING=3
COATED_TEXTURES=true
COLORED_LIGHTING=256
COLORGRADING=true
DAYLIGHT_CYCLE_COMPAT=true
DETAIL_QUALITY=3
DIRECTIONAL_LIGHTMAP_NORMALS=true
DRAGON_DEATH_EFFECT=2
EMISSIVE_ENCHANTING_TABLE=true
EMISSIVE_FLOWERS=0
EMISSIVE_SOUL_SAND=true
EMISSIVE_SPRING_FLOWERS=false
END_CRYSTAL_VORTEX=3
END_PORTAL_BEAM=true
END_SMOKE=true
END_TWINKLING_STARS=12
ENTITY_SHADOW=2
EP_END_FLASH=2
FANCY_GLASS=true
GENERATED_NORMALS=false
GENERATED_SPECULAR=false
GLOWING_ARMOR_TRIM=true
GLOWING_EMERALD_BLOCK=true
GLOWING_NETHER_TREES=false
GLOWING_ORE_MASTER=1
GLOWING_ORE_MULT=1.15
GLOWING_ORE_IRON=true
GLOWING_ORE_GOLD=true
GLOWING_ORE_COPPER=true
GLOWING_ORE_REDSTONE=true
GLOWING_ORE_LAPIS=true
GLOWING_ORE_EMERALD=true
GLOWING_ORE_DIAMOND=true
GLOWING_ORE_NETHERQUARTZ=true
GLOWING_ORE_NETHERGOLD=true
GLOWING_ORE_GILDEDBLACKSTONE=true
GLOWING_ORE_ANCIENTDEBRIS=true
GLOWING_ORE_MODDED=true
GLOWING_RAW_BLOCKS=true
GLOWING_WART=false
GREEN_SCREEN_LIME=true
HIGH_QUALITY_CLOUDS=true
IMAGE_SHARPENING=3
INTERACTIVE_FOLIAGE=true
IPBR_COMPAT_MODE_DEFINE=true
LAVA_EDGE_EFFECT=0
LAVA_VARIATION=0
LIGHTMAP_CURVES=true
LIGHTSHAFT_BEHAVIOUR=3
LIGHTSHAFT_DAY_I=160
LIGHTSHAFT_NIGHT_I=25
LIGHTSHAFT_QUALI_DEFINE=4
LIGHTSHAFT_SMOKE=true
LIGHT_COLOR_MULTS=true
MCBL_MAIN_DEFINE=3
MIRROR_TINTED_GLASS=true
MOON_PHASE_INF_PURKINJE=false
MOSS_IN_CAVES=0
NETHER_PORTAL_NOISE=1
NIGHT_BRIGHTNESS=80
NIGHT_DESATURATION=true
NIGHT_NEBULAE=1
NIGHT_NEBULA_I=50
NO_RAIN_ABOVE_CLOUDS=true
OVERWORLD_BEAMS=true
PARALLAX=true
PARALLAX_DEPTH=0.45
PARALLAX_QUALITY=64
PARALLAX_DISTANCE=32
SELF_SHADOW=false
SLOPE_NORMALS=true
PIXEL_WATER=0
PURPLE_END_FIRE=true
PURKINJE_OVERWRITE=0
RAIN_ATMOSPHERE=true
RAIN_PUDDLES=2
RAIN_STYLE=2
RANDOM_AURORA=2
REDSTONE_IPBR=true
REFLECTION_RES=1.0
RP_MODE=2
SAND_CONDITION=0
SEASONS=1
SHADOW_QUALITY=5
shadowDistance=256.0
shadowMapResolution=4096
SHADOW_SMOOTHING=1
SHOOTING_STARS=true
SITUATIONAL_GLOWING_TRIMS=true
SITUATIONAL_ORES=true
SOUL_SAND_VALLEY_OVERHAUL=true
SSAO_QUALI_DEFINE=3
STAR_AMOUNT=2
NIGHT_STAR_AMOUNT=3
STAR_BRIGHTNESS=16
STAR_LAYER_OW=1
STAR_ROUNDNESS_OW=10
STAR_SOFTNESS_OW=0.8
STAR_SIZE=0.7
SUN_GLARE_AMOUNT=0
SUN_INTENSITY=75
ROUND_SUN=false
SUN_MOON_STYLE=0
TWINKLING_STARS=12
WATER_ALPHA_MULT=130
WATER_BUMPINESS=1.10
WATER_BUMP_BIG=1.20
WATER_BUMP_MED=1.30
WATER_CAUSTIC_STRENGTH=1.50
WATER_CAUSTIC_STYLE_DEFINE=3
WATER_FOAM=false
WATER_FOAM_I=0
WATER_FOG_MULT=180
WATER_REFLECT_QUALITY=3
BLOCK_REFLECT_QUALITY=3
WATER_SPEED_MULT=1.10
WATER_STYLE_DEFINE=3
WAVING_FOLIAGE=true
WAVING_LEAVES=true
WAVING_WATER_VERTEX=true
WAVING_LAVA=false
WAVING_LANTERNS=true
WAVING_GRASS=true
WAVING_LILY_PAD=true
WAVING_SUGAR_CANE=true
WAVIER_LAVA=false
WB_ANAMORPHIC=true
WB_CHROMATIC=true
WB_FOV_SCALED=true
WORLD_BLUR=2
WORLD_SPACE_REFLECTIONS=1
DARKER_DEPTH_OCEANS=0
FOLIAGE_SSS=true
LEAF_SUBSURFACE=true
TRANSLUCENT_COLORED_SHADOWS=true
TAA=true
"""

with open(AETHERIS_TXT, "w", encoding="utf-8") as f:
    f.write(master_v11_preset)
with open(AETHERIS_ZIP_TXT, "w", encoding="utf-8") as f:
    f.write(master_v11_preset)

# Recompress shader
print("Recompressing Aetheris_Shader_Pack.zip...")
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

# D:\Games sync
d_games_txt = r"D:\Games\Aetheris_Shader_Pack.zip.txt"
if os.path.exists(os.path.dirname(d_games_txt)):
    shutil.copy2(AETHERIS_TXT, d_games_txt)
    print(f"Synced to {d_games_txt}")

print("\n==================================================")
print("  MASTER v11.0 DEPLOYED SUCCESSFULLY!             ")
print("==================================================")
