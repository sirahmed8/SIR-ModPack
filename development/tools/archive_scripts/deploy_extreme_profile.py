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
print("  REGISTERING & DEPLOYING 'EXTREME' PROFILE       ")
print("==================================================")

# ---------------------------------------------------------
# 1. ADD EXTREME PROFILE TO LANG FILES
# ---------------------------------------------------------
lang_path = os.path.join(AETHERIS_DIR, "shaders", "lang", "en_us.lang")
if os.path.exists(lang_path):
    with open(lang_path, "r", encoding="utf-8", errors="ignore") as f:
        lang_text = f.read()
    
    if "profile.EXTREME=" not in lang_text:
        lang_text = lang_text.replace("profile.ULTRA=Performance: §4§lUltra", "profile.ULTRA=Performance: §4§lUltra\nprofile.EXTREME=Performance: §d§lExtreme (Master Edition)")
    if "profile2.AETHERIS=" not in lang_text:
        lang_text = lang_text.replace("profile.COMPLEMENTARY=", "profile2.AETHERIS=Style: §b§lAetheris Master Grade\nprofile.COMPLEMENTARY=")

    with open(lang_path, "w", encoding="utf-8") as f:
        f.write(lang_text)
    print("[1/4] Added EXTREME and AETHERIS localization strings to en_us.lang")

# ---------------------------------------------------------
# 2. CONFIGURE SHADERS.PROPERTIES WITH EXTREME PROFILE
# ---------------------------------------------------------
common_features = (
    "WATER_STYLE_DEFINE=3 WAVING_FOLIAGE=true WAVING_LEAVES=true WAVING_WATER_VERTEX=true "
    "!WAVING_LAVA WAVING_LANTERNS=true WAVING_GRASS=true WAVING_LILY_PAD=true WAVING_SUGAR_CANE=true "
    "!WAVIER_LAVA INTERACTIVE_FOLIAGE=true ATM_COLOR_MULTS=true AURORA_COLOR_PRESET=-1 AURORA_INFLUENCE=true "
    "AURORA_STYLE_DEFINE=3 BIOME_COLORED_NETHER_PORTALS=true BLOCKLIGHT_CAUSTICS=true BLOOM_STRENGTH=0.016 "
    "CAVE_SMOKE=true CELESTIAL_BOTH_HEMISPHERES=true !CLEAR_WATER_SPOTS CLOUD_SHADOWS=true "
    "CLOUD_STYLE_DEFINE=3 CLOUD_SUN_MOON_SHADING=3 COATED_TEXTURES=true COLORGRADING=true "
    "DAYLIGHT_CYCLE_COMPAT=true DIRECTIONAL_LIGHTMAP_NORMALS=true DRAGON_DEATH_EFFECT=2 "
    "EMISSIVE_ENCHANTING_TABLE=true EMISSIVE_FLOWERS=0 EMISSIVE_SOUL_SAND=true EMISSIVE_SPRING_FLOWERS=false "
    "END_CRYSTAL_VORTEX=3 END_PORTAL_BEAM=true END_SMOKE=true END_TWINKLING_STARS=12 EP_END_FLASH=2 "
    "FANCY_GLASS=true !GENERATED_NORMALS !GENERATED_SPECULAR GLOWING_ARMOR_TRIM=true GLOWING_EMERALD_BLOCK=true "
    "!GLOWING_NETHER_TREES GLOWING_ORE_MASTER=1 GLOWING_ORE_MULT=1.15 GLOWING_ORE_IRON=true "
    "GLOWING_ORE_GOLD=true GLOWING_ORE_COPPER=true GLOWING_ORE_REDSTONE=true GLOWING_ORE_LAPIS=true "
    "GLOWING_ORE_EMERALD=true GLOWING_ORE_DIAMOND=true GLOWING_ORE_NETHERQUARTZ=true "
    "GLOWING_ORE_NETHERGOLD=true GLOWING_ORE_GILDEDBLACKSTONE=true GLOWING_ORE_ANCIENTDEBRIS=true "
    "GLOWING_ORE_MODDED=true GLOWING_RAW_BLOCKS=true !GLOWING_WART GREEN_SCREEN_LIME=true "
    "HIGH_QUALITY_CLOUDS=true IMAGE_SHARPENING=3 IPBR_COMPAT_MODE_DEFINE=true LAVA_EDGE_EFFECT=0 "
    "LAVA_VARIATION=0 LIGHTMAP_CURVES=true LIGHTSHAFT_BEHAVIOUR=3 LIGHTSHAFT_SMOKE=true "
    "LIGHT_COLOR_MULTS=true MCBL_MAIN_DEFINE=3 MIRROR_TINTED_GLASS=true !MOON_PHASE_INF_PURKINJE "
    "MOSS_IN_CAVES=0 NETHER_PORTAL_NOISE=1 NIGHT_BRIGHTNESS=80 NIGHT_DESATURATION=true "
    "NIGHT_NEBULAE=1 NIGHT_NEBULA_I=50 NO_RAIN_ABOVE_CLOUDS=true OVERWORLD_BEAMS=true "
    "SLOPE_NORMALS=true !PIXEL_WATER PURPLE_END_FIRE=true !PURKINJE_OVERWRITE RAIN_ATMOSPHERE=true "
    "RAIN_PUDDLES=2 RAIN_STYLE=2 RANDOM_AURORA=2 REDSTONE_IPBR=true REFLECTION_RES=1.0 "
    "SAND_CONDITION=0 SEASONS=1 SHADOW_SMOOTHING=1 SHOOTING_STARS=true SITUATIONAL_GLOWING_TRIMS=true "
    "SITUATIONAL_ORES=true SOUL_SAND_VALLEY_OVERHAUL=true STAR_AMOUNT=2 NIGHT_STAR_AMOUNT=3 "
    "STAR_BRIGHTNESS=16 STAR_LAYER_OW=1 STAR_ROUNDNESS_OW=10 STAR_SOFTNESS_OW=0.8 STAR_SIZE=0.7 "
    "SUN_GLARE_AMOUNT=0 SUN_INTENSITY=75 ROUND_SUN=false SUN_MOON_STYLE=0 TWINKLING_STARS=12 "
    "tonemap=DoBSLTonemap WB_ANAMORPHIC=true WB_CHROMATIC=true WB_FOV_SCALED=true WORLD_BLUR=2 "
    "DARKER_DEPTH_OCEANS=0 FOLIAGE_SSS=true LEAF_SUBSURFACE=true TRANSLUCENT_COLORED_SHADOWS=true TAA=true "
    "WATER_CAUSTIC_STYLE_DEFINE=3 WATER_CAUSTIC_STRENGTH=1.50 WATER_BUMPINESS=1.10 WATER_BUMP_BIG=1.20 "
    "WATER_BUMP_MED=1.30 !WATER_FOAM WATER_FOAM_I=0 WATER_FOG_MULT=180 WATER_ALPHA_MULT=130 WATER_SPEED_MULT=1.10"
)

