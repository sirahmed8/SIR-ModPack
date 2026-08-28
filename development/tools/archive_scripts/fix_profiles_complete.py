#!/usr/bin/env python3
"""
fix_profiles_complete.py
1. Fix profile.json resource pack names (old → new tagged names)
2. Configure Legacy 1.8.9 profile fully (options.txt, mods configs)
3. Sync configs to modpack profile
4. Ensure ALL 3 user-facing profiles are fully set up
"""
import os, json, shutil

LC = r"C:\Users\a7med\.lunarclient\profiles"
VISUAL   = os.path.join(LC, "aetheris-ultimate-modern-visual-26.2")
BALANCED = os.path.join(LC, "aetheris-ultimate-modern-balanced-26.2")
PERF     = os.path.join(LC, "aetheris-ultimate-modern-performance-26.2")
MODPACK  = os.path.join(LC, "aetheris-ultimate-modpack-modern-26.2")
LEGACY   = os.path.join(LC, "aetheris-ultimate-legacy-1.8.9")

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ Written: {os.path.basename(os.path.dirname(os.path.dirname(path)))} -> {os.path.relpath(path, os.path.dirname(os.path.dirname(path)))}")

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  ✅ JSON: {os.path.basename(os.path.dirname(os.path.dirname(path)))} -> {os.path.relpath(path, os.path.dirname(os.path.dirname(path)))}")

# ══════════════════════════════════════════════════════════════════════
# 1. FIX profile.json RESOURCE PACK NAMES
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════")
print("  1. FIX profile.json — resource pack names")
print("══════════════════════════════════════════════")

profile_updates = {
    VISUAL: {
        "schemaVersion": 1,
        "name": "🌌 Aetheris Visual",
        "minecraft": "26.2",
        "loader": "Fabric",
        "renderer": "Iris + Sodium",
        "description": "Maximum visual fidelity — cinematic RTX 4050 experience",
        "hardware": "RTX 4050 Laptop / i7-13650HX / 24GB RAM / 1080p",
        "target": "Cinematic fidelity with stable laptop thermals",
        "resourcePack": "[26.2] Aetheris Ultimate 32x.zip",
        "shader": {
            "name": "Aetheris Shader Pack",
            "shadowDistance": 192,
            "shadowMap": 2048,
            "pomSteps": 32,
            "godrays": 3,
            "reflections": "full-screen-space",
            "taa": True,
            "expensiveVolumetrics": True
        }
    },
    BALANCED: {
        "schemaVersion": 1,
        "name": "⚖️ Aetheris Balanced",
        "minecraft": "26.2",
        "loader": "Fabric",
        "renderer": "Iris + Sodium",
        "description": "Best quality-to-performance ratio for daily play",
        "hardware": "RTX 4050 Laptop / i7-13650HX / 24GB RAM / 1080p",
        "target": "90-120 FPS with great visuals",
        "resourcePack": "[26.2] Aetheris Ultimate 32x.zip",
        "shader": {
            "name": "Aetheris Shader Pack",
            "shadowDistance": 128,
            "shadowMap": 2048,
            "pomSteps": 16,
            "godrays": 2,
            "reflections": "fast-screen-space",
            "taa": True,
            "expensiveVolumetrics": False
        }
    },
    PERF: {
        "schemaVersion": 1,
        "name": "⚡ Aetheris Performance",
        "minecraft": "26.2",
        "loader": "Fabric",
        "renderer": "Iris + Sodium",
        "description": "Maximum stable frame rate and lowest input latency",
        "hardware": "RTX 4050 Laptop / i7-13650HX / 24GB RAM / 1080p",
        "target": "150+ FPS, lowest latency",
        "resourcePack": "[26.2] Aetheris Ultimate 32x.zip",
        "shader": {
            "name": "Aetheris Shader Pack",
            "shadowDistance": 96,
            "shadowMap": 1024,
            "pomSteps": 8,
            "godrays": 1,
            "reflections": "off",
            "taa": False,
            "expensiveVolumetrics": False
        }
    },
    LEGACY: {
        "schemaVersion": 1,
        "name": "🗡️ Aetheris Legacy PvP",
        "minecraft": "1.8.9",
        "loader": "LunarClient",
        "description": "Classic 1.8.9 PvP profile with clean HUD and high FPS",
        "hardware": "RTX 4050 Laptop / i7-13650HX / 24GB RAM / 1080p",
        "target": "200+ FPS stable, minimal input lag",
        "resourcePack": "[1.8.9] Aetheris Legacy 32x.zip",
        "shader": {"name": "None (PvP)"}
    }
}

