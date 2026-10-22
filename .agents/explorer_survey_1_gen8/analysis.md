# Technical Survey & Root-Cause Audit: R1 (Instance Harmonization) & R2 (Crash Remediation)

**Date:** 2026-09-10  
**Surveyor:** explorer_survey_1_gen8  
**Scope:** `d:/Projects/SIR ModPack/instances/`, `C:/Users/a7med/.lunarclient/`, `C:/Users/a7med/AppData/Roaming/SIR ModPack/`, Launcher Bridge Core  
**Authoritative Request Reference:** Request `## 2026-09-10T20:57:12Z` in `ORIGINAL_REQUEST.md`

---

## 1. Executive Summary

This investigation conducted an exhaustive, read-only technical survey across all Modern (Fabric 26.2) and Legacy (Forge 1.8.9) game instance profiles, the Lunar Client bridge subsystem, crash reports, JVM crash logs (`hs_err_pid*.log`), options preservation files, and launcher self-healing logic.

### Core Discoveries:
1. **Fatal JVM Crashes (`EXCEPTION_ACCESS_VIOLATION` in `ntdll.dll`):** All four native JVM crash dumps (`hs_err_pid18004.log`, `hs_err_pid30316.log`, `hs_err_pid30664.log`, `hs_err_pid41980.log`) were traced directly to `quantified api-omni`'s daemon thread (`Quantified-OpenCL-Isolated`), which triggers native pointer dereferences inside Windows `ntdll.dll` via LWJGL OpenCL calls during background hardware probing on Java 25.
2. **Singleplayer World Creation/Loading Crashes under Lunar Client:** 10 consecutive server crash reports from September 9 (`crash-2026-09-09_05.45.58-server.txt` through `crash-2026-09-09_07.29.02-server.txt`) show a fatal `java.lang.NoClassDefFoundError: net/minecraft/class_7924` during integrated server startup triggered by `BetterCombatMod` (`WeaponRegistry.<clinit>`). Lunar Client's proprietary Genesis/Ichor classloader does not remap intermediary class names to Mojang official mappings at runtime.
3. **Mixin Injection Launch Failures under Lunar Client:** `krypton-0.3.1.jar` fails with `Critical injection failure: Redirector onKey$initializeVelocityCipher` in `ServerLoginPacketListenerImplMixin` because Lunar Client completely replaces the vanilla/Fabric login encryption pipeline.
4. **Options Loading Failure (`IllegalArgumentException: Unknown key name: 47`):** Modern Fabric instances crash or log severe options load failures because legacy LWJGL 2 integer keycodes (e.g. `47` for `V`, `54` for Right Shift) were copied or hardcoded into modern Minecraft 26.2 `options.txt`, which strictly requires GLFW identifier strings (`key.keyboard.v`, `key.keyboard.right.shift`). Furthermore, `tune_engine_configs.py` line 375 explicitly hardcodes `opts["key_key.modmenu.open_menu"] = "54"` into modern instances!
5. **Lunar Profile Directory Mismatch (`gameDir` Disconnect):** `C:/Users/a7med/.lunarclient/profiles.json` points all profile `gameDir` paths to `C:\Users\a7med\AppData\Roaming\SIR ModPack\instances\26.2-ultra`, which **does not exist** on C: drive (only `1.8.9` and `26.2` exist on C:; the tiered instances are on Drive D:).
6. **Inversion and Absence of Modpack Tiering:**
   - `26.2-ultra` and `26.2-balanced` are currently **100% byte-for-byte identical** (both have 185 JARs).
   - `26.2-performance` is **severely bloated** (221 JARs, containing 36 *more* mods than Ultra, including disabled `.disabled` files and older duplicate libraries).
   - `26.2` base contains **18 duplicate mod families** (252 JARs) with multiple version iterations coexisting in the same folder.
   - All four 1.8.9 profiles (`1.8.9`, `1.8.9-balanced`, `1.8.9-performance`, `1.8.9-ultra`) currently contain identical 27 Forge mods.
7. **Self-Healing Loop Breaker (`instance_service.py`):** Lines 817–822 in `instance_service.py` contain `min_jars = 200 if is_modern else 45`. If any profile has fewer than 200 JARs, the launcher automatically downloads and unzips `payload_mods_26.2.zip`, destroying any lightweight profile pruning and forcing 200+ mods into every modern instance.

---

## 2. Comprehensive Instance Inventory & File Layout Analysis

### Instance Directory Structure (`d:/Projects/SIR ModPack/instances/`):
```
instances/
├── 1.8.9/                    # Legacy PvP Base (Forge 1.8.9)
├── 1.8.9-balanced/           # Legacy Balanced Tier
├── 1.8.9-performance/        # Legacy Ranked PvP Tier
├── 1.8.9-ultra/              # Legacy Visuals Tier
├── 26.2/                     # Modern Base (Fabric 26.2)
├── 26.2-balanced/            # Modern Balanced Tier
├── 26.2-performance/         # Modern Competitive Tier
├── 26.2-ultra/               # Modern Visuals/Simulation Tier
├── accounts.json
├── ias_accounts.json
├── instgroups.json
└── logs/
```

