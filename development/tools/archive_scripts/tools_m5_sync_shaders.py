import os, hashlib, shutil

def hash_file(p):
    if not os.path.exists(p): return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

shader_src = r"D:\shader"
share_shaders = r"D:\AetherisShare\shaders"
os.makedirs(share_shaders, exist_ok=True)

files_to_sync = [
    "Aetheris_Visual_Shader.zip",
    "Aetheris_Visual_Shader.zip.txt",
    "Aetheris_Balanced_Shader.zip",
    "Aetheris_Balanced_Shader.zip.txt",
    "Aetheris_Extreme_Shader.zip",
    "Aetheris_Extreme_Shader.zip.txt",
    "Aetheris_Shader_Pack.zip",
    "Aetheris_Shader_Pack.zip.txt",
    "Aetheris_Legacy_Shader_Pack.zip",
    "Aetheris_Legacy_Shader_Pack.zip.txt"
]

for fname in files_to_sync:
    src = os.path.join(shader_src, fname)
    dst = os.path.join(share_shaders, fname)
    if os.path.exists(src):
        src_h = hash_file(src)
        dst_h = hash_file(dst)
        if src_h != dst_h:
            shutil.copy2(src, dst)
            print(f"Updated {fname} in D:\\AetherisShare\\shaders")
        else:
            print(f"Match: {fname} ({src_h[:8]})")
    else:
        print(f"WARNING: Source not found for {fname}")
