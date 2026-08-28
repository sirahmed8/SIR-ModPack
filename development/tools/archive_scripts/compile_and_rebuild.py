import os, subprocess, shutil, zipfile, json, struct, zlib

BASE_DIR = r"d:\mods"
SRC_DIR = os.path.join(BASE_DIR, "src")
BUILD_DIR = os.path.join(BASE_DIR, "build_mod")
JAVAC = r"C:\Program Files\Java\jdk-17\bin\javac.exe"
MOD_JAR_NAME = "AetherisCore-fabric-26.2.jar"
MOD_JAR_PATH = os.path.join(BASE_DIR, MOD_JAR_NAME)

print("==================================================")
print("     COMPILING AETHERIS CORE CUSTOM FABRIC MOD    ")
print("==================================================")

# Clean build dir
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)
os.makedirs(BUILD_DIR, exist_ok=True)

# 1. Compile Java sources
java_files = []
for root, dirs, files in os.walk(os.path.join(SRC_DIR, "net")):
    for f in files:
        if f.endswith(".java"):
            java_files.append(os.path.join(root, f))

print(f"Compiling {len(java_files)} Java source files with JDK 17...")
cmd = [JAVAC, "-d", BUILD_DIR, "-source", "17", "-target", "17"] + java_files
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("Compilation error:")
    print(res.stderr)
    exit(1)
print("Compilation SUCCESSFUL! Bytecode generated.")

# 2. Copy fabric.mod.json
shutil.copy2(os.path.join(SRC_DIR, "fabric.mod.json"), os.path.join(BUILD_DIR, "fabric.mod.json"))

# 3. Create a minimal 64x64 PNG icon for Aetheris Core
icon_dir = os.path.join(BUILD_DIR, "assets", "aetheris_core")
os.makedirs(icon_dir, exist_ok=True)

def create_simple_png(path, width=64, height=64, color=(56, 189, 248)): # Aetheris Cyan
    # Construct minimal uncompressed PNG
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    
    header = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) # 8-bit RGB
    
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0) # Filter type 0
        for x in range(width):
            # Gradient circle pattern
            dx = x - width // 2
            dy = y - height // 2
            dist = (dx*dx + dy*dy)**0.5
            if dist < width // 2 - 2:
                raw_data.extend(bytes(color))
            else:
                raw_data.extend(bytes([15, 23, 42])) # Dark border
                
    idat = chunk(b"IDAT", zlib.compress(bytes(raw_data)))
    iend = chunk(b"IEND", b"")
    
    with open(path, "wb") as f:
        f.write(header + ihdr + idat + iend)

create_simple_png(os.path.join(icon_dir, "icon.png"))
print("Generated Aetheris Core icon asset.")

# 4. Package JAR
with zipfile.ZipFile(MOD_JAR_PATH, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(BUILD_DIR):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, BUILD_DIR)
            z.write(full, rel)

jar_size_kb = os.path.getsize(MOD_JAR_PATH) / 1024
print(f"Created custom mod: {MOD_JAR_NAME} ({jar_size_kb:.1f} KB)")

# 5. Distribute AetherisCore jar to all relevant locations
dests = [
    os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2"),
    r"C:\Users\a7med\.lunarclient\profiles\26\mods\fabric-26.2",
    r"C:\Users\a7med\AppData\Roaming\.minecraft\mods"
]
for dst_dir in dests:
    if os.path.exists(dst_dir):
        shutil.copy2(MOD_JAR_PATH, os.path.join(dst_dir, MOD_JAR_NAME))
        print(f"  -> Deployed AetherisCore to {dst_dir}")

# 6. Rebuild Modrinth .mrpack with 100% OFFLINE / LOCAL OVERRIDES
print("\n[REBUILD] Creating 100% Offline-Compatible Modrinth .mrpack...")
MRPACK_FILE = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.mrpack")

# modrinth.index.json with NO external download URLs (all inside overrides for 0% stall fix)
mrpack_index = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": "2.0.0-godtier",
    "name": "Aetheris Ultimate Modpack (Modern 26.2)",
    "summary": "100% Offline-Ready God-Tier Fabric 26.2 Modpack with Aetheris Core, Shader & Resource Pack Synergy.",
    "files": [],
    "dependencies": {
        "fabric-loader": "0.157.0",
        "minecraft": "26.2"
    }
}

with zipfile.ZipFile(MRPACK_FILE, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    # Write index
    z.writestr("modrinth.index.json", json.dumps(mrpack_index, indent=2))
    
    # Write all mods into overrides/mods/
    modern_mods = [f for f in os.listdir(BASE_DIR) if f.endswith(".jar")]
    for m in modern_mods:
        mpath = os.path.join(BASE_DIR, m)
        z.write(mpath, f"overrides/mods/{m}")
    
    # Write dependencies folder into overrides/mods/dependencies/
    dep_dir = os.path.join(BASE_DIR, "dependencies")
    if os.path.exists(dep_dir):
        for root, dirs, files in os.walk(dep_dir):
            for f in files:
                fpath = os.path.join(root, f)
                rel = os.path.relpath(fpath, BASE_DIR)
                z.write(fpath, f"overrides/{rel}")
                
    # Write configs into overrides/config/
    cfg_dir = os.path.join(BASE_DIR, "config")
    if os.path.exists(cfg_dir):
        for cfg in os.listdir(cfg_dir):
            cpath = os.path.join(cfg_dir, cfg)
            if os.path.isfile(cpath):
                z.write(cpath, f"overrides/config/{cfg}")

mrpack_size_mb = os.path.getsize(MRPACK_FILE) / (1024 * 1024)
print(f"Created Offline-Ready Modrinth Package: {os.path.basename(MRPACK_FILE)} ({mrpack_size_mb:.2f} MB)")

# 7. Update Aetheris_Modpack_Modern_26.2.zip
print("\n[REBUILD] Updating Aetheris_Modpack_Modern_26.2.zip...")
MODERN_ZIP = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.zip")
MODERN_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2")

with zipfile.ZipFile(MODERN_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(MODERN_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, MODERN_DIR)
            z.write(full_path, rel_path)

zip_size_mb = os.path.getsize(MODERN_ZIP) / (1024 * 1024)
print(f"Updated: {os.path.basename(MODERN_ZIP)} ({zip_size_mb:.2f} MB)")

print("\n==================================================")
print("       ALL BUILDS & FIXES COMPLETED SUCCESSFULLY!  ")
print("==================================================")
