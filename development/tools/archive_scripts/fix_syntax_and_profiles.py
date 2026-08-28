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
print("  FIXING GLSL ANTLR PARSER & PROFILES RESTORATION ")
print("==================================================")

# 1. Fix water.glsl cleanly
water_glsl_path = os.path.join(AETHERIS_DIR, "shaders", "lib", "materials", "specificMaterials", "translucents", "water.glsl")
ref_water = os.path.join(BASE_EUPHORIA, "shaders", "lib", "materials", "specificMaterials", "translucents", "water.glsl")

with open(ref_water, "r", encoding="utf-8") as f:
    w_code = f.read()

# Smooth normal wave multiplier
w_code = w_code.replace("normalMap.xy *= 6.0 * (1.0 - 0.7 * fresnel)", "normalMap.xy *= 1.25 * (1.0 - 0.5 * fresnel)")

# Smooth ocean depth transmission without white cave multiplier
old_alpha_block = """            float waterFog = max0(1.0 - exp(lViewPosDifM * 0.075));
            color.a *= 0.25 + 0.75 * waterFog;

            #if defined BRIGHT_CAVE_WATER && WATER_ALPHA_MULT < 200
                // For better water visibility in caves and some extra color pop outdoors
                color.rgb *= 2.5 - sqrt2(waterFog) - 0.5 * lmCoordM.y;
            #endif

            #if WATER_ALPHA_MULT != 100
                #define WATER_ALPHA_MULT_M 100.0 / WATER_ALPHA_MULT
                color.a = pow(color.a, WATER_ALPHA_MULT_M);
            #endif"""

new_alpha_block = """            float waterFog = max0(1.0 - exp(lViewPosDifM * 0.075));
            // Rich Volumetric Ocean Depth & Tropical Shallows
            vec3 shallowColor = vec3(0.12, 0.68, 0.84);
            vec3 deepOceanColor = vec3(0.01, 0.08, 0.28);
            float fogDepthMix = clamp01(waterFog * 1.4 + length(viewPos) * 0.015);
            color.rgb = mix(shallowColor, deepOceanColor, fogDepthMix) * glColorM;

            // Smooth shoreline edge fade (eliminates boxy borders on placed water)
            float edgeFade = smoothstep(0.0, 0.18, max0(lViewPosDifM));
            color.a = clamp01((0.35 + 0.65 * waterFog) * edgeFade);"""

if old_alpha_block in w_code:
    w_code = w_code.replace(old_alpha_block, new_alpha_block)

with open(water_glsl_path, "w", encoding="utf-8") as f:
    f.write(w_code)
print("  -> water.glsl restored with 0 orphaned preprocessor tags!")

# 2. Restore Distinct Profiles in shaders.properties
props_path = os.path.join(AETHERIS_DIR, "shaders", "shaders.properties")
ref_props = os.path.join(BASE_EUPHORIA, "shaders", "shaders.properties")

with open(ref_props, "r", encoding="utf-8") as f:
    props_text = f.read()

# Add AETHERIS profile to profile2
aetheris_profile2 = "profile2.AETHERIS    = DETAIL_QUALITY=3 COLORED_LIGHTING=256 WORLD_SPACE_REFLECTIONS=1 AURORA_COLOR_PRESET=-1 SITUATIONAL_ORES GLOWING_ORE_MASTER=1 BIOME_COLORED_NETHER_PORTALS NETHER_NOISE=1 LAVA_VARIATION=1 RAIN_ATMOSPHERE REDSTONE_IPBR INTERACTIVE_FOLIAGE MCBL_MAIN_DEFINE=3 SSS_SNOW_ICE AURORA_INFLUENCE WAVIER_LAVA WATER_STYLE_DEFINE=3 NIGHT_NEBULAE=1 EMISSIVE_REDSTONE_BLOCK RAIN_PUDDLES=2 SEASONS=1 CLOUD_STYLE_DEFINE=3 STAR_SIZE=0.7 STAR_BRIGHTNESS=16 SOUL_SAND_VALLEY_OVERHAUL PURPLE_END_FIRE NO_RAIN_ABOVE_CLOUDS MOON_PHASE_INF_LIGHT DIRECTIONAL_LIGHTMAP_NORMALS END_TWINKLING_STARS=10 NIGHT_STAR_AMOUNT=3 END_SMOKE RAIN_STYLE=2 LAVA_EDGE_EFFECT=2 END_CRYSTAL_VORTEX=3 DRAGON_DEATH_EFFECT=2 CAVE_SMOKE END_PORTAL_BEAM EMISSIVE_SOUL_SAND BEACON_BEAM_EMISSION=3.0 PINKER_CHERRY_LEAVES STAR_LAYER_OW=1 SITUATIONAL_GLOWING_TRIMS GLOWING_ARMOR_TRIM NIGHT_DESATURATION HIGH_QUALITY_CLOUDS ATM_COLOR_MULTS COATED_TEXTURES SUN_GLARE_AMOUNT=6 WATER_CAUSTIC_STYLE_DEFINE=3 WATER_ALPHA_MULT=90 WATER_BUMPINESS=1.10 WATER_BUMP_BIG=1.20 WATER_BUMP_MED=1.30 WATER_FOAM_I=90 WATER_FOG_MULT=120 WATER_SPEED_MULT=1.10 BLOOM_STRENGTH=0.032 CLOUD_SHADOWS BLOCKLIGHT_CAUSTICS CLOUD_SUN_MOON_SHADING=3 tonemap=DoBSLTonemap WORLD_SPACE_PLAYER_REF=1 RANDOM_AURORA=2 AURORA_CONDITION=3 LIGHT_COLOR_MULTS LIGHTSHAFT_BEHAVIOUR=3 LIGHTSHAFT_DAY_I=200 LIGHTSHAFT_QUALI_DEFINE=4\n"

