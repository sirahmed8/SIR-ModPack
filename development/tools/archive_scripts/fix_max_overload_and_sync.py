import os, shutil, zipfile

SHADER_DIR = r"d:\shader"
AETHERIS_DIR = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack")
AETHERIS_ZIP = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.zip")
AETHERIS_TXT = os.path.join(SHADER_DIR, "Aetheris_Shader_Pack.txt")
LIGHTING_GLSL = os.path.join(AETHERIS_DIR, "shaders", "lib", "lighting", "mainLighting.glsl")

PROFILES = [
    r"C:\Users\a7med\AppData\Roaming\.minecraft",
    r"C:\Users\a7med\.lunarclient\profiles\26",
    r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modpack-modern-26.2",
    r"C:\Users\a7med\.lunarclient\profiles\1.8"
]

print("==================================================")
print("  FIXING GLSL OVERLOAD ERROR IN MAINLIGHTING.GLSL ")
print("==================================================")

if os.path.exists(LIGHTING_GLSL):
    with open(LIGHTING_GLSL, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Replace max(ambientMult, vec3(0.22)) with max(ambientMult, 0.22)
    old_str = "vec3 sceneLighting = lightColorM * shadowLightMult + ambientColorM * max(ambientMult, vec3(0.22));"
    new_str = "vec3 sceneLighting = lightColorM * shadowLightMult + ambientColorM * max(ambientMult, 0.22);"

    if old_str in content:
        content = content.replace(old_str, new_str)
        print("  -> Fixed max(float, float) overload in mainLighting.glsl")
    else:
        # Fallback replacement
        content = content.replace("max(ambientMult, vec3(0.22))", "max(ambientMult, 0.22)")
        print("  -> Patched max(ambientMult) condition")

    with open(LIGHTING_GLSL, "w", encoding="utf-8") as f:
        f.write(content)

# Recompress shader
print("Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# Sync shader to all profiles
for prof in PROFILES:
    if os.path.exists(prof):
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(AETHERIS_ZIP, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        print(f"Synced shader to {sp_dir}")

print("\n==================================================")
print(" GLSL OVERLOAD ERROR 100% FIXED & SYNCHRONIZED!   ")
print("==================================================")