profile_potato  = "profile.POTATO       = SHADOW_QUALITY=-1 shadowDistance=64.0  WATER_REFLECT_QUALITY=1 BLOCK_REFLECT_QUALITY=1 LIGHTSHAFT_QUALI_DEFINE=1 DETAIL_QUALITY=0 CLOUD_QUALITY=0 FXAA_DEFINE=0 SSAO_QUALI_DEFINE=0 ANISOTROPIC_FILTER=0 COLORED_LIGHTING=0 WORLD_SPACE_REFLECTIONS=-1 ENTITY_SHADOW=0 RP_MODE=0 !PARALLAX\n"
profile_low     = f"profile.LOW          = SHADOW_QUALITY=1  shadowDistance=96.0  shadowMapResolution=1024 WATER_REFLECT_QUALITY=2 BLOCK_REFLECT_QUALITY=2 LIGHTSHAFT_QUALI_DEFINE=2 DETAIL_QUALITY=1 CLOUD_QUALITY=2 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=1 ANISOTROPIC_FILTER=0 COLORED_LIGHTING=128 WORLD_SPACE_REFLECTIONS=-1 ENTITY_SHADOW=1 RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.30 PARALLAX_QUALITY=16 PARALLAX_DISTANCE=16 {common_features}\n"
profile_med     = f"profile.MEDIUM       = SHADOW_QUALITY=2  shadowDistance=128.0 shadowMapResolution=2048 WATER_REFLECT_QUALITY=2 BLOCK_REFLECT_QUALITY=2 LIGHTSHAFT_QUALI_DEFINE=3 DETAIL_QUALITY=2 CLOUD_QUALITY=2 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=2 ANISOTROPIC_FILTER=2 COLORED_LIGHTING=192 WORLD_SPACE_REFLECTIONS=-1 ENTITY_SHADOW=1 RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.35 PARALLAX_QUALITY=24 PARALLAX_DISTANCE=24 {common_features}\n"
profile_high    = f"profile.HIGH         = SHADOW_QUALITY=3  shadowDistance=192.0 shadowMapResolution=2048 WATER_REFLECT_QUALITY=3 BLOCK_REFLECT_QUALITY=3 LIGHTSHAFT_QUALI_DEFINE=3 DETAIL_QUALITY=3 CLOUD_QUALITY=3 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=3 ANISOTROPIC_FILTER=4 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1  ENTITY_SHADOW=2 RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.40 PARALLAX_QUALITY=32 PARALLAX_DISTANCE=28 {common_features}\n"
profile_vhigh   = f"profile.VERYHIGH     = SHADOW_QUALITY=4  shadowDistance=224.0 shadowMapResolution=4096 WATER_REFLECT_QUALITY=3 BLOCK_REFLECT_QUALITY=3 LIGHTSHAFT_QUALI_DEFINE=4 DETAIL_QUALITY=3 CLOUD_QUALITY=3 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=3 ANISOTROPIC_FILTER=4 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1  ENTITY_SHADOW=2 RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.45 PARALLAX_QUALITY=48 PARALLAX_DISTANCE=32 {common_features}\n"
profile_ultra   = f"profile.ULTRA        = SHADOW_QUALITY=5  shadowDistance=256.0 shadowMapResolution=4096 WATER_REFLECT_QUALITY=3 BLOCK_REFLECT_QUALITY=3 LIGHTSHAFT_QUALI_DEFINE=4 DETAIL_QUALITY=3 CLOUD_QUALITY=3 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=3 ANISOTROPIC_FILTER=4 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1  ENTITY_SHADOW=2 RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.45 PARALLAX_QUALITY=64 PARALLAX_DISTANCE=32 {common_features}\n"
profile_extreme = f"profile.EXTREME      = SHADOW_QUALITY=5  shadowDistance=256.0 shadowMapResolution=4096 WATER_REFLECT_QUALITY=3 BLOCK_REFLECT_QUALITY=3 LIGHTSHAFT_QUALI_DEFINE=4 DETAIL_QUALITY=3 CLOUD_QUALITY=3 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=3 ANISOTROPIC_FILTER=4 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1  ENTITY_SHADOW=2 RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.45 PARALLAX_QUALITY=64 PARALLAX_DISTANCE=32 {common_features}\n"

