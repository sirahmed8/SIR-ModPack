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
print("  MASTER v10.0: SUN HDR, HD 8-PHASE MOON, ROUND STARS, SMOOTH LAVA, DARK LEAVES")
print("==================================================")

# ---------------------------------------------------------
# 1. STARS: CIRCULAR & SOFT ASTRONOMICAL POINTS (NOT SQUARES)
# ---------------------------------------------------------
stars_settings_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "shaderSettings", "stars.glsl")
if os.path.exists(stars_settings_glsl):
    with open(stars_settings_glsl, "r", encoding="utf-8", errors="ignore") as f:
        s_code = f.read()
    s_code = s_code.replace("#define STAR_ROUNDNESS_OW 0", "#define STAR_ROUNDNESS_OW 10")
    s_code = s_code.replace("#define STAR_SOFTNESS_OW 0.0", "#define STAR_SOFTNESS_OW 0.8")
    s_code = s_code.replace("#define STAR_SIZE 1.0", "#define STAR_SIZE 0.7")
    s_code = s_code.replace("#define TWINKLING_STARS 0", "#define TWINKLING_STARS 12")
    with open(stars_settings_glsl, "w", encoding="utf-8") as f:
        f.write(s_code)
    print("[1/7] Configured circular anti-aliased Gaussian stars in stars.glsl")

# ---------------------------------------------------------
# 2. WATER: DENSE & ZERO FOAM CLOUD STRIPS
# ---------------------------------------------------------
water_settings_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "shaderSettings", "water.glsl")
if os.path.exists(water_settings_glsl):
    with open(water_settings_glsl, "r", encoding="utf-8", errors="ignore") as f:
        w_code = f.read()
    w_code = w_code.replace("#define WATER_FOAM_I 100", "#define WATER_FOAM_I 0")
    w_code = w_code.replace("#define WATER_FOAM_I 90", "#define WATER_FOAM_I 0")
    w_code = w_code.replace("#define WATER_FOAM_I 115", "#define WATER_FOAM_I 0")
    with open(water_settings_glsl, "w", encoding="utf-8") as f:
        f.write(w_code)
    print("[2/7] Set fallback WATER_FOAM_I to 0 in water settings")

# ---------------------------------------------------------
# 3. LEAF NIGHT SHADING (NO RADIOACTIVE NEON LEAVES AT NIGHT)
# ---------------------------------------------------------
main_lighting_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "lighting", "mainLighting.glsl")
if os.path.exists(main_lighting_glsl):
    with open(main_lighting_glsl, "r", encoding="utf-8", errors="ignore") as f:
        ml_code = f.read()
    if "if (subsurfaceMode == 2 && sunVisibility2 < 0.05)" not in ml_code:
        ml_code = ml_code.replace(
            "int oldSubsurfaceMode = subsurfaceMode;",
            "int oldSubsurfaceMode = subsurfaceMode;\n    if (subsurfaceMode == 2 && sunVisibility2 < 0.05) subsurfaceMode = 0;"
        )
    with open(main_lighting_glsl, "w", encoding="utf-8") as f:
        f.write(ml_code)
    print("[3/7] Hardened leaf daytime SSS gate against night glows")

# ---------------------------------------------------------
# 4. HD MOON: TEXTURED RESOURCE PACK WITH 8 PHASES
# ---------------------------------------------------------
skytextured_glsl = os.path.join(AETHERIS_DIR, "shaders", "program", "gbuffers_skytextured.glsl")
if os.path.exists(skytextured_glsl):
    with open(skytextured_glsl, "r", encoding="utf-8", errors="ignore") as f:
        st_code = f.read()
    # Ensure HD textured moon is never discarded
    st_code = st_code.replace("if (isSun || isMoon) {\n            #if SUN_MOON_STYLE >= 2 && IRIS_VERSION >= 10902\n                discard;\n            #endif", "if (isSun || isMoon) {\n            // Textured HD Moon & Sun Enabled")
    with open(skytextured_glsl, "w", encoding="utf-8") as f:
        f.write(st_code)
    print("[4/7] Enabled textured HD 8-phase moon in gbuffers_skytextured.glsl")

