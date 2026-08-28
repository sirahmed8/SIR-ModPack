"""
write_shader_presets.py

Creates 3 shader presets based on Bliss, using EVERY real Bliss option:
  - Aetheris_Balanced_Shader.zip  → 80-100 FPS, high quality
  - Aetheris_Visual_Shader.zip    → 60-80 FPS, max playable quality
  - Aetheris_Extreme_Shader.zip   → 30-60 FPS, max everything (screenshots)

Install targets:
  VISUAL   profile: Visual (primary) + Balanced (secondary option)
  BALANCED profile: Balanced (primary) + Extreme (secondary option)
"""
import os, shutil, zipfile

SH_SRC   = r"D:\shader"
VISUAL   = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
BALANCED = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2"
OUT_DIR  = r"D:\mods\built"
os.makedirs(OUT_DIR, exist_ok=True)
BLISS = os.path.join(SH_SRC, "Bliss-Shader-Stable.zip")

# ══════════════════════════════════════════════════════════════════
# PRESET 1 — BALANCED  (80-100 FPS, high quality)
# ══════════════════════════════════════════════════════════════════
BALANCED_SETTINGS = """\
# ═══════════════════════════════════════════════════════════════════
# AETHERIS BALANCED SHADER  |  Based on Bliss by X0nk
# Target: 80-100 FPS  |  RTX 4050 Laptop 6GB  |  1080p
# Paired with Aetheris Ultimate Pack (Optimum Realism 64x PBR)
# ═══════════════════════════════════════════════════════════════════

# ── TONEMAP ──────────────────────────────────────────────────────
TONEMAP=ToneMap_AgX_minimal
USE_ACES_COLORSPACE_APPROXIMATION=false
SATURATION=1.05
CROSSTALK=0.02

# ── HDR AUTO-EXPOSURE ────────────────────────────────────────────
AUTO_EXPOSURE=true
EXPOSURE_MULTIPLIER=0.82
Exposure_Speed=2.0
Manual_exposure_value=0.0

# ── PURKINJE EFFECT (night eye adaptation) ───────────────────────
Purkinje_strength=0.8
Purkinje_R=0.4
Purkinje_G=0.6
Purkinje_B=1.0
Purkinje_Multiplier=1.0

# ── TAA ──────────────────────────────────────────────────────────
TAA=true
BLEND_FACTOR=0.1
TAA_UPSCALING=false
SCALE_FACTOR=1.0

# ── POST PROCESSING ───────────────────────────────────────────────
SHARPENING=0.2
BLOOM_STRENGTH=0.12
MOTION_BLUR=false
MOTION_BLUR_STRENGTH=1.0

# ── DEPTH OF FIELD ───────────────────────────────────────────────
DOF_QUALITY=0

# ── RESOURCE PACK ────────────────────────────────────────────────
RESOURCEPACK_SKY=1

# ── SUN BRIGHTNESS FIX ───────────────────────────────────────────
sun_illuminance=0.85
sunPathRotation=30.0
MOONPHASE_BASED_MOON=true
OLD_LIGHTLEAK_FIX=true

# ── POM (3D block depth from OR normal alpha) ────────────────────
POM=true
Adaptive_Step_length=true
MAX_ITERATIONS=16
POM_DEPTH=0.10
MAX_DIST=24.0
Horrible_slope_normals=false

# ── PBR SPECULAR REFLECTIONS ─────────────────────────────────────
Specular_Reflections=true
Sun_specular_Strength=1.1
Screen_Space_Reflections=false
reflection_quality=1
Rough_reflections=true
Roughness_Threshold=0.95

# ── SUBSURFACE SCATTERING ────────────────────────────────────────
SSS_TYPE=1
sss_density_multiplier=0.8
sss_absorbance_multiplier=0.8
LabSSS_Curve=2.0
MISC_BLOCK_SSS=true
MOB_SSS=false

# ── MATERIAL AO + EMISSIVES ──────────────────────────────────────
MATERIAL_AO=true
EMISSIVE_TYPE=1
Emissive_Brightness=1.0
Emissive_Curve=2.0

# ── SHADOWS ──────────────────────────────────────────────────────
shadowDistance=80.0
shadowMapResolution=1536
TRANSLUCENT_COLORED_SHADOWS=true
SCREENSPACE_CONTACT_SHADOWS=false
RENDER_ENTITY_SHADOWS=true
RENDER_PLAYER_SHADOWS=true
entityShadowDistanceMul=0.6

# ── VOLUMETRIC FOG ───────────────────────────────────────────────
VL_RENDER_RESOLUTION=0.5
VL_SAMPLES=6

# ── CLOUDS ───────────────────────────────────────────────────────
VOLUMETRIC_CLOUDS=true
CLOUDS_QUALITY=1
CLOUDS_SHADOWS=false
Cloud_Speed=0.3
CLOUD_SHADOW_STRENGTH=0.5
Rain_coverage=0.5
RAYMARCH_CLOUDS_WITH_FOG=false
CLOUDS_INTERSECT_TERRAIN=false

# ── WATER ────────────────────────────────────────────────────────
WATER_REFLECTIONS=true
Refraction=true
HYPER_DETAILED_WAVES=false
WATER_CAUSTICS_BRIGHTNESS=1.0

# ── ENVIRONMENT / CLIMATE ────────────────────────────────────────
Seasons=true
Season_Length=7
Start_Season=0
Snowy_Winter=true
PER_BIOME_ENVIRONMENT=true
SNOW_STORMS=true
SAND_STORMS=false

# ── AMBIENT OCCLUSION ────────────────────────────────────────────
AMBIENT_OCCLUSION=true

# ── GAMEPLAY EFFECTS ─────────────────────────────────────────────
DAMAGE_TAKEN_EFFECT=true
LOW_HEALTH_EFFECT=true
WATER_ON_CAMERA_EFFECT=true

# ── MISC ─────────────────────────────────────────────────────────
TRANSLUCENT_ENTITIES=true
PARTICLE_RENDERING_FIX=true
LIGHTNING_FLASH=true
BLOOMY_PARTICLES=false
BIOME_TINT_WATER=true
LIT_PARTICLE_BRIGHTNESS=1.0

# ── DISTANT HORIZONS ─────────────────────────────────────────────
DH_OVERDRAW_PREVENTION=true
OVERDRAW_MAX_DISTANCE=256
DH_AMBIENT_OCCLUSION=true
DH_SUBSURFACE_SCATTERING=false
DH_SCREENSPACE_REFLECTIONS=false
DH_NOISE_TEXTURE=true
NOISE_RESOLUTION=256
NOISE_INTENSITY=1.0
NOISE_DROPOFF=0.5
DISTANT_HORIZONS_SHADOWMAP=false
TOGGLE_VL_FOG=true
"""

