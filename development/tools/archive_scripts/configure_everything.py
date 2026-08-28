#!/usr/bin/env python3
"""
configure_everything.py
Configures ALL mods, video settings, and shader settings
for Aetheris profiles on RTX 4050 + i7-13650HX + 24GB RAM
"""
import os, json, shutil

VISUAL  = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-visual-26.2"
BALANCED= r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-balanced-26.2"
PERF    = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-modern-performance-26.2"
LEGACY  = r"C:\Users\a7med\.lunarclient\profiles\aetheris-ultimate-legacy-1.8.9"

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {os.path.relpath(path, os.path.dirname(os.path.dirname(path)))}")

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  ✅ {os.path.relpath(path, os.path.dirname(os.path.dirname(path)))}")

def patch_json(path, updates):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            try: data = json.load(f)
            except: data = {}
    else:
        data = {}
    data.update(updates)
    write_json(path, data)

# ══════════════════════════════════════════════════════════════════════
# 1. MINECRAFT VIDEO SETTINGS (options.txt)
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  1. VIDEO SETTINGS (options.txt)")
print("══════════════════════════════════════════════════")

VIDEO_VISUAL = """\
version:4903
ao:true
biomeBlendRadius:4
chunkSectionFadeInTime:0.5
cutoutLeaves:true
enableVsync:false
entityDistanceScaling:1.5
entityShadows:true
fov:0.0
fovEffectScale:0.0
darknessEffectScale:0.0
glintSpeed:0.5
glintStrength:0.75
preferredGraphicsBackend:"opengl"
graphicsPreset:"fancy"
prioritizeChunkUpdates:0
fullscreen:false
exclusiveFullscreen:true
gamma:0.5
guiScale:3
maxAnisotropyBit:4
textureFiltering:1
maxFps:260
improvedTransparency:true
inactivityFpsLimit:"afk"
mipmapLevels:4
narrator:0
particles:0
reducedDebugInfo:false
renderClouds:"fancy"
cloudRange:128
renderDistance:20
simulationDistance:12
screenEffectScale:0.5
vignette:true
weatherRadius:16
autoJump:false
bobView:true
toggleCrouch:false
toggleSprint:true
toggleAttack:false
toggleUse:false
darkMojangStudiosBackground:true
hideLightningFlashes:false
hideSplashTexts:false
mouseSensitivity:0.5
damageTiltStrength:0.5
highContrast:false
highContrastBlockOutline:false
narratorHotkey:false
resourcePacks:["vanilla","file/[26.2] Aetheris Ultimate 32x.zip","eatinganimationid:supporteatinganimation"]
incompatibleResourcePacks:[]
lastServer:
lang:en_us
chatVisibility:0
chatOpacity:1.0
chatLineSpacing:0.0
textBackgroundOpacity:0.5
backgroundForChatOnly:true
hideServerAddress:false
advancedItemTooltips:false
pauseOnLostFocus:true
overrideWidth:0
overrideHeight:0
chatHeightFocused:1.0
chatDelay:0.0
chatHeightUnfocused:0.4375
chatScale:1.0
chatWidth:1.0
notificationDisplayTime:1.0
useNativeTransport:true
mainHand:"right"
attackIndicator:1
tutorialStep:none
mouseWheelSensitivity:1.0
rawMouseInput:true
allowCursorChanges:true
glDebugVerbosity:1
skipMultiplayerWarning:true
hideMatchedNames:true
joinedFirstServer:false
syncChunkWrites:false
showAutosaveIndicator:true
allowServerListing:true
inGameNotification:false
onlyShowSecureChat:false
saveChatDrafts:false
panoramaScrollSpeed:1.0
telemetryOptInExtra:false
menuBackgroundBlurriness:3
startedCleanly:true
musicToast:"never"
musicFrequency:"DEFAULT"
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
key_key.smoothCamera:key.keyboard.unknown
key_key.fullscreen:key.keyboard.f11
key_key.spectatorOutlines:key.keyboard.unknown
soundCategory_master:1.0
soundCategory_music:0.5
soundCategory_record:1.0
soundCategory_weather:0.8
soundCategory_block:1.0
soundCategory_hostile:1.0
soundCategory_neutral:1.0
soundCategory_player:1.0
soundCategory_ambient:1.0
soundCategory_voice:1.0
"""