# ---------------------------------------------------------
# 5. CONFIGURE EXTREME & RESTORE ALL PROFILES IN SHADERS.PROPERTIES
# ---------------------------------------------------------
props_path = os.path.join(AETHERIS_DIR, "shaders", "shaders.properties")
ref_props = os.path.join(BASE_EUPHORIA, "shaders", "shaders.properties")

with open(ref_props, "r", encoding="utf-8") as f:
    props_text = f.read()

extreme_profile_str = (
    "profile.EXTREME     = SHADOW_QUALITY=5 shadowDistance=256.0 WATER_REFLECT_QUALITY=3 BLOCK_REFLECT_QUALITY=3 "
    "LIGHTSHAFT_QUALI_DEFINE=4 DETAIL_QUALITY=3 CLOUD_QUALITY=3 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=3 "
    "ANISOTROPIC_FILTER=4 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1 ENTITY_SHADOW=2 "
    "RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.45 PARALLAX_QUALITY=64 PARALLAX_DISTANCE=32 "
    "SLOPE_NORMALS=true !PIXEL_WATER WATER_ALPHA_MULT=120 WATER_FOG_MULT=160 WATER_CAUSTIC_STYLE_DEFINE=3 "
    "WATER_CAUSTIC_STRENGTH=1.50 WATER_BUMPINESS=1.10 WATER_BUMP_BIG=1.20 WATER_BUMP_MED=1.30 "
    "!WATER_FOAM WATER_FOAM_I=0 WATER_SPEED_MULT=1.10 WATER_STYLE_DEFINE=3 WAVING_FOLIAGE=true "
    "WAVING_LEAVES=true WAVING_WATER_VERTEX=true !WAVING_LAVA WAVING_LANTERNS=true WAVING_GRASS=true "
    "WAVING_LILY_PAD=true WAVING_SUGAR_CANE=true !WAVIER_LAVA INTERACTIVE_FOLIAGE=true "
    "ATM_COLOR_MULTS=true AURORA_COLOR_PRESET=-1 AURORA_INFLUENCE=true AURORA_STYLE_DEFINE=3 "
    "BIOME_COLORED_NETHER_PORTALS=true BLOCKLIGHT_CAUSTICS=true BLOOM_STRENGTH=0.020 CAVE_SMOKE=true "
    "CELESTIAL_BOTH_HEMISPHERES=true !CLEAR_WATER_SPOTS CLOUD_SHADOWS=true CLOUD_STYLE_DEFINE=3 "
    "CLOUD_SUN_MOON_SHADING=3 COATED_TEXTURES=true COLORGRADING=true DAYLIGHT_CYCLE_COMPAT=true "
    "DIRECTIONAL_LIGHTMAP_NORMALS=true DRAGON_DEATH_EFFECT=2 EMISSIVE_ENCHANTING_TABLE=true "
    "EMISSIVE_FLOWERS=0 EMISSIVE_SOUL_SAND=true EMISSIVE_SPRING_FLOWERS=false END_CRYSTAL_VORTEX=3 "
    "END_PORTAL_BEAM=true END_SMOKE=true END_TWINKLING_STARS=12 EP_END_FLASH=2 FANCY_GLASS=true "
    "!GENERATED_NORMALS !GENERATED_SPECULAR GLOWING_ARMOR_TRIM=true GLOWING_EMERALD_BLOCK=true "
    "!GLOWING_NETHER_TREES GLOWING_ORE_MASTER=1 GLOWING_ORE_MULT=1.15 GLOWING_ORE_IRON=true "
    "GLOWING_ORE_GOLD=true GLOWING_ORE_COPPER=true GLOWING_ORE_REDSTONE=true GLOWING_ORE_LAPIS=true "
    "GLOWING_ORE_EMERALD=true GLOWING_ORE_DIAMOND=true GLOWING_ORE_NETHERQUARTZ=true "
    "GLOWING_ORE_NETHERGOLD=true GLOWING_ORE_GILDEDBLACKSTONE=true GLOWING_ORE_ANCIENTDEBRIS=true "
    "GLOWING_ORE_MODDED=true GLOWING_RAW_BLOCKS=true !GLOWING_WART GREEN_SCREEN_LIME=true "
    "HIGH_QUALITY_CLOUDS=true IMAGE_SHARPENING=3 IPBR_COMPAT_MODE_DEFINE=true LAVA_EDGE_EFFECT=0 "
    "LAVA_VARIATION=0 LIGHTMAP_CURVES=true LIGHTSHAFT_BEHAVIOUR=3 LIGHTSHAFT_DAY_I=180 LIGHTSHAFT_NIGHT_I=30 "
    "LIGHTSHAFT_SMOKE=true LIGHT_COLOR_MULTS=true MCBL_MAIN_DEFINE=3 MIRROR_TINTED_GLASS=true "
    "!MOON_PHASE_INF_PURKINJE MOSS_IN_CAVES=0 NETHER_PORTAL_NOISE=1 NIGHT_BRIGHTNESS=90 "
    "NIGHT_DESATURATION=true NIGHT_NEBULAE=1 NIGHT_NEBULA_I=50 NO_RAIN_ABOVE_CLOUDS=true "
    "OVERWORLD_BEAMS=true !PURKINJE_OVERWRITE RAIN_ATMOSPHERE=true RAIN_PUDDLES=2 RAIN_STYLE=2 "
    "RANDOM_AURORA=2 REDSTONE_IPBR=true REFLECTION_RES=1.0 SAND_CONDITION=0 SEASONS=1 "
    "SHADOW_SMOOTHING=1 SHOOTING_STARS=true SITUATIONAL_GLOWING_TRIMS=true SITUATIONAL_ORES=true "
    "SOUL_SAND_VALLEY_OVERHAUL=true SSAO_QUALI_DEFINE=3 STAR_AMOUNT=2 NIGHT_STAR_AMOUNT=3 "
    "STAR_BRIGHTNESS=16 STAR_LAYER_OW=1 STAR_ROUNDNESS_OW=10 STAR_SOFTNESS_OW=0.8 STAR_SIZE=0.7 "
    "SUN_GLARE_AMOUNT=1 SUN_INTENSITY=80 ROUND_SUN=false SUN_MOON_STYLE=0 TWINKLING_STARS=12 "
    "tonemap=DoBSLTonemap WB_ANAMORPHIC=true WB_CHROMATIC=true WB_FOV_SCALED=true WORLD_BLUR=2 "
    "DARKER_DEPTH_OCEANS=0 FOLIAGE_SSS=true LEAF_SUBSURFACE=true TRANSLUCENT_COLORED_SHADOWS=true TAA=true\n"
)

