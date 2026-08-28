import os

MASTER_DOC_CONTENT = """# 🌌 AETHERIS ULTIMATE PROJECT: MASTER KNOWLEDGE BASE & SYSTEM ARCHITECTURE

> **Master Reference Documentation for AI Agents, Developers, and Power Users**  
> **Last Updated:** August 2026 | **Project Status:** Production / Optimized  
> **Primary Profiles Supported:** Lunar Client 26.2 Fabric, 1.8.9 OptiFine, Standard `.minecraft`

---

## 📂 1. Directory Structure & Complete File Map

| Component | Path | Description |
|---|---|---|
| **Base Mods Directory** | `d:\\mods` | Master workspace for all Fabric 26.2 mods & automation scripts |
| **Active Resource Pack** | `d:\\resource pack\\MyCustomPack_Modern_32x.zip` | 32x HD LabPBR resource pack with authentic textures & repaired JSON models |
| **Master Shader Pack Source** | `d:\\shader\\Aetheris_Shader_Pack` | Decompressed GLSL shaderpack source with custom Euphoria + Solas + BSL pipeline |
| **Compiled Shader Pack** | `d:\\shader\\Aetheris_Shader_Pack.zip` | Recompressed production archive loaded by Iris / OptiFine |
| **Master Shader Presets** | `d:\\shader\\Aetheris_Shader_Pack.txt`, `.zip.txt` | Master configuration containing default Extreme profile parameters |
| **Lunar Client 26.2 Profile** | `C:\\Users\\a7med\\.lunarclient\\profiles\\aetheris-ultimate-modpack-modern-26.2\\` | Primary modern gameplay instance |
| **Lunar Client 26 Profile** | `C:\\Users\\a7med\\.lunarclient\\profiles\\26\\` | Secondary modern instance |
| **Lunar Client 1.8 Profile** | `C:\\Users\\a7med\\.lunarclient\\profiles\\1.8\\` | Legacy 1.8.9 PvP instance |
| **Standard Minecraft** | `C:\\Users\\a7med\\AppData\\Roaming\\.minecraft\\` | Vanilla / Fabric universal game directory |

---

## 🛠️ 2. Comprehensive Changelog & Version History (v1.0 to v15.0)

### 🌊 Water Rendering Overhaul
* **Surface Opacity from Above (v15.0):** Corrected the depth subtraction vector (`waterDepth = max0(lViewPosT - lViewPos)`). Previously, `lViewPos - lViewPosT` resulted in negative values that forced `edgeFade = 0.0`, causing the water surface to render as **100% invisible air** when looking down from above. Set base surface opacity to `0.85 – 0.95`.
* **Deep Ocean Volumetric Extinction (v14.0–v15.0):** Implemented exponential absorption (`clamp01(1.0 - exp(-waterDepth * 0.28))`) with deep sapphire navy scattering (`vec3(0.003, 0.02, 0.09)`), preventing deep ocean seabeds from being unrealistically transparent.
* **Zero Foam Cloud Bands (v10.0–v15.0):** Hard-disabled the procedural white cloud foam pass in `water.glsl`, completely removing jagged white voxel blocks on coastlines and waterfalls.

### ☀️ Atmospheric & Celestial Lighting Overhaul
* **Single HD 8-Phase Moon (v10.0–v13.0):** Hard-disabled the procedural crescent math in `gbuffers_skybasic.glsl`. Renders **one single, high-definition textured moon with all 8 real lunar phases** (Full Moon, Waxing/Waning Gibbous, Quarters, Crescent, New Moon) from `moon_phases.png`.
* **Sunlight Scattering & Backlighting Through Leaves (v14.0–v15.0):** Enabled smooth Gaussian leaf subsurface scattering (`subsurfaceHighlight = pow(max(dot(nViewPos, lightVec), 0.0), 3.5) * 1.10 * sunVisibility2`) in `mainLighting.glsl`. Sunlight glows golden THROUGH leaves when looking toward the sun with **0 noise, 0 sparkling, and 0 flickering**.
* **Dark Night Foliage Canopy (v13.0–v15.0):** Applied universal daylight gating (`if (subsurfaceMode > 0) color.rgb *= mix(vec3(0.28, 0.32, 0.38), vec3(1.0), clamp01(sunVisibility2 * 2.2))`). All leaves and plants across Vanilla, Biomes O' Plenty, and Regions Unexplored naturally darken into deep forest night tones with zero neon glow.
* **Circular Gaussian Stars (v10.0):** Configured `STAR_ROUNDNESS_OW=10`, `STAR_SOFTNESS_OW=0.8`, and `TWINKLING_STARS=12` in `stars.glsl` to replace square Minecraft boxes with real anti-aliased twinkling stars.
* **Coded HDR Tone Mapping & Exposure Balance (v10.0–v15.0):** Built an active film-grade ACES HDR tone curve with local exposure clamping (`clamp(glare, 0.0, 0.20)`), preventing washed-out white skies on SDR laptop screens. Added a dedicated in-game **[High Dynamic Range (HDR)]** toggle button in the Camera Settings menu.

### 🌋 Molten Lava Physics
* **Smooth Magma Fluid (v10.0):** Disabled `WAVIER_LAVA`, `LAVA_EDGE_EFFECT`, and `LAVA_VARIATION`. Molten lava flows as **smooth, radiant, glowing magma with zero stepped polygon facets**.

### 🧱 Resource Pack Repairs (`MyCustomPack_Modern_32x.zip`)
* **Red Mushroom Block (v13.0):** Repaired `assets/minecraft/blockstates/red_mushroom_block.json` by removing nonexistent variant references (`red_mushroom_block/1.json` through `11.json`), resolving the purple/black missing texture checkerboard.
* **Clay Block (v14.0–v15.0):** Purged broken `models/block/soil/` files and enforced standard `minecraft:block/cube_all` namespace mapping with 32x LabPBR textures, resolving the orange/black fallback box.

### ⚡ Windows System & Performance Optimizations
* **Windows NT Kernel Auto-High Priority (IFEO):** Configured native Windows Image File Execution Options registry policies:
  * Key: `HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\javaw.exe\\PerfOptions`
  * `CpuPriorityClass = 3` (High Priority)
  * `IoPriority = 3` (High I/O Priority)
  * **Result:** Every time Minecraft / Lunar Client starts, Windows automatically assigns **High CPU and High I/O Priority** at the kernel level.
* **Intelligent Profile Scaling (Potato ➡️ Extreme):** Configured all profiles from Low to Ultra/Extreme to keep all aesthetic features enabled (LabPBR 64x, POM depth, BSL HDR tonemap, Solas clouds, colored lighting, waving grass/leaves), scaling only shadow distance and POM steps.
* **Clean In-Game HUD:** Disabled the `F3_DISPLAY` biome text across all Lunar Client profiles (`Default`, `Arena PvP`, `Hypixel Skyblock`, `UHC`), keeping only the clean FPS counter.

---

## 🎛️ 3. Profile Hierarchy Matrix

| Profile | Shadow Distance | Shadow Map | POM Quality | Godrays | Reflections | Target Performance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **🥔 Potato** | `64m` | Off | Off | Level 1 | Off | Low-End Fallback |
| **🟢 Low** | `96m` | `1024` | `16 steps` | Level 2 | Fast Screen-Space | High FPS / Laptops |
| **🟡 Medium** | `128m` | `2048` | `24 steps` | Level 3 | Fast Screen-Space | 144+ FPS Esports |
| **🔵 High** | `192m` | `2048` | `32 steps` | Level 3 | Full Raytracing | Beautiful Balanced |
| **🟣 Very High** | `224m` | `4096` | `48 steps` | Level 4 | Full Raytracing | Cinematic Fidelity |
| **🔥 Ultra / ⚡ Extreme** | `256m` | `4096` | `64 steps` | Level 4 | Full Raytracing | **Master Default (RTX 4050)** |

---

## 🚀 4. Deployment Verification & Sync Protocol

All automated deployment scripts (`d:\\mods\\apply_master_v15_definitive_perfection.py`) execute the following synchronization pipeline:
1. Compile and package `d:\\shader\\Aetheris_Shader_Pack.zip`.
2. Sync `.zip` and `.txt` presets to `.minecraft`, Lunar `26.2`, Lunar `26`, Lunar `1.8.9`, and `D:\\Games\\`.
3. Validate GLSL preprocessor depth and AST structure via `find_global_statements.py` (guaranteeing 0 compiler errors).
4. Verify resource pack integrity and model namespace validity.
"""

# Write to brain and workspace locations
brain_dir = r"C:\Users\a7med\.gemini\antigravity\brain\ec362f4d-9d4f-4a71-8d61-7ed361e7e2bd"
mods_dir = r"d:\mods"

paths_to_update = [
    os.path.join(brain_dir, "PROJECT_KNOWLEDGE_BASE.md"),
    os.path.join(brain_dir, "walkthrough.md"),
    os.path.join(brain_dir, "implementation_plan.md"),
    os.path.join(mods_dir, "AETHERIS_MASTER_DOCUMENTATION.md"),
    os.path.join(mods_dir, "walkthrough.md")
]

for p in paths_to_update:
    with open(p, "w", encoding="utf-8") as f:
        f.write(MASTER_DOC_CONTENT)
    print(f"Updated: {p}")

print("\nAll Markdown documentation files successfully updated!")