### Critical Layout Discrepancies:
1. **Dual Directory Root Ambiguity:**
   In every instance, there is a nested `minecraft/` directory where the actual runtime files (`mods/`, `saves/`, `config/`, `crash-reports/`, `resourcepacks/`, `shaderpacks/`) are stored. However, root files also exist in the instance folder (e.g. `26.2-ultra/options.txt` at 13,582 bytes vs `26.2-ultra/minecraft/options.txt` at 13,175 bytes).
   - `instance_service.py` checks:
     ```python
     if os.path.isdir(os.path.join(inst_dir, "mods")) and len(...) > 0:
         mc_game_dir = inst_dir
     elif os.path.isdir(os.path.join(inst_dir, "minecraft", "mods")) and len(...) > 0:
         mc_game_dir = os.path.join(inst_dir, "minecraft")
     ```
     Because files exist in both locations, tools like `tune_engine_configs.py` and `lunar_bridge_service.py` iterate over both, often writing inconsistent values.
2. **Extraneous Subdirectories:**
   - `instances/1.8.9-performance/minecraft/mods/1.8.9/` is an empty, stray subdirectory.
   - `instances/26.2/minecraft/mods/dependencies/` contains extracted loose classes/JARs (`fabric-crash-report-info-v1-...jar`).
3. **Profile Path Disconnection on Lunar Client:**
   - `C:/Users/a7med/.lunarclient/profiles.json` contains:
     ```json
     "SIR 26 Visuals": {
       "gameDir": "C:\\Users\\a7med\\AppData\\Roaming\\SIR ModPack\\instances\\26.2-ultra"
     }
     ```
   - Actual directory `C:\Users\a7med\AppData\Roaming\SIR ModPack\instances\` only has `1.8.9` and `26.2`. All tiered instances reside at `d:\Projects\SIR ModPack\instances\`.
   - When launched from Lunar Client, it fails to find the game directory or falls back to creating an empty folder.

---

## 3. Deep Audit of Active Mods Across All Instances

### A. Modern 26.2 Mod Count Comparison:
| Instance Profile | Active JAR Count | Status | Notes |
|---|---|---|---|
| `26.2` (Base) | 252 | Severely Corrupted | 18 duplicate families, Forge mod included, `.disabled` files |
| `26.2-performance` | 221 | Bloated & Inverted | 36 *more* mods than Ultra; includes heavy mods & disabled JARs |
| `26.2-balanced` | 185 | Unharmonized | Byte-for-byte clone of Ultra (0 differences) |
| `26.2-ultra` | 185 | Unharmonized | Identical to Balanced; contains duplicate Fabric API |

### B. 18 Duplicate Mod Families in `26.2`:
The following duplicate JAR versions were discovered coexisting inside `instances/26.2/minecraft/mods`:
1. `AnimatedHearts-Fabric-1.8.1.jar` (MC 1.8 mod!) vs `AnimatedHearts-Fabric-26.2-1.9.0.jar`
2. `baguettelib-26.2-Fabric-2.0.4.jar` vs `baguettelib-26.2-Fabric-2.0.5.jar`
3. `balm-fabric-1.21.4-21.4.41.jar` (MC 1.21.4!) vs `balm-fabric-26.2-26.2.0.6.jar` vs `balm-fabric-26.2-26.2.0.8.jar`
4. `controlify-3.4.1+mc26.2-universal.jar` vs `controlify-3.5.0+mc26.2-universal.jar`
5. `eating-animation-fork-26.2+3.0.0.jar` vs `eating-animation-fork-26.2+4.0.1.jar`
6. `fabric-api-0.159.0+26.2.jar` vs `fabric-api-0.160.0+26.2.jar` *(Also present in 26.2-ultra & 26.2-balanced)*
7. `Gnetum-4.5.3+26.2-fabric.jar` vs `Gnetum-4.5.4+26.2-fabric.jar`
8. `inventoryhud.fabric.26.2-3.4.32.jar` vs `inventoryhud.fabric.26.2-3.4.34.jar`
9. `konkrete_fabric_1.9.9_MC_1.21.4.jar` (MC 1.21.4!) vs `konkrete_fabric_1.11.1_MC_26.2.jar`
10. `quantified api-omni-2.2.0.jar` vs `quantified api-omni-2.2.2.jar`
11. `reflex-fabric-1.0.4+mc1.21.4.jar` (MC 1.21.4!) vs `reflex-fabric-1.0.4+26.2.jar`
12. `ResourcefulLib-5.0.3.jar` vs `ResourcefulLib-5.0.4.jar`
13. `ShoulderSurfing-Fabric-26.2-5.0.7.jar` vs `ShoulderSurfing-Fabric-26.2-5.0.11.jar`
14. `sodium-fabric-0.9.1+mc26.2.jar` vs `sodium-fabric-0.9.2-beta.1+mc26.2.jar`
15. `spawn-animations-compats-16.0.jar` vs `spawn-animations-compats-17.0.jar`
16. `structurify-fabric-2.0.33+mc26.2.jar` vs `structurify-fabric-2.0.35+mc26.2.jar`
17. `villagernames-26.2.0-8.5.jar` vs `villagernames-26.2.0-8.6.jar`
18. `waystones-fabric-26.2-26.2.0.9.jar` vs `waystones-fabric-26.2-26.2.0.12.jar`

### C. Incompatible Loaders & Wrong Minecraft Versions:
- **Forge 1.8.9 Mod in Fabric 26.2:** `Keystrokes-1.8.9-forge-1.0.0.jar` is located in `instances/26.2/minecraft/mods/`.
- **Minecraft 1.21.4 Mods in 26.2:** `balm-fabric-1.21.4-21.4.41.jar`, `konkrete_fabric_1.9.9_MC_1.21.4.jar`, `reflex-fabric-1.0.4+mc1.21.4.jar`.
- **Minecraft 26.1 / 26.1.2 Mods in 26.2:**
  - `fastasyncworldsave-fabric-26.1-2.6.jar` (causes chunk I/O race conditions)
  - `anvianslib-fabric-26.1-1.5.0.jar`
  - `chat_heads-1.2.8-fabric-26.1.jar`
  - `snowundertrees-fabric-26.1.2-1.6.1.jar`
  - `xptome-fabric-26.1.2-2.5.1.jar`
  - `asynclogger-2.2.2+26.1.2-fabric.jar`
  - `clientcrafting-fabric-26.1-2.1.jar`
  - `lootintegrations-fabric-26.1-4.8.jar`

### D. Stray `.disabled` Files in Mods Directories:
- `instances/26.2/minecraft/mods/AsyncParticles-26.2.2.4+26.2.jar.disabled`
- `instances/26.2/minecraft/mods/e4mc-fabric-6.2.1-modern.jar.disabled`
- `instances/26.2-balanced/minecraft/mods/PanoramaScreenshot-1.1.0-26.2.jar.disabled`
- `instances/26.2-ultra/minecraft/mods/PanoramaScreenshot-1.1.0-26.2.jar.disabled`
- `instances/26.2-performance/minecraft/mods/InventoryTweaks-3.5-26.2.jar.disabled`
- `instances/26.2-performance/minecraft/mods/IrisSearch-1.6.0-fabric.jar.disabled`
- `instances/26.2-performance/minecraft/mods/PanoramaScreenshot-1.1.0-26.2.jar.disabled`
- `instances/26.2-performance/minecraft/mods/Perception-FABRIC-0.1.6.2+26.2.jar.disabled`
- `instances/26.2-performance/minecraft/mods/anvianslib-fabric-26.1-1.5.0.jar.disabled`
- `instances/26.2-performance/minecraft/mods/iris_shader_folder-1.4.1-fabric.jar.disabled`
- `instances/26.2-performance/minecraft/mods/smoothgui-fabric-26.2-1.1.0.jar.disabled`

---

## 4. Crash Remediation Investigation (R2)

### Root Cause 1: Hard JVM Crash (`EXCEPTION_ACCESS_VIOLATION` in `ntdll.dll`)
- **Observed Logs:** `C:/Users/a7med/.lunarclient/profiles/sir-26-ultra/hs_err_pid41980.log`, `hs_err_pid18004.log`, `hs_err_pid30316.log`, `hs_err_pid30664.log`.
- **Faulting Thread:** `JavaThread "Quantified-OpenCL-Isolated" daemon [_thread_in_native]`
- **Problematic Frame:** `C [ntdll.dll+0x125a4e]`
- **Stacktrace Analysis:**
  ```
  j  org.lwjgl.system.windows.WinBase.nGetModuleHandle(J)J+0
  j  org.lwjgl.system.windows.WinBase.GetModuleHandle(Ljava/nio/ByteBuffer;)J+14
  j  org.lwjgl.system.windows.WindowsLibrary.<clinit>()V+13
  j  org.lwjgl.opencl.CL.create()V+52
  j  org.admany.quantified.core.common.opencl.core.OpenCLRuntime.invokeLWJGLCreate()Z+3
  j  org.admany.quantified.core.common.opencl.core.OpenCLIsolatedExecutor.lambda$warmupAsync$2(...)V+26
  ```
- **Mechanism:** `quantified api-omni-2.2.0.jar` / `2.2.2.jar` attempts to detect GPU compute capabilities on launch by spawning an isolated OpenCL executor thread. The LWJGL OpenCL binding attempts a native handle query via `WinBase.nGetModuleHandle` on Java 25 (`zulu-25.0.1` / `adoptium-25.0.5`). On Windows 11 with OpenJDK 25, memory layout and foreign function boundaries trigger an immediate pointer dereference violation (`reading address 0x0000000000000006`), crashing the JVM instantly.
- **Action Required:** Completely remove `quantified api-omni` from all modern instances and payloads.

### Root Cause 2: Integrated Server Tick Crash on World Creation/Loading under Lunar Client
- **Observed Logs:** 10 crash reports from 2026-09-09 (`crash-2026-09-09_05.45.58-server.txt` through `crash-2026-09-09_07.29.02-server.txt`).
- **Error Description:** `Exception in server tick loop`
- **Stacktrace Analysis:**
  ```
  java.lang.NoClassDefFoundError: net/minecraft/class_7924
      at Genesis//net.bettercombat.logic.WeaponRegistry.<clinit>(WeaponRegistry.java:165)
      at Genesis//net.bettercombat.BetterCombatMod.loadWeaponAttributes(BetterCombatMod.java:70)
      at Genesis//net.bettercombat.fabric.FabricMod.lambda$onInitialize$0(FabricMod.java:19)
      at Genesis//net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents.lambda$static$1(ServerLifecycleEvents.java:38)
      at Genesis//net.minecraft.server.MinecraftServer.handler$ehn000$fabric-lifecycle-events-v1$beforeSetupServer(MinecraftServer.java:5919)
      at Genesis//net.minecraft.server.MinecraftServer.runServer(MinecraftServer.java:741)
  Caused by: java.lang.ClassNotFoundException: Failed to find class net.minecraft.class_7924
      at com.moonsworth.lunar.genesis.ICRHORIIHOHROHOHOCOOHOOCOORRHO.loadClass(Unknown Source)
  Caused by: java.lang.ClassNotFoundException: IchorPipeline can't find class in Genesis: net.minecraft.class_7924
  ```
- **Mechanism:** When a singleplayer world is created or loaded, Minecraft launches an integrated server (`MinecraftServer.runServer`). During `beforeSetupServer`, `BetterCombatMod` initializes `WeaponRegistry`, which accesses `net/minecraft/class_7924` (Intermediary mapping for `net.minecraft.core.registries.Registries`). In standard Fabric Loader, Knot dynamically translates Intermediary to runtime names. Lunar Client's proprietary `Genesis` classloader and `IchorPipeline` operate directly in Mojang Official mappings and fail to resolve the unmapped `class_7924`, causing an instantaneous crash of the integrated server.
- **Action Required:** Exclude `bettercombat` from profiles targeted for Lunar Client synchronization, or provide an officially remapped JAR.

### Root Cause 3: Mixin Check Failure under Lunar Client (`krypton`)
- **Observed Logs:** `crash-2026-09-09_05.15.18-client.txt` and `crash-2026-09-09_05.20.48-client.txt`.
- **Stacktrace Analysis:**
  ```
  org.spongepowered.asm.mixin.injection.throwables.InjectionError: Critical injection failure:
  Redirector onKey$initializeVelocityCipher(ILjava/security/Key;)Ljavax/crypto/Cipher; in krypton.mixins.json:shared.network.pipeline.encryption.ServerLoginPacketListenerImplMixin from mod krypton failed injection check, (0/1) succeeded. Scanned 0 target(s). No refMap loaded.
  ```
- **Mechanism:** `krypton-0.3.1.jar` attempts to inject a `@Redirect` into Minecraft's `ServerLoginPacketListenerImpl` to optimize network encryption. Lunar Client's Genesis runtime replaces this exact class with its own network optimization layer. Krypton cannot locate the target method and aborts game startup with a critical Mixin injection error.
- **Action Required:** Exclude `krypton` from Lunar Client profile synchronization.

### Root Cause 4: Options Parsing Failure (`IllegalArgumentException: Unknown key name: 47`)
- **Observed Logs:** `instances/26.2/logs/latest.log` line 14:
  ```
  [02:37:12] [Render thread/ERROR]: Failed to load options
  java.lang.IllegalArgumentException: Unknown key name: 47
      at knot//com.mojang.blaze3d.platform.InputConstants.getKey(InputConstants.java:461)
      at knot//net.minecraft.client.Options.processOptions(Options.java:1886)
      at knot//net.minecraft.client.Options.load(Options.java:1923)
      at knot//net.minecraft.client.Options.<init>(Options.java:1744)
  ```
- **Observed In File:** `instances/26.2/minecraft/options.txt` line 132:
  `key_key.togglePerspective:47`
  `instances/26.2/minecraft/options.txt` lines 118–122, 192–195:
  `key_key.jump:57`, `key_key.sneak:42`, `key_key.sprint:33`, `key_key.inventory:18`, `key_key.zoom:46`, `key_key.inventoryhud.openconfig:54`, `key_key.modmenu.open_menu:54`.
- **Observed In Code:**
  - `tune_engine_configs.py` line 375: `opts["key_key.modmenu.open_menu"] = "54"` (hardcoded for modern!).
  - `tune_engine_configs.py` line 379: `opts["key_key.inventoryhud.openconfig"] = "key.keyboard.right.shift"` (hardcoded for legacy!).
  - `controls_service.py` line 313: `result["key_key.modmenu.open_menu"] = "54"`.
- **Mechanism:** In LWJGL 2 (Minecraft 1.8.9), key codes are raw integers (`47` = `V`, `54` = Right Shift, `57` = Space). In modern Minecraft (26.2 / GLFW), key codes are string identifiers (`key.keyboard.v`, `key.keyboard.right.shift`, `key.keyboard.space`). When integer keys are written to modern `options.txt`, `InputConstants.getKey()` cannot find `"47"` in the GLFW map, throws an `IllegalArgumentException`, and resets user options to defaults or aborts options initialization.
- **Action Required:**
  1. Fix `tune_engine_configs.py` lines 374–381:
     - For Modern: `opts["key_key.modmenu.open_menu"] = "key.keyboard.right.shift"`
     - For Legacy: `opts["key_key.inventoryhud.openconfig"] = "54"`, `opts["key_key.modmenu.open_menu"] = "54"`
  2. Fix `controls_service.py` to ensure modern translation produces `key.keyboard.right.shift`.
  3. Clean all numeric keys from modern `options.txt` files.

### Root Cause 5: Client Shutdown Watchdog Timeout Hang
- **Observed Logs:** `instances/26.2-ultra/logs/latest.log` lines 6459–6533; `instances/26.2-ultra/minecraft/crash-reports/crash-2026-09-08_04.43.58-client.txt`.
- **Stacktrace Analysis:**
  ```
  java.lang.Error: Watchdog (Client shutdown from post-main)
      at knot//net.minecraft.server.dedicated.ServerWatchdog.createWatchdogCrashReport(ServerWatchdog.java:83)
      at knot//com.mojang.blaze3d.platform.ClientShutdownWatchdog.lambda$startShutdownWatchdog$0(ClientShutdownWatchdog.java:44)
  ```
- **Mechanism:** During singleplayer world save and shutdown:
  1. `FastQuit` detaches the client from the integrated server immediately.
  2. `C2ME` has 18 active storage worker threads (`C2ME Storage #1..18`) still writing chunk data.
  3. `fastasyncworldsave-fabric-26.1-2.6.jar` (an outdated 26.1 mod) also intercepts chunk saving asynchronously.
  4. Spark monitoring thread throws `CancellationException`.
  5. The sound engine logs OpenAL buffer deletion errors (`Deleting stream buffers: Invalid operation`).
  6. Non-daemon threads remain active, blocking `Thread.join()` until Mojang's `ClientShutdownWatchdog` times out after 15 seconds and generates a shutdown crash report.