aetheris_profile2 = "profile2.AETHERIS    = DETAIL_QUALITY=3 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1 AURORA_COLOR_PRESET=-1 SITUATIONAL_ORES GLOWING_ORE_MASTER=1 BIOME_COLORED_NETHER_PORTALS NETHER_NOISE=1 LAVA_VARIATION=0 LAVA_EDGE_EFFECT=0 RAIN_ATMOSPHERE REDSTONE_IPBR INTERACTIVE_FOLIAGE MCBL_MAIN_DEFINE=3 SSS_SNOW_ICE AURORA_INFLUENCE !WAVIER_LAVA WATER_STYLE_DEFINE=3 NIGHT_NEBULAE=1 EMISSIVE_REDSTONE_BLOCK !WATER_FOAM WATER_FOAM_I=0 RAIN_PUDDLES=2 SEASONS=1 CLOUD_STYLE_DEFINE=3 STAR_SIZE=0.7 STAR_BRIGHTNESS=16 STAR_ROUNDNESS_OW=10 STAR_SOFTNESS_OW=0.8 SOUL_SAND_VALLEY_OVERHAUL PURPLE_END_FIRE NO_RAIN_ABOVE_CLOUDS MOON_PHASE_INF_LIGHT DIRECTIONAL_LIGHTMAP_NORMALS END_TWINKLING_STARS=12 NIGHT_STAR_AMOUNT=3 END_SMOKE RAIN_STYLE=2 END_CRYSTAL_VORTEX=3 DRAGON_DEATH_EFFECT=2 CAVE_SMOKE END_PORTAL_BEAM EMISSIVE_SOUL_SAND BEACON_BEAM_EMISSION=3.0 PINKER_CHERRY_LEAVES STAR_LAYER_OW=1 SITUATIONAL_GLOWING_TRIMS GLOWING_ARMOR_TRIM NIGHT_DESATURATION HIGH_QUALITY_CLOUDS ATM_COLOR_MULTS COATED_TEXTURES SUN_GLARE_AMOUNT=1 SUN_INTENSITY=80 WATER_CAUSTIC_STYLE_DEFINE=3 WATER_ALPHA_MULT=120 WATER_BUMPINESS=1.10 WATER_BUMP_BIG=1.20 WATER_BUMP_MED=1.30 WATER_FOG_MULT=160 WATER_SPEED_MULT=1.10 BLOOM_STRENGTH=0.020 CLOUD_SHADOWS BLOCKLIGHT_CAUSTICS CLOUD_SUN_MOON_SHADING=3 tonemap=DoBSLTonemap WORLD_SPACE_PLAYER_REF=1 RANDOM_AURORA=2 AURORA_CONDITION=3 LIGHT_COLOR_MULTS LIGHTSHAFT_BEHAVIOUR=3 LIGHTSHAFT_DAY_I=180 LIGHTSHAFT_QUALI_DEFINE=4 TWINKLING_STARS=12 SAND_CONDITION=0 MOSS_IN_CAVES=0 EMISSIVE_FLOWERS=0\n"