# ══════════════════════════════════════════════════════════════════
# PRESET 2 — VISUAL MAX  (60-80 FPS, maximum playable quality)
# ══════════════════════════════════════════════════════════════════
VISUAL_SETTINGS = """\
# ═══════════════════════════════════════════════════════════════════
# AETHERIS VISUAL SHADER  |  Based on Bliss by X0nk
# Target: 60-80 FPS  |  RTX 4050 Laptop 6GB  |  1080p  |  MAX QUALITY
# Paired with Aetheris Ultimate Pack (Optimum Realism 64x PBR)
# ═══════════════════════════════════════════════════════════════════

# ── TONEMAP ──────────────────────────────────────────────────────
TONEMAP=ToneMap_AgX_minimal
USE_ACES_COLORSPACE_APPROXIMATION=false
SATURATION=1.08
CROSSTALK=0.03

# ── HDR AUTO-EXPOSURE ────────────────────────────────────────────
AUTO_EXPOSURE=true
EXPOSURE_MULTIPLIER=0.80
Exposure_Speed=2.5
Manual_exposure_value=0.0

# ── PURKINJE EFFECT ──────────────────────────────────────────────
Purkinje_strength=1.0
Purkinje_R=0.4
Purkinje_G=0.6
Purkinje_B=1.0
Purkinje_Multiplier=1.2

# ── TAA ──────────────────────────────────────────────────────────
TAA=true
BLEND_FACTOR=0.08
TAA_UPSCALING=false
SCALE_FACTOR=1.0

# ── POST PROCESSING ───────────────────────────────────────────────
SHARPENING=0.25
BLOOM_STRENGTH=0.15
MOTION_BLUR=false
MOTION_BLUR_STRENGTH=1.0

# ── DEPTH OF FIELD ───────────────────────────────────────────────
DOF_QUALITY=0

# ── RESOURCE PACK ────────────────────────────────────────────────
RESOURCEPACK_SKY=1

# ── SUN BRIGHTNESS FIX ───────────────────────────────────────────
sun_illuminance=0.80
sunPathRotation=30.0
MOONPHASE_BASED_MOON=true
OLD_LIGHTLEAK_FIX=true

# ── POM (3D block depth from OR normal alpha) ────────────────────
POM=true
Adaptive_Step_length=true
MAX_ITERATIONS=32
POM_DEPTH=0.15
MAX_DIST=32.0
Horrible_slope_normals=false

# ── PBR SPECULAR REFLECTIONS ─────────────────────────────────────
Specular_Reflections=true
Sun_specular_Strength=1.3
Screen_Space_Reflections=true
reflection_quality=2
Rough_reflections=true
Roughness_Threshold=0.95

# ── SUBSURFACE SCATTERING ────────────────────────────────────────
SSS_TYPE=1
sss_density_multiplier=1.2
sss_absorbance_multiplier=1.0
LabSSS_Curve=2.0
MISC_BLOCK_SSS=true
MOB_SSS=true

# ── MATERIAL AO + EMISSIVES ──────────────────────────────────────
MATERIAL_AO=true
EMISSIVE_TYPE=1
Emissive_Brightness=1.2
Emissive_Curve=2.0

# ── SHADOWS ──────────────────────────────────────────────────────
shadowDistance=128.0
shadowMapResolution=2048
TRANSLUCENT_COLORED_SHADOWS=true
SCREENSPACE_CONTACT_SHADOWS=true
RENDER_ENTITY_SHADOWS=true
RENDER_PLAYER_SHADOWS=true
entityShadowDistanceMul=1.0

# ── VOLUMETRIC FOG ───────────────────────────────────────────────
VL_RENDER_RESOLUTION=0.75
VL_SAMPLES=12

# ── CLOUDS ───────────────────────────────────────────────────────
VOLUMETRIC_CLOUDS=true
CLOUDS_QUALITY=2
CLOUDS_SHADOWS=true
Cloud_Speed=0.3
CLOUD_SHADOW_STRENGTH=0.6
Rain_coverage=0.6
RAYMARCH_CLOUDS_WITH_FOG=true
CLOUDS_INTERSECT_TERRAIN=false

# ── WATER ────────────────────────────────────────────────────────
WATER_REFLECTIONS=true
Refraction=true
HYPER_DETAILED_WAVES=true
WATER_CAUSTICS_BRIGHTNESS=1.2

# ── ENVIRONMENT / CLIMATE ────────────────────────────────────────
Seasons=true
Season_Length=7
Start_Season=0
Snowy_Winter=true
PER_BIOME_ENVIRONMENT=true
SNOW_STORMS=true
SAND_STORMS=true

# ── AMBIENT OCCLUSION ────────────────────────────────────────────
AMBIENT_OCCLUSION=true

# ── GAMEPLAY EFFECTS ─────────────────────────────────────────────
DAMAGE_TAKEN_EFFECT=true
LOW_HEALTH_EFFECT=true
WATER_ON_CAMERA_EFFECT=true

# ── MISC ─────────────────────────────────────────────────────────
TRANSLUCENT_ENTITIES=true
PARTICLE_RENDERING_FIX=true
LIGHTNING_FLASH=true
BLOOMY_PARTICLES=true
BIOME_TINT_WATER=true
LIT_PARTICLE_BRIGHTNESS=1.2
FORCE_TRANSLUCENT_GLASS=true

# ── DISTANT HORIZONS ─────────────────────────────────────────────
DH_OVERDRAW_PREVENTION=true
OVERDRAW_MAX_DISTANCE=512
DH_AMBIENT_OCCLUSION=true
DH_SUBSURFACE_SCATTERING=true
DH_SCREENSPACE_REFLECTIONS=true
DH_NOISE_TEXTURE=true
NOISE_RESOLUTION=512
NOISE_INTENSITY=1.0
NOISE_DROPOFF=0.5
DISTANT_HORIZONS_SHADOWMAP=true
TOGGLE_VL_FOG=true
"""