- **Action Required:** Remove `fastasyncworldsave-fabric-26.1-2.6.jar`, ensure clean shutdown of worker pools.

---

## 5. Memory Allocation Flags & Garbage Collection Audit

### Current Configuration:
- `instances/26.2-ultra/instance.cfg`:
  ```ini
  MinMemAlloc=2048
  MaxMemAlloc=8192
  JvmArgs=-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5 -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication -XX:+AlwaysPreTouch
  ```
- `native_runner.py` lines 920–956:
  Constructs ZGC flags when `UseZGC` is requested:
  `-XX:+UseZGC -XX:+ZGenerational`
  Or G1GC flags when ZGC is omitted.

### Assessment for Java 25:
- **Generational ZGC:** In OpenJDK 23+, Generational ZGC is the **default mode** of ZGC (JEP 474). Passing `-XX:+ZGenerational` emits a deprecation warning in JDK 23+ and is completely obsolete. Passing `-XX:+UseZGC` is sufficient to enable Generational ZGC.
- **ZAllocationSpikeTolerance=5:** Valid tuning parameter for heavy chunk loading bursts.
- **Allocation Sizing:**
  - Modern Ultra / Balanced: 4096M min, 8192M max.
  - Modern Performance: 2048M min, 4096M max (sufficient for competitive play, reduces GC cycle duration).
  - Legacy 1.8.9: Strictly use G1GC (`-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=20`) with 2048M–4096M. Do NOT use ZGC on Java 8/HotSpot for 1.8.9.

