# Architectural & Codebase Investigation Report: Feature 14 (1-Click Video Preset Engine)
**Milestone 3 — Desktop Client UI, Video Presets & Accounts**
**Explorer 2 Investigation Report**
**Date**: 2026-08-30
**Working Directory**: `D:\Projects\SIR ModPack\.agents\explorer_m3_2\`

---

## Executive Summary

Feature 14 provides a seamless, **Tri-Layer 1-Click Video Preset Engine** capable of instantly injecting synchronized graphics, display, shader, and performance configurations across both **Modern Minecraft (1.21.4 / 26.2 Fabric with Sodium + Iris)** and **Legacy Minecraft (1.8.9 Forge with OptiFine + BetterFps/FoamFix/Patcher)** as well as user-created custom instances.

This investigation analyzes the existing implementation across `development/launcher_core/` (bridge, instance_service, shaders_service, controls_service), `development/launcher_ui/` (launchpad, instance cards, settings), `instances/` (26.2, 26.2-ultra, 1.8.9, custom instances), and `tests/` (test_launcher_bridge.py, adversarial test suites).

---

## 1. Architectural Blueprint: The Tri-Layer Injection Model

The Video Preset Engine operates across three decoupled yet synchronized configuration layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       1-Click Video Preset Engine                           │
│                     (Ultra | Balanced | Competitive)                        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
 ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
 │       LAYER 1        │   │       LAYER 2        │   │       LAYER 3        │
 │  Vanilla options.txt │   │ Sodium Configuration │   │    Iris / OptiFine   │
 │   (Display/Quality)  │   │ (sodium-options.json)│   │  (Shaders Pipeline)  │
 └──────────────────────┘   └──────────────────────┘   └──────────────────────┘
            │                          │                          │
            ├─ Modern 26.2:            ├─ Modern 26.2:            ├─ Modern 26.2:
            │  • renderDistance        │  • quality (leaves,      │  • config/iris.properties
            │  • simulationDistance    │    clouds, blur,         │    enableShaders=true/false
            │  • graphicsMode          │    transparency, radius) │    shaderPack=Extreme/
            │  • biomeBlendRadius      │  • performance           │               Balanced/OFF
            │  • particles, mipmaps    │    (chunk_builder,       │
            │  • entityDistanceScaling │    animate_textures)     │
            │                          │                          │
            ├─ Legacy 1.8.9:           ├─ Legacy 1.8.9:           ├─ Legacy 1.8.9:
            │  • renderDistance        │  • optionsof.txt         │  • optionsshaders.txt
            │  • fancyGraphics, ao     │    (ofFastRender,        │    shaderPack=Extreme/
            │  • particles, clouds     │    ofDynamicLights,      │               Balanced/OFF
            │  • anisotropicFiltering  │    ofConnectedTextures)  │    antialiasing, shadowRes
```

---

## 2. Configuration Parameters Matrix (Preset Specifications)

### Layer 1: Vanilla `options.txt`