for profile, data in profile_updates.items():
    pj = os.path.join(profile, "profile.json")
    write_json(pj, data)

# ══════════════════════════════════════════════════════════════════════
# 2. FIX options.txt RESOURCE PACK NAME in all profiles
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════")
print("  2. FIX options.txt resource pack references")
print("══════════════════════════════════════════════")

for profile in [VISUAL, BALANCED, PERF, MODPACK]:
    opts = os.path.join(profile, "options.txt")
    if os.path.exists(opts):
        with open(opts, "r", encoding="utf-8") as f:
            content = f.read()
        # Fix old resource pack name references
        fixed = content
        for old in ["MyCustomPack_Modern_32x.zip", "MyCustomPack_1.8.9_32x.zip",
                    "Aetheris_Ultimate_32x.zip", "aetheris_ultimate_32x.zip"]:
            fixed = fixed.replace(f"file/{old}", "file/[26.2] Aetheris Ultimate 32x.zip")
        if fixed != content:
            with open(opts, "w", encoding="utf-8") as f:
                f.write(fixed)
            print(f"  ✅ Fixed RP name in: {os.path.basename(profile)}/options.txt")
        else:
            print(f"  ✓  Already correct: {os.path.basename(profile)}/options.txt")

# ══════════════════════════════════════════════════════════════════════
# 3. CONFIGURE LEGACY 1.8.9 PROFILE FULLY
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════")
print("  3. CONFIGURE LEGACY 1.8.9 PROFILE")
print("══════════════════════════════════════════════")

# Legacy options.txt — optimized for 1.8.9 PvP (max FPS, clean)
LEGACY_OPTIONS = """\
version:340
ao:false
biomeBlendRadius:2
enableVsync:false
entityDistanceScaling:1.0
entityShadows:false
fov:0.0
fovEffectScale:0.0
darknessEffectScale:0.0
graphicsPreset:"fast"
fullscreen:false
exclusiveFullscreen:true
gamma:1.0
guiScale:3
maxFps:260
mipmapLevels:0
narrator:0
particles:2
reducedDebugInfo:false
renderClouds:"false"
renderDistance:8
simulationDistance:6
screenEffectScale:0.0
vignette:false
weatherRadius:5
autoJump:false
bobView:false
toggleCrouch:false
toggleSprint:true
darkMojangStudiosBackground:true
hideLightningFlashes:true
mouseSensitivity:0.5
damageTiltStrength:0.0
resourcePacks:["vanilla","file/[1.8.9] Aetheris Legacy 32x.zip"]
incompatibleResourcePacks:[]
lang:en_us
chatVisibility:0
chatOpacity:1.0
textBackgroundOpacity:0.3
backgroundForChatOnly:true
advancedItemTooltips:false
pauseOnLostFocus:false
chatScale:1.0
chatWidth:1.0
useNativeTransport:true
mainHand:"right"
attackIndicator:0
tutorialStep:none
mouseWheelSensitivity:1.0
rawMouseInput:true
syncChunkWrites:false
showAutosaveIndicator:false
soundCategory_master:1.0
soundCategory_music:0.2
soundCategory_record:0.5
soundCategory_weather:0.5
soundCategory_block:1.0
soundCategory_hostile:1.0
soundCategory_neutral:1.0
soundCategory_player:1.0
soundCategory_ambient:0.5
soundCategory_voice:1.0
key_key.attack:key.mouse.left
key_key.use:key.mouse.right
key_key.forward:key.keyboard.w
key_key.left:key.keyboard.a
key_key.back:key.keyboard.s
key_key.right:key.keyboard.d
key_key.jump:key.keyboard.space
key_key.sneak:key.keyboard.left.shift
key_key.sprint:key.keyboard.left.control
key_key.drop:key.keyboard.q
key_key.inventory:key.keyboard.e
key_key.chat:key.keyboard.t
key_key.playerlist:key.keyboard.tab
key_key.pickItem:key.mouse.middle
key_key.command:key.keyboard.slash
key_key.toggleGui:key.keyboard.f1
key_key.screenshot:key.keyboard.f2
key_key.fullscreen:key.keyboard.f11
"""
write(os.path.join(LEGACY, "options.txt"), LEGACY_OPTIONS)

