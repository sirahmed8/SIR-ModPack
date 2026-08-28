"""
phase2_3_shaders_and_pack.py

Phase 2: Install LPV shader (voxel GI) + update all shader settings with correct LPV option names
Phase 3: Create emissive block.properties for LPV shader (mod block glow mapping)
"""
import os, shutil, zipfile, json

SH_DIR   = r"D:\shader"
RP_SRC   = r"D:\resource pack"
VISUAL   = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
BALANCED = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2"
OUT_DIR  = r"D:\mods\built"
os.makedirs(OUT_DIR, exist_ok=True)

BLISS_STABLE = os.path.join(SH_DIR, "Bliss-Shader-Stable.zip")
BLISS_LPV    = os.path.join(SH_DIR, "Bliss-Shader-lpv.shift.zip")

# ══════════════════════════════════════════════════════════════════
# LPV SHADER SETTINGS (voxel GI - uses different option names)
# ══════════════════════════════════════════════════════════════════
LPV_SETTINGS = """\
# ═══════════════════════════════════════════════════════════════════
# AETHERIS LPV SHADER  |  Based on Bliss LPV by X0nk
# RTX 4050 Laptop 6GB  |  LPV_SIZE=6 (64^3 voxels)
# TARGET: 30-50 FPS  |  USE FOR: Screenshots, Exploration, Cinematic
# FEATURE: Torches/Lava/Ores emit REAL colored light on nearby blocks
# ═══════════════════════════════════════════════════════════════════

# ── LPV VOXEL GI ─────────────────────────────────────────────────
# LPV_ENABLED is a compile-time define in this shader (always on)
# LPV_SIZE=6 = 64x64x64 voxel volume (affordable on RTX 4050)
LPV_SIZE=6

# ── TONEMAP ──────────────────────────────────────────────────────
TONEMAP=ToneMap_AgX_minimal
USE_ACES_COLORSPACE_APPROXIMATION=false
SATURATION=1.10
CROSSTALK=0.04
WHITE_BALANCE=0.0

# ── HDR AUTO-EXPOSURE (LPV names) ────────────────────────────────
AUTO_EXPOSURE=true
AUTO_EXPOSURE_ADJUST_RATE=2.5
EXPOSURE_MULTIPLIER=0.78
EXPOSURE_DARKENING=1.0
EXPOSURE_BRIGHTENING=1.0
Manual_exposure_value=0.0

# ── PURKINJE (LPV uses PURKINJE_AMOUNT) ──────────────────────────
PURKINJE_AMOUNT=1.2
Purkinje_R=0.4
Purkinje_G=0.6
Purkinje_B=1.0
Purkinje_Multiplier=1.5

# ── TAA (LPV uses TAA_MODE) ──────────────────────────────────────
TAA_MODE=1
SCALE_FACTOR=1.0
BLEND_FACTOR=0.07
BLEND_FACTOR_DURING_MOVEMENT=0.12
NEIGHBORHOOD_CLAMP_RADIUS_MULT_DURING_MOVEMENT=1.5

# ── POST PROCESSING ───────────────────────────────────────────────
BLOOM_STRENGTH=0.18
SHARPENING_AMOUNT=0.30
MOTION_BLUR_AMOUNT=0.5
CHROMATIC_ABERRATION_AMOUNT=0.02
VIGNETTE_AMOUNT=0.15

# ── CINEMATIC ────────────────────────────────────────────────────
CINEMATIC_BORDER_COVERAGE_VERTICAL=0.0
CINEMATIC_BORDER_COVERAGE_HORIZONTAL=0.0

# ── DEPTH OF FIELD (cinematic) ───────────────────────────────────
DOF_QUALITY=2
MANUAL_FOCUS=false
focal=70.0
aperture=5.6
DoF_Adaptation_Speed=2.0
DOF_ANAMORPHIC_RATIO=1.0
DOF_DISPERSION_MULT=1.0
FAR_BLUR_ONLY=false

# ── GAMEPLAY EFFECTS ─────────────────────────────────────────────
MOTION_AMOUNT=1.0
WATER_ON_CAMERA_EFFECT_AMOUNT=1.0
ON_FIRE_DISTORT_EFFECT_AMOUNT=1.0
MINOR_DAMAGE_TAKEN_EFFECT_START=0.5
CRITICAL_DAMAGE_TAKEN_EFFECT_START=0.3
LOW_HEALTH_EFFECT_START=0.25

# ── RESOURCE PACK ────────────────────────────────────────────────
RESOURCEPACK_SKY=1

# ── SUN BRIGHTNESS ───────────────────────────────────────────────
sun_illuminance=0.78
sunPathRotation=30.0
MOONPHASE_BASED_MOON=true
OLD_LIGHTLEAK_FIX=true

# ── POM ULTRA ────────────────────────────────────────────────────
POM=true
Adaptive_Step_length=true
MAX_ITERATIONS=64
POM_DEPTH=0.20
MAX_DIST=48.0
Horrible_slope_normals=false

# ── PBR REFLECTIONS ──────────────────────────────────────────────
Specular_Reflections=true
Sun_specular_Strength=1.5
Screen_Space_Reflections=true
reflection_quality=3
Rough_reflections=true
Roughness_Threshold=0.98

# ── SSS ──────────────────────────────────────────────────────────
SSS_TYPE=1
sss_density_multiplier=1.5
sss_absorbance_multiplier=1.0
LabSSS_Curve=2.0
MISC_BLOCK_SSS=true
MOB_SSS=true

# ── MATERIAL ─────────────────────────────────────────────────────
MATERIAL_AO=true
EMISSIVE_TYPE=1
Emissive_Brightness=1.5
Emissive_Curve=2.0

# ── SHADOWS ULTRA ────────────────────────────────────────────────
shadowDistance=192.0
shadowMapResolution=4096
TRANSLUCENT_COLORED_SHADOWS=true
SCREENSPACE_CONTACT_SHADOWS=true
RENDER_ENTITY_SHADOWS=true
RENDER_PLAYER_SHADOWS=true
entityShadowDistanceMul=1.0

# ── VOLUMETRIC FOG ───────────────────────────────────────────────
VL_RENDER_RESOLUTION=1.0
VL_SAMPLES=20

# ── CLOUDS ULTRA ─────────────────────────────────────────────────
VOLUMETRIC_CLOUDS=true
CLOUDS_QUALITY=3
CLOUDS_SHADOWS=true
Cloud_Speed=0.3
CLOUD_SHADOW_STRENGTH=0.8
Rain_coverage=0.7
RAYMARCH_CLOUDS_WITH_FOG=true

# ── WATER ────────────────────────────────────────────────────────
WATER_REFLECTIONS=true
Refraction=true
HYPER_DETAILED_WAVES=true
WATER_CAUSTICS_BRIGHTNESS=1.5

# ── ENVIRONMENT ──────────────────────────────────────────────────
Seasons=true
Season_Length=7
PER_BIOME_ENVIRONMENT=true
SNOW_STORMS=true
SAND_STORMS=true

# ── MISC ─────────────────────────────────────────────────────────
AMBIENT_OCCLUSION=true
TRANSLUCENT_ENTITIES=true
PARTICLE_RENDERING_FIX=true
LIGHTNING_FLASH=true
BLOOMY_PARTICLES=true
BIOME_TINT_WATER=true
LIT_PARTICLE_BRIGHTNESS=1.5
FORCE_TRANSLUCENT_GLASS=true

# ── DISTANT HORIZONS ─────────────────────────────────────────────
DH_OVERDRAW_PREVENTION=true
OVERDRAW_MAX_DISTANCE=1024
DH_AMBIENT_OCCLUSION=true
DH_SUBSURFACE_SCATTERING=true
DH_SCREENSPACE_REFLECTIONS=true
DH_NOISE_TEXTURE=true
NOISE_RESOLUTION=1024
NOISE_INTENSITY=1.0
NOISE_DROPOFF=0.5
DISTANT_HORIZONS_SHADOWMAP=true
TOGGLE_VL_FOG=true
"""