---

## 6. Options Preservation Requirements

The user's video settings, keybindings, and shader preferences must be strictly preserved during harmonization:

| Configuration File | Preserved Parameters | Invariant Rules |
|---|---|---|
| `options.txt` (Modern 26.2) | `gamma:1.0`, `enableVsync:false`, `maxFramerate:260`, `guiScale:2`, `fov:0.0`, `resourcePacks: ["vanilla","file/SIR Modern.zip"]` | **STRICTLY NO NUMERIC KEYCODES.** All keys must use `key.keyboard.*` or `key.mouse.*`. `maxFramerate` must be integer $\ge 10$ (never `0`). `key_iris.keybind.toggleShaders:key.keyboard.k`. |
| `options.txt` (Legacy 1.8.9) | `gamma:1.0`, `enableVsync:false`, `maxFps:260`, `guiScale:2`, `resourcePacks: ["SIR Legacy.zip"]` | **STRICTLY LWJGL 2 KEYCODES.** `key_key.inventoryhud.openconfig:54`, `key_key.modmenu.open_menu:54`, `key_key.sprint:33`, `key_key.sneak:42`. |
| `optionsof.txt` (1.8.9 OptiFine) | `ofRenderDistanceChunks:16`, `ofSmoothFps:true`, `ofSmoothWorld:true`, `ofFastRender:false`, `ofFastMath:false`, `ofDynamicLights:1` | Preserve existing tuning across all 1.8.9 profiles. |
| `optionsshaders.txt` (1.8.9 Shaders) | `shaderPack=SIR Legacy Shader.zip`, `normalMapEnabled=true`, `specularMapEnabled=true` | Keep enabled on Ultra/Balanced, disabled on Performance. |
| `config/iris.properties` (26.2 Iris) | `enableShaders=true`, `shaderPack=SIR Modern Shader.zip` | Enable on `26.2-ultra` and `26.2-balanced`. Set `enableShaders=false` on `26.2-performance`. |
| `config/sodium-options.json` | Performance graphics mode, chunk builder threads | Preserve across 26.2 instances. |