VIDEO_BALANCED = VIDEO_VISUAL.replace(
    "renderDistance:20", "renderDistance:16"
).replace(
    "simulationDistance:12", "simulationDistance:10"
).replace(
    "entityDistanceScaling:1.5", "entityDistanceScaling:1.0"
).replace(
    "graphicsPreset:\"fancy\"", "graphicsPreset:\"fast\""
).replace(
    "particles:0", "particles:1"
).replace(
    "renderClouds:\"fancy\"", "renderClouds:\"fast\""
).replace(
    "cloudRange:128", "cloudRange:64"
).replace(
    "improvedTransparency:true", "improvedTransparency:false"
).replace(
    "maxAnisotropyBit:4", "maxAnisotropyBit:2"
)

VIDEO_PERF = VIDEO_VISUAL.replace(
    "renderDistance:20", "renderDistance:12"
).replace(
    "simulationDistance:12", "simulationDistance:8"
).replace(
    "entityDistanceScaling:1.5", "entityDistanceScaling:0.75"
).replace(
    "graphicsPreset:\"fancy\"", "graphicsPreset:\"fast\""
).replace(
    "particles:0", "particles:2"
).replace(
    "renderClouds:\"fancy\"", "renderClouds:\"false\""
).replace(
    "cloudRange:128", "cloudRange:32"
).replace(
    "improvedTransparency:true", "improvedTransparency:false"
).replace(
    "maxAnisotropyBit:4", "maxAnisotropyBit:1"
).replace(
    "mipmapLevels:4", "mipmapLevels:2"
).replace(
    "biomeBlendRadius:4", "biomeBlendRadius:2"
).replace(
    "file/[26.2] Aetheris Ultimate 32x.zip", "file/[26.2] Aetheris Ultimate 32x.zip"
)

for profile, video in [(VISUAL, VIDEO_VISUAL), (BALANCED, VIDEO_BALANCED), (PERF, VIDEO_PERF)]:
    write(os.path.join(profile, "options.txt"), video)

# ══════════════════════════════════════════════════════════════════════
# 2. SHADER SETTINGS
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  2. SHADER SETTINGS")
print("══════════════════════════════════════════════════")

# Aetheris shader options for Visual profile (maximum quality)
SHADER_VISUAL = """\
# Aetheris Shader — Visual Ultra preset
# Hardware: RTX 4050 6GB | i7-13650HX | 26.2 Fabric
profile=HIGH
profile2=SPACEAGLE17
tonemap=ACESTonemap

# ── Temporal Anti-Aliasing ──────────────────────────────────────
TAA_MODE=1
TAA_SMOOTHING=4
IMAGE_SHARPENING=0.20

# ── Bloom ───────────────────────────────────────────────────────
BLOOM=true
BLOOM_ENABLED=true
BLOOM_STRENGTH=0.14

# ── Reflections ─────────────────────────────────────────────────
WORLD_SPACE_REFLECTIONS=1
WATER_REFLECT_QUALITY=3
BLOCK_REFLECT_QUALITY=3

# ── Parallax Occlusion Mapping ──────────────────────────────────
POM=true
POM_QUALITY=32
POM_DEPTH=0.40

# ── Shadows ─────────────────────────────────────────────────────
SHADOW_QUALITY=3

# ── Lighting ────────────────────────────────────────────────────
COLORED_LIGHTING=256
LIGHTSHAFT_QUALI=2
LIGHTSHAFT_QUALI_DEFINE=3

# ── Clouds ──────────────────────────────────────────────────────
CLOUD_QUALITY=3

# ── Details ─────────────────────────────────────────────────────
DETAIL_QUALITY=3
ANISOTROPIC_FILTER=4

# ── Water ───────────────────────────────────────────────────────
WATER_STYLE_DEFINE=3
PIXEL_WATER=0
WATER_FOAM=false
WATER_FOAM_I=0
FRESNEL_MULTIPLIER=1.0

# ── Atmosphere ──────────────────────────────────────────────────
ROUND_SUN=true

# ── Flowers / Foliage ───────────────────────────────────────────
EMISSIVE_FLOWERS=0
"""