| Parameter | Ultra Visuals | Balanced (144+ FPS) | Competitive (Max FPS / 0ms) |
|---|---|---|---|
| **Modern 26.2** | | | |
| `renderDistance` | `16` | `12` | `8` |
| `simulationDistance` | `10` | `8` | `6` |
| `graphicsMode` | `0` (Fancy) | `0` (Fancy) | `1` (Fast) |
| `smoothLighting` | `true` | `true` | `false` |
| `biomeBlendRadius` | `15` | `15` | `3` |
| `entityDistanceScaling` | `1.5` | `1.0` | `0.8` |
| `entityShadows` | `true` | `true` | `false` |
| `particles` | `0` (All) | `0` (All) | `2` (Minimal) |
| `mipmapLevels` | `4` | `4` | `0` |
| `clouds` | `"fancy"` | `"fancy"` | `"false"` |
| `gamma` | `1.0` | `0.0` / `1.0` | `1.0` (Full Bright) |
| `maxFps` | `0` (Unlimited) | `0` (Unlimited) | `0` (Unlimited) |
| `enableVsync` | `false` | `false` | `false` |
| `guiScale` | `2` | `2` | `2` |
| `resourcePacks` | `["vanilla","file/SIR_Ultimate_Pack.zip"]` | `["vanilla","file/SIR_Ultimate_Pack.zip"]` | `["vanilla","file/SIR_Ultimate_Pack.zip"]` |
| `onboardAccessibility` | `"false"` | `"false"` | `"false"` |
| **Legacy 1.8.9** | | | |
| `renderDistance` | `16` | `12` | `8` |
| `fancyGraphics` | `true` | `true` | `false` |
| `ao` (Ambient Occlusion)| `2` (Maximum) | `2` (Maximum) | `0` (Off) |
| `smoothLighting` | `true` | `true` | `false` |
| `clouds` | `true` | `true` | `false` |
| `particles` | `0` (All) | `0` (All) | `2` (Minimal) |
| `anisotropicFiltering` | `8` | `4` | `1` (Off) |
| `mipmapLevels` | `4` | `4` | `0` |
| `resourcePacks` | `["SIR_Legacy_32x.zip"]` | `["SIR_Legacy_32x.zip"]` | `["SIR_Legacy_32x.zip"]` |
| `autoJump` | `false` | `false` | `false` |

---

### Layer 2: Sodium & OptiFine Options

#### Modern Sodium (`config/sodium-options.json`):
```json
// Ultra Preset
{
  "quality": {
    "leaves_quality": "CUTOUT",
    "weather_quality": "HIGH",
    "cloud_distance": 128,
    "menu_background_blur": 5,
    "improved_transparency": true,
    "weather_radius": 10,
    "vignette": true
  },
  "performance": {
    "chunk_builder": "SEMI_BLOCKING",
    "animate_only_visible_textures": true
  },
  "notifications": {
    "hide_donation_prompt": true
  }
}

// Balanced Preset
{
  "quality": {
    "leaves_quality": "CUTOUT",
    "weather_quality": "HIGH",
    "cloud_distance": 128,
    "menu_background_blur": 5,
    "improved_transparency": true,
    "weather_radius": 10,
    "vignette": true
  },
  "performance": {
    "chunk_builder": "SEMI_BLOCKING",
    "animate_only_visible_textures": true
  },
  "notifications": {
    "hide_donation_prompt": true
  }
}

// Competitive Preset
{
  "quality": {
    "leaves_quality": "FAST",
    "weather_quality": "FAST",
    "cloud_distance": 32,
    "menu_background_blur": 0,
    "improved_transparency": false,
    "weather_radius": 5,
    "vignette": false
  },
  "performance": {
    "chunk_builder": "IMMEDIATE",
    "animate_only_visible_textures": true
  },
  "notifications": {
    "hide_donation_prompt": true
  }
}
```

#### Legacy 1.8.9 OptiFine (`optionsof.txt`):
- **Ultra**: `ofRenderDistanceChunks:16`, `ofDynamicLights:1`, `ofCustomSky:true`, `ofCustomFonts:true`, `ofConnectedTextures:1`, `ofNaturalTextures:true`, `ofFastRender:false`, `ofFastMath:false`
- **Balanced**: `ofRenderDistanceChunks:12`, `ofDynamicLights:2`, `ofCustomSky:true`, `ofCustomFonts:true`, `ofConnectedTextures:2`, `ofNaturalTextures:false`, `ofFastRender:false`, `ofFastMath:true`
- **Competitive**: `ofRenderDistanceChunks:8`, `ofDynamicLights:3` (Off), `ofCustomSky:false`, `ofCustomFonts:false`, `ofConnectedTextures:3` (Off), `ofNaturalTextures:false`, `ofFastRender:true`, `ofFastMath:true`, `ofLazyChunkLoading:true`

---

### Layer 3: Shaders Pipeline

#### Modern Iris (`config/iris.properties`):
- **Ultra**:
  ```properties
  enableShaders=true
  shaderPack=SIR_Extreme_Shader.zip
  ```
- **Balanced**:
  ```properties
  enableShaders=true
  shaderPack=SIR_Balanced_Shader.zip
  ```