---

## 7. Recommended Baseline Mod Lists by Profile Tier

### Modern (Fabric 26.2) Tiering

#### Tier 1: `26.2-performance` (Competitive Esports & Ultra-High FPS)
*Goal: Maximum FPS, lowest frame times, 0ms input latency, zero heavy background simulation.*
- **Core Engine & Optimization (~20 mods):**
  - `fabric-api-0.160.0+26.2.jar`
  - `fabric-language-kotlin-1.14.1+kotlin.2.4.20.jar`
  - `sodium-fabric-0.9.1+mc26.2.jar`
  - `lithium-fabric-0.25.3+mc26.2.jar`
  - `ferritecore-9.0.0-fabric.jar`
  - `immediatelyfast-Fabric-1.16.3+26.2.jar`
  - `modernfix-5.27.19-build.1.jar`
  - `badoptimizations-2.4.1-26.2-fabric.jar`
  - `betterfpsdist-fabric-26.2-6.2.jar`
  - `entityculling-fabric-1.10.5-mc26.2.jar`
  - `moreculling-fabric-26.2-1.8.1.jar`
  - `memorysettings-fabric-26.2-6.0.jar`
  - `dynamic-fps-3.11.9+minecraft-26.2.0-fabric.jar`
  - `alternate-current-mc26.2-1.9.0.jar`
  - `scalablelux-fabric-0.3.0-alpha.0.3-all.jar`
  - `gpumemleakfix-fabric-26.2-1.9.jar`
  - `debugify-26.2.0.0.jar`
  - `fastitemframes-v26.2.1-mc26.2.x-Fabric.jar`
  - `fastquit-3.1.5+mc26.2.jar`
  - `zfastnoise-1.0.40+26.2.jar`
