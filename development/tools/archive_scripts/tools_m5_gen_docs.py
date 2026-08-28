import os

docs_dir = r"D:\AetherisShare\docs"
os.makedirs(docs_dir, exist_ok=True)

install_guide = """# Aetheris Ecosystem — Installation & Deployment Guide

## Overview
Aetheris is an optimized Minecraft ecosystem supporting both **Modern (Minecraft 26.2 Fabric)** and **Legacy (Minecraft 1.8.9 Forge)**.
This distribution provides automated installers and manual configuration files for Lunar Client, Prism Launcher, and standard `.minecraft`.

---

## 1. Automated Installation (Lunar Client)

### Quick Start
1. Close Lunar Client completely (ensure no background `javaw.exe` or Lunar launcher processes are running).
2. Double-click `install.bat` in `D:\\AetherisShare`.
3. The interactive installer will prompt you to select an installation mode:
   - **[1] Full Installation (Recommended)**: Deploys all 8 Lunar profiles, HUD presets, shaders, resource packs, and registers all profiles in `profiles.db` with 8GB memory and tuned G1GC parameters.
   - **[2] Modern Profiles Only**: Deploys Visual, Balanced, Performance, and Modpack Modern 26.2 profiles.
   - **[3] Legacy Profiles Only**: Deploys PvP, Visual, Balanced, and Performance 1.8.9 Forge profiles.
   - **[4] Selective Profile**: Choose specific individual profiles to deploy.
   - **[5] Prism Launcher Deployment**: Deploys complete modern and legacy instances to Prism Launcher.
   - **[6] Standard .minecraft Deployment**: Synchronizes mods, shaders, resource packs, and configs to `.minecraft`.
   - **[7] Complete Ecosystem Deployment**: Deploys to Lunar Client, Prism Launcher, and `.minecraft` simultaneously.
   - **[8] Standalone Assets**: Deploys standalone shaders, resource packs, or HUD presets.

### Unattended / Scripted Execution
The PowerShell installer (`install.ps1`) supports command-line parameters for headless and automated execution:
```powershell
# Install all profiles silently
powershell -ExecutionPolicy Bypass -File "D:\\AetherisShare\\install.ps1" -Mode All -NonInteractive

# Install only modern visual and balanced profiles
powershell -ExecutionPolicy Bypass -File "D:\\AetherisShare\\install.ps1" -Mode Selective -ProfileNames visual,balanced -NonInteractive

# Deploy to Prism Launcher instances
powershell -ExecutionPolicy Bypass -File "D:\\AetherisShare\\install.ps1" -Mode Prism -NonInteractive
```

---

## 2. Prism Launcher Deployment

Aetheris includes pre-configured instances and modpack archives for Prism Launcher:
1. **Importing Modpack Archives**:
   - In Prism Launcher, click **Add Instance** -> **Import from zip**.
   - Select `D:\\AetherisShare\\modpacks\\Aetheris_Modpack_Modern_26.2.zip` for Modern Fabric 26.2.
   - Select `D:\\AetherisShare\\modpacks\\Aetheris_Modpack_Legacy_1.8.9.zip` for Legacy Forge 1.8.9.
2. **Direct Instance Synchronization**:
   - The automated installer automatically synchronizes mods, configs, shaders, options, and JVM memory flags directly into:
     - `C:\\Users\\%USERNAME%\\AppData\\Roaming\\PrismLauncher\\instances\\Minecraft 26.2\\.minecraft`
     - `C:\\Users\\%USERNAME%\\AppData\\Roaming\\PrismLauncher\\instances\\Minecraft 1.8.9\\.minecraft`

---

## 3. Standard .minecraft Deployment

For standard vanilla launcher or third-party loaders:
1. Run `install.ps1 -Mode Minecraft -NonInteractive` or manually copy:
   - `mods/` -> `%APPDATA%\\.minecraft\\mods`
   - `config/` -> `%APPDATA%\\.minecraft\\config`
   - `shaderpacks/` -> `%APPDATA%\\.minecraft\\shaderpacks`
   - `resourcepacks/` -> `%APPDATA%\\.minecraft\\resourcepacks`
   - `options.txt` and `sodium-options.json` -> `%APPDATA%\\.minecraft\\`
"""

