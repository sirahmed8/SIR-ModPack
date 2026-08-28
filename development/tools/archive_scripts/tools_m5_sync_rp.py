import os, shutil

source_rp_dir = r"D:\resource pack"
target_rp_dirs = [
    r"D:\AetherisShare\resourcepacks",
    r"D:\resourcepacks",
    r"D:\mods\resourcepacks"
]

files_to_sync = [
    "Aetheris_Ultimate_32x.zip",
    "Aetheris_Ultimate_Pack.zip",
    "Aetheris_Legacy_32x.zip",
    "MyCustomPack_Modern_32x.zip",
    "MyCustomPack_1.8.9_32x.zip",
    "Private Default.zip",
    "[1.8.9] Aetheris Legacy 32x.zip"
]

for tdir in target_rp_dirs:
    os.makedirs(tdir, exist_ok=True)
    for fname in files_to_sync:
        src = os.path.join(source_rp_dir, fname)
        dst = os.path.join(tdir, fname)
        if os.path.exists(src):
            if not os.path.exists(dst) or os.path.getsize(src) != os.path.getsize(dst):
                shutil.copy2(src, dst)
                print(f"Synced {fname} -> {tdir}")
        else:
            print(f"WARNING: Source not found: {src}")

print("Resource packs sync complete.")