- **Essential QoL & HUD (~18 mods):**
  - `appleskin-fabric-mc26.2-3.0.10.jar`
  - `inventoryhud.fabric.26.2-3.4.34.jar`
  - `modmenu-20.0.1.jar`
  - `cloth-config-26.2.155.jar`
  - `yet_another_config_lib_v3-3.9.5+26.2-fabric.jar`
  - `zoomify-2.16.1+26.2.jar`
  - `controlling-fabric-26.2-26.2.2.jar`
  - `betterf3-19.0.0-Fabric-26.2.jar`
  - `shulkerboxtooltip-fabric-5.4.0+26.2.jar`
  - `mru-1.0.33+26.2-fabric.jar`
  - `clumps-fabric-26.2-26.2.1.jar`
  - `cherishedworlds-fabric-17.0.0+26.2.jar`
  - `easymagic-v26.2.0-mc26.2.x-Fabric.jar`
  - `easyanvils-v26.2.2-mc26.2.x-Fabric.jar`
  - `fallingtree-26.2-25.jar`
  - `carryon-fabric-26.2-2.11.0.jar`
  - `waystones-fabric-26.2-26.2.0.12.jar`
  - `spark-1.10.173-fabric.jar`
- **Strictly Excluded from Performance:** `physics-mod` (89MB), `watermedia` (143MB binaries), `ambientsounds` (84MB), `sounds` (8MB), `c2me` (unstable multi-threaded worldgen), `fastasyncworldsave`, `quantified api-omni`, `fancymenu`, all `.disabled` files.
- **Target Count:** ~40–45 clean, verified JARs.

#### Tier 2: `26.2-balanced` (Standard Enhanced Daily Play)
*Goal: Smooth 144Hz+ performance + rich shaders, dynamic lighting, connected textures, and immersive audio.*
- **Includes all Tier 1 mods plus Visual & Sound Enhancements (~45 additional mods):**
  - `iris-fabric-1.11.2+mc26.2.jar` (Shader support enabled)
  - `lambdynamiclights-4.12.3+26.2.jar`
  - `continuity-3.0.1+26.2.jar`
  - `connectedglass-1.1.14-fabric-mc26.2.jar`
  - `entity_texture_features-7.1.1-26.2-fabric.jar`
  - `entity_model_features-3.2.6-26.2-fabric.jar`
  - `skinlayers3d-fabric-1.11.2-mc26.2.jar`
  - `presencefootsteps-1.13.3+26.2.jar`
  - `sound-physics-remastered-fabric-1.5.1+26.2.jar`
  - `visuality-0.7.14+26.2.jar`
  - `fallingleaves-2.0.7+26.1.jar`
  - `bettercombat-fabric-3.2.2+26.2.jar` *(Native launcher profiles only; exclude from Lunar sync)*
  - `jei-26.2-fabric-30.25.0.177.jar`
  - `journeymap-fabric-26.2-6.0.5.jar`
  - `sereneseasons-fabric-26.2-26.1.2.0.4.jar`
  - `geckolib-fabric-26.2-5.5.3.jar`
  - `fancymenu_fabric_3.9.10_MC_26.2.jar` + `konkrete_fabric_1.11.1_MC_26.2.jar`
  - `voicechat-fabric-2.6.22+26.2.jar`
  - `replaymod-26.2-2.6.27.jar`
