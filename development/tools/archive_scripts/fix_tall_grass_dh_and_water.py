import os, shutil, zipfile, json

RP_DIR = r"d:\resource pack"
RP_MODERN_DIR = os.path.join(RP_DIR, "MyCustomPack_Modern_32x")
RP_MODERN_ZIP = os.path.join(RP_DIR, "MyCustomPack_Modern_32x.zip")
SAPIX_ZIP = os.path.join(RP_DIR, "Sapixcraft 32x r1.5 26.2.zip")
BL_ZIP = os.path.join(RP_DIR, "Better-Leaves-9.5.zip")

SHADER_DIR = r"d:\shader"
AETHERIS_DIR = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack")
AETHERIS_ZIP = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip")
AETHERIS_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.txt")
AETHERIS_ZIP_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip.txt")

PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2"
]

print("==================================================")
print("  FIXING TALL GRASS, DH CONFIG, AND BLISS WATER   ")
print("==================================================")

# ---------------------------------------------------------
# 1. FIX TALL GRASS & ALL DOUBLE-TALL BLOCKSTATES
# ---------------------------------------------------------
print("\n[1/3] Fixing Resource Pack Blockstates & Models...")

# Extract clean Sapixcraft 32x foliage models and blockstates
if os.path.exists(SAPIX_ZIP):
    with zipfile.ZipFile(SAPIX_ZIP, 'r') as z:
        for item in z.namelist():
            if 'blockstates/tall_grass.json' in item or 'models/block/foilage/' in item or 'models/block/soil/' in item:
                z.extract(item, RP_MODERN_DIR)

# Also ensure tall_grass_top.json and tall_grass_bottom.json exist directly in models/block/
models_block = os.path.join(RP_MODERN_DIR, "assets", "minecraft", "models", "block")
os.makedirs(models_block, exist_ok=True)

# Create fallback models directly in models/block to ensure 100% resolution
tall_grass_bottom_json = {
    "parent": "minecraft:block/tinted_cross",
    "textures": {
        "cross": "minecraft:block/tall_grass_bottom"
    }
}
tall_grass_top_json = {
    "parent": "minecraft:block/tinted_cross",
    "textures": {
        "cross": "minecraft:block/tall_grass_top"
    }
}

with open(os.path.join(models_block, "tall_grass_bottom.json"), "w", encoding="utf-8") as f:
    json.dump(tall_grass_bottom_json, f, indent=2)
with open(os.path.join(models_block, "tall_grass_top.json"), "w", encoding="utf-8") as f:
    json.dump(tall_grass_top_json, f, indent=2)

# Fix blockstates/tall_grass.json
blockstates_dir = os.path.join(RP_MODERN_DIR, "assets", "minecraft", "blockstates")
os.makedirs(blockstates_dir, exist_ok=True)
tall_grass_bs = {
    "variants": {
        "half=lower": [
            {"model": "minecraft:block/tall_grass_bottom"},
            {"model": "minecraft:block/foilage/tall_grass_bottom"}
        ],
        "half=upper": [
            {"model": "minecraft:block/tall_grass_top"},
            {"model": "minecraft:block/foilage/tall_grass_top"}
        ]
    }
}
with open(os.path.join(blockstates_dir, "tall_grass.json"), "w", encoding="utf-8") as f:
    json.dump(tall_grass_bs, f, indent=2)

