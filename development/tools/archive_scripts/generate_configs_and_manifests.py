import os, json, hashlib, zipfile, datetime

BASE_DIR = r"d:\mods"
CONFIG_DIR = os.path.join(BASE_DIR, "config")
MODERN_DIR = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2")
os.makedirs(CONFIG_DIR, exist_ok=True)

print("==================================================")
print(" GENERATING OPTIMIZED CONFIGS & MODPACK MANIFESTS ")
print("==================================================")

# 1. Sodium Options (Tuned for RTX 4050 + i7-13650HX)
sodium_cfg = {
  "quality": {
    "hidden_fluid_culling": True,
    "improved_fluid_shaping": True,
    "use_closest_point_entity_sort": True,
    "pixel_filtering_mode": "NEAREST"
  },
  "performance": {
    "chunk_builder_threads": 20,
    "chunk_build_defer_mode": "ZERO_FRAMES",
    "animate_only_visible_textures": False,
    "use_entity_culling": False,
    "use_fog_occlusion": True,
    "use_block_face_culling": False,
    "use_no_error_g_l_context": True,
    "quad_splitting_mode": "UNLIMITED"
  },
  "advanced": {
    "enable_memory_tracing": False
  },
  "debug": {
    "terrain_sorting_enabled": True
  },
  "notifications": {
    "has_cleared_donation_button": True,
    "has_seen_donation_prompt": True,
    "has_edited_fullscreen_option": True
  }
}

with open(os.path.join(CONFIG_DIR, "sodium-options.json"), "w") as f:
    json.dump(sodium_cfg, f, indent=2)

# 2. Iris Properties (Auto-loading Aetheris Shader Pack)
iris_props = """#This file stores configuration options for Iris
allowUnknownShaders=false
colorSpace=SRGB
disableUpdateMessage=true
enableDebugOptions=false
enableShaders=true
maxShadowRenderDistance=32
shaderPack=Aetheris_Shader_Pack.zip
"""

with open(os.path.join(CONFIG_DIR, "iris.properties"), "w") as f:
    f.write(iris_props)

# 3. Continuity Config (CTM Connected Textures)
continuity_cfg = {
  "connectedTextures": True,
  "emissiveTextures": True,
  "glassPaneCullingFix": True,
  "useModelFeatures": True
}
with open(os.path.join(CONFIG_DIR, "continuity.json"), "w") as f:
    json.dump(continuity_cfg, f, indent=2)

# 4. Entity Model Features (EMF - Fresh Animations)
emf_cfg = {
  "enabled": True,
  "freshAnimationsSupport": True,
  "customEntityModels": True,
  "blinking": True,
  "physicsFeatures": True
}
with open(os.path.join(CONFIG_DIR, "entity_model_features.json"), "w") as f:
    json.dump(emf_cfg, f, indent=2)

# 5. Entity Texture Features (ETF - Emissive & Random Mobs)
etf_cfg = {
  "enableEmissiveTextures": True,
  "enableRandomTextures": True,
  "enableCustomSkinFeatures": True,
  "enablePlayerSkins": True
}
with open(os.path.join(CONFIG_DIR, "entity_texture_features.json"), "w") as f:
    json.dump(etf_cfg, f, indent=2)

# 6. Sound Physics Remastered (Acoustic Raytracing for Faithless Audio)
sound_physics_cfg = {
  "enabled": True,
  "globalVolume": 1.0,
  "reverbEnabled": True,
  "occlusionEnabled": True,
  "airAbsorptionEnabled": True,
  "raytraceSteps": 64,
  "reverbTimeMultiplier": 1.0
}
with open(os.path.join(CONFIG_DIR, "sound_physics_remastered.json"), "w") as f:
    json.dump(sound_physics_cfg, f, indent=2)

# 7. Dynamic FPS
dynamic_fps_cfg = {
  "idle_fps": 30,
  "unfocused_fps": 30,
  "hidden_fps": 15,
  "show_toasts": False
}
with open(os.path.join(CONFIG_DIR, "dynamic_fps.json"), "w") as f:
    json.dump(dynamic_fps_cfg, f, indent=2)