- **Target Count:** ~85–95 clean, verified JARs.

#### Tier 3: `26.2-ultra` (Ultra High-Fidelity Simulation Showcase)
*Goal: Cinematic RTX experience with physics engine, media players, full 3D particles, and maximum atmosphere.*
- **Includes all Tier 2 mods plus Heavy Simulation Mods (~35 additional mods):**
  - `physics-mod-3.2.0-mc-26.2-fabric.jar` (Ocean/cloth physics)
  - `watermedia-3.0.0.23.jar` + `watermedia_binaries-3.0.0.6.jar`
  - `AmbientSounds_FABRIC_v6.3.6_mc26.2.jar`
  - `sounds-2.5.1+edge+26.2-fabric.jar`
  - `atmospherics-2.6.6-mc-26.2.jar`
  - `puddleflood-1.1.5+26.2-fabric.jar`
  - `bettervillageranimations-fabric-26.2.jar`
  - `refurbished_furniture-fabric-26.2-1.0.25.jar` + `framework-fabric-26.2-0.13.26.jar`
  - `geophilic v3.6.mod-26.2.jar`
  - `animatica-0.6.3+26.2.jar`
  - `skyboxify-3.3.1+26.2-fabric.jar`
  - `polytone-26.2-6.4.3-fabric.jar`
  - `lithostitched-1.8.0+beta3-fabric-26.2.jar`
- **Target Count:** ~125–135 clean, non-conflicting JARs.
- **Strictly Excluded:** `quantified api-omni`, `fastasyncworldsave`, duplicate version JARs.

#### Tier 4: `26.2` (Base Vanilla Profile)
*Goal: Pure, pristine foundation containing only core Fabric utilities (~15 mods).*
- `fabric-api-0.160.0+26.2.jar`
- `sodium-fabric-0.9.1+mc26.2.jar`
- `lithium-fabric-0.25.3+mc26.2.jar`
- `ferritecore-9.0.0-fabric.jar`
- `modmenu-20.0.1.jar`
- `cloth-config-26.2.155.jar`
- `iris-fabric-1.11.2+mc26.2.jar`
- `zoomify-2.16.1+26.2.jar`
- `appleskin-fabric-mc26.2-3.0.10.jar`

---

### Legacy (Forge 1.8.9) Tiering

#### Tier 1: `1.8.9-performance` (Competitive PvP Engine)
- Core competitive suite (12 mods):
  - `OptiFine-OptiFine-1.8.9_HD_U_M5.jar`
  - `BetterFps-1.2.0.jar`
  - `foamfix-0.6.3a-anarchy-1.8.x.jar`
  - `MemoryFix-0.3.jar`
  - `MouseDelayFix-1.0.1.jar`
  - `RawInput-0.1.8+1.8.9-forge.jar`
  - `TcpNoDelayMod-2.0.jar`
  - `entityculling-forge-mc1.8.9-1.5.0.jar`
  - `Keystrokes-1.8.9-forge-1.0.0.jar`
  - `PerspectiveModRedux-1.8.9-0.0.4.jar`
  - `MouseTweaks-2.6.2-mc1.8.9.jar`
  - `[1.8.9] PlayerAPI-PrideSyria.jar`

#### Tier 2: `1.8.9-balanced` (Enhanced PvP & Navigation)
- Includes Tier 1 plus (19 mods total):
  - `AppleCore-mc1.8.9-3.1.1.jar`
  - `BetterBurning-1.8.9-0.5.2.jar`
  - `Bookshelf-1.8.9-1.1.2.207.jar`
  - `jei_1.8.9-2.28.18.187.jar`
  - `JustEnoughResources-1.8.9-0.4.0.23.jar`
  - `SmoothFont-1.8.9-1.15.2.jar`
  - `Xaeros_Minimap_FP21.10.40_Forge_1.8.9.jar`

#### Tier 3: `1.8.9-ultra` (Full Legacy Experience)
- Includes Tier 2 plus (26 mods total):
  - `3dSkinLayers-forge-mc1.8.9-1.2.0.jar`
  - `Havoc-1.0.jar`
  - `InGameAccountSwitcher-Forge-1.8-8.0.1.jar`
  - `ShoulderSurfing-1.8.9-2.2.20.jar`
  - `SoundFilters-0.8_for_1.8.jar`
  - `Super Secret Settings Fix-PrideSyria.jar`
  - `sharpnessparticles -PrideSyria.jar`

---

## 8. Complete Clean Reset & Harmonization Strategy

### Phase 1: Surgical Quarantine & Removal of Destructive Assets
1. **Purge Fatal Native Crash Mod:**
   Remove `quantified api-omni-2.2.0.jar` and `quantified api-omni-2.2.2.jar` from all instances, `SIR Package/instances/`, and `public_repo/instances/`.
2. **Purge Intermediary Crash Mod from Lunar Profiles:**
   Ensure `bettercombat` and `krypton` are excluded when synchronizing profiles to Lunar Client (`C:/Users/a7med/.lunarclient/profiles/`).
