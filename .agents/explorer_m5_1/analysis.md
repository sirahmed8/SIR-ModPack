# Milestone 5 Analysis: Instance Profile Matrix Parity & E2E Verification

## Executive Summary
Milestone 5 (Features 21 & 22) targets complete Instance Profile Matrix Parity and End-to-End verification across all 8 standard profile archetypes in the SIR Minecraft Ecosystem: 4 Modern Fabric 26.2 profiles and 4 Legacy Forge 1.8.9 profiles.

During this investigation, we audited:
1. instances/ filesystem structure, file configurations, mod catalogs, and Prism instgroups.json.
2. development/launcher_core/instance_service.py, ideo_preset_service.py, controls_service.py, 
ative_runner.py, clone_service.py, and ridge.py.
3. Health diagnosis via python ecosystem_doctor.py.
4. The full automated test harness in 	ests/ (312 tests executing with 100% pass rate).

---

## 1. Instance Profile Matrix Inventory & Parity Audit

The ecosystem roadmap specifies an 8-profile matrix across Modern (26.2 Fabric) and Legacy (1.8.9 Forge).

| # | Profile ID | Display Name | Archetype / Loader | Target Dir | Status on Disk | Missing Components |
|---|------------|--------------|-------------------|------------|----------------|--------------------|
| 1 | sir-26-ultra | SIR 26 (Ultra Visuals) | Modern Fabric 26.2 | instances/26.2-ultra/ | Incomplete (1597 files) | Missing mmc-pack.json; instance.cfg lacks memory overrides/group; options.txt has balanced renderDistance (12) instead of ultra (16). |
| 2 | sir-26-balanced | SIR 26 (Balanced 144+ FPS) | Modern Fabric 26.2 | instances/26.2-balanced/ | Partial (6 files) | Missing instance.cfg, mmc-pack.json, minecraft/mods/ catalog, and GLFW keybindings in options.txt. |
| 3 | sir-26-competitive | SIR 26 (Competitive Speed) | Modern Fabric 26.2 | instances/26.2-performance/ | **Missing** | Entire directory absent from disk. |
| 4 | sir-26-vanilla | SIR 26 (Modular Vanilla+) | Modern Fabric 26.2 | instances/26.2/ | Complete (261 files) | Fully populated with mmc-pack.json, instance.cfg, options.txt, sodium-options.json, iris.properties, 238 mod JARs. |
| 5 | sir-189-pvp | Legacy 1.8.9 PvP Battle Suite | Legacy Forge 1.8.9 | instances/1.8.9/ | Complete (140 files) | Fully populated with mmc-pack.json, instance.cfg, options.txt, optionsof.txt, optionsshaders.txt, 57 mod JARs. |
| 6 | sir-189-ultra | Legacy 1.8.9 Ultra Visuals | Legacy Forge 1.8.9 | instances/1.8.9-ultra/ | **Missing** | Entire directory absent from disk. |
| 7 | sir-189-balanced | Legacy 1.8.9 Ranked Bedwars | Legacy Forge 1.8.9 | instances/1.8.9-balanced/ | **Missing** | Entire directory absent from disk. |
| 8 | sir-189-competitive | Legacy 1.8.9 Zero-Delay 500+ FPS | Legacy Forge 1.8.9 | instances/1.8.9-performance/ | **Missing** | Entire directory absent from disk. |

---

## 2. Configuration & Metadata Specification for Matrix Profiles

### A. Modern Fabric 26.2 Archetypes (4 Profiles)

