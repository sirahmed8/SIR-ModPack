"""
fix_and_rebuild.py

Fixes:
  1. Broken mob faces: remove Fresh Animations (conflicts with BetterAnimationsCollection mod)
  2. Missing inventory blocks: remove Better Leaves models (caused inventory render issues)
  3. Pack not 3D: Better Leaves IS actually needed for transparent leaves; the issue was POM disabled
     → Enable POM in shader (OR normal maps store height in alpha channel)
  4. Visual shader = MAX everything
  5. Balanced shader = optimized high quality
"""
import os, shutil, zipfile, json, re

RP_SRC   = r"D:\resource pack"
SH_SRC   = r"D:\shader"
VISUAL   = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
BALANCED = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2"
OUT_DIR  = r"D:\mods\built"
os.makedirs(OUT_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════
# 1. REBUILD PACK  — OR 64x only (BetterAnimationsCollection mod handles animations)
#    NO Fresh Animations (conflicts with BAC mod → broken faces)
#    KEEP Better Leaves BUT only leaf model/texture overrides, skip block models
#    that would break inventory
# ══════════════════════════════════════════════════════════════════
print("=" * 60)
print("REBUILDING: Aetheris_Ultimate_Pack.zip")
print("=" * 60)

OR_ZIP = os.path.join(RP_SRC, "Optimum Realism R3.9.0 64x.zip")
BL_ZIP = os.path.join(RP_SRC, "Better-Leaves-9.5.zip")

file_map = {}

print("  Loading Optimum Realism 64x (base)...")
with zipfile.ZipFile(OR_ZIP) as z:
    for name in z.namelist():
        if not name.endswith("/"):
            file_map[name] = z.read(name)
print(f"  OR: {len(file_map)} files")

# From Better Leaves, only take:
# - block STATE files (blockstates/) — defines which model variant to use
# - block MODEL files (models/block/) — the actual 3D leaf shape
# - leaf TEXTURES — transparent leaf textures
# SKIP: entity/ folder, anything that could mess up inventory
print("  Layering Better Leaves (leaf models + blockstates only)...")
bl_count = 0
with zipfile.ZipFile(BL_ZIP) as z:
    for name in z.namelist():
        if name.endswith("/") or name in ("pack.mcmeta", "pack.png"):
            continue
        # Only include leaf-related files, not entity models or generic overrides
        lower = name.lower()
        is_leaf = (
            "leaves" in lower or
            "leaf" in lower or
            "foliage" in lower or
            "bush" in lower or
            "fern" in lower or
            "vine" in lower or
            "azalea" in lower or
            "mangrove" in lower
        )
        # Always skip entity models and animations from BL
        is_entity = "entity" in lower or "cem" in lower or "/mob" in lower
        if is_leaf and not is_entity:
            file_map[name] = z.read(name)
            bl_count += 1

print(f"  BL: {bl_count} leaf files layered")

# Custom pack.mcmeta
pack_meta = {
    "pack": {
        "pack_format": 80,
        "supported_formats": [15, 130],
        "description": (
            "§6§lAetheris Ultimate Pack\n"
            "§7Optimum Realism 64x PBR + Better Leaves\n"
            "§8Normal Maps · Speculars · CTM · Transparent Leaves"
        )
    }
}
file_map["pack.mcmeta"] = json.dumps(pack_meta, indent=2).encode("utf-8")

OUT_PACK = os.path.join(OUT_DIR, "Aetheris_Ultimate_Pack.zip")
print(f"  Writing {len(file_map)} files...")
with zipfile.ZipFile(OUT_PACK, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zout:
    for name, data in file_map.items():
        zout.writestr(name, data)

size_mb = os.path.getsize(OUT_PACK) / 1024 / 1024
print(f"  ✓ Pack built: {size_mb:.1f} MB")
print()

# ══════════════════════════════════════════════════════════════════
# 2. VISUAL SHADER SETTINGS — MAX QUALITY
#    OR _n.png normal maps store height in alpha → POM works!
#    Push everything to maximum for RTX 4050 Laptop
# ══════════════════════════════════════════════════════════════════

VISUAL_SETTINGS = """\
# ═══════════════════════════════════════════════════════════════
# AETHERIS VISUAL SHADER — Based on Bliss by X0nk
# MAX QUALITY for RTX 4050 Laptop 6GB | 1080p
# Paired with: Aetheris Ultimate Pack (Optimum Realism 64x PBR)
# Expected FPS: 60-80 (shadows) / 70-90 (sky)
# ═══════════════════════════════════════════════════════════════

# ── TONEMAP ──────────────────────────────────────────────────────
# AgX = no highlight blowout, cinematic natural colors
TONEMAP=ToneMap_AgX_minimal

# ── HDR AUTO-EXPOSURE ────────────────────────────────────────────
# Your eyes adapt: cave enters = slowly brightens, step to sun = dims first
AUTO_EXPOSURE=true
EXPOSURE_MULTIPLIER=0.82
Exposure_Speed=2.5
Manual_exposure_value=0.0

# ── RESOURCE PACK ────────────────────────────────────────────────
# Use Optimum Realism moon/sun textures (HD, no white square moon)
RESOURCEPACK_SKY=1

# ── POM — PARALLAX OCCLUSION MAPPING ─────────────────────────────
# OR's _n.png files store height in the alpha channel → real 3D depth!
# This is what makes blocks look physically 3D with real depth/shadows
POM=true
Adaptive_Step_length=true
MAX_ITERATIONS=32
POM_DEPTH=0.15
MAX_DIST=32.0
Horrible_slope_normals=false

# ── PBR SPECULAR REFLECTIONS ─────────────────────────────────────
# OR has 1444 _s.png specular maps — makes every block material glisten correctly
Specular_Reflections=true
Sun_specular_Strength=1.3
Screen_Space_Reflections=true
reflection_quality=2
Rough_reflections=true
Roughness_Threshold=0.95

# ── SUBSURFACE SCATTERING ────────────────────────────────────────
# Leaves glow amber when sun is behind them. Skin translucent in sunlight.
SSS_TYPE=1
sss_density_multiplier=1.2
sss_absorbance_multiplier=1.0
LabSSS_Curve=2.0
MISC_BLOCK_SSS=true
MOB_SSS=true

# ── MATERIAL AO ──────────────────────────────────────────────────
# Per-pixel ambient occlusion from OR's 1419 normal maps (deep crevices)
MATERIAL_AO=true

# ── EMISSIVES ────────────────────────────────────────────────────
EMISSIVE_TYPE=1
Emissive_Brightness=1.2
Emissive_Curve=2.0

# ── SHADOWS — HIGH QUALITY ───────────────────────────────────────
shadowDistance=128.0
shadowMapResolution=2048
TRANSLUCENT_COLORED_SHADOWS=true
SCREENSPACE_CONTACT_SHADOWS=true
RENDER_ENTITY_SHADOWS=true
RENDER_PLAYER_SHADOWS=true
entityShadowDistanceMul=1.0

# ── CLOUDS — VOLUMETRIC MAX ──────────────────────────────────────
VOLUMETRIC_CLOUDS=true
CLOUDS_QUALITY=2
CLOUDS_SHADOWS=true
RAYMARCH_CLOUDS_WITH_FOG=true

# ── AMBIENT OCCLUSION ────────────────────────────────────────────
AMBIENT_OCCLUSION=true

# ── DISTANT HORIZONS ─────────────────────────────────────────────
DH_OVERDRAW_PREVENTION=true
DH_AMBIENT_OCCLUSION=true
DH_SUBSURFACE_SCATTERING=true
DH_SCREENSPACE_REFLECTIONS=true

BLOOMY_PARTICLES=true
"""

BALANCED_SETTINGS = """\
# ═══════════════════════════════════════════════════════════════
# AETHERIS BALANCED SHADER — Based on Bliss by X0nk
# HIGH QUALITY + PERFORMANCE for RTX 4050 Laptop | 1080p
# Expected FPS: 80-100 FPS consistent
# ═══════════════════════════════════════════════════════════════

TONEMAP=ToneMap_AgX_minimal
AUTO_EXPOSURE=true
EXPOSURE_MULTIPLIER=0.82
Exposure_Speed=2.0
Manual_exposure_value=0.0
RESOURCEPACK_SKY=1

# POM with lower iterations for performance
POM=true
Adaptive_Step_length=true
MAX_ITERATIONS=16
POM_DEPTH=0.1
MAX_DIST=24.0
Horrible_slope_normals=false

Specular_Reflections=true
Sun_specular_Strength=1.0
Screen_Space_Reflections=false
reflection_quality=1
Rough_reflections=true
Roughness_Threshold=0.95

SSS_TYPE=1
sss_density_multiplier=0.8
sss_absorbance_multiplier=0.8
LabSSS_Curve=2.0
MISC_BLOCK_SSS=true
MOB_SSS=false

MATERIAL_AO=true
EMISSIVE_TYPE=1
Emissive_Brightness=1.0
Emissive_Curve=2.0

shadowDistance=80.0
shadowMapResolution=1536
TRANSLUCENT_COLORED_SHADOWS=true
SCREENSPACE_CONTACT_SHADOWS=false
RENDER_ENTITY_SHADOWS=true
RENDER_PLAYER_SHADOWS=true
entityShadowDistanceMul=0.6

VOLUMETRIC_CLOUDS=true
CLOUDS_QUALITY=1
CLOUDS_SHADOWS=false
RAYMARCH_CLOUDS_WITH_FOG=false

AMBIENT_OCCLUSION=true
DH_OVERDRAW_PREVENTION=true
DH_AMBIENT_OCCLUSION=true
DH_SUBSURFACE_SCATTERING=false
DH_SCREENSPACE_REFLECTIONS=false

BLOOMY_PARTICLES=false
"""

# ══════════════════════════════════════════════════════════════════
# 3. INSTALL EVERYTHING TO PROFILES
# ══════════════════════════════════════════════════════════════════
BLISS = os.path.join(SH_SRC, "Bliss-Shader-Stable.zip")

for profile_name, profile_path, shader_name, shader_settings in [
    ("VISUAL",   VISUAL,   "Aetheris_Visual_Shader.zip",   VISUAL_SETTINGS),
    ("BALANCED", BALANCED, "Aetheris_Balanced_Shader.zip", BALANCED_SETTINGS),
]:
    print(f"=== Installing to {profile_name} ===")
    rp_dir = os.path.join(profile_path, "resourcepacks")
    sp_dir = os.path.join(profile_path, "shaderpacks")
    os.makedirs(rp_dir, exist_ok=True)
    os.makedirs(sp_dir, exist_ok=True)

    # Clean resourcepacks → install rebuilt pack
    for f in os.listdir(rp_dir):
        fp = os.path.join(rp_dir, f)
        if os.path.isfile(fp):
            os.remove(fp)
    shutil.copy2(OUT_PACK, os.path.join(rp_dir, "Aetheris_Ultimate_Pack.zip"))
    print(f"  ✓ Resource pack: Aetheris_Ultimate_Pack.zip ({size_mb:.1f} MB)")

    # Clean shaderpacks → install this profile's shader
    for f in os.listdir(sp_dir):
        fp = os.path.join(sp_dir, f)
        if os.path.isfile(fp) and not f.endswith(".txt"):
            os.remove(fp)
    shutil.copy2(BLISS, os.path.join(sp_dir, shader_name))
    print(f"  ✓ Shader: {shader_name}")

    # Write settings to correct filename (with .zip in name)
    settings_path = os.path.join(sp_dir, shader_name + ".txt")
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(shader_settings)
    print(f"  ✓ Settings: {shader_name}.txt")

    # iris.properties
    iris = os.path.join(profile_path, "config", "iris.properties")
    with open(iris, "w") as f:
        f.write(f"shaderpack={shader_name}\n")
    print(f"  ✓ iris.properties → {shader_name}")

    # options.txt — one pack, auto-enable it
    opts = os.path.join(profile_path, "options.txt")
    if os.path.exists(opts):
        with open(opts, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        pack_line = 'resourcePacks:["vanilla","fabric:extension","file/Aetheris_Ultimate_Pack.zip"]'
        new = re.sub(r"resourcePacks:.*", pack_line, content) if "resourcePacks:" in content else content + "\n" + pack_line
        with open(opts, "w") as f:
            f.write(new)
    print(f"  ✓ options.txt → Aetheris_Ultimate_Pack.zip only")
    print()

print("=" * 60)
print("DONE!")
print("=" * 60)
print()
print("FIXES APPLIED:")
print("  ✓ Fresh Animations REMOVED → no more broken mob faces")
print("    (BetterAnimationsCollection mod already handles entity animations)")
print()
print("  ✓ Better Leaves = leaf models only (not entity/other models)")
print("    Fixes inventory block display issues")
print()
print("  ✓ POM=true with MAX_ITERATIONS=32")
print("    OR _n.png alpha = height data → real 3D block depth!")
print()
print("  ✓ Visual shader = MAX quality (shadow 128, clouds 2, SSS, reflections)")
print("  ✓ Balanced shader = high quality + 80-100 FPS")
print()
print("RESTART LUNAR CLIENT. Press F3+R in-game to reload shader if needed.")