# 8. C2ME Threading & Parallel Worldgen (16 Cores / 20 Threads)
c2me_toml = """version = "0.4.2"
[threadedWorldGen]
enabled = true
allowThreadedFeatures = true
globalExecutorParallelism = 20

[asyncIO]
enabled = true
ioThreads = 8

[clientUncapVD]
enabled = true
"""
with open(os.path.join(CONFIG_DIR, "c2me.toml"), "w") as f:
    f.write(c2me_toml)

# Copy all configs to modern modpack directory
modern_cfg_dir = os.path.join(MODERN_DIR, "config")
os.makedirs(modern_cfg_dir, exist_ok=True)
for fname in os.listdir(CONFIG_DIR):
    src = os.path.join(CONFIG_DIR, fname)
    dst = os.path.join(modern_cfg_dir, fname)
    if os.path.isfile(src):
        with open(src, "rb") as sf, open(dst, "wb") as df:
            df.write(sf.read())

print("Configs generated and synced to d:\\mods\\config\\ and modpack directory.")

# 9. Generate Modrinth .mrpack index (modrinth.index.json)
print("\nGenerating Modrinth modrinth.index.json...")
jars = sorted([f for f in os.listdir(BASE_DIR) if f.endswith(".jar")])

files_list = []
for j in jars:
    jar_path = os.path.join(BASE_DIR, j)
    fsize = os.path.getsize(jar_path)
    
    with open(jar_path, "rb") as f:
        data = f.read()
        sha1 = hashlib.sha1(data).hexdigest()
        sha512 = hashlib.sha512(data).hexdigest()
    
    files_list.append({
        "path": f"mods/{j}",
        "hashes": {
            "sha1": sha1,
            "sha512": sha512
        },
        "env": {
            "client": "required",
            "server": "required"
        },
        "downloads": [
            f"https://cdn.modrinth.com/data/custom/{j}"
        ],
        "fileSize": fsize
    })

mrpack_index = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": "2.0.0-godtier",
    "name": "Aetheris Ultimate Modpack (Modern 26.2)",
    "summary": "The God-Tier 26.2 Fabric Modpack with complete 3-way synergy between Aetheris Shader Pack, MyCustomPack 32x Resource Pack, and RTX 4050 + i7-13650HX hardware optimizations.",
    "files": files_list,
    "dependencies": {
        "fabric-loader": "0.157.0",
        "minecraft": "26.2"
    }
}

index_path = os.path.join(BASE_DIR, "modrinth.index.json")
with open(index_path, "w", encoding="utf-8") as f:
    json.dump(mrpack_index, f, indent=2)

# Create Aetheris_Modpack_Modern_26.2.mrpack
mrpack_out = os.path.join(BASE_DIR, "Aetheris_Modpack_Modern_26.2.mrpack")
with zipfile.ZipFile(mrpack_out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(index_path, "modrinth.index.json")
    for cfg in os.listdir(CONFIG_DIR):
        cfg_file = os.path.join(CONFIG_DIR, cfg)
        if os.path.isfile(cfg_file):
            z.write(cfg_file, f"overrides/config/{cfg}")

print(f"Created Modrinth Package: {os.path.basename(mrpack_out)} ({os.path.getsize(mrpack_out)/1024:.1f} KB)")

# 10. Generate CurseForge manifest.json
print("\nGenerating CurseForge manifest.json...")
manifest = {
    "minecraft": {
        "version": "26.2",
        "modLoaders": [
            {
                "id": "fabric-0.157.0",
                "primary": True
            }
        ]
    },
    "manifestType": "minecraftModpack",
    "manifestVersion": 1,
    "name": "Aetheris Ultimate Modpack",
    "version": "2.0.0",
    "author": "Aetheris Team",
    "files": [],
    "overrides": "overrides"
}
with open(os.path.join(BASE_DIR, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("CurseForge manifest.json generated successfully!")
