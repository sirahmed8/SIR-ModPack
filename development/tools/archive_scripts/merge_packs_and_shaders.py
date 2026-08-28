"""
Aetheris Ultimate - Resource Pack & Shader Merger
Merges the best content from other resource packs and shaders into our custom pack/shader.
"""

import os
import zipfile
import shutil
import json

PACK_DIR = r"D:\resource pack\MyCustomPack_Modern_32x"
SHADER_DIR = r"D:\shader\Aetheris_Shader_Pack"
PACKS_SOURCE = r"D:\resource pack"
SHADERS_SOURCE = r"D:\shader"
TEMP = r"D:\shader\_temp_merge"

os.makedirs(TEMP, exist_ok=True)

print("=" * 60)
print("AETHERIS ULTIMATE - PACK & SHADER MERGER")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# 1. DRAMATIC SKYS - Extract sky panorama backgrounds
# ─────────────────────────────────────────────────────────────
print("\n[1/4] Processing Dramatic Skys...")
dramatic_path = os.path.join(PACKS_SOURCE, "Dramatic Skys Demo 1.5.3.36.5.zip")
dramatic_temp = os.path.join(TEMP, "dramatic_skys")
os.makedirs(dramatic_temp, exist_ok=True)

if os.path.exists(dramatic_path):
    with zipfile.ZipFile(dramatic_path, 'r') as z:
        all_names = z.namelist()
        sky_files = [n for n in all_names if
                     'panorama' in n.lower() or
                     'sky' in n.lower() or
                     'environment' in n.lower() or
                     'background' in n.lower() or
                     n.endswith('.png') and ('title' in n.lower() or 'clouds' in n.lower())]

        print(f"  Found {len(sky_files)} sky/panorama files in Dramatic Skys")
        for f in sky_files[:20]:  # Show first 20
            print(f"    {f}")

        # Extract ALL png files from the pack for analysis
        png_files = [n for n in all_names if n.endswith('.png')]
        print(f"\n  Total PNG files: {len(png_files)}")
        print("  Sample files:")
        for f in png_files[:30]:
            print(f"    {f}")

        # Extract the good sky/panorama assets
        sky_dest_dirs = ['title', 'panorama', 'sky', 'environment', 'clouds']
        merged = 0
        for member in all_names:
            lower = member.lower()
            if any(d in lower for d in sky_dest_dirs) and member.endswith('.png'):
                try:
                    z.extract(member, dramatic_temp)
                    merged += 1
                except Exception as e:
                    pass
        print(f"  Extracted {merged} sky assets for review")
else:
    print(f"  [SKIP] File not found: {dramatic_path}")

# ─────────────────────────────────────────────────────────────
# 2. VANILLA EXPERIENCE+ - Extract vanilla improvements
# ─────────────────────────────────────────────────────────────
print("\n[2/4] Processing Vanilla Experience+...")
vanilla_path = None
for f in os.listdir(PACKS_SOURCE):
    if 'Vanilla Experience' in f and f.endswith('.zip'):
        vanilla_path = os.path.join(PACKS_SOURCE, f)
        break

if vanilla_path and os.path.exists(vanilla_path):
    vanilla_temp = os.path.join(TEMP, "vanilla_exp")
    os.makedirs(vanilla_temp, exist_ok=True)

    with zipfile.ZipFile(vanilla_path, 'r') as z:
        all_names = z.namelist()
        print(f"  Total files: {len(all_names)}")

        # Show structure
        dirs = set()
        for name in all_names:
            parts = name.split('/')
            if len(parts) > 1:
                dirs.add('/'.join(parts[:3]))
        print("  Directory structure (first 30):")
        for d in sorted(dirs)[:30]:
            print(f"    {d}")

        # Extract ALL assets to temp for selective merging
        z.extractall(vanilla_temp)
        print(f"  Extracted to: {vanilla_temp}")
else:
    print(f"  [SKIP] Vanilla Experience+ not found")

# ─────────────────────────────────────────────────────────────
# 3. FRESH ANIMATIONS - Extract entity animations
# ─────────────────────────────────────────────────────────────
print("\n[3/4] Processing FreshAnimations...")
fresh_path = os.path.join(PACKS_SOURCE, "FreshAnimations_v1.10.5.zip")
fresh_temp = os.path.join(TEMP, "fresh_anims")
os.makedirs(fresh_temp, exist_ok=True)

if os.path.exists(fresh_path):
    with zipfile.ZipFile(fresh_path, 'r') as z:
        all_names = z.namelist()
        print(f"  Total files: {len(all_names)}")
        # FreshAnimations uses OptiFine CEM format
        jem_files = [n for n in all_names if n.endswith('.jem') or n.endswith('.jpm')]
        png_files = [n for n in all_names if n.endswith('.png')]
        print(f"  JEM/JPM animation files: {len(jem_files)}")
        print(f"  PNG texture files: {len(png_files)}")
        print("  Sample JEM files:")
        for f in jem_files[:15]:
            print(f"    {f}")
        z.extractall(fresh_temp)
        print(f"  Extracted to: {fresh_temp}")
else:
    print(f"  [SKIP] FreshAnimations not found")

# ─────────────────────────────────────────────────────────────
# 4. SHADER ANALYSIS - Best techniques to cherry-pick
# ─────────────────────────────────────────────────────────────
print("\n[4/4] Analyzing shaders for cherry-picking...")

shaders_to_check = [
    ("Complementary+Euphoria", "ComplementaryUnbound_r5.8.1 + EuphoriaPatches_1.9.3.zip"),
    ("BSL", "BSL_v10.1.3.zip"),
    ("Bliss Stable", "Bliss-Shader-Stable.zip"),
    ("Solas", "Solas Shader V3.7.zip"),
]

for name, filename in shaders_to_check:
    path = os.path.join(SHADERS_SOURCE, filename)
    if os.path.exists(path):
        with zipfile.ZipFile(path, 'r') as z:
            all_names = z.namelist()
            glsl_files = [n for n in all_names if n.endswith('.glsl') or n.endswith('.fsh') or n.endswith('.vsh')]
            print(f"\n  {name}: {len(glsl_files)} GLSL files")

            # Key files we want to study
            key_files = ['water', 'cloud', 'fog', 'sky', 'sun', 'shadow', 'bloom', 'dof', 'motion']
            interesting = [f for f in glsl_files if any(k in f.lower() for k in key_files)]
            print(f"  Interesting files ({len(interesting)}):")
            for f in interesting[:10]:
                print(f"    {f}")
    else:
        print(f"  [{name}] File not found: {path}")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE!")
print(f"Temp files extracted to: {TEMP}")
print("=" * 60)