# Shader options for Balanced profile (quality/perf tradeoff)
SHADER_BALANCED = """\
# Aetheris Shader — Balanced preset
profile=MEDIUM
tonemap=ACESTonemap

TAA_MODE=1
TAA_SMOOTHING=2
IMAGE_SHARPENING=0.15

BLOOM=true
BLOOM_ENABLED=true
BLOOM_STRENGTH=0.10

WORLD_SPACE_REFLECTIONS=0
WATER_REFLECT_QUALITY=2
BLOCK_REFLECT_QUALITY=1

POM=false
POM_QUALITY=16
POM_DEPTH=0.25

SHADOW_QUALITY=2

COLORED_LIGHTING=128
LIGHTSHAFT_QUALI=1
LIGHTSHAFT_QUALI_DEFINE=2

CLOUD_QUALITY=2

DETAIL_QUALITY=2
ANISOTROPIC_FILTER=2

WATER_STYLE_DEFINE=2
PIXEL_WATER=0
WATER_FOAM=false
FRESNEL_MULTIPLIER=0.8

ROUND_SUN=true
EMISSIVE_FLOWERS=0
"""

# Shader options for Performance profile (max FPS)
SHADER_PERF = """\
# Aetheris Shader — Performance preset
profile=LOW
tonemap=ACESTonemap

TAA_MODE=0
IMAGE_SHARPENING=0.10

BLOOM=false
BLOOM_ENABLED=false

WORLD_SPACE_REFLECTIONS=0
WATER_REFLECT_QUALITY=1
BLOCK_REFLECT_QUALITY=0

POM=false

SHADOW_QUALITY=1

COLORED_LIGHTING=0
LIGHTSHAFT_QUALI=0
LIGHTSHAFT_QUALI_DEFINE=1

CLOUD_QUALITY=1

DETAIL_QUALITY=1
ANISOTROPIC_FILTER=0

WATER_STYLE_DEFINE=1
PIXEL_WATER=0
WATER_FOAM=false

ROUND_SUN=false
EMISSIVE_FLOWERS=0
"""

for profile, shader_cfg in [
    (VISUAL, SHADER_VISUAL),
    (BALANCED, SHADER_BALANCED),
    (PERF, SHADER_PERF),
]:
    write(os.path.join(profile, "shaderpacks", "Aetheris_Shader_Pack.txt"), shader_cfg)

# ══════════════════════════════════════════════════════════════════════
# 3. SODIUM / IRIS / RENDERING
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  3. SODIUM / IRIS / RENDERING MODS")
print("══════════════════════════════════════════════════")

SODIUM_OPTIONS = """\
{
  "version": 3,
  "options": {
    "quality": {
      "graphicsQuality": "FANCY",
      "cloudQuality": "FANCY",
      "weatherQuality": "FANCY",
      "leavesQuality": "FANCY",
      "particleQuality": "HIGH",
      "animateOnlyVisibleTextures": true,
      "enableVignette": true,
      "entityDistanceScaling": 1.5
    },
    "performance": {
      "chunkBuilderThreads": 0,
      "deferChunkUpdates": false,
      "alwaysDeferChunkUpdates": false,
      "allowCpuRenderAheadLimit": true,
      "sortBehavior": "DEFER"
    },
    "advanced": {
      "useCompactVertexFormat": true,
      "useTranslucentFaceSorting": true,
      "enableDriverWorkarounds": true,
      "disableIncompatibleModWarnings": false,
      "useEntityCulling": true,
      "allowDirectMemoryAccess": true,
      "ignoreDriverBlacklist": false,
      "useBlockFaceCulling": true,
      "enableMemoryTracing": false,
      "translucencyRenderingMode": "SIMPLE"
    }
  }
}
"""
for profile in [VISUAL, BALANCED, PERF]:
    cfg_path = os.path.join(profile, "config", "sodium-options.json")
    write(cfg_path, SODIUM_OPTIONS)

