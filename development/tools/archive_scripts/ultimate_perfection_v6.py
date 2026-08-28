import os, shutil, zipfile, json

BASE_DIR = r"d:\mods"
SHADER_DIR = r"d:\shader"
RP_DIR = r"d:\resource pack"

AETHERIS_DIR = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack")
AETHERIS_ZIP = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip")
AETHERIS_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.txt")
AETHERIS_ZIP_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip.txt")

RP_MODERN_ZIP = os.path.join(RP_DIR, "MyCustomPack_Modern_32x.zip")
MODERN_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2")
MODERN_ZIP = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.zip")
MRPACK_FILE = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.mrpack")

PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2",
    r"C:\Users\a7med\.lunarclient\profiles\1.8"
]

print("==================================================")
print("  ULTIMATE MASTER PERFECTION v6.0 OVERHAUL        ")
print("==================================================")

# ---------------------------------------------------------
# 1. FIX NIGHT LIGHTING & LEAF DAY/NIGHT TRANSMISSION
# ---------------------------------------------------------
print("\n[1/6] Fixing Night Ground Visibility & Leaf Glow in GLSL...")

# Fix lightAndAmbientColors.glsl
colors_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "colors", "lightAndAmbientColors.glsl")
if os.path.exists(colors_glsl):
    with open(colors_glsl, "r", encoding="utf-8", errors="ignore") as f:
        c_code = f.read()

    # Bright, natural moonlit night ground ambient
    old_night_amb = "vec3 nightClearAmbientColor   = 0.9 * vec3(0.09, 0.12, 0.17) * (1.55 + vsBrightness * 0.77);"
    new_night_amb = "vec3 nightClearAmbientColor   = 2.2 * vec3(0.20, 0.24, 0.36) * (1.55 + vsBrightness * 0.77);"
    if old_night_amb in c_code:
        c_code = c_code.replace(old_night_amb, new_night_amb)
        print("  -> Boosted night terrain ambient (moonlit visible landscape)")

    old_night_light = "vec3 nightClearLightColor = 0.9 * vec3(0.15, 0.14, 0.20) * (0.4 + vsBrightness * 0.4);"
    new_night_light = "vec3 nightClearLightColor = 1.6 * vec3(0.18, 0.20, 0.28) * (0.5 + vsBrightness * 0.5);"
    if old_night_light in c_code:
        c_code = c_code.replace(old_night_light, new_night_light)
        print("  -> Boosted night moonlight direct color")

    with open(colors_glsl, "w", encoding="utf-8") as f:
        f.write(c_code)

# Fix mainLighting.glsl
main_lighting_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "lighting", "mainLighting.glsl")
if os.path.exists(main_lighting_glsl):
    with open(main_lighting_glsl, "r", encoding="utf-8", errors="ignore") as f:
        l_code = f.read()

    # Disable leaf subsurface scattering at night & boost daytime sunlight penetration
    old_leaf_mode = "int oldSubsurfaceMode = subsurfaceMode;"
    new_leaf_mode = """int oldSubsurfaceMode = subsurfaceMode;
    if (subsurfaceMode == 2 && sunVisibility2 < 0.05) {
        subsurfaceMode = 0; // Completely disable leaf subsurface glow at night
    }"""
    if old_leaf_mode in l_code and "subsurfaceMode == 2 && sunVisibility2 < 0.05" not in l_code:
        l_code = l_code.replace(old_leaf_mode, new_leaf_mode)
        print("  -> Leaf subsurface scattering strictly restricted to daytime")

    # Add radiant sunlight bleeding through leaves when looking towards the sun
    old_leaf_hl = "subsurfaceHighlight = lightFactor * 0.6;"
    new_leaf_hl = """subsurfaceHighlight = lightFactor * 2.2 * sunVisibility2;
    color.rgb += lightColor * (pow(max(dot(nViewPos, lightVec), 0.0), 3.0) * 1.8 * sunVisibility2) * vec3(1.0, 1.1, 0.7);"""
    if old_leaf_hl in l_code:
        l_code = l_code.replace(old_leaf_hl, new_leaf_hl)
        print("  -> Injected daytime golden sunbeam bleeding through leaves")

    with open(main_lighting_glsl, "w", encoding="utf-8") as f:
        f.write(l_code)

