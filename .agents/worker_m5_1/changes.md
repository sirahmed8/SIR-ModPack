# Milestone 5 Change Log — Worker M5-1

## Summary of Changes

### 1. Instance Profile Matrix Parity (`instances/` - Feature 21)
- **`instances/26.2-ultra/`**:
  - Added `mmc-pack.json` with Fabric Loader 0.16.10, Intermediary 26.2, LWJGL 3.4.1 components.
  - Updated `instance.cfg` with full memory allocation parameters (`MinMemAlloc=6144`, `MaxMemAlloc=12288`, `group=Modern`, `AutomaticJava=true`, G1GC args).
- **`instances/26.2-balanced/`**:
  - Created `instance.cfg` with `MinMemAlloc=4096`, `MaxMemAlloc=8192`, `group=Modern`, `name=SIR 26 (Balanced 144+ FPS)`.
  - Created `mmc-pack.json` with Fabric Loader 0.16.10, Intermediary 26.2, LWJGL 3.4.1.
- **`instances/26.2-performance/`**:
  - Created directory and provisioned `instance.cfg` (`MinMemAlloc=3072`, `MaxMemAlloc=6144`, `group=Modern`, `name=SIR 26 (Competitive Speed)`).
  - Created `mmc-pack.json` with Fabric Loader 0.16.10, Intermediary 26.2, LWJGL 3.4.1.
  - Created `options.txt` (renderDistance: 8, simulationDistance: 6, graphicsMode: 1, smoothLighting: false, particles: 2).
  - Created `config/sodium-options.json` (leaves_quality: FAST, chunk_builder: IMMEDIATE, weather_quality: FAST).
  - Created `config/iris.properties` (enableShaders: false, shaderPack: OFF).
  - Provisioned matching `minecraft/` subfolder configurations.
- **`instances/1.8.9-ultra/`**:
  - Created directory and provisioned `instance.cfg` (`MinMemAlloc=3072`, `MaxMemAlloc=6144`, `group=Legacy`, `name=Legacy 1.8.9 Ultra Visuals`).
  - Created `mmc-pack.json` with Forge 11.15.1.2318 and Minecraft 1.8.9 components.
  - Created `options.txt` (renderDistance: 16, anisotropicFiltering: 8, fancyGraphics: true, ao: 2).
  - Created `optionsof.txt` (ofRenderDistanceChunks: 16, ofFastRender: false, ofFastMath: false, ofSmoothFps: true, ofSmoothWorld: true).
  - Created `optionsshaders.txt` (shaderPack=SIR_Extreme_Shader.zip).
  - Provisioned matching `minecraft/` subfolder configurations.
- **`instances/1.8.9-balanced/`**:
  - Created directory and provisioned `instance.cfg` (`MinMemAlloc=2048`, `MaxMemAlloc=4096`, `group=Legacy`, `name=Legacy 1.8.9 Ranked Bedwars`).
  - Created `mmc-pack.json` with Forge 11.15.1.2318 and Minecraft 1.8.9 components.
  - Created `options.txt` (renderDistance: 12, anisotropicFiltering: 4, fancyGraphics: true, ao: 2).
  - Created `optionsof.txt` (ofRenderDistanceChunks: 12, ofFastRender: false, ofFastMath: true, ofSmoothFps: true, ofSmoothWorld: true).
  - Created `optionsshaders.txt` (shaderPack=SIR_Balanced_Shader.zip).
  - Provisioned matching `minecraft/` subfolder configurations.
- **`instances/1.8.9-performance/`**:
  - Created directory and provisioned `instance.cfg` (`MinMemAlloc=1536`, `MaxMemAlloc=3072`, `group=Legacy`, `name=Legacy 1.8.9 Zero-Delay 500+ FPS`).
  - Created `mmc-pack.json` with Forge 11.15.1.2318 and Minecraft 1.8.9 components.
  - Created `options.txt` (renderDistance: 8, anisotropicFiltering: 1, fancyGraphics: false, ao: 1).
  - Created `optionsof.txt` (ofRenderDistanceChunks: 8, ofFastRender: true, ofFastMath: true, ofSmoothFps: false, ofSmoothWorld: false).
  - Created `optionsshaders.txt` (shaderPack=OFF).
  - Provisioned matching `minecraft/` subfolder configurations.

### 2. Automated E2E Verification Suite (`tests/test_instance_matrix_parity.py` - Feature 22)
- Created `tests/test_instance_matrix_parity.py` with 16 automated tests covering:
  - Physical directory presence across all 8 profiles.
  - `InstanceService.get_instances()` discovery and availability reporting (`available: True`).
  - `instances/instgroups.json` category partition (`Modern` vs `Legacy`).
  - `mmc-pack.json` component validation for Fabric Loader / Forge / LWJGL 3 / Minecraft.
  - `instance.cfg` memory overrides, group tags, and G1GC arguments parsing.
  - Tri-layer video preset injection across Modern (options.txt + sodium-options.json + iris.properties) and Legacy (options.txt + optionsof.txt + optionsshaders.txt).
  - Preset alias normalization (`fps`, `low`, `cinematic`, `boost`, `pvp`).
  - Dual-mode keybinding conversion (GLFW token strings vs numeric LWJGL 2 scancodes).
  - `NativeMinecraftRunner.inspect_instance_config` extraction of loader and memory parameters.
  - `calculate_ram_parameters` strict memory enforcement and dynamic G1GC region sizing.
  - Custom instance creation, cloning, and deletion safety lifecycle.
- Resolved race condition in `ProcessLogStreamer._exit_watcher` by awaiting tail worker thread flush before running crash analyzer.
- Full test discovery suite: 328/328 unit & integration tests passing with 100% OK.

### 3. Comprehensive Documentation Suite
- **`walkthrough.md`**: Created complete 5-milestone engineering walkthrough (M1 Core Engine, M2 Native JVM Pipeline, M3 Cyber-Dark Desktop UI, M4 Next.js 16 Web Hub, M5 Profile Matrix Parity & E2E Verification), architecture diagrams, empirical test logs, and reproduction instructions.
- **`PROJECT_ARCHITECTURE_EXPLANATION.md`**: Updated with system architecture blueprint, memory governor model, tri-layer preset engine, 8-profile matrix tables, cloud sync highway, and multi-layer security architecture.
- **`README.md`**: Updated with application overview, 8-profile matrix table, 1-click video presets guide, quickstart instructions, and legal policies index.