Each Modern profile must contain:
1. **mmc-pack.json**:
`json
{
   components: [
    {cachedName: LWJGL 3, cachedVersion: 3.4.1, cachedVolatile: true, dependencyOnly: true, uid: org.lwjgl3, version: 3.4.1},
    {cachedName: Minecraft, cachedVersion: 26.2, important: true, uid: net.minecraft, version: 26.2},
    {cachedName: Intermediary Mappings, cachedVersion: 26.2, cachedVolatile: true, dependencyOnly: true, uid: net.fabricmc.intermediary, version: 26.2},
    {cachedName: Fabric Loader, cachedVersion: 0.19.3, uid: net.fabricmc.fabric-loader, version: 0.19.3}
  ],
  formatVersion: 1
}
`
2. **instance.cfg**:
`ini
[General]
ConfigVersion=1.3
InstanceType=OneSix
iconKey=sir_crystal
name=<PROFILE_DISPLAY_NAME>
group=Modern
AutomaticJava=true
OverrideJavaLocation=true
JavaPath=C:/Users/a7med/AppData/Roaming/SIR ModPack/runtime/java-25/bin/javaw.exe
OverrideJavaArgs=true
OverrideMemory=true
MinMemAlloc=4096
MaxMemAlloc=8192
JvmArgs=-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication
`
3. **options.txt**: Modern GLFW token strings (key.keyboard.f, key.keyboard.left.shift, key.keyboard.space, key.mouse.left, key.mouse.right), ersion:3465, esourcePacks:[\vanilla\,\file/SIR_Ultimate_Pack.zip\], onboardAccessibility:false, and profile-specific graphics settings.
4. **config/sodium-options.json**:
   - 26.2-ultra & 26.2-balanced: CUTOUT leaves, HIGH weather, 128 cloud distance, SEMI_BLOCKING chunk builder.
   - 26.2-performance: FAST leaves, FAST weather, 32 cloud distance, IMMEDIATE chunk builder.
5. **config/iris.properties**:
   - 26.2-ultra: nableShaders=true, shaderPack=SIR_Extreme_Shader.zip
   - 26.2-balanced: nableShaders=true, shaderPack=SIR_Balanced_Shader.zip
   - 26.2-performance & 26.2: nableShaders=false, shaderPack=OFF