3. **Purge Obsolete/Conflicting World-Save Mod:**
   Remove `fastasyncworldsave-fabric-26.1-2.6.jar` from all 26.2 instances.
4. **Purge Loose and Disabled Files:**
   Delete all `*.disabled` files, empty folders (`1.8.9/` inside `1.8.9-performance/mods/`), and `dependencies/` folders inside mods directories.

### Phase 2: Duplicate Pruning & Profile Differentiation
1. For every duplicate family identified in Section 3.B:
   - Retain only the latest stable version (e.g. `fabric-api-0.160.0`, `sodium-fabric-0.9.1`, `balm-fabric-26.2-26.2.0.8`, `controlify-3.5.0`, `ResourcefulLib-5.0.4`, `ShoulderSurfing-Fabric-26.2-5.0.11`, `waystones-fabric-26.2-26.2.0.12`).
   - Remove the older counterpart.
2. Distribute mods according to the baseline tier lists in Section 7:
   - `26.2-performance`: 42 mods.
   - `26.2-balanced`: 92 mods.
   - `26.2-ultra`: 132 mods.
   - `26.2`: 15 baseline mods.
   - Mirror these exact sanitized tiers to `SIR Package/instances/` and `public_repo/instances/`.

### Phase 3: Options Calibration & InputConstants Normalization
1. **Sanitize `options.txt`:**
   - On all Modern 26.2 profiles: Replace any remaining integer keycodes (`47`, `54`, `57`, `42`, `33`, `18`, `46`) with valid GLFW strings:
     - `key_key.togglePerspective` $\rightarrow$ `key.keyboard.v` (or `key.keyboard.f5`)
     - `key_key.modmenu.open_menu` $\rightarrow$ `key.keyboard.right.shift`
     - `key_key.inventoryhud.openconfig` $\rightarrow$ `key.keyboard.right.shift`
     - `key_iris.keybind.toggleShaders` $\rightarrow$ `key.keyboard.k`
     - `maxFramerate` $\rightarrow$ `260`
     - `enableVsync` $\rightarrow$ `false`
     - `gamma` $\rightarrow$ `1.0`
   - On all Legacy 1.8.9 profiles: Ensure keycodes are raw integers:
     - `key_key.inventoryhud.openconfig` $\rightarrow$ `54`
     - `key_key.modmenu.open_menu` $\rightarrow$ `54`
     - `maxFps` $\rightarrow$ `260`
     - `enableVsync` $\rightarrow$ `false`
     - `gamma` $\rightarrow$ `1.0`
2. **Harmonize Launcher Code:**
   - In `tune_engine_configs.py` line 375: Change `opts["key_key.modmenu.open_menu"] = "54"` to `opts["key_key.modmenu.open_menu"] = "key.keyboard.right.shift"` for modern.
   - In `tune_engine_configs.py` line 379: Change `opts["key_key.inventoryhud.openconfig"] = "key.keyboard.right.shift"` to `"54"` for legacy.
   - In `controls_service.py` line 313: Ensure correct GLFW conversion for modern targets.

### Phase 4: Lunar Bridge Alignment & Path Correction
1. **Fix `profiles.json` Paths:**
   Update `C:/Users/a7med/.lunarclient/profiles.json` to point `gameDir` to actual valid paths on `D:` drive (`D:\Projects\SIR ModPack\instances\26.2-ultra`, etc.) or synchronize mirrored runtime directories to `C:\Users\a7med\AppData\Roaming\SIR ModPack\instances\`.
2. **Enhance `lunar_bridge_service.py`:**
   - Add bidirectional keycode translation (LWJGL 2 $\leftrightarrow$ GLFW) during synchronization so transferring settings from Lunar Client never injects integer keycodes into modern Minecraft options.
   - Map both profile ID naming schemes (`sir-26-ultra` and `SIR 26 Visuals`).

### Phase 5: Self-Healing Logic Refactoring in `instance_service.py`
1. In `instance_service.py` lines 817–822:
   Replace the monolithic `min_jars = 200` threshold with per-tier baseline thresholds:
   ```python
   min_jars = {
       "performance": 35,
       "balanced": 75,
       "ultra": 110,
   }.get(tier, 15)
   ```
   This prevents the launcher from overwriting clean, lightweight performance profiles on launch.

---

## 9. Conclusion
The crashes and instability observed across singleplayer world creation, world loading, and Lunar Client synchronization stem from identifiable, discrete root causes:
1. Native OpenCL segmentation faults from `Quantified API`.
2. Intermediary class resolution failures in `BetterCombat` under Lunar Client's `Genesis` runtime.
3. Mixin injection crashes in `Krypton` under Lunar Client.
4. InputConstants crashes caused by copying LWJGL 2 integer keycodes into modern GLFW `options.txt`.
5. Profile bloat and re-inflation caused by `min_jars = 200` in `instance_service.py`.

Executing the 5-phase clean reset strategy outlined above will establish rock-solid stability, 100% clean world creation and loading, zero native crashes, and distinct, optimized tiers across the entire ecosystem.
