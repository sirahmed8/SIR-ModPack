#!/usr/bin/env python3
"""
densify_leaves.py
Densifies leaf textures using PIL / numpy to fill transparent black holes.
Also generates denser leaf textures for Croptopia and other modded leaves.
"""
import os, shutil

try:
    from PIL import Image
    import numpy as np
    PIL_OK = True
except ImportError:
    PIL_OK = False
    print("ERROR: Pillow/numpy still not installed. Run: pip install Pillow numpy")
    exit(1)

def densify_texture(tex_path, threshold=0.30, min_neighbors=2):
    """Fill transparent pixels that are surrounded by enough opaque neighbors."""
    if not os.path.exists(tex_path):
        return False
    
    img = Image.open(tex_path).convert("RGBA")
    data = np.array(img, dtype=np.uint8)
    h, w = data.shape[:2]
    
    alpha = data[:, :, 3]
    transparent_mask = alpha < 64  # very transparent pixels
    total_transparent = np.sum(transparent_mask)
    ratio = total_transparent / (h * w)
    
    if ratio < 0.20:
        print(f"  ✓ OK (only {ratio:.0%} transparent): {os.path.basename(tex_path)}")
        return False
    
    print(f"  Densifying {os.path.basename(tex_path)} ({ratio:.0%} transparent, {h}x{w})...")
    
    new_data = data.copy()
    ys, xs = np.where(transparent_mask)
    
    fixed = 0
    for y, x in zip(ys, xs):
        neighbors_rgb = []
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if dy == 0 and dx == 0:
                    continue
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and data[ny, nx, 3] >= 128:
                    neighbors_rgb.append(data[ny, nx, :3].astype(float))
        
        if len(neighbors_rgb) >= min_neighbors:
            avg_rgb = np.mean(neighbors_rgb, axis=0)
            # Darken slightly at edges
            dist_to_center = len(neighbors_rgb) / 24.0  # max 24 neighbors in 5x5
            alpha_val = int(128 + 80 * dist_to_center)
            new_data[y, x, :3] = np.clip(avg_rgb * (0.7 + 0.3 * dist_to_center), 0, 255).astype(np.uint8)
            new_data[y, x, 3] = min(alpha_val, 220)
            fixed += 1
    
    # Backup
    backup = tex_path + ".bak"
    if not os.path.exists(backup):
        shutil.copy2(tex_path, backup)
    
    result = Image.fromarray(new_data, "RGBA")
    result.save(tex_path, "PNG", optimize=True)
    
    new_ratio = np.sum(new_data[:, :, 3] < 64) / (h * w)
    print(f"    → {ratio:.0%} → {new_ratio:.0%} transparent, filled {fixed} pixels")
    return True

pack_dir = r"D:\resource pack\MyCustomPack_Modern_32x\assets"

# Minecraft vanilla leaves
mc_leaves = [
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\oak_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\azalea_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\flowering_azalea_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\birch_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\dark_oak_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\jungle_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\acacia_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\spruce_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\cherry_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\pale_oak_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\mangrove_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\bamboo_large_leaves.png",
    r"D:\resource pack\MyCustomPack_Modern_32x\assets\minecraft\textures\block\bamboo_small_leaves.png",
]

print("=== Densifying Minecraft Leaf Textures ===")
for tex in mc_leaves:
    densify_texture(tex)

# Also densify all modded namespace leaves that are small (<1500 bytes) = sparse textures
print("\n=== Densifying Modded Namespace Leaf Textures ===")
modded_count = 0
for ns in os.listdir(pack_dir):
    if ns == "minecraft":
        continue
    tex_block = os.path.join(pack_dir, ns, "textures", "block")
    if not os.path.exists(tex_block):
        continue
    for f in os.listdir(tex_block):
        if ("leaves" in f.lower() or "leaf" in f.lower()) and f.endswith(".png") and not f.endswith("_n.png") and not f.endswith("_s.png"):
            fp = os.path.join(tex_block, f)
            if densify_texture(fp, threshold=0.20, min_neighbors=1):
                modded_count += 1

print(f"\n✅ Densified {modded_count} modded leaf textures")
print("✅ Leaf texture densification complete!")