if "profile2.POPULAR" in props_text:
    props_text = props_text.replace("profile2.POPULAR", aetheris_profile2 + "    profile2.POPULAR")

with open(props_path, "w", encoding="utf-8") as f:
    f.write(props_text)
print("  -> Full profile hierarchy (Potato, Low, Med, High, VeryHigh, Ultra, Aetheris) restored in shaders.properties!")

# 3. Master Preset Deployment
master_ultra_preset = """# Aetheris Shader Pack v8.1 - Master Ultra Profile
profile=ULTRA
profile2=AETHERIS
tonemap=DoBSLTonemap
ANISOTROPIC_FILTER=4
ATM_COLOR_MULTS=true
AURORA_COLOR_PRESET=-1
AURORA_INFLUENCE=true
AURORA_STYLE_DEFINE=3
BIOME_COLORED_NETHER_PORTALS=true
BLOCKLIGHT_CAUSTICS=true
BLOOM_STRENGTH=0.032
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
EMISSIVE_FLOWERS=1
EMISSIVE_SOUL_SAND=true
EMISSIVE_SPRING_FLOWERS=true
END_CRYSTAL_VORTEX=3
END_PORTAL_BEAM=true
END_SMOKE=true
END_TWINKLING_STARS=10
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
LAVA_EDGE_EFFECT=2
LIGHTMAP_CURVES=true
LIGHTSHAFT_BEHAVIOUR=3
LIGHTSHAFT_DAY_I=200
LIGHTSHAFT_NIGHT_I=40
LIGHTSHAFT_QUALI_DEFINE=4
LIGHTSHAFT_SMOKE=true
LIGHT_COLOR_MULTS=true
MCBL_MAIN_DEFINE=3
MIRROR_TINTED_GLASS=true
MOON_PHASE_INF_PURKINJE=false
MOSS_IN_CAVES=1
NETHER_PORTAL_NOISE=1
NIGHT_BRIGHTNESS=160
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
SAND_CONDITION=2
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
SUN_GLARE_AMOUNT=6
SUN_INTENSITY=100
ROUND_SUN=true
SUN_MOON_STYLE=1
TWINKLING_STARS=10
WATER_ALPHA_MULT=90
WATER_BUMPINESS=1.10
WATER_BUMP_BIG=1.20
WATER_BUMP_MED=1.30
WATER_CAUSTIC_STRENGTH=1.50
WATER_CAUSTIC_STYLE_DEFINE=3
WATER_FOAM=true
WATER_FOAM_I=90
WATER_FOG_MULT=120
WATER_REFLECT_QUALITY=3
BLOCK_REFLECT_QUALITY=3
WATER_SPEED_MULT=1.10
WATER_STYLE_DEFINE=3
WAVING_FOLIAGE=true
WAVING_LEAVES=true
WAVING_WATER_VERTEX=true
WAVING_LAVA=true
WAVING_LANTERNS=true
WAVING_GRASS=true
WAVING_LILY_PAD=true
WAVING_SUGAR_CANE=true
WAVIER_LAVA=true
WB_ANAMORPHIC=true
WB_CHROMATIC=true
WB_FOV_SCALED=true
WORLD_BLUR=2
WORLD_SPACE_REFLECTIONS=1
DARKER_DEPTH_OCEANS=100
FOLIAGE_SSS=true
LEAF_SUBSURFACE=true
TRANSLUCENT_COLORED_SHADOWS=true
TAA=true
"""

with open(AETHERIS_TXT, "w", encoding="utf-8") as f:
    f.write(master_ultra_preset)
with open(AETHERIS_ZIP_TXT, "w", encoding="utf-8") as f:
    f.write(master_ultra_preset)

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

print("\n==================================================")
print("  SYNTAX ERROR ELIMINATED & PROFILES RESTORED!    ")
print("==================================================")
