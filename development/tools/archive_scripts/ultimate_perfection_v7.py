import os, shutil, zipfile, json

BASE_DIR = r"d:\mods"
SHADER_DIR = r"d:\shader"
RP_DIR = r"d:\resource pack"

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
print("  MASTER v7.0 OVERHAUL: WATER, OCEAN, PHYSICS, ULTRA")
print("==================================================")

# ---------------------------------------------------------
# 1. OVERHAUL WATER.GLSL (NO WHITE SPOTS, SMOOTH EDGES, DEEP OCEANS)
# ---------------------------------------------------------
print("\n[1/4] Overhauling water.glsl (volumetric ocean fog, no white spots, smooth flow)...")

water_glsl_path = os.path.join(AETHERIS_DIR, "shaders", "lib", "materials", "specificMaterials", "translucents", "water.glsl")
if os.path.exists(water_glsl_path):
    with open(water_glsl_path, "r", encoding="utf-8", errors="ignore") as f:
        w_code = f.read()

    # Remove artificial bright cave water that creates white cloud spots
    if "color.rgb *= 2.5 - sqrt2(waterFog) - 0.5 * lmCoordM.y;" in w_code:
        w_code = w_code.replace("color.rgb *= 2.5 - sqrt2(waterFog) - 0.5 * lmCoordM.y;", "// Cave water multiplier removed")
        print("  -> Permanently removed 2.5x white cloud spot multiplier")

    # Replace color gradient with rich volumetric ocean depth
    ocean_transmission_code = """// Rich Volumetric Ocean Depth & Tropical Shallows
            vec3 shallowColor = vec3(0.12, 0.68, 0.84);
            vec3 deepOceanColor = vec3(0.01, 0.08, 0.28);
            float fogDepthMix = clamp01(waterFog * 1.4 + length(viewPos) * 0.015);
            color.rgb = mix(shallowColor, deepOceanColor, fogDepthMix) * glColorM;
            
            // Smooth shoreline edge fade (eliminates boxy borders on placed water)
            float edgeFade = smoothstep(0.0, 0.18, max0(lViewPosDifM));
            color.a = clamp01((0.35 + 0.65 * waterFog) * edgeFade);"""

    if "color.a *= 0.25 + 0.75 * waterFog;" in w_code:
        start_idx = w_code.find("color.a *= 0.25 + 0.75 * waterFog;")
        end_idx = w_code.find("color.a = pow(color.a, WATER_ALPHA_MULT_M);", start_idx) + 43
        if start_idx != -1 and end_idx != -1:
            w_code = w_code[:start_idx] + ocean_transmission_code + w_code[end_idx:]
            print("  -> Injected volumetric ocean fog & smooth shoreline edge blending")

    with open(water_glsl_path, "w", encoding="utf-8") as f:
        f.write(w_code)

# ---------------------------------------------------------
# 2. CONFIGURE REAL OCEAN WAVES & PHYSICS IN PHYSICS MOD
# ---------------------------------------------------------
print("\n[2/4] Enabling Real Ocean Waves & Water Splash Physics in PhysicsMod...")

for prof in PROFILES:
    cfg_dir = os.path.join(prof, "config", "physicsmod")
    if os.path.exists(cfg_dir):
        p_cfg = os.path.join(cfg_dir, "physics_client_config.json")
        if os.path.exists(p_cfg):
            try:
                with open(p_cfg, "r", encoding="utf-8") as f:
                    p_data = json.load(f)
                p_data["oceanPhysics"] = True
                p_data["oceanParticles"] = True
                p_data["oceanWeatherClear"] = 0.65 # Waves in clear weather!
                p_data["oceanWeatherRain"] = 1.0
                p_data["oceanWeatherThunder"] = 1.5
                p_data["oceanDetail"] = 2.0
                p_data["oceanWaveHeightMultiplier"] = 1.5
                p_data["oceanFoamAmount"] = 1.0
                p_data["oceanFoamOpacity"] = 0.7
                p_data["liquidPhysics"] = True
                p_data["sprintingPhysicsParticles"] = True
                p_data["snowTracks"] = True
                with open(p_cfg, "w", encoding="utf-8") as f:
                    json.dump(p_data, f, indent=2)
                print(f"  -> Configured real ocean waves & splash particles in {p_cfg}")
            except Exception as e:
                print(f"  -> Error updating {p_cfg}: {e}")