# Sodium extra config
SODIUM_EXTRA = """\
{
  "version": 2,
  "renderSettings": {
    "animationSettings": {
      "rain": true,
      "lava": true,
      "fire": true,
      "portal": true,
      "blockAnimations": true,
      "sculkSensor": true,
      "enchantingTable": true
    },
    "detailSettings": {
      "sky": true,
      "stars": true,
      "sunMoon": true,
      "vignette": true,
      "lilyPadTilt": true,
      "biasBotom": false,
      "fog": true
    },
    "particleSettings": {
      "rainSplash": true,
      "crit": true,
      "drip": true,
      "portal": true,
      "explosion": true,
      "terrain": true,
      "flame": true,
      "enchantment": true
    },
    "extraSettings": {
      "chunkUpdateDuration": true,
      "chunkBorderOverlay": false,
      "toasts": true,
      "windParticles": true
    }
  }
}
"""
for profile in [VISUAL, BALANCED, PERF]:
    cfg_path = os.path.join(profile, "config", "sodium-extra-options.json")
    write(cfg_path, SODIUM_EXTRA)

# ══════════════════════════════════════════════════════════════════════
# 4. PHYSICS MOD
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  4. PHYSICS MOD")
print("══════════════════════════════════════════════════")

PHYSICS_CLIENT = {
    "quickSetupNormalComplete": True,
    "quickSetupProComplete": True,
    "maxPhysicsObjects": 5000,          # Reduced from 10000 — better perf
    "cpuThreads": 4,                    # i7-13650HX — 4 dedicated physics threads
    "clothThreads": 2,
    "itemPhysics": True,
    "vinePhysics": True,
    "capePhysics": True,
    "fishingRodPhysics": True,
    "leashPhysics": True,
    "bannerPhysics": True,
    "clothSmoothShading": True,
    "showUpdateNotifications": False,
    "crackPhysicsParticles": True,
    "liquidPhysics": True,
    "bannerPhysicsRange": 64.0,
    "soundVolume": 0.8,
    "blockPhysicsRange": 48.0,          # Reduced from 96 — keeps physics local
    "vineRange": 24.0,
    "pvpServerCompatibility": False,
    "minecraftBlockBreakParticles": True,
    "particleLifetimeItems": 3.0,
    "particleLifetimeVines": 4.0,
    "particleLifetimeLiquids": 4.0,
}

for profile in [VISUAL, BALANCED]:
    cfg_path = os.path.join(profile, "config", "physicsmod", "physics_client_config.json")
    if os.path.exists(os.path.dirname(cfg_path)):
        write_json(cfg_path, PHYSICS_CLIENT)

# ══════════════════════════════════════════════════════════════════════
# 5. SOUND PHYSICS REMASTERED
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  5. SOUND PHYSICS REMASTERED")
print("══════════════════════════════════════════════════")

SOUND_PHYSICS = """\
# Sound Physics Remastered — Aetheris Optimized
# Immersive 3D sound with reverb and occlusion

# Master toggle
enabled=true

# Sound attenuation with distance (1.0 = physically correct)
attenuation_factor=1.0

# Reverb gain — how much echo you hear in caves/rooms
reverb_gain=0.9

# Reverb brightness — higher = more high freq in reverb
reverb_brightness=1.0

# Distance of reverb relative to sound distance (1.5 = natural)
reverb_distance=1.5

# Sound absorption through blocks (1.0 = full muffling through walls)
block_absorption=1.0

# Occlusion variation — smaller = more consistent muffling
occlusion_variation=0.25

# Default block reflectivity (0.5 = natural)
default_block_reflectivity=0.5

# Default block occlusion
default_block_occlusion_factor=1.0

# Max reverb bounces (higher = more natural, heavier CPU)
max_order=4

# Update rate for reverb (lower = more responsive, heavier CPU)
reverb_update_rate=10

# Disable reverb in the Nether (different acoustics)
underwater_reverb_gain=0.3

# Reverb attenuation distance (0 = disabled)
reverb_attenuation_distance=0.0

# Log level (0 = errors only)
log_level=0
"""