# ══════════════════════════════════════════════════════════════════
# PRESET 3 — EXTREME  (30-60 FPS, EVERYTHING maxed, for screenshots)
# ══════════════════════════════════════════════════════════════════
EXTREME_SETTINGS = """\
# ═══════════════════════════════════════════════════════════════════
# AETHERIS EXTREME SHADER  |  Based on Bliss by X0nk
# Target: 30-60 FPS  |  RTX 4050 Laptop 6GB  |  1080p  |  ULTRA MAX
# For screenshots and cinematic gameplay. Every setting maxed.
# ═══════════════════════════════════════════════════════════════════

# ── TONEMAP ──────────────────────────────────────────────────────
TONEMAP=ToneMap_AgX_minimal
USE_ACES_COLORSPACE_APPROXIMATION=false
SATURATION=1.10
CROSSTALK=0.04

# ── HDR AUTO-EXPOSURE ────────────────────────────────────────────
AUTO_EXPOSURE=true
EXPOSURE_MULTIPLIER=0.78
Exposure_Speed=3.0
Manual_exposure_value=0.0

# ── PURKINJE EFFECT ──────────────────────────────────────────────
Purkinje_strength=1.2
Purkinje_R=0.4
Purkinje_G=0.6
Purkinje_B=1.0
Purkinje_Multiplier=1.5

# ── TAA ──────────────────────────────────────────────────────────
TAA=true
BLEND_FACTOR=0.07
TAA_UPSCALING=false
SCALE_FACTOR=1.0

# ── POST PROCESSING ───────────────────────────────────────────────
SHARPENING=0.30
BLOOM_STRENGTH=0.18
MOTION_BLUR=true
MOTION_BLUR_STRENGTH=0.8

# ── DEPTH OF FIELD (cinematic) ───────────────────────────────────
DOF_QUALITY=2
DOF_ANAMORPHIC_RATIO=1.0
fstop=5.6
focal=70.0
MANUAL_FOCUS=false
DoF_Adaptation_Speed=2.0
FAR_BLUR_ONLY=false

# ── RESOURCE PACK ────────────────────────────────────────────────
RESOURCEPACK_SKY=1

# ── SUN BRIGHTNESS FIX ───────────────────────────────────────────
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

# ── PBR SPECULAR REFLECTIONS ─────────────────────────────────────
Specular_Reflections=true
Sun_specular_Strength=1.5
Screen_Space_Reflections=true
reflection_quality=3
Rough_reflections=true
Roughness_Threshold=0.98

# ── SUBSURFACE SCATTERING FULL ───────────────────────────────────
SSS_TYPE=1
sss_density_multiplier=1.5
sss_absorbance_multiplier=1.0
LabSSS_Curve=2.0
MISC_BLOCK_SSS=true
MOB_SSS=true

# ── MATERIAL AO + EMISSIVES ──────────────────────────────────────
MATERIAL_AO=true
EMISSIVE_TYPE=1
Emissive_Brightness=1.4
Emissive_Curve=2.0

# ── SHADOWS ULTRA ────────────────────────────────────────────────
shadowDistance=192.0
shadowMapResolution=4096
TRANSLUCENT_COLORED_SHADOWS=true
SCREENSPACE_CONTACT_SHADOWS=true
RENDER_ENTITY_SHADOWS=true
RENDER_PLAYER_SHADOWS=true
entityShadowDistanceMul=1.0

# ── VOLUMETRIC FOG ULTRA ─────────────────────────────────────────
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
CLOUDS_INTERSECT_TERRAIN=true

# ── WATER ULTRA ──────────────────────────────────────────────────
WATER_REFLECTIONS=true
Refraction=true
HYPER_DETAILED_WAVES=true
WATER_CAUSTICS_BRIGHTNESS=1.5

# ── ENVIRONMENT / CLIMATE ────────────────────────────────────────
Seasons=true
Season_Length=7
Start_Season=0
Snowy_Winter=true
PER_BIOME_ENVIRONMENT=true
SNOW_STORMS=true
SAND_STORMS=true

# ── AMBIENT OCCLUSION ────────────────────────────────────────────
AMBIENT_OCCLUSION=true

# ── GAMEPLAY EFFECTS ─────────────────────────────────────────────
DAMAGE_TAKEN_EFFECT=true
LOW_HEALTH_EFFECT=true
WATER_ON_CAMERA_EFFECT=true
MOTION_AMOUNT=1.0

# ── MISC ─────────────────────────────────────────────────────────
TRANSLUCENT_ENTITIES=true
PARTICLE_RENDERING_FIX=true
LIGHTNING_FLASH=true
BLOOMY_PARTICLES=true
BIOME_TINT_WATER=true
LIT_PARTICLE_BRIGHTNESS=1.5
FORCE_TRANSLUCENT_GLASS=true
PLANET_GROUND_BRIGHTNESS=0.5
OLD_CAVE_DETECTION=false

# ── DISTANT HORIZONS ULTRA ───────────────────────────────────────
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
# BUILD AND INSTALL
# ══════════════════════════════════════════════════════════════════
presets = {
    "Aetheris_Balanced_Shader.zip": BALANCED_SETTINGS,
    "Aetheris_Visual_Shader.zip":   VISUAL_SETTINGS,
    "Aetheris_Extreme_Shader.zip":  EXTREME_SETTINGS,
}

# Build all 3 shader ZIPs to D:\mods\built\
print("Building shader ZIPs...")
for name in presets:
    dst = os.path.join(OUT_DIR, name)
    shutil.copy2(BLISS, dst)
    print(f"  ✓ {name}")

print()
print("Installing to profiles...")

# VISUAL profile: primary=Visual, also add Balanced as option
# BALANCED profile: primary=Balanced, also add Extreme as option
profile_installs = {
    "VISUAL": {
        "path": VISUAL,
        "primary": "Aetheris_Visual_Shader.zip",
        "extras": ["Aetheris_Balanced_Shader.zip"],  # user can switch in Video Settings
    },
    "BALANCED": {
        "path": BALANCED,
        "primary": "Aetheris_Balanced_Shader.zip",
        "extras": ["Aetheris_Extreme_Shader.zip"],   # user can switch in Video Settings
    },
}

for profile_name, cfg in profile_installs.items():
    sp_dir = os.path.join(cfg["path"], "shaderpacks")
    os.makedirs(sp_dir, exist_ok=True)

    # Remove ALL old shader ZIPs (keep .txt files)
    for f in os.listdir(sp_dir):
        fp = os.path.join(sp_dir, f)
        if os.path.isfile(fp) and f.endswith(".zip"):
            os.remove(fp)
            print(f"  [{profile_name}] removed old: {f}")

    # Install primary shader
    primary = cfg["primary"]
    shutil.copy2(os.path.join(OUT_DIR, primary), os.path.join(sp_dir, primary))
    # Write primary settings
    with open(os.path.join(sp_dir, primary + ".txt"), "w") as f:
        f.write(presets[primary])
    print(f"  [{profile_name}] ✓ primary: {primary}")

    # Install extra shaders (for user to switch)
    for extra in cfg["extras"]:
        shutil.copy2(os.path.join(OUT_DIR, extra), os.path.join(sp_dir, extra))
        with open(os.path.join(sp_dir, extra + ".txt"), "w") as f:
            f.write(presets[extra])
        print(f"  [{profile_name}] + extra:   {extra}")

    # iris.properties → primary shader
    iris = os.path.join(cfg["path"], "config", "iris.properties")
    with open(iris, "w") as f:
        f.write(f"shaderpack={primary}\n")
    print(f"  [{profile_name}] iris.properties → {primary}")
    print()

print("=" * 65)
print("DONE! Shader presets installed:")
print()
print("  VISUAL   profile:")
print("    [PRIMARY]  Aetheris_Visual_Shader   — max quality, ~60-80 FPS")
print("    [OPTIONAL] Aetheris_Balanced_Shader — high quality, ~80-100 FPS")
print("    → Switch in: Esc → Options → Video Settings → Shader Packs")
print()
print("  BALANCED profile:")
print("    [PRIMARY]  Aetheris_Balanced_Shader — high quality, ~80-100 FPS")
print("    [OPTIONAL] Aetheris_Extreme_Shader  — ultra max, ~30-60 FPS")
print("    → Switch in: Esc → Options → Video Settings → Shader Packs")
print()
print("All presets feature:")
print("  AUTO_EXPOSURE — real HDR eye adaptation (cave ↔ sun)")
print("  sun_illuminance=0.78-0.85 — sun is no longer blinding")
print("  POM — OR normal alpha = real 3D block depth")
print("  TRANSLUCENT_COLORED_SHADOWS — dappled sunlight through leaves")
print("  Specular_Reflections — OR _s.png maps active")
print("  RESOURCEPACK_SKY=1 — HD moon from Optimum Realism")
print("  Seasons + PER_BIOME_ENVIRONMENT — dynamic world")