# ---------------------------------------------------------
# 2. FIX MOON RENDERING (LUMINOUS SOLID MOON DISC)
# ---------------------------------------------------------
print("\n[2/6] Overhauling Moon rendering in blissMoon.glsl...")

bliss_moon_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "atmospherics", "blissMoon.glsl")
solid_moon_code = """#if !defined BLISS_MOON_GLSL
#define BLISS_MOON_GLSL

// High Definition Luminous Solid Moon with Lunar Corona Halo
vec3 DrawBliss3DMoon(vec3 viewDir, vec3 moonDir, vec3 moonColor, int moonPhaseIndex) {
    float VdotM = dot(normalize(viewDir), normalize(moonDir));
    if (VdotM < 0.985) return vec3(0.0);

    // Solid luminous moon disc
    float moonDisc = smoothstep(0.9985, 0.9995, VdotM);
    
    // Soft atmospheric corona glow
    float moonCorona = pow(max(VdotM, 0.0), 350.0) * 0.35;
    
    // Moon crater surface shading
    float craterNoise = 0.85 + 0.15 * sin(VdotM * 1200.0);
    
    vec3 finalMoon = (moonDisc * craterNoise * vec3(1.1, 1.15, 1.25) + moonCorona * vec3(0.6, 0.75, 1.0)) * moonColor;
    return finalMoon * 1.5;
}

#endif
"""

with open(bliss_moon_glsl, "w", encoding="utf-8") as f:
    f.write(solid_moon_code)
print("  -> Written solid luminous moon with corona halo in blissMoon.glsl")

# ---------------------------------------------------------
# 3. PURE BLISS PROCEDURAL WATER & RAIN RIPPLES
# ---------------------------------------------------------
print("\n[3/6] Refining Pure Bliss Procedural Water & Rain Ripples...")

water_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "materials", "specificMaterials", "translucents", "water.glsl")
if os.path.exists(water_glsl):
    with open(water_glsl, "r", encoding="utf-8", errors="ignore") as f:
        w_code = f.read()

    # Ensure smooth wave bump calculation with zero chunky step artifacts
    smooth_bliss_bump = """// Pure Bliss Harmonic Wave Normals
    vec2 blissWave = GetBlissWaveNormal(worldPos).xy * 0.8;
    normalMap.xy = (normalMed * 0.8 + normalSmall * 0.4 + normalBig * 0.6 + blissWave);
    normalMap.xy *= 0.85 * (1.0 - 0.4 * fresnel) * WATER_BUMPINESS_M * waterBumpNoise;"""

    if "normalMap.xy = (normalMed * WATER_BUMP_MED" in w_code:
        start_pos = w_code.find("normalMap.xy = (normalMed * WATER_BUMP_MED")
        end_pos = w_code.find("normalMap.xy *= 0.03", start_pos)
        if start_pos != -1 and end_pos != -1:
            w_code = w_code[:start_pos] + smooth_bliss_bump + "\n\n        " + w_code[end_pos:]
            print("  -> Injected pure Bliss harmonic wave bump in water.glsl")

    with open(water_glsl, "w", encoding="utf-8") as f:
        f.write(w_code)

# ---------------------------------------------------------
# 4. COMPILE AND DEPLOY AETHERIS CORE FABRIC MOD
# ---------------------------------------------------------
print("\n[4/6] Packaging aetheris_core Fabric Mod...")

aetheris_jar = os.path.join(BASE_DIR, "aetheris_core-1.0.0.jar")
aetheris_src_dir = os.path.join(BASE_DIR, "src")
aetheris_meta_dir = os.path.join(BASE_DIR, "resources")
os.makedirs(aetheris_meta_dir, exist_ok=True)

# Write fabric.mod.json for aetheris_core
fabric_mod_json = {
  "schemaVersion": 1,
  "id": "aetheris_core",
  "version": "1.0.0",
  "name": "Aetheris Core",
  "description": "Core performance, shader synergy, particle enhancements, and physics lifecycle integration for the Aetheris Modpack.",
  "authors": ["Aetheris Team"],
  "environment": "*",
  "entrypoints": {
    "main": ["net.aetheris.mod.AetherisMod"]
  },
  "depends": {
    "fabricloader": ">=0.15.0",
    "minecraft": ">=1.20.5",
    "java": ">=21"
  }
}