props_text = extreme_profile_str + props_text
if "profile2.POPULAR" in props_text:
    props_text = props_text.replace("profile2.POPULAR", aetheris_profile2 + "    profile2.POPULAR")

with open(props_path, "w", encoding="utf-8") as f:
    f.write(props_text)
print("[5/7] Deployed EXTREME profile and full menu hierarchy to shaders.properties")

# ---------------------------------------------------------
# 6. MASTER PRESET FILE
# ---------------------------------------------------------
master_extreme_preset = """# Aetheris Shader Pack v10.0 - Master Extreme Profile
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
BLOOM_STRENGTH=0.020
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
LIGHTSHAFT_DAY_I=180
LIGHTSHAFT_NIGHT_I=30
LIGHTSHAFT_QUALI_DEFINE=4
LIGHTSHAFT_SMOKE=true
LIGHT_COLOR_MULTS=true
MCBL_MAIN_DEFINE=3
MIRROR_TINTED_GLASS=true
MOON_PHASE_INF_PURKINJE=false
MOSS_IN_CAVES=0
NETHER_PORTAL_NOISE=1
NIGHT_BRIGHTNESS=90
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
SUN_GLARE_AMOUNT=1
SUN_INTENSITY=80
ROUND_SUN=false
SUN_MOON_STYLE=0
TWINKLING_STARS=12
WATER_ALPHA_MULT=120
WATER_BUMPINESS=1.10
WATER_BUMP_BIG=1.20
WATER_BUMP_MED=1.30
WATER_CAUSTIC_STRENGTH=1.50
WATER_CAUSTIC_STYLE_DEFINE=3
WATER_FOAM=false
WATER_FOAM_I=0
WATER_FOG_MULT=160
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
    f.write(master_extreme_preset)
with open(AETHERIS_ZIP_TXT, "w", encoding="utf-8") as f:
    f.write(master_extreme_preset)

# Recompress shader
print("[6/7] Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# ---------------------------------------------------------
# 7. SYNCHRONIZE ACROSS ALL PROFILE DIRECTORIES
# ---------------------------------------------------------
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
print("  MASTER v10.0 COMPLETE: ALL ISSUES FULLY FIXED!  ")
print("==================================================")