for profile in [VISUAL, BALANCED]:
    cfg_dir = os.path.join(profile, "config", "sound_physics_remastered")
    if os.path.exists(cfg_dir):
        write(os.path.join(cfg_dir, "soundphysics.properties"), SOUND_PHYSICS)

# ══════════════════════════════════════════════════════════════════════
# 6. PRESENCE FOOTSTEPS
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  6. PRESENCE FOOTSTEPS")
print("══════════════════════════════════════════════════")

FOOTSTEPS = """\
{
  "volume": {
    "volume": 80,
    "foliageSoundsVolume": 80,
    "clientPlayerVolume": 100,
    "passiveEntitiesVolume": 80,
    "runningVolumeIncrease": 15,
    "wetSoundsVolume": 70,
    "hostileEntitiesVolume": 60,
    "otherPlayerVolume": 70
  },
  "debug": {
    "visualiser": false
  },
  "performance": {
    "maxEntitiesPerFrame": 20
  }
}
"""
for profile in [VISUAL, BALANCED]:
    cfg_path = os.path.join(profile, "config", "presencefootsteps", "userconfig.json5")
    if os.path.exists(os.path.dirname(cfg_path)):
        write(cfg_path, FOOTSTEPS)

# ══════════════════════════════════════════════════════════════════════
# 7. JADE (Block Info Tooltip)
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  7. JADE")
print("══════════════════════════════════════════════════")

JADE_CFG = {
  "general": {
    "enabled": True,
    "displayMode": 0,
    "displayEntities": True,
    "displayBlocks": True,
    "showItemModNameTooltip": True,
    "hintOverlayToggle": True,
    "narrate": False,
    "hideFromDebug": True,
    "enableTextToSpeech": False
  },
  "rendering": {
    "alpha": 0.85,
    "scale": 1.0,
    "titleLineExpansion": 0,
    "subtitleLineExpansion": 0,
    "wrapWidth": 250,
    "position": [4, 4],
    "positionMode": 0,
    "showProgressBar": True,
    "showServerTime": False,
    "builtinCamouflage": True
  }
}
for profile in [VISUAL, BALANCED]:
    jade_path = os.path.join(profile, "config", "jade", "jade.json")
    if os.path.exists(os.path.dirname(jade_path)):
        if os.path.exists(jade_path):
            with open(jade_path, "r", encoding="utf-8", errors="replace") as f:
                try: existing = json.load(f)
                except: existing = {}
            # Only patch the fields we care about
            for section, vals in JADE_CFG.items():
                if section not in existing:
                    existing[section] = {}
                existing[section].update(vals)
            write_json(jade_path, existing)
        else:
            write_json(jade_path, JADE_CFG)

# ══════════════════════════════════════════════════════════════════════
# 8. VEINMINER
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  8. VEINMINER")
print("══════════════════════════════════════════════════")

VEINMINER_SETTINGS = {
  "activationStrategy": "HOLD",          # Hold key to vein mine
  "maxVeinSize": 64,                     # Max blocks per vein
  "collectItemsAtSource": True,          # Items go to inventory directly
  "wireframeEnabled": True,              # Show outline of detected vein
  "wireframeColor": {"r": 0, "g": 200, "b": 255, "a": 180}
}
for profile in [VISUAL, BALANCED]:
    vm_path = os.path.join(profile, "config", "Veinminer", "settings.json")
    if os.path.exists(os.path.dirname(vm_path)):
        write_json(vm_path, VEINMINER_SETTINGS)

# ══════════════════════════════════════════════════════════════════════
# 9. SERENE SEASONS
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  9. SERENE SEASONS")
print("══════════════════════════════════════════════════")