# ══════════════════════════════════════════════════════════════════
# PHASE 3: EMISSIVE BLOCK.PROPERTIES for LPV
# Maps all modded glowing blocks so LPV GI picks them up
# ══════════════════════════════════════════════════════════════════
EMISSIVE_BLOCK_PROPS = """\
# block.properties — Emissive blocks for Bliss LPV shader
# These blocks emit colored light that propagates through the voxel grid
# Format: block.NNNN = modid:blockname  where NNNN is a unique ID 1-32767
# Light colors are defined by the shader reading these block IDs

# ── VANILLA GLOWING BLOCKS ───────────────────────────────────────
block.1     = minecraft:glowstone
block.2     = minecraft:sea_lantern
block.3     = minecraft:beacon
block.4     = minecraft:end_rod
block.5     = minecraft:fire
block.6     = minecraft:soul_fire
block.7     = minecraft:campfire
block.8     = minecraft:soul_campfire
block.9     = minecraft:torch
block.10    = minecraft:wall_torch
block.11    = minecraft:soul_torch
block.12    = minecraft:soul_wall_torch
block.13    = minecraft:lava
block.14    = minecraft:magma_block
block.15    = minecraft:shroomlight
block.16    = minecraft:jack_o_lantern
block.17    = minecraft:lantern
block.18    = minecraft:soul_lantern
block.19    = minecraft:crying_obsidian
block.20    = minecraft:respawn_anchor
block.21    = minecraft:lightning_rod
block.22    = minecraft:cave_vines
block.23    = minecraft:cave_vines_plant
block.24    = minecraft:small_dripleaf
block.25    = minecraft:big_dripleaf
block.26    = minecraft:sculk_sensor
block.27    = minecraft:sculk_shrieker
block.28    = minecraft:calibrated_sculk_sensor
block.29    = minecraft:ochre_froglight
block.30    = minecraft:verdant_froglight
block.31    = minecraft:pearlescent_froglight
block.32    = minecraft:nether_portal

# ── VANILLA ORES (glow from natural luminosity) ──────────────────
block.40    = minecraft:redstone_lamp[lit=true]
block.41    = minecraft:redstone_torch
block.42    = minecraft:redstone_wall_torch
block.43    = minecraft:brewing_stand
block.44    = minecraft:blast_furnace[lit=true]
block.45    = minecraft:smoker[lit=true]
block.46    = minecraft:furnace[lit=true]

# ── TERRALITH GLOWING BLOCKS ─────────────────────────────────────
block.100   = terralith:glowing_lichen
block.101   = terralith:luminous_caves_glow

# ── BETTER NETHER ────────────────────────────────────────────────
block.110   = betternether:glowing_ink_block
block.111   = betternether:lumyre
block.112   = betternether:glowing_mushroom
block.113   = betternether:jellyfish_mushroom

# ── BETTER END ───────────────────────────────────────────────────
block.120   = betterend:aurora_crystal
block.121   = betterend:glowing_pillar_bulb
block.122   = betterend:amber_block
block.123   = betterend:ether_stone
block.124   = betterend:blossom_berry_bush
block.125   = betterend:shadow_berries
block.126   = betterend:hydralux_petal_block
block.127   = betterend:hydralux_sapling
block.128   = betterend:neon_cactus

# ── BIOMES O PLENTY ──────────────────────────────────────────────
block.130   = biomesoplenty:glowshroom
block.131   = biomesoplenty:brimstone
block.132   = biomesoplenty:willow_vine

# ── MACAW'S LIGHTS ───────────────────────────────────────────────
block.140   = mcwlights:lamppost
block.141   = mcwlights:wall_lamp
block.142   = mcwlights:ceiling_lamp
block.143   = mcwlights:arc_lamp
block.144   = mcwlights:industrial_lamp
block.145   = mcwlights:cage_lamp
block.146   = mcwlights:table_lamp
block.147   = mcwlights:cone_lamp
block.148   = mcwlights:light_bulb
block.149   = mcwlights:chandelier

# ── RECHISELED / FUSION GLOWING BLOCKS ───────────────────────────
block.150   = rechiseled:chiseled_glowstone
block.151   = rechiseled:chiseled_sea_lantern

# ── VISUALITY / PARTICLE EMITTING BLOCKS ─────────────────────────
block.160   = minecraft:prismarine
block.161   = minecraft:dark_prismarine
block.162   = minecraft:prismarine_bricks
block.163   = minecraft:conduit
"""