- **Competitive / Performance**:
  ```properties
  enableShaders=false
  shaderPack=OFF
  ```

#### Legacy Shaders (`optionsshaders.txt`):
- **Ultra**:
  ```properties
  shaderPack=SIR_Extreme_Shader.zip
  antialiasing=0
  shadowMapResolution=2048
  ```
- **Balanced**:
  ```properties
  shaderPack=SIR_Balanced_Shader.zip
  antialiasing=0
  shadowMapResolution=1024
  ```
- **Competitive**:
  ```properties
  shaderPack=OFF
  ```

---

## 3. Analysis of Existing Codebase & Services

### 1. `development/launcher_core/instance_service.py` (`apply_video_preset`)
- **Strengths**:
  - Implements atomic file writes using `atomic_write_text` and `atomic_write_json`.
  - Non-destructive `options.txt` parsing: reads existing options first into dictionary, overrides only target graphic keys, preserving custom keybindings, volume sliders, and narration flags.
  - Automatically targets both instance root and `minecraft/` subdirectory.
- **Identified Gaps & Enhancement Opportunities**:
  1. **Flexible Instance Resolution**: Currently looks up instances by `i["id"] == inst_id`. If given directory names (`26.2`, `1.8.9`, `26.2-ultra`, `sir-custom-test`) or custom profile IDs, resolution should fallback gracefully to `dir_name`, `instance_id`, or existing directory existence check.
  2. **1.8.9 Tri-Layer Completeness**: Currently updates only `options.txt` on 1.8.9. Should also inject `optionsof.txt` (OptiFine options) and `optionsshaders.txt` (OptiFine shader pipeline) to provide full parity with Modern 26.2.
  3. **Return Contract Parity**: `PROJECT.md` specifies `apply_video_preset(instance_name, preset_name)` -> `{"success": bool, "applied": list[str], "error": str}`. Returning `"applied": ["options.txt", "config/sodium-options.json", "config/iris.properties"]` provides rigorous traceability for test assertions.

### 2. `development/launcher_core/bridge.py`
- Exposes `apply_video_preset(inst_id="sir-26-ultra", preset_name="balanced")` directly to the webview JS frontend.
- Fully wired and non-blocking.

### 3. `development/launcher_ui/` Frontend Wiring
- `index.html`:
  - Launchpad card includes 3 dedicated 1-click preset buttons: Balanced, Ultra Visuals, Max FPS (`applyVideoPreset('...')`).
  - Instances matrix card includes 🖥️ preset modal prompt (`applyVideoPresetPrompt('${inst.id}')`).
- `js/launch.js`:
  - Exposes `window.applyVideoPreset(presetName, instId)` which invokes `window.pywebview.api.apply_video_preset(...)` and triggers responsive feedback toasts.
- `js/instances.js`:
  - Exposes `window.applyVideoPresetPrompt(instId)`.

### 4. `tests/` Test Infrastructure
- Current coverage in `test_launcher_bridge.py` has a basic smoke test (`test_video_presets_exist`).
- Milestone 3 requires a comprehensive test suite (Feature, Boundary, Cross-Feature, and Real-World Scenarios) validating:
  - All 3 preset tiers (Ultra, Balanced, Competitive) across Modern 26.2 and Legacy 1.8.9.
  - Non-destructive keybinding and audio preservation.
  - Valid JSON schema generation for Sodium and properties for Iris.
  - Custom profile preset application.

---

## 4. Recommended Implementation Strategy for Implementer

1. **Refine `InstanceService.apply_video_preset`**:
   - Enhance instance identifier matching (`id`, `instance_id`, `dir_name`, or filesystem path).
   - Add full 1.8.9 `optionsof.txt` and `optionsshaders.txt` injection.
   - Return structured response including `"applied": list[str]` of modified configuration paths.
2. **Preset Self-Healing**:
   - Ensure `heal_instance_if_needed` initializes default video presets if configurations are missing during launch.
3. **Automated Verification**:
   - Build a comprehensive test suite in `tests/test_video_presets.py` covering all permutations and corner cases with 100% assertions pass rate.