SEASONS_CFG = """\
# Serene Seasons — Aetheris Config
# Realistic season lengths (1 real-world week per season at normal play speed)

[general]
    # Season length in days (20min/day = 120 MC days = ~40hr per season)
    seasonDuration = 28

    # Dimensions where seasons are active
    dimensionList = ["minecraft:overworld"]
    dimensionListType = "WHITELIST"

    # Enable crop growth changes per season
    enableSeasonalCropGrowth = true

    # Enable random crop death in winter
    enableRandomCropDeath = false

    # Enable season tooltips in game
    enableSeasonTooltip = true

[server]
    # Announce season change in chat
    announceSeasonChange = true
"""
for profile in [VISUAL, BALANCED]:
    ss_path = os.path.join(profile, "config", "sereneseasons", "seasons.toml")
    if os.path.exists(os.path.dirname(ss_path)):
        write(ss_path, SEASONS_CFG)

# ══════════════════════════════════════════════════════════════════════
# 10. DYNAMIC FPS
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  10. DYNAMIC FPS")
print("══════════════════════════════════════════════════")

DYNFPS = """\
{
  "version": 1,
  "powerSavingMode": false,
  "idleTargetFps": 10,
  "unfocusedTargetFps": 30,
  "afkTargetFps": 5,
  "reduceResolutionOnUnfocus": false,
  "degradeResolutionOnUnfocus": false
}
"""
for profile in [VISUAL, BALANCED, PERF]:
    cfg = os.path.join(profile, "config", "dynamic-fps.json")
    write(cfg, DYNFPS)

# ══════════════════════════════════════════════════════════════════════
# 11. SPARK (Performance Profiler)
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  11. SPARK")
print("══════════════════════════════════════════════════")

SPARK_CFG = {"backgroundProfiler": False, "backgroundProfilerInterval": 60}
for profile in [VISUAL, BALANCED]:
    cfg = os.path.join(profile, "config", "spark", "config.json")
    if os.path.exists(os.path.dirname(cfg)):
        write_json(cfg, SPARK_CFG)

# ══════════════════════════════════════════════════════════════════════
# 12. EUPHORIA PATCHER
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  12. EUPHORIA PATCHER")
print("══════════════════════════════════════════════════")

EUPHORIA_CFG = """\
# Euphoria Patcher — Aetheris Config
# Made for Euphoria Patches 1.9.3

[display]
    doPopUpLogging = false
    doDisplayShaderInGameMessage = false

[updates]
    doUpdateChecking = "none"

[maintenance]
    doRenameOldShaderFiles = false
    doDeleteOldShaderFiles = false

[debug]
    doDebugLogging = false

[advanced]
    alternativeShaderNames = ""
    autoMergeBlockProperties = false
"""
for profile in [VISUAL, BALANCED]:
    cfg = os.path.join(profile, "config", "euphoria_patcher", "settings.toml")
    if os.path.exists(os.path.dirname(cfg)):
        write(cfg, EUPHORIA_CFG)

# ══════════════════════════════════════════════════════════════════════
# 13. INVENTORY PROFILES NEXT
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  13. INVENTORY PROFILES NEXT")
print("══════════════════════════════════════════════════")

IPN_CFG = {"sortOrder": "by_category_group", "enableAutoRefill": True, "autoRefillBeforeTool": True}
for profile in [VISUAL, BALANCED]:
    cfg = os.path.join(profile, "config", "inventoryprofilesnext", "inventoryprofiles.json")
    if os.path.exists(os.path.dirname(cfg)):
        write_json(cfg, IPN_CFG)

# ══════════════════════════════════════════════════════════════════════
# 14. JUST ENOUGH ITEMS (JEI)
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  14. JEI")
print("══════════════════════════════════════════════════")

JEI_CLIENT = """\
[client-only-settings]
    [client-only-settings.search-colors]
        colorSearchEnabled = true
    [client-only-settings.search-mods]
        modNameSearchEnabled = true
    [client-only-settings.search-tooltips]
        tooltipSearchEnabled = true

[common-settings]
    [common-settings.debug]
        debugEnabled = false
    [common-settings.search]
        maxSearchResults = 200
    [common-settings.performance]
        lowMemorySlowSearchEnabled = false
"""
for profile in [VISUAL, BALANCED]:
    cfg = os.path.join(profile, "config", "jei", "jei-client.ini")
    if os.path.exists(os.path.dirname(cfg)):
        pass  # JEI uses .ini, don't overwrite user settings — they're already good

