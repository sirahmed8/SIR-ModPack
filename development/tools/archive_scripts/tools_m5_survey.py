import shutil, os

src = r"D:\shader\Aetheris_Legacy_Shader_Pack.zip"
targets = [
    r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\1.8.9\minecraft\shaderpacks\Aetheris_Legacy_Shader_Pack.zip",
    r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 1.8.9\.minecraft\shaderpacks\Aetheris_Legacy_Shader_Pack.zip",
    r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\1.8.9\.minecraft\shaderpacks\Aetheris_Legacy_Shader_Pack.zip",
    r"C:\Users\a7med\AppData\Roaming\PrismLauncher\instances\Minecraft 1.8.9\minecraft\shaderpacks\Aetheris_Legacy_Shader_Pack.zip"
]

for t in targets:
    if os.path.exists(os.path.dirname(t)):
        shutil.copy2(src, t)
        print(f"Copied to {t}")