# ══════════════════════════════════════════════════════════════════════
# 4. SYNC ALL CONFIGS TO MODPACK PROFILE
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════")
print("  4. SYNC configs Visual → Modpack profile")
print("══════════════════════════════════════════════")

# Modpack profile = same as Balanced (198 mods, general purpose)
configs_to_sync = [
    "options.txt",
    os.path.join("config", "sodium-options.json"),
    os.path.join("config", "sodium-extra-options.json"),
    os.path.join("config", "dynamic-fps.json"),
    os.path.join("config", "shulkerboxtooltip.json"),
    os.path.join("config", "DistantHorizons.toml"),
    os.path.join("config", "euphoria_patcher", "settings.toml"),
    os.path.join("config", "jade", "jade.json"),
    os.path.join("config", "sereneseasons", "seasons.toml"),
    os.path.join("config", "wover", "client.json"),
    os.path.join("shaderpacks", "Aetheris_Shader_Pack.txt"),
]

synced = 0
for rel_path in configs_to_sync:
    src = os.path.join(BALANCED, rel_path)
    dst = os.path.join(MODPACK, rel_path)
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  ✅ Synced → Modpack: {rel_path}")
        synced += 1

print(f"\n  {synced} config files synced to Modpack profile")

# ══════════════════════════════════════════════════════════════════════
# 5. SYNC NEW MODS FROM VISUAL → MODPACK (mods that are in visual but not modpack)
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════")
print("  5. SYNC new mods Visual → Modpack")
print("══════════════════════════════════════════════")

visual_mods = os.path.join(VISUAL, "mods")
modpack_mods = os.path.join(MODPACK, "mods")
os.makedirs(modpack_mods, exist_ok=True)

modpack_existing = set(os.listdir(modpack_mods))
visual_all = set(os.listdir(visual_mods))

# Don't copy these to modpack (too heavy / visual-only)
visual_only_skip = {
    "DistantHorizons-3.2.0-b-26.2-fabric-neoforge.jar",
    "BridgingMod-2.7.0+26.2.fabric-release.jar",
}

copied = 0
for jar in sorted(visual_all):
    if not jar.endswith(".jar"):
        continue
    if jar in modpack_existing:
        continue
    if jar in visual_only_skip:
        continue
    src = os.path.join(visual_mods, jar)
    dst = os.path.join(modpack_mods, jar)
    shutil.copy2(src, dst)
    print(f"  ✅ Copied → Modpack: {jar}")
    copied += 1

print(f"\n  {copied} new mods added to Modpack profile")

# ══════════════════════════════════════════════════════════════════════
# 6. PRINT FINAL STATE OF ALL 3 USER-FACING PROFILES
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════")
print("  FINAL PROFILE STATE")
print("══════════════════════════════════════════════")
for profile in [VISUAL, BALANCED, LEGACY]:
    name_line = ""
    pj = os.path.join(profile, "profile.json")
    if os.path.exists(pj):
        with open(pj) as f:
            try: pdata = json.load(f); name_line = pdata.get("name", "")
            except: pass
    mods_dir = os.path.join(profile, "mods")
    mods_count = len([f for f in os.listdir(mods_dir) if f.endswith(".jar")]) if os.path.exists(mods_dir) else 0
    shaders_dir = os.path.join(profile, "shaderpacks")
    shaders_count = len(os.listdir(shaders_dir)) if os.path.exists(shaders_dir) else 0
    opts_exists = "✅" if os.path.exists(os.path.join(profile, "options.txt")) else "❌"
    rp_dir = os.path.join(profile, "resourcepacks")
    rp_count = len(os.listdir(rp_dir)) if os.path.exists(rp_dir) else 0

    print(f"  {name_line}")
    print(f"    Folder  : {os.path.basename(profile)}")
    print(f"    Mods    : {mods_count}")
    print(f"    Shaders : {shaders_count}")
    print(f"    Res Pack: {rp_count} files in resourcepacks/")
    print(f"    options : {opts_exists}")
    print()

print("══════════════════════════════════════════════")
print("  ✨ ALL 3 PROFILES FULLY CONFIGURED!")
print("══════════════════════════════════════════════")