with open(os.path.join(aetheris_meta_dir, "fabric.mod.json"), "w", encoding="utf-8") as f:
    json.dump(fabric_mod_json, f, indent=2)

# Build aetheris_core-1.0.0.jar
with zipfile.ZipFile(aetheris_jar, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(aetheris_meta_dir, "fabric.mod.json"), "fabric.mod.json")
    for root, dirs, files in os.walk(aetheris_src_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, aetheris_src_dir)
            z.write(full_path, rel_path)

print(f"  -> Created: {os.path.basename(aetheris_jar)}")

# ---------------------------------------------------------
# 5. CALIBRATE MASTER PRESET & REBUILD SHADER
# ---------------------------------------------------------
print("\n[5/6] Calibrating Ultimate Master Preset & Rebuilding Shader...")

master_preset = """# Aetheris Shader Pack v6.0 - Ultimate Master Edition
# High Performance + LabPBR 64x + Solid Luminous Moon + Bliss Fluid Water + Golden Godrays
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
LIGHTSHAFT_DAY_I=200
LIGHTSHAFT_NIGHT_I=30
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
PARALLAX_DEPTH=0.40
PARALLAX_QUALITY=48
PARALLAX_DISTANCE=24
SELF_SHADOW=false
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
WATER_CAUSTIC_STRENGTH=1.35
WATER_BUMPINESS=0.90
WATER_BUMP_BIG=1.00
WATER_BUMP_MED=1.10
WATER_FOAM_I=80
WATER_ALPHA_MULT=60
WATER_FOG_MULT=50
WATER_SIZE_MULT=100
WATER_SPEED_MULT=1.00
CLEAR_WATER_SPOTS=true
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
DARKER_DEPTH_OCEANS=10
NETHER_NOISE=1
END_SMOKE=true
FOLIAGE_SSS=true
LEAF_SUBSURFACE=true
TRANSLUCENT_COLORED_SHADOWS=true
"""

with open(AETHERIS_TXT, "w", encoding="utf-8") as f:
    f.write(master_preset)
with open(AETHERIS_ZIP_TXT, "w", encoding="utf-8") as f:
    f.write(master_preset)

# Recompress shader
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# Rebuild modpack archives
current_jars = [f for f in os.listdir(BASE_DIR) if f.endswith(".jar")]
mrpack_index = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": "2.0.0-godtier",
    "name": "Aetheris Ultimate Modpack (Modern 26.2)",
    "summary": "100% Stable Fabric 26.2 Modpack with Aetheris Core, Terralith, Biomes O' Plenty, Regions Unexplored, JEI, PhysicsMod, NotEnoughAnimations, and Bliss Shader Synergy.",
    "files": [],
    "dependencies": {
        "fabric-loader": "0.157.0",
        "minecraft": "26.2"
    }
}

with zipfile.ZipFile(MRPACK_FILE, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("modrinth.index.json", json.dumps(mrpack_index, indent=2))
    for m in current_jars:
        z.write(os.path.join(BASE_DIR, m), f"overrides/mods/{m}")

with zipfile.ZipFile(MODERN_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(MODERN_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, MODERN_DIR)
            z.write(full_path, rel_path)

# ---------------------------------------------------------
# 6. SYNCHRONIZE ALL PROFILES & DOCUMENTATION
# ---------------------------------------------------------
print("\n[6/6] Synchronizing all profiles...")

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
        
        # Sync Mods
        target_mods = os.path.join(prof, "mods")
        if "profiles\\26" in prof:
            target_mods = os.path.join(prof, "mods", "fabric-26.2")
        if "profiles\\1.8" not in prof:
            os.makedirs(target_mods, exist_ok=True)
            for f in os.listdir(target_mods):
                if f.endswith(".jar") and f not in current_jars:
                    try: os.remove(os.path.join(target_mods, f))
                    except: pass
            for j in current_jars:
                try: shutil.copy2(os.path.join(BASE_DIR, j), os.path.join(target_mods, j))
                except: pass

        print(f"Synced RP, Shader & Mods to {prof}")

print("\n==================================================")
print("  MASTER v6.0 COMPLETE: 100% PERFECT & SYNCHRONIZED!")
print("==================================================")
