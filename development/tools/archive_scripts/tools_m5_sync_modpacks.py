import os, zipfile, json, shutil

modpack_dir = r"D:\AetherisShare\modpacks"
os.makedirs(modpack_dir, exist_ok=True)

# Copy Legacy Modpack
src_legacy = r"D:\mods\Aetheris_Modpack_Legacy_1.8.9.zip"
dst_legacy = os.path.join(modpack_dir, "Aetheris_Modpack_Legacy_1.8.9.zip")
if os.path.exists(src_legacy):
    if not os.path.exists(dst_legacy) or os.path.getsize(src_legacy) != os.path.getsize(dst_legacy):
        shutil.copy2(src_legacy, dst_legacy)
        print(f"Copied {src_legacy} -> {dst_legacy}")
    else:
        print(f"Legacy modpack up-to-date in {dst_legacy}")

# Build Modern 26.2 Modpack if not exists or needs update
modern_zip_path = r"D:\mods\Aetheris_Modpack_Modern_26.2.zip"
dst_modern = os.path.join(modpack_dir, "Aetheris_Modpack_Modern_26.2.zip")

print("Building Modern 26.2 Modpack Archive...")
profile_src = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"

with zipfile.ZipFile(modern_zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    # 1. Add all 252 mods from D:\mods
    for f in sorted(os.listdir(r"D:\mods")):
        if f.endswith(".jar"):
            p = os.path.join(r"D:\mods", f)
            z.write(p, f"mods/{f}")
    
    # 2. Add config directory
    cfg_dir = os.path.join(profile_src, "config")
    if os.path.exists(cfg_dir):
        for root, dirs, files in os.walk(cfg_dir):
            for f in files:
                p = os.path.join(root, f)
                rel = os.path.relpath(p, cfg_dir)
                z.write(p, f"config/{rel}")
                
    # 3. Add shaderpacks
    for sf in ["Aetheris_Visual_Shader.zip", "Aetheris_Visual_Shader.zip.txt", 
               "Aetheris_Balanced_Shader.zip", "Aetheris_Balanced_Shader.zip.txt",
               "Aetheris_Shader_Pack.zip", "Aetheris_Shader_Pack.zip.txt"]:
        sp = os.path.join(r"D:\shader", sf)
        if os.path.exists(sp):
            z.write(sp, f"shaderpacks/{sf}")
            
    # 4. Add resourcepacks
    for rf in ["Aetheris_Ultimate_32x.zip", "Aetheris_Ultimate_Pack.zip", "MyCustomPack_Modern_32x.zip"]:
        rp = os.path.join(r"D:\resourcepacks", rf)
        if os.path.exists(rp):
            z.write(rp, f"resourcepacks/{rf}")
            
    # 5. Add root options and settings
    for opt in ["options.txt", "optionsLC.txt", "jvm-options.txt"]:
        op = os.path.join(profile_src, opt)
        if os.path.exists(op):
            z.write(op, opt)
            
    # sodium-options.json
    sod = os.path.join(profile_src, "config", "sodium-options.json")
    if os.path.exists(sod):
        z.write(sod, "sodium-options.json")
        
    # iris.properties
    iris = os.path.join(profile_src, "config", "iris.properties")
    if os.path.exists(iris):
        z.write(iris, "iris.properties")
        
    # mmc-pack.json for Prism/MultiMC import
    mmc_pack = {
        "components": [
            {
                "cachedName": "Minecraft",
                "cachedVersion": "26.2",
                "important": True,
                "uid": "net.minecraft",
                "version": "26.2"
            },
            {
                "cachedName": "Fabric Loader",
                "cachedVersion": "0.16.10",
                "important": True,
                "uid": "net.fabricmc.fabric-loader",
                "version": "0.16.10"
            }
        ],
        "formatVersion": 1
    }
    z.writestr("mmc-pack.json", json.dumps(mmc_pack, indent=2))
    
    instance_cfg = (
        "[General]\n"
        "ConfigVersion=1.3\n"
        "InstanceType=OneSix\n"
        "iconKey=default\n"
        "name=Aetheris Modern 26.2\n"
        "OverrideMemory=true\n"
        "MinMemAlloc=4096\n"
        "MaxMemAlloc=8192\n"
        "OverrideJavaArgs=true\n"
        "JvmArgs=-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -XX:+OptimizeStringConcat -XX:+UseStringDeduplication -Djava.net.preferIPv4Stack=true -Dfile.encoding=UTF-8\n"
    )
    z.writestr("instance.cfg", instance_cfg)

shutil.copy2(modern_zip_path, dst_modern)
print(f"Created and synced {dst_modern} ({os.path.getsize(dst_modern):,} bytes)")