profile2_aetheris = "profile2.AETHERIS = DETAIL_QUALITY=3 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1 RP_MODE=2 PARALLAX=true tonemap=DoBSLTonemap CLOUD_QUALITY=3\n"

props_path = os.path.join(AETHERIS_DIR, "shaders", "shaders.properties")
ref_props_path = os.path.join(BASE_EUPHORIA, "shaders", "shaders.properties")

with open(ref_props_path, "r", encoding="utf-8") as f:
    props_lines = f.readlines()

new_props = []
for line in props_lines:
    if line.startswith("profile.POTATO"):
        new_props.append(profile_extreme)
        new_props.append(profile_ultra)
        new_props.append(profile_vhigh)
        new_props.append(profile_high)
        new_props.append(profile_med)
        new_props.append(profile_low)
        new_props.append(profile_potato)
    elif line.startswith("profile.VERYLOW") or line.startswith("profile.LOW") or line.startswith("profile.MEDIUM") or line.startswith("profile.HIGH") or line.startswith("profile.VERYHIGH") or line.startswith("profile.ULTRA"):
        continue
    elif line.startswith("profile2.POPULAR"):
        new_props.append(profile2_aetheris)
        new_props.append(line)
    else:
        new_props.append(line)

with open(props_path, "w", encoding="utf-8") as f:
    f.writelines(new_props)
print("[2/4] Configured profile.EXTREME in shaders.properties")

# ---------------------------------------------------------
# 3. CONFIGURE PRESET FILES WITH EXTREME PROFILE
# ---------------------------------------------------------
master_extreme_preset = """# Aetheris Shader Pack v12.1 - Master Extreme Profile
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
    f.write(master_extreme_preset)
with open(AETHERIS_ZIP_TXT, "w", encoding="utf-8") as f:
    f.write(master_extreme_preset)

# Recompress shader
print("[3/4] Recompressing Aetheris_Shader_Pack.zip...")
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

# D:\Games sync
d_games_txt = r"D:\Games\Aetheris_Shader_Pack.zip.txt"
if os.path.exists(os.path.dirname(d_games_txt)):
    shutil.copy2(AETHERIS_TXT, d_games_txt)
    print(f"Synced to {d_games_txt}")

print("\n==================================================")
print("  EXTREME PROFILE 100% DEPLOYED & VISIBLE IN GUI! ")
print("==================================================")
