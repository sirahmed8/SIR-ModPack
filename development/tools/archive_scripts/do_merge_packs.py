"""
Aetheris Ultimate - Smart Resource Pack Merger
Intelligently merges the best content from available packs into our custom pack.
"""

import os
import zipfile
import shutil

PACK_DIR = r"D:\resource pack\MyCustomPack_Modern_32x"
PACKS_SOURCE = r"D:\resource pack"
TEMP = r"D:\shader\_temp_merge"

print("=" * 60)
print("AETHERIS ULTIMATE - SMART RESOURCE PACK MERGER")
print("=" * 60)

merged_count = 0

# ─────────────────────────────────────────────────────────────
# 1. DRAMATIC SKYS - Moon phase textures (beautiful!)
#    Keep: improved moon phases (8 phases vs vanilla 1)
#    Skip: celestial sky definitions (could conflict with shader)
# ─────────────────────────────────────────────────────────────
print("\n[1/3] Merging Dramatic Skys moon textures...")
dramatic_path = os.path.join(PACKS_SOURCE, "Dramatic Skys Demo 1.5.3.36.5.zip")

if os.path.exists(dramatic_path):
    with zipfile.ZipFile(dramatic_path, 'r') as z:
        all_names = z.namelist()
        # Only grab moon textures - these work with shaders perfectly
        moon_files = [n for n in all_names if
                      'moon' in n.lower() and n.endswith('.png') and
                      'assets/minecraft' in n]

        for member in moon_files:
            # Convert path: assets/minecraft/textures/environment/celestial/moon/full_moon.png
            # -> assets/minecraft/textures/environment/moon_phases.png (original)
            # Actually we want to keep the beautiful individual phases
            data = z.read(member)
            rel_path = member  # Keep full path structure
            dest = os.path.join(PACK_DIR, rel_path.replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(data)
            print(f"  + {rel_path}")
            merged_count += 1

        # Also grab clouds texture (improved clouds)
        cloud_files = [n for n in all_names if 'clouds.png' in n.lower() and 'assets/minecraft' in n]
        for member in cloud_files:
            data = z.read(member)
            rel_path = member
            dest = os.path.join(PACK_DIR, rel_path.replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(data)
            print(f"  + {rel_path}")
            merged_count += 1

    print(f"  ✅ Merged {merged_count} Dramatic Skys assets")
else:
    print(f"  [SKIP] {dramatic_path} not found")

# ─────────────────────────────────────────────────────────────
# 2. VANILLA EXPERIENCE+ - Merge improved vanilla textures
#    Take: textures, models (block/item improvements)
#    Skip: conflicting items already in our pack
# ─────────────────────────────────────────────────────────────
print("\n[2/3] Merging Vanilla Experience+ textures...")
vanilla_path = None
for f in os.listdir(PACKS_SOURCE):
    if 'Vanilla Experience' in f and f.endswith('.zip'):
        vanilla_path = os.path.join(PACKS_SOURCE, f)
        break

vanilla_merged = 0
if vanilla_path and os.path.exists(vanilla_path):
    with zipfile.ZipFile(vanilla_path, 'r') as z:
        all_names = z.namelist()

        # Key assets worth merging (not in subdirectory versions - those are for older versions)
        # Take from the root 'assets/' path (latest 26.2 compatible)
        good_files = []
        for name in all_names:
            # Skip the versioned subdirectories (1.21.11/, 1.21.11-26.1.2/)
            if name.startswith('1.') or name.startswith('assets/respackopts'):
                continue
            if not name.startswith('assets/'):
                continue
            # Take textures and models (not optifine CEM - it's for entities, handled by FreshAnim)
            if name.endswith('.png') or name.endswith('.json'):
                if 'optifine/cem' not in name:  # Skip OptiFine CEM, we handle separately
                    good_files.append(name)

        print(f"  Found {len(good_files)} files to potentially merge")

        # Merge but DON'T overwrite existing higher-quality 32x textures we made
        # Only add files that don't exist in our pack OR add new content
        for member in good_files:
            dest = os.path.join(PACK_DIR, member.replace('/', os.sep))

            # Block list - things we DON'T want to overwrite from vanilla experience
            skip_keywords = [
                'leaves',  # We fixed leaves already
                'water',   # Our water is custom
                'lava',    # Custom
                'fire',    # Custom
            ]

            basename = os.path.basename(member)
            should_skip = any(kw in basename.lower() for kw in skip_keywords)

            if should_skip:
                continue

            # Only merge if destination doesn't exist (don't override our 32x textures)
            if not os.path.exists(dest):
                data = z.read(member)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, 'wb') as f:
                    f.write(data)
                vanilla_merged += 1

    print(f"  ✅ Added {vanilla_merged} new assets from Vanilla Experience+")
    merged_count += vanilla_merged
else:
    print(f"  [SKIP] Vanilla Experience+ not found")

# ─────────────────────────────────────────────────────────────
# 3. FRESH ANIMATIONS - Add OptiFine CEM entity animations
#    These work with Entity Model Features (EMF) mod on Fabric
#    They give mobs smooth and realistic animations!
# ─────────────────────────────────────────────────────────────
print("\n[3/3] Merging FreshAnimations entity animations...")
fresh_path = os.path.join(PACKS_SOURCE, "FreshAnimations_v1.10.5.zip")
fresh_merged = 0

if os.path.exists(fresh_path):
    with zipfile.ZipFile(fresh_path, 'r') as z:
        all_names = z.namelist()

        # FreshAnimations uses optifine/cem/ folder
        # With EMF mod installed, this works natively in Fabric
        anim_files = [n for n in all_names if
                      ('optifine/cem' in n or 'cem/' in n) and
                      (n.endswith('.jem') or n.endswith('.jpm') or n.endswith('.png'))]

        print(f"  Found {len(anim_files)} animation files")

        for member in anim_files:
            data = z.read(member)
            dest = os.path.join(PACK_DIR, member.replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(data)
            fresh_merged += 1

    print(f"  ✅ Merged {fresh_merged} FreshAnimations files")
    merged_count += fresh_merged
else:
    print(f"  [SKIP] {fresh_path} not found")

# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"MERGE COMPLETE! Total new assets added: {merged_count}")
print(f"Pack directory: {PACK_DIR}")
print("=" * 60)

# Show what's now in our pack
total = sum(len(files) for _, _, files in os.walk(PACK_DIR))
print(f"Total files in pack now: {total}")
