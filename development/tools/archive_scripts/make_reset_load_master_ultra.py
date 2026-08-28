import os, shutil, zipfile

SHADER_DIR = r"d:\shader"
AETHERIS_DIR = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack")
AETHERIS_ZIP = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip")
AETHERIS_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.txt")
AETHERIS_ZIP_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip.txt")
SHADERS_PROPS = os.path.join(AETHERIS_DIR, "shaders", "shaders.properties")

PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2",
    r"C:\Users\a7med\.lunarclient\profiles\1.8"
]

print("==================================================")
print("  CONFIGURING 'RESET' BUTTON TO LOAD MASTER ULTRA ")
print("==================================================")

# Single line condensed ultra options for shaders.properties profile definitions
ultra_line_opts = (
    "SHADOW_QUALITY=5 shadowDistance=256.0 WATER_REFLECT_QUALITY=3 BLOCK_REFLECT_QUALITY=3 "
    "LIGHTSHAFT_QUALI_DEFINE=4 DETAIL_QUALITY=3 CLOUD_QUALITY=3 FXAA_DEFINE=1 SSAO_QUALI_DEFINE=3 "
    "ANISOTROPIC_FILTER=4 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1 ENTITY_SHADOW=2 "
    "RP_MODE=2 PARALLAX=true PARALLAX_DEPTH=0.45 PARALLAX_QUALITY=64 PARALLAX_DISTANCE=32 "
    "SLOPE_NORMALS=true !PIXEL_WATER WATER_ALPHA_MULT=90 WATER_FOG_MULT=120 WATER_CAUSTIC_STYLE_DEFINE=3 "
    "WATER_CAUSTIC_STRENGTH=1.50 WATER_BUMPINESS=1.10 WATER_BUMP_BIG=1.20 WATER_BUMP_MED=1.30 "
    "WATER_FOAM=true WATER_FOAM_I=90 WATER_SPEED_MULT=1.10 WATER_STYLE_DEFINE=3 WAVING_FOLIAGE=true "
    "WAVING_LEAVES=true WAVING_WATER_VERTEX=true WAVING_LAVA=true WAVING_LANTERNS=true WAVING_GRASS=true "
    "WAVING_LILY_PAD=true WAVING_SUGAR_CANE=true WAVIER_LAVA=true INTERACTIVE_FOLIAGE=true "
    "ATM_COLOR_MULTS=true AURORA_COLOR_PRESET=-1 AURORA_INFLUENCE=true AURORA_STYLE_DEFINE=3 "
    "BIOME_COLORED_NETHER_PORTALS=true BLOCKLIGHT_CAUSTICS=true BLOOM_STRENGTH=0.032 CAVE_SMOKE=true "
    "CELESTIAL_BOTH_HEMISPHERES=true !CLEAR_WATER_SPOTS CLOUD_SHADOWS=true CLOUD_STYLE_DEFINE=3 "
    "CLOUD_SUN_MOON_SHADING=3 COATED_TEXTURES=true COLORGRADING=true DAYLIGHT_CYCLE_COMPAT=true "
    "DIRECTIONAL_LIGHTMAP_NORMALS=true DRAGON_DEATH_EFFECT=2 EMISSIVE_ENCHANTING_TABLE=true "
    "EMISSIVE_FLOWERS=1 EMISSIVE_SOUL_SAND=true EMISSIVE_SPRING_FLOWERS=true END_CRYSTAL_VORTEX=3 "
    "END_PORTAL_BEAM=true END_SMOKE=true END_TWINKLING_STARS=10 EP_END_FLASH=2 FANCY_GLASS=true "
    "!GENERATED_NORMALS !GENERATED_SPECULAR GLOWING_ARMOR_TRIM=true GLOWING_EMERALD_BLOCK=true "
    "!GLOWING_NETHER_TREES GLOWING_ORE_MASTER=1 GLOWING_ORE_MULT=1.15 GLOWING_ORE_IRON=true "
    "GLOWING_ORE_GOLD=true GLOWING_ORE_COPPER=true GLOWING_ORE_REDSTONE=true GLOWING_ORE_LAPIS=true "
    "GLOWING_ORE_EMERALD=true GLOWING_ORE_DIAMOND=true GLOWING_ORE_NETHERQUARTZ=true "
    "GLOWING_ORE_NETHERGOLD=true GLOWING_ORE_GILDEDBLACKSTONE=true GLOWING_ORE_ANCIENTDEBRIS=true "
    "GLOWING_ORE_MODDED=true GLOWING_RAW_BLOCKS=true !GLOWING_WART GREEN_SCREEN_LIME=true "
    "HIGH_QUALITY_CLOUDS=true IMAGE_SHARPENING=3 IPBR_COMPAT_MODE_DEFINE=true LAVA_EDGE_EFFECT=2 "
    "LIGHTMAP_CURVES=true LIGHTSHAFT_BEHAVIOUR=3 LIGHTSHAFT_DAY_I=200 LIGHTSHAFT_NIGHT_I=40 "
    "LIGHTSHAFT_SMOKE=true LIGHT_COLOR_MULTS=true MCBL_MAIN_DEFINE=3 MIRROR_TINTED_GLASS=true "
    "!MOON_PHASE_INF_PURKINJE MOSS_IN_CAVES=1 NETHER_PORTAL_NOISE=1 NIGHT_BRIGHTNESS=160 "
    "NIGHT_DESATURATION=true NIGHT_NEBULAE=1 NIGHT_NEBULA_I=50 NO_RAIN_ABOVE_CLOUDS=true "
    "OVERWORLD_BEAMS=true !PURKINJE_OVERWRITE RAIN_ATMOSPHERE=true RAIN_PUDDLES=2 RAIN_STYLE=2 "
    "RANDOM_AURORA=2 REDSTONE_IPBR=true REFLECTION_RES=1.0 SAND_CONDITION=2 SEASONS=1 "
    "SHADOW_SMOOTHING=1 SHOOTING_STARS=true SITUATIONAL_GLOWING_TRIMS=true SITUATIONAL_ORES=true "
    "SOUL_SAND_VALLEY_OVERHAUL=true SSAO_QUALI_DEFINE=3 STAR_AMOUNT=2 NIGHT_STAR_AMOUNT=3 "
    "STAR_BRIGHTNESS=16 STAR_LAYER_OW=1 SUN_GLARE_AMOUNT=6 SUN_INTENSITY=100 ROUND_SUN=true "
    "SUN_MOON_STYLE=1 TWINKLING_STARS=10 tonemap=DoBSLTonemap WB_ANAMORPHIC=true WB_CHROMATIC=true "
    "WB_FOV_SCALED=true WORLD_BLUR=2 DARKER_DEPTH_OCEANS=100 FOLIAGE_SSS=true LEAF_SUBSURFACE=true "
    "TRANSLUCENT_COLORED_SHADOWS=true TAA=true"
)

# Read shaders.properties
with open(SHADERS_PROPS, "r", encoding="utf-8", errors="ignore") as f:
    props_lines = f.readlines()

new_props_lines = []
for line in props_lines:
    if line.strip().startswith("profile.") or line.strip().startswith("profile2."):
        key = line.split("=")[0].strip()
        new_props_lines.append(f"{key} = {ultra_line_opts}\n")
    else:
        new_props_lines.append(line)

with open(SHADERS_PROPS, "w", encoding="utf-8") as f:
    f.writelines(new_props_lines)
print("  -> Updated all profile definitions in shaders.properties to Master Ultra!")

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
        print(f"Synced Master Ultra to {sp_dir}")

print("\n==================================================")
print("  RESET BUTTON NOW ALWAYS RESTORES MASTER ULTRA!  ")
print("==================================================")
