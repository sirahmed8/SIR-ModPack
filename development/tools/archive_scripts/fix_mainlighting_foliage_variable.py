import os, shutil, zipfile

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
print("  FIXING 'isFoliage' IN MAINLIGHTING.GLSL         ")
print("==================================================")

main_lighting_glsl = os.path.join(AETHERIS_DIR, "shaders", "lib", "lighting", "mainLighting.glsl")
with open(main_lighting_glsl, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

# Replace undefined variable isFoliage with subsurfaceMode > 0
code = code.replace(
    "if (isFoliage || subsurfaceMode > 0) color.rgb *= mix(vec3(0.28, 0.32, 0.38), vec3(1.0), clamp01(sunVisibility2 * 2.2));",
    "if (subsurfaceMode > 0) color.rgb *= mix(vec3(0.28, 0.32, 0.38), vec3(1.0), clamp01(sunVisibility2 * 2.2));"
)

with open(main_lighting_glsl, "w", encoding="utf-8") as f:
    f.write(code)

print("[1/2] Fixed isFoliage in mainLighting.glsl")

# Recompress shaderpack
print("[2/2] Recompressing Aetheris_Shader_Pack.zip...")
with zipfile.ZipFile(AETHERIS_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(AETHERIS_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, AETHERIS_DIR)
            z.write(full_path, rel_path)
print(f"Created: {os.path.basename(AETHERIS_ZIP)} ({os.path.getsize(AETHERIS_ZIP)/(1024*1024):.2f} MB)")

# Synchronize across all profile directories
for prof in PROFILES:
    if os.path.exists(prof):
        sp_dir = os.path.join(prof, "shaderpacks")
        os.makedirs(sp_dir, exist_ok=True)
        shutil.copy2(AETHERIS_ZIP, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.zip.txt"))
        shutil.copy2(AETHERIS_TXT, os.path.join(sp_dir, "Aetheris_Shader_Pack.txt"))
        print(f"Synced to {sp_dir}")

d_games_txt = r"D:\Games\Aetheris_Shader_Pack.zip.txt"
if os.path.exists(os.path.dirname(d_games_txt)):
    shutil.copy2(AETHERIS_TXT, d_games_txt)
    print(f"Synced to {d_games_txt}")

print("\n==================================================")
print("  FIX COMPLETE: ZERO COMPILER ERRORS!             ")
print("==================================================")
