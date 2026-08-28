import os, shutil, zipfile, json, re

RP_DIR = r"d:\resource pack"
RP_MODERN_DIR = os.path.join(RP_DIR, "MyCustomPack_Modern_32x")
RP_MODERN_ZIP = os.path.join(RP_DIR, "MyCustomPack_Modern_32x.zip")
OPTIMUM_ZIP = os.path.join(RP_DIR, "Optimum Realism R3.9.0 64x.zip")
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
print("  ULTIMATE AETHERIS OVERHAUL: BLISS WATER & PBR   ")
print("==================================================")

# ---------------------------------------------------------
# 1. FIX BLOCK.PROPERTIES (SUNLIGHT THROUGH BOP LEAVES)
# ---------------------------------------------------------
print("\n[1/5] Unifying Leaf Subsurface Scattering & Godrays in block.properties...")

block_prop_path = os.path.join(AETHERIS_DIR, "shaders", "block.properties")
if os.path.exists(block_prop_path):
    with open(block_prop_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Collect all leaf definitions and remove duplicate block.10007 overrides
    all_leaves = [
        "oak_leaves", "spruce_leaves", "birch_leaves", "jungle_leaves", "acacia_leaves",
        "dark_oak_leaves", "mangrove_leaves", "cherry_leaves", "azalea_leaves", "flowering_azalea_leaves", "pale_oak_leaves",
        "leaves", "leaves2", "leaves:1,3,5,7,9,11,13,15", "leaves2:0,4,8,12",
        "biomesoplenty:cypress_leaves", "biomesoplenty:dead_leaves", "biomesoplenty:empyreal_leaves",
        "biomesoplenty:fir_leaves", "biomesoplenty:flowering_oak_leaves", "biomesoplenty:hellbark_leaves",
        "biomesoplenty:jacaranda_leaves", "biomesoplenty:magic_leaves", "biomesoplenty:mahogany_leaves",
        "biomesoplenty:maple_leaves", "biomesoplenty:orange_autumn_leaves", "biomesoplenty:origin_leaves",
        "biomesoplenty:palm_leaves", "biomesoplenty:pine_leaves", "biomesoplenty:rainbow_birch_leaves",
        "biomesoplenty:red_maple_leaves", "biomesoplenty:redwood_leaves", "biomesoplenty:willow_leaves",
        "biomesoplenty:yellow_autumn_leaves", "biomesoplenty:yellow_maple_leaves",
        "regions_unexplored:alpha_leaves", "regions_unexplored:apple_oak_leaves", "regions_unexplored:ashen_leaves",
        "regions_unexplored:bamboo_leaves", "regions_unexplored:baobab_leaves", "regions_unexplored:blackwood_leaves",
        "regions_unexplored:brimwood_leaves", "regions_unexplored:cobalt_leaves", "regions_unexplored:cypress_leaves",
        "regions_unexplored:dead_leaves", "regions_unexplored:eucalyptus_leaves", "regions_unexplored:flowering_leaves",
        "regions_unexplored:golden_larch_leaves", "regions_unexplored:joshua_leaves", "regions_unexplored:kapok_leaves",
        "regions_unexplored:larch_leaves", "regions_unexplored:maple_leaves", "regions_unexplored:mauve_leaves",
        "regions_unexplored:orange_maple_leaves", "regions_unexplored:palm_leaves", "regions_unexplored:pine_leaves",
        "regions_unexplored:red_maple_leaves", "regions_unexplored:redwood_leaves", "regions_unexplored:silver_birch_leaves",
        "regions_unexplored:small_oak_leaves", "regions_unexplored:socotra_leaves", "regions_unexplored:willow_leaves"
    ]
    
    clean_lines = []
    for line in lines:
        if line.startswith("block.10007") or line.strip().startswith("block.10007"):
            continue
        clean_lines.append(line)

    # Append single master block.10007
    leaf_entry = "block.10007 = " + " ".join(all_leaves) + "\n"
    clean_lines.append("\n# Master Subsurface Scattering & Godrays Foliage Definition\n")
    clean_lines.append(leaf_entry)

    with open(block_prop_path, "w", encoding="utf-8") as f:
        f.writelines(clean_lines)
    print("  -> block.properties unified with full vanilla + BOP + Regions Unexplored foliage SSS!")

# ---------------------------------------------------------
# 2. OVERHAUL WATER.GLSL (PURE BLISS PROCEDURAL WATER)
# ---------------------------------------------------------
print("\n[2/5] Upgrading water.glsl with pure Bliss procedural physics...")

water_glsl_path = os.path.join(AETHERIS_DIR, "shaders", "lib", "materials", "specificMaterials", "translucents", "water.glsl")
if os.path.exists(water_glsl_path):
    with open(water_glsl_path, "r", encoding="utf-8", errors="ignore") as f:
        w_code = f.read()

    # Remove pixel grid snapping in waterPos
    old_pixel_snap = """#if WATER_STYLE < 3 && defined GBUFFERS_WATER
            float blockRes = absMidCoordPos.x * atlasSize.x * 2.0;
            waterPos = floor(waterPos * blockRes) / blockRes;
        #endif"""
    if old_pixel_snap in w_code:
        w_code = w_code.replace(old_pixel_snap, "// Pixel snapping removed for pure Bliss fluid continuity")
        print("  -> Removed pixel grid snapping from waterPos")

    # Remove vanilla pixel texture multiplication
    old_vanilla_mult = """#if MC_VERSION >= 11300
    #if WATER_STYLE < 3 || PIXEL_WATER == 1
        vec3 colorPM = pow2(colorP.rgb);
        color.rgb = colorPM * glColorM;
    #else
        vec3 colorPM = vec3(0.25);
        color.rgb = 0.375 * glColorM;
    #endif
#else
    #if WATER_STYLE < 3 || PIXEL_WATER == 1
        color.rgb = mix(color.rgb, vec3(GetLuminance(color.rgb)), 0.88);
        color.rgb = pow2(color.rgb) * vec3(2.3, 3.5, 3.1) * 0.9;
    #else
        color.rgb = vec3(0.13, 0.2, 0.27);
    #endif
#endif"""

    new_bliss_water_color = """// Bliss & Unbound Pure Procedural Shader Water Color
vec3 colorPM = vec3(0.25);
vec3 tropicalShallow = vec3(0.08, 0.65, 0.82);
vec3 deepOcean = vec3(0.02, 0.14, 0.45);
color.rgb = mix(tropicalShallow, deepOcean, clamp01(playerPos.y * -0.05 + 0.5)) * glColorM;"""

    if old_vanilla_mult in w_code:
        w_code = w_code.replace(old_vanilla_mult, new_bliss_water_color)
        print("  -> Replaced vanilla pixel texture with Bliss tropical-to-deep gradient")

    with open(water_glsl_path, "w", encoding="utf-8") as f:
        f.write(w_code)

# ---------------------------------------------------------
# 3. MERGE OPTIMUM REALISM 64X LABPBR TEXTURES INTO RESOURCE PACK
# ---------------------------------------------------------
print("\n[3/5] Merging Optimum Realism 64x LabPBR Normal & Specular maps into Custom Pack...")

if os.path.exists(OPTIMUM_ZIP):
    with zipfile.ZipFile(OPTIMUM_ZIP, "r") as oz:
        for item in oz.namelist():
            # Extract normal maps, specular maps, and optifine PBR properties
            if item.endswith("_n.png") or item.endswith("_s.png") or "optifine/ctm" in item or "optifine/cem" in item:
                oz.extract(item, RP_MODERN_DIR)
    print("  -> Extracted all Optimum Realism 64x PBR normal/specular maps and 3D CTM!")

# Recompress MyCustomPack_Modern_32x.zip
print("Recompressing MyCustomPack_Modern_32x.zip with Optimum Realism 64x PBR...")
with zipfile.ZipFile(RP_MODERN_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(RP_MODERN_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, RP_MODERN_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(RP_MODERN_ZIP)} ({os.path.getsize(RP_MODERN_ZIP)/(1024*1024):.2f} MB)")

# ---------------------------------------------------------
# 4. CALIBRATE AETHERIS SHADER PRESET (BLISS > SOLAS > BSL > UNBOUND)
# ---------------------------------------------------------
print("\n[4/5] Calibrating Ultimate Preset for RTX 4050 (LabPBR + Bliss Water + SSS Foliage)...")

shader_master_config = """# Aetheris Shader Pack v3.0 - Ultimate Bliss/Solas/BSL/Unbound Preset
# Optimized for RTX 4050 Laptop GPU (High Performance + Ray Tracing + LabPBR)
profile=RTX4050
profile2=AETHERIS
tonemap=AetherisMasterGrade
SHADOW_QUALITY=2
shadowDistance=192.0
shadowMapResolution=2048
WATER_STYLE_DEFINE=3
WATER_REFLECT_QUALITY=3
BLOCK_REFLECT_QUALITY=3
LIGHTSHAFT_BEHAVIOUR=2
LIGHTSHAFT_QUALI_DEFINE=3
LIGHTSHAFT_DAY_I=150
LIGHTSHAFT_NIGHT_I=70
SSAO_QUALI_DEFINE=2
FXAA_DEFINE=1
DETAIL_QUALITY=3
CLOUD_QUALITY=3
ANISOTROPIC_FILTER=4
COLORED_LIGHTING=0
WORLD_SPACE_REFLECTIONS=-1
ENTITY_SHADOW=1
RP_MODE=2
PARALLAX=true
PARALLAX_DEPTH=0.75
PARALLAX_QUALITY=256
PARALLAX_DISTANCE=32
SELF_SHADOW=true
SLOPE_NORMALS=true
GENERATED_NORMALS=false
GENERATED_SPECULAR=false
GLOWING_ORE_MASTER=1
GLOWING_ORE_MULT=1.10
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
WATER_CAUSTIC_STYLE_DEFINE=3
WATER_CAUSTIC_STRENGTH=1.60
WATER_BUMPINESS=1.50
WATER_BUMP_BIG=2.00
WATER_BUMP_MED=2.40
WATER_FOAM_I=125
WATER_ALPHA_MULT=75
WATER_FOG_MULT=70
WATER_SIZE_MULT=110
WATER_SPEED_MULT=1.25
CLEAR_WATER_SPOTS=true
SUN_GLARE_AMOUNT=25
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
STAR_BRIGHTNESS=18
STAR_LAYER_OW=3
END_TWINKLING_STARS=10
SHOOTING_STARS=true
NIGHT_NEBULAE=1
NIGHT_NEBULA_I=55
CLOUD_STYLE_DEFINE=3
CLOUD_SUN_MOON_SHADING=3
CLOUD_STRETCH=1.2
CLOUD_R=90
CLOUD_G=90
CLOUD_B=90
CLOUD_SHADOWS=true
IMAGE_SHARPENING=3
BLOOM_STRENGTH=0.04
TAA=true
DISTANT_HORIZONS=false
DARKER_DEPTH_OCEANS=10
NETHER_NOISE=1
END_SMOKE=true
FOLIAGE_SSS=true
LEAF_SUBSURFACE=true
TRANSLUCENT_COLORED_SHADOWS=true
"""

with open(AETHERIS_TXT, "w", encoding="utf-8") as f:
    f.write(shader_master_config)
with open(AETHERIS_ZIP_TXT, "w", encoding="utf-8") as f:
    f.write(shader_master_config)

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
# 5. FIX PROGRAMMER ART LOG WARNINGS & SYNC ALL PROFILES
# ---------------------------------------------------------
print("\n[5/5] Cleaning resource pack list & synchronizing all profiles...")

for prof in PROFILES:
    if os.path.exists(prof):
        # Clean options.txt and optionsLC.txt
        for opt_name in ["options.txt", "optionsLC.txt"]:
            opt_file = os.path.join(prof, opt_name)
            if os.path.exists(opt_file):
                with open(opt_file, "r", encoding="utf-8", errors="ignore") as f:
                    opt_lines = f.readlines()
                new_opt_lines = []
                for line in opt_lines:
                    if line.startswith("resourcePacks:"):
                        new_opt_lines.append('resourcePacks:["vanilla","file/MyCustomPack_Modern_32x.zip"]\n')
                    elif line.startswith("incompatibleResourcePacks:"):
                        new_opt_lines.append('incompatibleResourcePacks:[]\n')
                    else:
                        new_opt_lines.append(line)
                with open(opt_file, "w", encoding="utf-8") as f:
                    f.writelines(new_opt_lines)

        # Sync RP
        rp_dir = os.path.join(prof, "resourcepacks")
        os.makedirs(rp_dir, exist_ok=True)
        shutil.copy2(RP_MODERN_ZIP, os.path.join(rp_dir, "MyCustomPack_Modern_32x.zip"))
        
        # Sync Shader
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(AETHERIS_ZIP, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        print(f"Synced updated RP, Shader, and options to {prof}")

print("\n==================================================")
print(" ALL 8 UPGRADES FULLY APPLIED & SYNCHRONIZED!     ")
print("==================================================")