6. **minecraft/mods/**: 238 Fabric mods catalog.

---

### B. Legacy Forge 1.8.9 Archetypes (4 Profiles)

Each Legacy profile must contain:
1. **mmc-pack.json**:
`json
{
  components: [
    {
      cachedName: Minecraft,
      cachedVersion: 1.8.9,
      important: true,
      uid: net.minecraft,
      version: 1.8.9
    },
    {
      cachedName: Forge,
      cachedVersion: 11.15.1.2318,
      important: true,
      uid: net.minecraftforge,
      version: 11.15.1.2318
    }
  ],
  formatVersion: 1
}
`
2. **instance.cfg**:
`ini
[General]
ConfigVersion=1.3
InstanceType=OneSix
iconKey=sir_crystal
name=<PROFILE_DISPLAY_NAME>
group=Legacy
AutomaticJava=true
OverrideJavaLocation=true
JavaPath=C:/Program Files/Java/jre1.8.0_503/bin/javaw.exe
OverrideJavaArgs=true
OverrideMemory=true
MinMemAlloc=2048
MaxMemAlloc=4096
JvmArgs=-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:+AlwaysPreTouch -XX:+UseStringDeduplication -XX:ParallelGCThreads=4
`
3. **options.txt**: Legacy numeric LWJGL 2 scancodes (key_key.sprint:33, key_key.sneak:42, key_key.jump:57, key_key.togglePerspective:47, key_key.attack:-100, key_key.use:-99), esourcePacks:[\SIR_Legacy_32x.zip\].
4. **optionsof.txt**:
   - 1.8.9-ultra: ofRenderDistanceChunks:16, ofFastRender:false, ofFastMath:false, ofSmoothFps:true, ofAo:2, ofClouds:1, ofTrees:2.
   - 1.8.9-balanced: ofRenderDistanceChunks:12, ofFastRender:false, ofFastMath:true, ofSmoothFps:true, ofAo:2, ofClouds:1, ofTrees:2.
   - 1.8.9-performance & 1.8.9: ofRenderDistanceChunks:8, ofFastRender:true, ofFastMath:true, ofSmoothFps:false, ofAo:1, ofClouds:3, ofTrees:1.
5. **optionsshaders.txt**:
   - 1.8.9-ultra: shaderPack=SIR_Extreme_Shader.zip
   - 1.8.9-balanced: shaderPack=SIR_Balanced_Shader.zip
   - 1.8.9-performance & 1.8.9: shaderPack=OFF
6. **minecraft/mods/**: 57 Forge mods catalog.

---

## 3. Subsystem Cross-Matrix Compatibility Findings

### 1. Profile Discovery & Availability (InstanceService.get_instances())
- In instance_service.py, get_instances() computes instance[\available\] = os.path.isdir(instance[\instancePath\]).
- Currently, sir-26-competitive, sir-189-ultra, sir-189-balanced, and sir-189-competitive return vailable: False.
- Once the directory matrix is fully populated, all 8 profiles return vailable: True.

### 2. Video Preset Injection (VideoPresetService & InstanceService.apply_video_preset())
- VideoPresetService correctly distinguishes between Modern (26.2) and Legacy (1.8.9) based on version hint, directory name, or instance ID.
- Dual-mode target handling:
  - Fabric (26.2): Updates options.txt, writes config/sodium-options.json, writes config/iris.properties.
  - Forge (1.8.9): Updates options.txt, writes optionsof.txt, writes optionsshaders.txt.
- Successfully verified on both existing and new instance folders.

### 3. Keybinding Injection (ControlsService.apply_control_profile())
- ControlsService supports dual-mode keybinding conversion:
  - MODERN_GLFW: outputs token strings like key.keyboard.f, key.mouse.4.
  - LEGACY_LWJGL2: outputs scancodes like 33, -97.
- Verified keybinding aliases (key_key.togglePerspective vs key_key.perspective, key_of.key.zoom vs key_key.zoom).

### 4. Custom Instance Provisioning (InstanceService.create_custom_instance())
- Creates isolated Prism-compatible instances in instances/sir-custom-<name>.
- Auto-detects runtime requirements (Java 8 vs 17 vs 21/25).
- Generates mmc-pack.json with correct loader components (Fabric, Forge, NeoForge, Quilt, Vanilla).
- Persists to custom_instances.json and launcher_settings.json.

### 5. Native Launch Engine Classpath Assembly (NativeMinecraftRunner)
- NativeMinecraftRunner.inspect_instance_config() extracts loader and Minecraft version from mmc-pack.json and instance.cfg.
- Fabric 26.2 classpath builds 97 JARs (Fabric Loader 0.19.3, Intermediary Mappings 26.2, ASM 9.10.1, Sponge Mixin 0.17.4).
- Forge 1.8.9 classpath builds 50 JARs (Forge 11.15.1.2318, LaunchWrapper 1.12, ASM 5.0.3).

---

## 4. Implementation Recommendations for Milestone 5

1. **Matrix Provisioning**:
   - Provision instances/26.2-performance, instances/1.8.9-ultra, instances/1.8.9-balanced, and instances/1.8.9-performance.
   - Repair instances/26.2-balanced and instances/26.2-ultra by adding complete mmc-pack.json and instance.cfg.
   - Ensure all 8 instances have proper options.txt, config/sodium-options.json / config/iris.properties (for Modern) and optionsof.txt / optionsshaders.txt (for Legacy), along with their corresponding mod catalogs (minecraft/mods/).

2. **Self-Healing Hardening in instance_service.py**:
   - Enhance heal_instance_if_needed to automatically synthesize complete mmc-pack.json and instance.cfg if missing from any profile directory.
   - Align init_default_instances() so that dir_name and instance_id consistently point to each profile directory (26.2-ultra, 26.2-balanced, 26.2-performance, 26.2, 1.8.9-ultra, 1.8.9-balanced, 1.8.9-performance, 1.8.9).

3. **Automated E2E Test Suite (Feature 22)**:
   - Add 	ests/test_instance_matrix_parity.py covering:
     - 8-profile matrix directory existence and metadata completeness.
     - mmc-pack.json component validation across Modern Fabric and Legacy Forge.
     - instance.cfg key validation (JavaPath, JvmArgs, memory limits, group, name).
     - Dual-mode video presets injection across all 8 profiles.
     - Dual-mode keybinding injection across GLFW and LWJGL 2 formats.
     - Custom instance creation, cloning, and deletion lifecycle.
     - Native runner classpath assembly across all matrix permutations.
   - Verify python ecosystem_doctor.py passes 100% with 0 issues.