# ══════════════════════════════════════════════════════════════════
# BUILD AND INSTALL
# ══════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 2: Building shaders")
print("=" * 60)

# Build LPV shader ZIP
LPV_SHADER_DST = os.path.join(OUT_DIR, "Aetheris_LPV_Shader.zip")
shutil.copy2(BLISS_LPV, LPV_SHADER_DST)
print("  ✓ Aetheris_LPV_Shader.zip built from Bliss LPV")

# Install LPV to VISUAL profile (as optional shader)
v_sp = os.path.join(VISUAL, "shaderpacks")
shutil.copy2(LPV_SHADER_DST, os.path.join(v_sp, "Aetheris_LPV_Shader.zip"))
with open(os.path.join(v_sp, "Aetheris_LPV_Shader.zip.txt"), "w") as f:
    f.write(LPV_SETTINGS)
print("  ✓ Aetheris_LPV_Shader installed to VISUAL profile")
print("    Switch to it: Esc → Video Settings → Shader Packs → Aetheris_LPV_Shader")

# VISUAL profile now has 3 shaders:
# Primary: Aetheris_Visual_Shader (max quality, 60-80 FPS)
# Option2: Aetheris_Balanced_Shader (fast, 80-100 FPS)
# Option3: Aetheris_LPV_Shader (voxel GI, 30-50 FPS, screenshots)