profiles_overview = """# Aetheris Ecosystem — Profiles & Architecture Overview

## Profile Matrix

### Modern 26.2 Fabric Profiles
| Profile Name | Folder / Key | Mod Count | Target FPS | Primary Use Case |
|---|---|---|---|---|
| **Aetheris Ultra Visual** | `aetheris-ultimate-modern-visual-26.2` (`visual`) | 199 mods | 100-140 FPS | Ray-traced shaders, 3D POM block depth, PBR specular reflections, 20 chunk threads. |
| **Aetheris Balanced** | `aetheris-ultimate-modern-balanced-26.2` (`balanced`) | 198 mods | 140-180 FPS | Optimal balance of shaders, fluid frame pacing, and everyday gameplay. 6 chunk threads. |
| **Aetheris Ultimate Performance** | `aetheris-ultimate-modern-performance-26.2` (`performance`) | 181 mods | 260-350+ FPS | Ultra-responsive competitive play, pure FPS optimization, 4 chunk threads. |
| **Aetheris Modern Modpack** | `aetheris-ultimate-modpack-modern-26.2` (`modpack`) | 250+ mods | 120-160 FPS | Full comprehensive mod suite with all world generation, animations, and tools. |

### Legacy 1.8.9 Forge Profiles
| Profile Name | Folder / Key | Mod Count | Target FPS | Primary Use Case |
|---|---|---|---|---|
| **Aetheris Legacy PvP** | `aetheris-ultimate-legacy-1.8.9` (`legacy`) | 58 mods | 500+ FPS | Competitive tournament and PvP, ultra-low latency, custom hit reg and textures. |
| **Aetheris Legacy Visual** | `aetheris-ultimate-legacy-visual-1.8.9` (`legacy-visual`) | 58 mods | 250+ FPS | Customized OptiFine shaders, dynamic water reflections, HD skybox. |
| **Aetheris Legacy Balanced** | `aetheris-ultimate-legacy-balanced-1.8.9` (`legacy-balanced`) | 58 mods | 400+ FPS | Classic 1.8.9 with smooth lighting, enhanced textures, and high stability. |
| **Aetheris Legacy Performance** | `aetheris-ultimate-legacy-performance-1.8.9` (`legacy-performance`) | 58 mods | 600+ FPS | Stripped-down pure maximum FPS configuration for 1.8.9. |

---

## Hardware Tuning & JVM Arguments
All Aetheris profiles are standardized with 8GB memory allocation (`-Xms4G -Xmx8G`) and advanced G1GC tuning parameters:
```
-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -XX:+OptimizeStringConcat -XX:+UseStringDeduplication -Djava.net.preferIPv4Stack=true -Dfile.encoding=UTF-8
```
"""