# ---------------------------------------------------------
# 3. CONFIGURE ALL SHADER OPTIONS TO HIGHEST / ULTRA BY DEFAULT
# ---------------------------------------------------------
print("\n[3/4] Configuring Ultra-Quality Master Preset (All Max Quality)...")

ultra_preset = """# Aetheris Shader Pack v7.0 - Ultimate Ultra-High Quality Preset
# Maximum Visual Quality + LabPBR 64x + Real Volumetric Oceans + Solas Atmosphere + BSL Tonemap
profile=RTX4050
profile2=AETHERIS
tonemap=DoBSLTonemap
SHADOW_QUALITY=3
shadowDistance=256.0
shadowMapResolution=4096
WATER_STYLE_DEFINE=3
WATER_REFLECT_QUALITY=3
BLOCK_REFLECT_QUALITY=3
LIGHTSHAFT_BEHAVIOUR=2
LIGHTSHAFT_QUALI_DEFINE=3
LIGHTSHAFT_DAY_I=200
LIGHTSHAFT_NIGHT_I=30
SSAO_QUALI_DEFINE=3
FXAA_DEFINE=1
DETAIL_QUALITY=3
CLOUD_QUALITY=3
ANISOTROPIC_FILTER=4
COLORED_LIGHTING=0
WORLD_SPACE_REFLECTIONS=-1
ENTITY_SHADOW=1
RP_MODE=2
PARALLAX=true
PARALLAX_DEPTH=0.45
PARALLAX_QUALITY=64
PARALLAX_DISTANCE=32
SELF_SHADOW=false
SLOPE_NORMALS=true
GENERATED_NORMALS=false
GENERATED_SPECULAR=false
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
GLOWING_AMETHYST=2
GLOWING_LICHEN=0
EMISSIVE_REDSTONE_BLOCK=true
EMISSIVE_LAPIS_BLOCK=true
EMISSIVE_ENCHANTING_TABLE=true
EMISSIVE_SOUL_SAND=true
GLOWING_WART=false
GLOWING_EMERALD_BLOCK=true
GLOWING_NETHER_TREES=false
SITUATIONAL_ORES=true
DO_IPBR_LIGHTS=true
DYNAMIC_HANDLIGHT=true
AURORA_COLOR_PRESET=1
AURORA_INFLUENCE=false
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
WATER_CAUSTIC_STRENGTH=1.40
WATER_BUMPINESS=1.00
WATER_BUMP_BIG=1.10
WATER_BUMP_MED=1.20
WATER_FOAM_I=90
WATER_ALPHA_MULT=100
WATER_FOG_MULT=130
WATER_SIZE_MULT=100
WATER_SPEED_MULT=1.00
CLEAR_WATER_SPOTS=false
SUN_GLARE_AMOUNT=5
SUN_INTENSITY=100
ROUND_SUN=true
SUN_MOON_STYLE=1
NIGHT_BRIGHTNESS=160
PURKINJE_OVERWRITE=0
DIRECTIONAL_LIGHTMAP_NORMALS=true
BLOCKLIGHT_CAUSTICS=true
RAIN_ATMOSPHERE=true
RAIN_PUDDLES=2
RAIN_STYLE=2
REDSTONE_IPBR=true
SSS_SNOW_ICE=true
STAR_AMOUNT=2
NIGHT_STAR_AMOUNT=3
STAR_BRIGHTNESS=16
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
IMAGE_SHARPENING=3
BLOOM_STRENGTH=0.028
TAA=true
DISTANT_HORIZONS=false
DARKER_DEPTH_OCEANS=100
NETHER_NOISE=1
END_SMOKE=true
FOLIAGE_SSS=true
LEAF_SUBSURFACE=true
TRANSLUCENT_COLORED_SHADOWS=true
"""

with open(AETHERIS_TXT, "w", encoding="utf-8") as f:
    f.write(ultra_preset)
with open(AETHERIS_ZIP_TXT, "w", encoding="utf-8") as f:
    f.write(ultra_preset)

# Recompress shader
print("Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# ---------------------------------------------------------
# 4. SYNCHRONIZE TO ALL PROFILES
# ---------------------------------------------------------
print("\n[4/4] Synchronizing all profiles...")

for prof in PROFILES:
    if os.path.exists(prof):
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(AETHERIS_ZIP, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.txt"))
        print(f"Synced Ultra shader to {sp_dir}")

print("\n==================================================")
print("  MASTER v7.0 COMPLETE: ULTRA QUALITY & REAL PHYSICS!")
print("==================================================")