print()
print("  VISUAL profile shaders:")
for f in sorted(os.listdir(v_sp)):
    if f.endswith(".zip"):
        sz = os.path.getsize(os.path.join(v_sp, f)) / 1024 / 1024
        print("    " + f + " (" + str(round(sz,1)) + "MB)")

print()
print("=" * 60)
print("PHASE 3: Emissive block.properties for LPV")
print("=" * 60)

# Inject block.properties into the LPV shader ZIP in the profile
# Bliss LPV reads block.properties from shader ZIP or shaderpacks folder
lpv_in_profile = os.path.join(v_sp, "Aetheris_LPV_Shader.zip")
import zipfile as zf

# Read existing ZIP, add block.properties
temp_zip = lpv_in_profile + ".tmp"
with zf.ZipFile(lpv_in_profile, "r") as zin:
    with zf.ZipFile(temp_zip, "w", zf.ZIP_DEFLATED, compresslevel=6) as zout:
        for item in zin.infolist():
            if "block.properties" not in item.filename:
                zout.writestr(item, zin.read(item.filename))
        # Find the shaders directory prefix
        shader_dirs = set()
        for n in zin.namelist():
            parts = n.split("/")
            if len(parts) > 1 and parts[0]:
                shader_dirs.add(parts[0])
        # Use the first dir or root
        prefix = (list(shader_dirs)[0] + "/") if shader_dirs else ""
        # Add block.properties at the right path
        zout.writestr(prefix + "shaders/block.properties", EMISSIVE_BLOCK_PROPS)
        print("  ✓ Injected block.properties: " + str(len([l for l in EMISSIVE_BLOCK_PROPS.splitlines() if l.startswith("block.")])) + " emissive block mappings")

os.replace(temp_zip, lpv_in_profile)
print("  ✓ LPV shader updated with emissive map")
print()
print("What this means:")
print("  Torches → warm orange glow on walls around them")
print("  Lava → hot orange-red light on nearby stone")
print("  Glowstone → bright white-yellow light spreads across ceiling")
print("  Lanterns → warm amber pools of light on ground")
print("  BetterEnd crystals → colored ambient glow")
print("  Macaw's lights → proper lamp illumination")
print()
print("=" * 60)
print("PHASE 2+3 COMPLETE")
print("=" * 60)
