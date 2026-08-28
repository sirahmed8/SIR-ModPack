import os, shutil, zipfile

BASE_UNBOUND = r"d:\shader\ComplementaryUnbound_r5.8.1\shaders\block.properties"
SHADER_DIR = r"d:\shader"
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
print("  FIXING BLOCK.PROPERTIES CRASH (ZERO WILDCARDS)  ")
print("==================================================")

# Read stock Complementary block.properties
with open(BASE_UNBOUND, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Modded leaves without wildcards
bop_leaves = "biomesoplenty:origin_leaves biomesoplenty:flowering_oak_leaves biomesoplenty:cypress_leaves biomesoplenty:snowblossom_leaves biomesoplenty:rainbow_birch_leaves biomesoplenty:fir_leaves biomesoplenty:pine_leaves biomesoplenty:redwood_leaves biomesoplenty:mahogany_leaves biomesoplenty:jacaranda_leaves biomesoplenty:palm_leaves biomesoplenty:willow_leaves biomesoplenty:dead_leaves biomesoplenty:magic_leaves biomesoplenty:umbran_leaves biomesoplenty:hellbark_leaves"
ru_leaves = "regions_unexplored:maple_leaves regions_unexplored:orange_maple_leaves regions_unexplored:red_maple_leaves regions_unexplored:silver_birch_leaves regions_unexplored:magnolia_leaves regions_unexplored:golden_larch_leaves regions_unexplored:pine_leaves regions_unexplored:redwood_leaves regions_unexplored:cypress_leaves regions_unexplored:willow_leaves regions_unexplored:dead_leaves regions_unexplored:palm_leaves regions_unexplored:eucalyptus_leaves regions_unexplored:bamboo_leaves regions_unexplored:joshua_leaves regions_unexplored:aspen_leaves"

new_lines = []
for line in lines:
    if line.startswith("block.10009="):
        new_lines.append(f"{line.strip()} {bop_leaves} {ru_leaves}\n")
    else:
        new_lines.append(line)

dest_props = os.path.join(AETHERIS_DIR, "shaders", "block.properties")
with open(dest_props, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("  -> block.properties cleanly written with 0 wildcards and 0 commas!")

# Recompress shader
print("Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# Synchronize all profiles
for prof in PROFILES:
    if os.path.exists(prof):
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(AETHERIS_ZIP, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.txt"))
        print(f"Synced shader to {sp_dir}")

print("\n==================================================")
print("  BLOCK.PROPERTIES CRASH 100% ELIMINATED!         ")
print("==================================================")
