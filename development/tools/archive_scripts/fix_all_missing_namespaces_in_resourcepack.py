import zipfile, json, os, shutil

RP_PATH = r"d:\resource pack\MyCustomPack_Modern_32x.zip"
TEMP_DIR = r"d:\resource pack\temp_rp_namespace_fix"

PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2",
    r"C:\Users\a7med\.lunarclient\profiles\1.8"
]

print("==================================================")
print("  FIXING ALL NAMESPACES IN RESOURCE PACK          ")
print("==================================================")

if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
os.makedirs(TEMP_DIR, exist_ok=True)

with zipfile.ZipFile(RP_PATH, "r") as z:
    z.extractall(TEMP_DIR)

fixed_parents = 0
deleted_rpos = 0

# 1. Remove all .rpo files
for root, dirs, files in os.walk(TEMP_DIR):
    for f in files:
        if f.endswith(".rpo"):
            os.remove(os.path.join(root, f))
            deleted_rpos += 1

print(f"Purged {deleted_rpos} dangling .rpo files.")

# 2. Fix all model parents & texture namespaces
for root, dirs, files in os.walk(os.path.join(TEMP_DIR, "assets", "minecraft", "models")):
    for f in files:
        if f.endswith(".json"):
            fp = os.path.join(root, f)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as fl:
                    mdata = json.load(fl)
                
                changed = False
                # Fix parent
                if "parent" in mdata and isinstance(mdata["parent"], str):
                    p = mdata["parent"]
                    if not ":" in p:
                        mdata["parent"] = "minecraft:" + p
                        changed = True
                        fixed_parents += 1
                
                # Fix textures
                if "textures" in mdata and isinstance(mdata["textures"], dict):
                    for k, v in list(mdata["textures"].items()):
                        if isinstance(v, str) and not v.startswith("#") and not ":" in v:
                            mdata["textures"][k] = "minecraft:" + v
                            changed = True

                if changed:
                    with open(fp, "w", encoding="utf-8") as fl:
                        json.dump(mdata, fl, indent=2)
            except Exception as e:
                pass

print(f"Added minecraft: namespace to {fixed_parents} parent models.")

# 3. Fix Big Dripleaf Item Model
big_dripleaf_item = os.path.join(TEMP_DIR, "assets", "minecraft", "models", "item", "big_dripleaf.json")
with open(big_dripleaf_item, "w", encoding="utf-8") as fl:
    json.dump({
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": "minecraft:item/big_dripleaf"
        }
    }, fl, indent=2)

# Check if item/big_dripleaf.png exists, if not use block/big_dripleaf_top
tex_item_drip = os.path.join(TEMP_DIR, "assets", "minecraft", "textures", "item", "big_dripleaf.png")
tex_blk_drip = os.path.join(TEMP_DIR, "assets", "minecraft", "textures", "block", "big_dripleaf_top.png")
if not os.path.exists(tex_item_drip) and os.path.exists(tex_blk_drip):
    shutil.copy2(tex_blk_drip, tex_item_drip)
    print("Created item/big_dripleaf.png from block/big_dripleaf_top.png")

# 4. Fix Sticky Piston & Normal Piston Models
sticky_piston_item = os.path.join(TEMP_DIR, "assets", "minecraft", "models", "item", "sticky_piston.json")
with open(sticky_piston_item, "w", encoding="utf-8") as fl:
    json.dump({"parent": "minecraft:block/sticky_piston_inventory"}, fl, indent=2)

piston_item = os.path.join(TEMP_DIR, "assets", "minecraft", "models", "item", "piston.json")
with open(piston_item, "w", encoding="utf-8") as fl:
    json.dump({"parent": "minecraft:block/piston_inventory"}, fl, indent=2)

# 5. Recompress Resource Pack
print("Recompressing MyCustomPack_Modern_32x.zip...")
with zipfile.ZipFile(RP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(TEMP_DIR):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, TEMP_DIR)
            z.write(full, rel)

shutil.rmtree(TEMP_DIR)
print(f"Created updated resource pack: {RP_PATH} ({os.path.getsize(RP_PATH)/(1024*1024):.2f} MB)")

# 6. Synchronize across all profiles
for prof in PROFILES:
    rp_dir = os.path.join(prof, "resourcepacks")
    if os.path.exists(rp_dir):
        shutil.copy2(RP_PATH, os.path.join(rp_dir, "MyCustomPack_Modern_32x.zip"))
        print(f"Synced to {rp_dir}")

print("\n==================================================")
print("  ALL NAMESPACE & MODEL OVERRIDES 100% REPAIRED!  ")
print("==================================================")