shaders_textures = """# Aetheris Ecosystem — Shaders & Resource Packs Guide

## Shaders Suite (`D:\\AetherisShare\\shaders\\`)

1. **Aetheris_Visual_Shader.zip** (Companion: `Aetheris_Visual_Shader.zip.txt`)
   - 4096 shadow map resolution, Volumetric Light samples: 12, POM depth: 40, SSS enabled on mobs and blocks.
   - Calibrated for RTX 40-Series mobile hardware delivering smooth 100+ FPS.
2. **Aetheris_Balanced_Shader.zip** (Companion: `Aetheris_Balanced_Shader.zip.txt`)
   - 2048 shadow map resolution, Volumetric Light samples: 6, POM depth: 25.
   - High visual fidelity with reduced thermal/power footprint.
3. **Aetheris_Extreme_Shader.zip** (Companion: `Aetheris_Extreme_Shader.zip.txt`)
   - 4096 shadow map resolution, Volumetric Light samples: 20, POM depth: 64, full LabPBR/LabSSS material reflections.
4. **Aetheris_Shader_Pack.zip** (Companion: `Aetheris_Shader_Pack.zip.txt`)
   - Dynamic godrays, water caustics, and lightweight deferred post-processing.
5. **Aetheris_Legacy_Shader_Pack.zip** (Companion: `Aetheris_Legacy_Shader_Pack.zip.txt`)
   - Optimized BSL v10.1.3 build for OptiFine 1.8.9 OpenGL 2.1/3.0 architecture.

### Keybinding Notice
- **Iris Instant Shader Toggle**: Bound to `K` (`key_iris.keybind.toggleShaders: key.keyboard.k`).
- CraftingTweaks compression keys have been deconflicted and remapped to prevent keypress interception.

---

## Resource Packs Suite (`D:\\AetherisShare\\resourcepacks\\`)

1. **Aetheris_Ultimate_32x.zip** (`pack_format: 88` [15, 88])
   - Master 32x high-definition resource pack for Modern 26.2.
   - 0 missing texture references across all 16,700+ assets.
   - 271 Custom Entity Model (CEM) files with Fresh Animations v1.10.5 and ETF/EMF support.
   - 98 paintings (52 vanilla + 46 dark paintings).
   - Custom Glowing Cyan & Gold Title screen banner (`edition_dark.png` and `edition.png`) + 24 custom splashes.
2. **Aetheris_Legacy_32x.zip** (`pack_format: 1`)
   - Master 32x resource pack tailored for Minecraft 1.8.9 OptiFine.
3. **Private Default.zip** (`pack_format: 1`)
   - Clean flat root archive layout without nested directories.
"""

troubleshooting = """# Aetheris Ecosystem — Troubleshooting & Maintenance

## 1. Lunar Client Profiles Not Visible
- Ensure Lunar Client was completely closed prior to installation.
- Verify `C:\\Users\\%USERNAME%\\.lunarclient\\db\\profiles.db` was updated. The installer automatically updates `profiles.db` with SQLite entries for all 8 profiles.
- Run `install.ps1 -Mode All` to re-register profiles in the SQLite database.

## 2. Keybinding Conflicts
- If pressing `K` does not toggle shaders:
  - Check `options.txt` to verify `key_iris.keybind.toggleShaders:key.keyboard.k` is set.
  - Verify CraftingTweaks compress keys are set to `key.keyboard.unknown` so they do not intercept container keypress events.

## 3. Distant Horizons & OpenGL Depth Rendering
- The ecosystem configures `DistantHorizons.toml` with:
  - `enableDistantHorizonsSupportingShaders = true`
  - `glErrorHandlingMode = "IGNORE"`
  - `overrideVanillaGLLogger = true`
- This prevents shader context initialization NPEs during deferred buffer creation.

## 4. JVM Memory & Out of Memory Errors
- All profiles require a minimum of 4GB and allocate 8GB (`-Xms4G -Xmx8G`).
- If you experience GC pauses, verify the G1GC flags in `jvm-options.txt` or `instance.cfg`.
"""

with open(os.path.join(docs_dir, "INSTALLATION_GUIDE.md"), "w", encoding="utf-8") as f:
    f.write(install_guide)

with open(os.path.join(docs_dir, "PROFILES_OVERVIEW.md"), "w", encoding="utf-8") as f:
    f.write(profiles_overview)

with open(os.path.join(docs_dir, "SHADERS_AND_TEXTURES.md"), "w", encoding="utf-8") as f:
    f.write(shaders_textures)

with open(os.path.join(docs_dir, "TROUBLESHOOTING.md"), "w", encoding="utf-8") as f:
    f.write(troubleshooting)

print("Documentation generated in D:\\AetherisShare\\docs\\")