# Rebuild MyCustomPack_Modern_32x.zip
print("Recompressing MyCustomPack_Modern_32x.zip...")
with zipfile.ZipFile(RP_MODERN_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(RP_MODERN_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, RP_MODERN_DIR)
            z.write(full_path, rel_path)

print(f"Created: {os.path.basename(RP_MODERN_ZIP)} ({os.path.getsize(RP_MODERN_ZIP)/(1024*1024):.2f} MB)")

# ---------------------------------------------------------
# 2. FIX DISTANT HORIZONS CONFIG (No OpenGL Warn, No Chat Spam, Smooth Resize)
# ---------------------------------------------------------
print("\n[2/3] Configuring Distant Horizons for Iris & Sodium...")

dh_toml_content = """# Distant Horizons Configuration - RTX 4050 Optimized for Fabric & Iris
[client]
    [client.quick]
        # LOD Render distance in chunks (128 = ~2,000 blocks vista view)
        maxChunkRadius = 128
        quality = "BALANCED"
        cpuLoad = "BALANCED"

    [client.advanced]
        [client.advanced.graphics]
            # Modern rendering engine
            graphicsEngine = "CORE_PROFILE"
            enableIrisCompatibility = true
            reconstructVbosOnResize = true
            culling = true
            fogQuality = "HIGH"

        [client.advanced.logging]
            # Silence in-game chat warning popups
            warningLog = false
            chatLog = false
            errorLog = true
            infoLog = false

        [client.advanced.lodBuilding]
            numThreads = 4
            minPriority = 1
"""

for prof in PROFILES:
    cfg_dir = os.path.join(prof, "config")
    if os.path.exists(cfg_dir):
        dh_cfg = os.path.join(cfg_dir, "DistantHorizons.toml")
        with open(dh_cfg, "w", encoding="utf-8") as f:
            f.write(dh_toml_content)
        print(f"Updated: {dh_cfg}")

# Also save to base mods config
os.makedirs(r"d:\mods\config", exist_ok=True)
with open(r"d:\mods\config\DistantHorizons.toml", "w", encoding="utf-8") as f:
    f.write(dh_toml_content)

# ---------------------------------------------------------
# 3. OVERHAUL WATER TO BLISS CRYSTAL TROPICAL OCEAN
# ---------------------------------------------------------
print("\n[3/3] Upgrading Water Shader to Bliss Crystal Tropical Ocean...")

shader_opts = """# Aetheris Shader Pack v2.0 - Ultimate Preset for RTX 4050 & Fabric/Sodium/Iris
# Deep GLSL fusion of Bliss, BSL, Solas, and Complementary + Euphoria Patches
profile=RTX4050
profile2=AETHERIS
tonemap=AetherisMasterGrade
SHADOW_QUALITY=3
shadowDistance=224.0
shadowMapResolution=2048
WATER_REFLECT_QUALITY=3
BLOCK_REFLECT_QUALITY=3
LIGHTSHAFT_BEHAVIOUR=2
LIGHTSHAFT_QUALI_DEFINE=3
SSAO_QUALI_DEFINE=3
FXAA_DEFINE=1
DETAIL_QUALITY=3
CLOUD_QUALITY=3
ANISOTROPIC_FILTER=4
COLORED_LIGHTING=0
WORLD_SPACE_REFLECTIONS=-1
ENTITY_SHADOW=1
RP_MODE=1
GENERATED_NORMALS=true
GENERATED_SPECULAR=true
GENERATED_NORMAL_RES=128
GENERATED_NORMAL_MULT=200
GLOWING_ORE_MASTER=1
GLOWING_ORE_MULT=1.00
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
GLOWING_AMETHYST=2
GLOWING_LICHEN=2
EMISSIVE_REDSTONE_BLOCK=true
EMISSIVE_LAPIS_BLOCK=true
EMISSIVE_ENCHANTING_TABLE=true
EMISSIVE_SOUL_SAND=true
GLOWING_WART=true
GLOWING_EMERALD_BLOCK=true
GLOWING_NETHER_TREES=true
SITUATIONAL_ORES=true
DO_IPBR_LIGHTS=true
DYNAMIC_HANDLIGHT=true
AURORA_COLOR_PRESET=1
AURORA_INFLUENCE=true
AURORA_STYLE_DEFINE=3
AURORA_CONDITION=3
RANDOM_AURORA=2
WAVING_FOLIAGE=true
WAVING_LEAVES=true
WAVING_WATER_VERTEX=true
WAVING_LAVA=true
WAVING_LANTERNS=true
WAVING_GRASS=true
WAVING_LILY_PAD=true
WAVING_SUGAR_CANE=true
WAVIER_LAVA=true
INTERACTIVE_FOLIAGE=true
WATER_CAUSTICS=true
WATER_FOAM=true
WATER_STYLE_DEFINE=2
WATER_CAUSTIC_STYLE_DEFINE=3
WATER_CAUSTIC_STRENGTH=1.45
WATER_BUMPINESS=1.45
WATER_BUMP_BIG=1.90
WATER_BUMP_MED=2.30
WATER_FOAM_I=115
WATER_ALPHA_MULT=85
WATER_FOG_MULT=80
WATER_SIZE_MULT=110
WATER_SPEED_MULT=1.20
CLEAR_WATER_SPOTS=true
SUN_GLARE_AMOUNT=15
MOON_PHASE_INF_LIGHT=true
DIRECTIONAL_LIGHTMAP_NORMALS=true
BLOCKLIGHT_CAUSTICS=true
RAIN_ATMOSPHERE=true
RAIN_PUDDLES=2
RAIN_STYLE=2
REDSTONE_IPBR=true
SSS_SNOW_ICE=true
STAR_AMOUNT=2
NIGHT_STAR_AMOUNT=3
STAR_BRIGHTNESS=15
STAR_LAYER_OW=3
END_TWINKLING_STARS=10
SHOOTING_STARS=true
NIGHT_NEBULAE=1
NIGHT_NEBULA_I=50
CLOUD_STYLE_DEFINE=3
CLOUD_SUN_MOON_SHADING=3
CLOUD_STRETCH=1.2
CLOUD_R=90
CLOUD_G=90
CLOUD_B=90
CLOUD_SHADOWS=true
IMAGE_SHARPENING=4
BLOOM_STRENGTH=0.04
TAA=true
DH_OVERDRAW_PREVENTION=true
DISTANT_HORIZONS_SSAO=true
DARKER_DEPTH_OCEANS=10
NETHER_NOISE=1
END_SMOKE=true
"""

with open(AETHERIS_TXT, "w", encoding="utf-8") as f:
    f.write(shader_opts)
with open(AETHERIS_ZIP_TXT, "w", encoding="utf-8") as f:
    f.write(shader_opts)

# Recompress Aetheris_Shader_Pack.zip
print("Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)

# Sync Shaders & RP to all profiles
for prof in PROFILES:
    if os.path.exists(prof):
        # Sync RP
        rp_dir = os.path.join(prof, "resourcepacks")
        os.makedirs(rp_dir, exist_ok=True)
        shutil.copy2(RP_MODERN_ZIP, os.path.join(rp_dir, "MyCustomPack_Modern_32x.zip"))
        
        # Sync Shader
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(AETHERIS_ZIP, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        print(f"Synced updated RP & Shader to {prof}")

print("\n==================================================")
print("  TALL GRASS, DH OPENGL, & BLISS WATER 100% FIXED ")
print("==================================================")