# ══════════════════════════════════════════════════════════════════════
# 15. WOVER (World Override — BetterNether/BCLib settings)
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  15. WOVER / BCLIB")
print("══════════════════════════════════════════════════")

WOVER_CLIENT = {
    "enabled": True,
    "showUpdateInfo": False,
    "showBetaInfo": False
}
for profile in [VISUAL, BALANCED]:
    cfg = os.path.join(profile, "config", "wover", "client.json")
    if os.path.exists(os.path.dirname(cfg)):
        write_json(cfg, WOVER_CLIENT)

# ══════════════════════════════════════════════════════════════════════
# 16. SHULKER BOX TOOLTIP
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  16. SHULKER BOX TOOLTIP")
print("══════════════════════════════════════════════════")

SBT_CFG = """\
{
  "version": 2,
  "style": {
    "background": {
      "enabled": true,
      "color": { "r": 0, "g": 0, "b": 0, "a": 180 }
    },
    "border": {
      "enabled": true,
      "colorStart": { "r": 100, "g": 80, "b": 200, "a": 255 },
      "colorEnd": { "r": 40, "g": 20, "b": 120, "a": 255 }
    }
  },
  "display": {
    "enabled": true,
    "maxSlotsShown": 54,
    "showEmptySlots": false,
    "alwaysOn": false,
    "slotStyle": "VANILLA"
  },
  "server": {
    "enabled": true
  }
}
"""
for profile in [VISUAL, BALANCED]:
    cfg = os.path.join(profile, "config", "shulkerboxtooltip.json")
    write(cfg, SBT_CFG)

# ══════════════════════════════════════════════════════════════════════
# 17. VOICECHAT
# ══════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════════════")
print("  17. SIMPLE VOICE CHAT")
print("══════════════════════════════════════════════════")

VOICECHAT = """\
# Simple Voice Chat — Client Config
voice_chat_volume=1.0
microphone_amplification=1.0
voice_activation_threshold=-30.0
output_buffer_size=5
audio_sample_rate=48000
compressor_threshold=0.5
voice_activation_type=PTT
crouch_while_talking=false
auto_reconnect=true
show_log_button=false
mute_on_join=false
disable_audio_processing=false
runwhiletalking=true
hide_icons=false
icon_location=TOP_LEFT
disable_voice_chat=false
recording_destination=
"""
for profile in [VISUAL, BALANCED]:
    cfg = os.path.join(profile, "config", "voicechat", "voicechat-client.properties")
    if os.path.exists(os.path.dirname(cfg)):
        write(cfg, VOICECHAT)

print("\n══════════════════════════════════════════════════")
print("  ✨ ALL CONFIGURATIONS COMPLETE!")
print("══════════════════════════════════════════════════")
print()
print("  Profiles configured:")
print(f"   Visual  → {VISUAL}")
print(f"   Balanced→ {BALANCED}")
print(f"   Perf    → {PERF}")
print()
print("  What was configured:")
print("   [1]  Video Settings (options.txt) — per profile tier")
print("   [2]  Shader Settings — Visual/Balanced/Performance presets")
print("   [3]  Sodium + Sodium Extra — max quality settings")
print("   [4]  Physics Mod — 5000 max objects, 4 CPU threads")
print("   [5]  Sound Physics Remastered — natural reverb/occlusion")
print("   [6]  Presence Footsteps — immersive volumes")
print("   [7]  Jade — clean block info tooltips")
print("   [8]  VeinMiner — hold-to-mine, 64 block limit")
print("   [9]  Serene Seasons — 28-day season cycle")
print("   [10] Dynamic FPS — 5fps AFK, 30fps unfocused")
print("   [11] Spark — background profiler off")
print("   [12] Euphoria Patcher — no popups/updates")
print("   [13] Inventory Profiles Next — auto refill, sort by category")
print("   [14] Shulker Box Tooltip — purple border, 54 slots shown")
print("   [15] Wover/BCLib — update notices off")
print("   [16] Simple Voice Chat — PTT, 48kHz, no mute on join")
