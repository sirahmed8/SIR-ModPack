"""
rebuild_share.py  — Rebuilds D:\AetherisShare with all latest files
"""
import os, shutil, json, zipfile

VISUAL   = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
BALANCED = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2"
LEGACY   = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9"
SHARE    = r"D:\AetherisShare"
BUILT    = r"D:\mods\built"

# Wipe and recreate
if os.path.exists(SHARE):
    shutil.rmtree(SHARE)
os.makedirs(SHARE)

def cp(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    sz = os.path.getsize(dst) / 1024 / 1024
    print("  + " + os.path.relpath(dst, SHARE) + " (" + str(round(sz,1)) + "MB)")

print("Building AetherisShare...")

# ── SHADERS ──────────────────────────────────────────────────────
print("\n[Shaders]")
for shader in ["Aetheris_Visual_Shader.zip", "Aetheris_Balanced_Shader.zip",
               "Aetheris_Extreme_Shader.zip", "Aetheris_LPV_Shader.zip"]:
    src = os.path.join(VISUAL, "shaderpacks", shader)
    if not os.path.exists(src):
        src = os.path.join(BALANCED, "shaderpacks", shader)
    if os.path.exists(src):
        cp(src, os.path.join(SHARE, "shaders", shader))
        # Also copy the settings file
        st = src + ".txt"
        if os.path.exists(st):
            cp(st, os.path.join(SHARE, "shaders", shader + ".txt"))

# ── RESOURCE PACK ────────────────────────────────────────────────
print("\n[Resource Pack]")
pack = os.path.join(VISUAL, "resourcepacks", "Aetheris_Ultimate_Pack.zip")
if os.path.exists(pack):
    cp(pack, os.path.join(SHARE, "resourcepacks", "Aetheris_Ultimate_Pack.zip"))

leg_pack = os.path.join(LEGACY, "resourcepacks")
if os.path.exists(leg_pack):
    for f in os.listdir(leg_pack):
        if f.endswith(".zip"):
            cp(os.path.join(leg_pack, f), os.path.join(SHARE, "resourcepacks", f))

# ── PROFILE CONFIGS ──────────────────────────────────────────────
print("\n[Profile Configs]")
for profile_name, profile_path in [
    ("visual", VISUAL), ("balanced", BALANCED), ("legacy", LEGACY)
]:
    out = os.path.join(SHARE, "profiles", profile_name)
    os.makedirs(out, exist_ok=True)

    # profile.json
    pj = os.path.join(profile_path, "profile.json")
    if os.path.exists(pj):
        cp(pj, os.path.join(out, "profile.json"))

    # key configs
    for cfg_rel in ["config/c2me.toml", "config/lithium.properties",
                    "config/sodium-options.json", "config/iris.properties",
                    "options.txt"]:
        src = os.path.join(profile_path, cfg_rel)
        if os.path.exists(src):
            cp(src, os.path.join(out, cfg_rel))

# ── README ───────────────────────────────────────────────────────
print("\n[README]")
README = """\
# 🌌 AETHERIS ULTIMATE SHARE PACKAGE
Built: 2026-08-19 | RTX 4050 Laptop / i7-13650HX / 24GB DDR5 / 1080p

## Contents

### /shaders/
| File | Profile | FPS | Notes |
|---|---|---|---|
| Aetheris_Visual_Shader.zip | Visual PRIMARY | 60-80 | Max quality, POM, SSR, Seasons, HDR |
| Aetheris_LPV_Shader.zip | Visual optional | 30-50 | Voxel GI — torch glow on walls |
| Aetheris_Balanced_Shader.zip | Balanced PRIMARY | 80-100 | High quality + fast |
| Aetheris_Extreme_Shader.zip | Balanced optional | 30-60 | Ultra max screenshots |

Each shader has a matching .txt settings file (Iris reads these automatically).

### /resourcepacks/
- **Aetheris_Ultimate_Pack.zip** — Optimum Realism 64x + Better Leaves merged
  - 1419 normal maps, 1444 specular maps, 3D blocks, CTM connected textures
- **[1.8.9] Aetheris Legacy 32x.zip** — Legacy PvP pack

### /profiles/
Config files for each profile. Copy to your Lunar profile folder.

## Installation
1. Copy shaderpacks to: `.lunarclient/profiles/[profile]/shaderpacks/`
2. Copy resourcepacks to: `.lunarclient/profiles/[profile]/resourcepacks/`
3. In Iris: Esc → Options → Video Settings → Shader Packs
4. Switch between shaders anytime without restarting

## Switching Shaders In-Game
`Esc → Options → Video Settings → Shader Packs`
All shaders are pre-configured for RTX 4050 @ 1080p.

## Features Active
- ✅ HDR Auto-Exposure (cave ↔ sun eye adaptation)
- ✅ POM 3D block depth (OR normal maps)
- ✅ Dappled leaf sunlight (TRANSLUCENT_COLORED_SHADOWS)
- ✅ PBR Specular Reflections (1444 OR specular maps)
- ✅ Material AO (1419 OR normal maps)
- ✅ Dynamic Seasons + Biome Environments
- ✅ HD Moon (Optimum Realism RESOURCEPACK_SKY=1)
- 🌟 LPV ONLY: Torch/lava/ore voxel GI (73 emissive blocks mapped)
"""
with open(os.path.join(SHARE, "README.md"), "w", encoding="utf-8") as f:
    f.write(README)
print("  + README.md")

# Summary
total = sum(os.path.getsize(os.path.join(r,f))
            for r,_,fs in os.walk(SHARE) for f in fs)
print()
print("=" * 50)
print("AetherisShare rebuilt: " + str(round(total/1024/1024/1024, 2)) + " GB")
print(SHARE)
