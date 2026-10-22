# Milestone 2 Deep-Dive Investigation: Features 8 & 9
**Native JVM Launch Pipeline & Compatibility Analysis**
**Agent**: Explorer 1 (`explorer_m2_1`)
**Date**: 2026-08-29
**Status**: Complete Investigation Report

---

## 1. Executive Summary

This report delivers a comprehensive investigation of **Feature 8 (Pre-Launch Natives Extraction)** and **Feature 9 (Dynamic Classpath Assembly)** for Milestone 2 of the SIR Minecraft Ecosystem.

The SIR launcher is architected with a dual-execution strategy:
1. **Primary Launch Engine**: `NativeMinecraftRunner` (`development/launcher_core/native_runner.py`), a 100% self-contained, independent native JVM launcher that directly boots Minecraft via Python `subprocess.Popen` with zero background launcher dependencies.
2. **Managed Secondary Fallback**: Prism Launcher runner (`development/launcher_core/instance_service.py`) for managed debugging and fallback.

### Key Investigation Findings:
- **Feature 8 (Pre-Launch Natives Extraction)**:
  - **LWJGL 2 (Legacy 1.8.9)** requires strict extraction of `lwjgl64.dll`, `OpenAL64.dll`, `jinput-dx8_64.dll`, `jinput-raw_64.dll`, and `twitchsdk.dll` from native JARs into a directory specified via `-Djava.library.path`.
  - **LWJGL 3 (Modern 26.2 / 1.21.4)** modular DLLs (`lwjgl.dll`, `glfw.dll`, `jemalloc.dll`, `OpenAL.dll`, `freetype.dll`, `shaderc.dll`, `spvc.dll`, `stb.dll`, `tinyfd.dll`, `vma.dll`) must be extracted and exposed via `-Djava.library.path` and `-Dorg.lwjgl.system.SharedLibraryExtractPath`.
  - **Critical Gap Identified**: The current `native_runner.py` only extracts natives during download time within `ensure_version_downloaded()`. If version files or libraries are already present on disk (or pre-cached), `resolve_natives_dir()` points to an existing directory without verifying that DLLs actually exist inside it. In our codebase audit, `C:\Users\a7med\AppData\Roaming\.minecraft\versions\26.2\natives` was found to be completely empty. Furthermore, Windows file-locking (`ERROR_SHARING_VIOLATION` / WinError 32) during rapid restarts or concurrent instance launches is currently unhandled.

- **Feature 9 (Dynamic Classpath Assembly)**:
  - Instances in the SIR ecosystem are structured in Prism / MultiMC format containing `mmc-pack.json` and `instance.cfg` (e.g. `instances/26.2/mmc-pack.json`, `instances/1.8.9/mmc-pack.json`).
  - **Critical Gap Identified**: `NativeMinecraftRunner.build_classpath()` currently uses hardcoded dependency lists for Fabric 0.15.11 and Forge 1.8.9 rather than dynamically resolving components declared in `mmc-pack.json` (such as `net.fabricmc.fabric-loader` version `0.19.3` or `0.16.10`, `org.lwjgl3` version `3.4.1`, `net.minecraftforge` version `11.15.1.2318`).
  - `build_classpath()` does not evaluate Mojang OS rule conditions (`rules: [{"action": "allow", "os": {"name": "windows"}}]`), risking inclusion of OS X / Linux artifacts or omitting Windows-specific classifiers.
  - Multi-root library discovery requires unified resolution across `<root>/libraries`, `<root>/SIR Launcher/libraries`, `%APPDATA%/.minecraft/libraries`, `%APPDATA%/SIR ModPack/libraries`, and `%APPDATA%/PrismLauncher/libraries`.

---

## 2. Codebase & File Structure Observations

### 2.1 File Map & Locations

| Component | Path | Responsibility |
|---|---|---|
| **Native Launch Engine** | `development/launcher_core/native_runner.py` | JVM argument construction, classpath resolution, native DLL extraction, process spawning |
| **Instance Management Service** | `development/launcher_core/instance_service.py` | Instance metadata, presets, Prism fallback, self-healing, directory resolution |
| **Java Discovery Service** | `development/launcher_core/java_service.py` | Windows registry probing, filesystem scanning, JRE 21 & JRE 8 discovery |
| **Shared Runtime Primitives** | `development/shared_core/runtime.py` | Atomic persistence, resilient downloading, system Java fallback |
| **Bridge API Layer** | `development/launcher_core/bridge.py` | UI IPC interface for launch, accounts, video presets |
| **Modern 26.2 Instance Configs** | `instances/26.2/instance.cfg`, `instances/26.2/mmc-pack.json` | Component definitions (LWJGL 3 3.4.1, MC 26.2, Intermediary 26.2, Fabric Loader 0.19.3) |
| **Legacy 1.8.9 Instance Configs** | `instances/1.8.9/instance.cfg`, `instances/1.8.9/mmc-pack.json` | Component definitions (MC 1.8.9, Forge 11.15.1.2318) |
| **Test Suite** | `tests/test_native_runner.py` | Native runner unit tests |

### 2.2 Instance Profile Configurations

#### `instances/26.2/mmc-pack.json`:
```json
{
  "components": [
    {"cachedName": "LWJGL 3", "cachedVersion": "3.4.1", "cachedVolatile": true, "dependencyOnly": true, "uid": "org.lwjgl3", "version": "3.4.1"},
    {"cachedName": "Minecraft", "cachedVersion": "26.2", "important": true, "uid": "net.minecraft", "version": "26.2"},
    {"cachedName": "Intermediary Mappings", "cachedVersion": "26.2", "cachedVolatile": true, "dependencyOnly": true, "uid": "net.fabricmc.intermediary", "version": "26.2"},
    {"cachedName": "Fabric Loader", "cachedVersion": "0.19.3", "uid": "net.fabricmc.fabric-loader", "version": "0.19.3"}
  ],
  "formatVersion": 1
}
```

#### `instances/1.8.9/mmc-pack.json`:
```json
{
    "components": [
        {
            "cachedName": "Minecraft",
            "cachedVersion": "1.8.9",
            "important": true,
            "uid": "net.minecraft",
            "version": "1.8.9"
        },
        {
            "cachedName": "Forge",
            "cachedVersion": "11.15.1.2318",
            "important": true,
            "uid": "net.minecraftforge",
            "version": "11.15.1.2318"
        }
    ],
    "formatVersion": 1
}
```

#### `instances/26.2/instance.cfg` & `instances/1.8.9/instance.cfg`:
- Both define `MinMemAlloc`, `MaxMemAlloc`, `OverrideMemory=true`, `OverrideJavaLocation=true`, `JavaPath=...`, and `JvmArgs=...`.

---

## 3. Deep Dive: Feature 8 — Pre-Launch Natives Extraction

### 3.1 Mechanism & Problem Boundary

Minecraft relies on native C/C++ libraries compiled into `.dll` (Windows), `.so` (Linux), and `.dylib` (macOS) binaries for rendering, audio, controller input, window management, and hardware acceleration:
- **LWJGL 2** (Minecraft 1.8.9): Single monolithic native libraries.
- **LWJGL 3** (Minecraft 1.21.4 / 26.2): Modular multi-component libraries.

If the JVM fails to find these libraries at runtime, the process immediately crashes during static class initialization with fatal errors:
- `java.lang.UnsatisfiedLinkError: no lwjgl in java.library.path`
- `java.lang.UnsatisfiedLinkError: Could not load library: OpenAL64`
- `java.lang.NoClassDefFoundError: Could not initialize class org.lwjgl.glfw.GLFW`

### 3.2 Matrix of Required Native DLLs

| Profile Archetype | Loader / Version | Source Native JARs | Extracted Native DLLs | Key JVM System Properties |
|---|---|---|---|---|
| **Legacy 1.8.9** | Forge 1.8.9 / Vanilla 1.8.9 | `lwjgl-platform-2.9.4-*-natives-windows.jar`, `jinput-platform-2.0.5-natives-windows.jar`, `twitch-platform-6.5-natives-windows-64.jar` | `lwjgl64.dll`, `lwjgl.dll`, `OpenAL64.dll`, `OpenAL32.dll`, `jinput-dx8_64.dll`, `jinput-raw_64.dll`, `jinput-wintab.dll`, `twitchsdk.dll` | `-Djava.library.path=<natives_dir>` |
| **Modern 26.2** | Fabric 26.2 / Vanilla 1.21.4 | `lwjgl-*-3.4.1-natives-windows.jar` (lwjgl, glfw, jemalloc, openal, opengl, stb, tinyfd, vma, shaderc, spvc, freetype), `jtracy-*-natives-windows.jar` | `lwjgl.dll`, `glfw.dll`, `jemalloc.dll`, `OpenAL.dll`, `freetype.dll`, `shaderc.dll`, `spvc.dll`, `stb.dll`, `tinyfd.dll`, `vma.dll` | `-Djava.library.path=<natives_dir>`, `-Dorg.lwjgl.system.SharedLibraryExtractPath=<natives_dir>/lwjgl`, `-Djna.tmpdir=<natives_dir>/jna`, `-Dio.netty.native.workdir=<natives_dir>/netty` |

### 3.3 Identified Defects & Gaps in Current Code

1. **Extraction on Download Only**:
   In `native_runner.py` (lines 383-391), JAR extraction only occurs when `_download_single` runs during fresh downloads. If libraries are already present on disk, this block is bypassed.
2. **Missing Pre-Launch Verification**:
   `resolve_natives_dir()` checks if a directory exists, but does not verify that essential DLLs (`lwjgl64.dll`, `OpenAL64.dll`, `glfw.dll`) are inside it.
3. **Windows File-Lock Collisions (`WinError 32`)**:
   When Minecraft runs, Windows holds exclusive read/exec locks on loaded DLLs. If a second instance launches or a game restarts quickly while the old PID is terminating, writing to a shared natives directory throws `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`.
4. **Architecture Filtering**:
   Natives jars exist for `natives-windows`, `natives-windows-arm64`, and `natives-windows-x86`. The extractor must target host machine architecture (`x64` by default on modern Windows 64-bit).

---

## 4. Deep Dive: Feature 9 — Dynamic Classpath Assembly

### 4.1 Mechanism & Problem Boundary

The Java Classpath (`-cp`) instructs the JVM where to find bytecode `.class` files. If classes are missing or ordered incorrectly:
- Missing loader: `ClassNotFoundException: net.fabricmc.loader.impl.launch.knot.KnotClient` or `ClassNotFoundException: net.minecraft.launchwrapper.Launch`
- Outdated ASM: `IllegalArgumentException: Unsupported class file major version 69` (when running Java 21/25 with old ASM 5.0.3 on Modern Minecraft).
- Duplicate Mixin libraries: Mixin bootstrap collisions or `ClassCircularityError`.

### 4.2 Classpath Precedence & Layering

The classpath must be constructed in strict order:

```
[Layer 1: Mod Loader & Core Launch Bootstrap]
  ├── Fabric: net.fabricmc:fabric-loader, net.fabricmc:intermediary
  └── Forge 1.8.9: net.minecraftforge:forge, net.minecraft:launchwrapper:1.12

[Layer 2: Bytecode Manipulation & Runtime Mixins]
  ├── Modern: org.ow2.asm (asm, asm-analysis, asm-commons, asm-tree, asm-util 9.10+), sponge-mixin 0.8.7+
  └── Legacy: org.ow2.asm:asm-all:5.0.3, scala-library 2.11.1, akka-actor 2.3.3

[Layer 3: Mojang / Vanilla Libraries (OS Rule Filtered)]
  ├── Fastutil, Netty, Guava, Gson, JNA, Oshi, Brigadier, Authlib, DFU, DataFixerUpper
  └── LWJGL 3 Java Bindings (for Modern) / LWJGL 2 Java Bindings (for Legacy)

[Layer 4: Minecraft Client Executable JAR]
  └── 26.2.jar (or 1.21.4.jar) / 1.8.9.jar
```

### 4.3 Identified Defects & Gaps in Current Code

1. **Hardcoded Loader Versions**:
   In `native_runner.py` (lines 434-456), Fabric loader is hardcoded to `0.15.11` and ASM to `9.10.1`, ignoring `mmc-pack.json` which specifies `Fabric Loader 0.19.3` or `0.16.10`.
2. **Missing `mmc-pack.json` & `instance.cfg` Integration**:
   `NativeMinecraftRunner.launch()` receives simple string arguments and does not inspect the instance folder for component patches, custom loader version, or `instance.cfg` JVM / memory configurations.
3. **No Rule Engine for Mojang Libraries**:
   `version.json` defines rules such as:
   ```json
   "rules": [{"action": "allow", "os": {"name": "osx"}}]
   ```
   Without rule evaluation, OS X-specific jars (e.g. `ca.weblite:java-objc-bridge`, `jtracy-natives-macos.jar`) or Linux epoll jars may be parsed into the Windows classpath, causing noise or path errors.
4. **Library Path Resolution Robustness**:
   Libraries must be resolved by probing multiple search roots:
   - `<root_dir>/libraries`
   - `<root_dir>/SIR Launcher/libraries`
   - `%APPDATA%/.minecraft/libraries`
   - `%APPDATA%/SIR ModPack/libraries`
   - `%APPDATA%/PrismLauncher/libraries`
   - `<instance_dir>/libraries`

---

## 5. Recommended Architecture & Implementation Strategy

### 5.1 Architecture for Feature 8: `Pre-Launch Natives Extractor`

Add a dedicated, robust extraction engine in `NativeMinecraftRunner`:

```python
def extract_natives(self, version_json: Dict[str, Any], target_dir: str, is_legacy: bool = False) -> str:
    """
    Extracts all platform-matching native DLLs into target_dir.
    - Handles Windows x64 architecture matching.
    - Skips files if already extracted and uncorrupted.
    - Handles Windows ERROR_SHARING_VIOLATION (WinError 32) by using unique subfolder fallback if locked.
    - Validates presence of critical linkage DLLs (lwjgl64.dll, OpenAL64.dll for LWJGL 2; lwjgl.dll, glfw.dll for LWJGL 3).
    """
```

**Key Elements**:
1. **Target Directory Strategy**:
   - Default: `os.path.join(instance_dir, "natives")` or `os.path.join(self.state_dir, "natives", mc_version)`.
   - Fallback on Lock: If existing DLLs in the directory are locked by an active process, create a process-isolated temp folder: `os.path.join(tempfile.gettempdir(), f"sir_natives_{mc_version}_{os.getpid()}_{int(time.time())}")`.
2. **Safe Zip Extraction**:
   - Only extract entries ending with `.dll`.
   - Skip `META-INF/` and `.git/`.
   - Catch `PermissionError` on existing locked files: if content size matches, continue safely; if different and locked, fall back to unique folder.
3. **Validation Assertion**:
   - For Legacy (1.8.9): assert `lwjgl64.dll` (or `lwjgl.dll`) and `OpenAL64.dll` (or `OpenAL32.dll`) exist in `target_dir`.
   - For Modern (26.2 / 1.21.4): assert `lwjgl.dll` and `glfw.dll` exist in `target_dir`.

### 5.2 Architecture for Feature 9: `Dynamic Classpath Assembler`

Refactor classpath resolution to support full `mmc-pack.json` & `instance.cfg` inspection:

```python
def inspect_instance_config(self, instance_dir: str) -> Dict[str, Any]:
    """Parses mmc-pack.json and instance.cfg to extract components, memory bounds, and JVM overrides."""

def evaluate_library_rules(self, rules: List[Dict[str, Any]], target_os: str = "windows", target_arch: str = "x64") -> bool:
    """Evaluates Mojang library rule conditions ('allow'/'disallow' by OS and features)."""

def resolve_maven_coordinate_path(self, coordinate: str, classifier: str = "") -> Optional[str]:
    """Scans all configured library search roots for a matching jar."""

def build_dynamic_classpath(self, instance_dir: str, version_json: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Constructs the ordered classpath:
    1. Loader components from mmc-pack.json (Fabric Loader, Intermediary, Forge).
    2. Bytecode & Mixin engine (ASM 9.x for Modern, ASM 5.0.3 for Legacy).
    3. OS-rule-filtered libraries from version.json.
    4. Minecraft Client JAR.
    """
```

---

## 6. Comprehensive Verification & Test Plan

To satisfy the requirements in `TEST_INFRA.md`, the test harness in `tests/test_native_runner.py` should be expanded to cover Tier 1 through Tier 4 test categories:

### Test Inventory Matrix

| Tier | Category | Test Case | Target Assertion |
|---|---|---|---|
| **Tier 1** | Feature (F8) | `test_legacy_189_natives_extraction` | Extracts `lwjgl64.dll` and `OpenAL64.dll` to destination directory; returns valid path. |
| **Tier 1** | Feature (F8) | `test_modern_262_natives_extraction` | Extracts `lwjgl.dll`, `glfw.dll`, `jemalloc.dll` to destination directory. |
| **Tier 1** | Feature (F9) | `test_dynamic_mmc_pack_fabric_resolution` | Reads `instances/26.2/mmc-pack.json`, resolves Fabric Loader 0.19.3/0.16.10, Intermediary, and KnotClient. |
| **Tier 1** | Feature (F9) | `test_dynamic_mmc_pack_forge_resolution` | Reads `instances/1.8.9/mmc-pack.json`, resolves Forge 11.15.1.2318 and FMLTweaker. |
| **Tier 1** | Feature (F9) | `test_instance_cfg_memory_parsing` | Parses `MinMemAlloc=4096` and `MaxMemAlloc=8192` from `instance.cfg` and reflects in `-Xms4G` / `-Xmx8G`. |
| **Tier 2** | Boundary (F8) | `test_natives_extraction_file_lock_recovery` | Simulates locked DLL in target directory; verifies fallback to isolated directory without crash. |
| **Tier 2** | Boundary (F8) | `test_natives_extraction_corrupt_jar_handling` | Gracefully handles truncated or invalid native JAR with fallback. |
| **Tier 2** | Boundary (F9) | `test_os_rule_filtering_osx_linux_exclusion` | Verifies OS X / Linux-only libraries (e.g. `java-objc-bridge`, `epoll-linux`) are excluded from Windows classpath. |
| **Tier 2** | Boundary (F9) | `test_multi_search_root_fallback` | Finds libraries across alternative search roots (`%APPDATA%/.minecraft`, `%APPDATA%/SIR ModPack`, repo). |
| **Tier 2** | Boundary (F9) | `test_asm_conflict_prevention` | Ensures old ASM 5.0.3 is never included on Modern Fabric 26.2 classpath. |
| **Tier 3** | Integration | `test_full_command_generation_fabric_262` | Generates full launch command with Java runtime, JVM flags, `-cp`, KnotClient, and game args. |
| **Tier 3** | Integration | `test_full_command_generation_forge_189` | Generates full launch command with Java 8 runtime, `-Djava.library.path`, LaunchWrapper, and FMLTweaker. |
| **Tier 4** | Scenario | `test_end_to_end_launch_dry_run` | Simulates complete launch flow for both 26.2 and 1.8.9 profiles with mock subprocess verification. |

---

## 7. Logic Chain & Evidence Summary

1. **Observation 1**: `instances/26.2/mmc-pack.json` declares component `net.fabricmc.fabric-loader` version `0.19.3` and `org.lwjgl3` version `3.4.1`.
   - *Logic*: Hardcoding `0.15.11` in `native_runner.py` disconnects the native runner from instance configuration. Dynamic parsing of `mmc-pack.json` resolves this divergence.
2. **Observation 2**: `C:\Users\a7med\AppData\Roaming\.minecraft\versions\26.2\natives` was empty on disk, while `Forge 1.8.9\natives` contained `lwjgl64.dll` and `OpenAL64.dll`.
   - *Logic*: `ensure_version_downloaded()` only extracts DLLs during network download. A pre-launch verification and extraction step is required to guarantee DLL presence prior to launching.
3. **Observation 3**: `instance.cfg` files across all instances define explicit `MinMemAlloc`, `MaxMemAlloc`, `JavaPath`, and `JvmArgs`.
   - *Logic*: `instance_service.py` and `native_runner.py` should parse these instance-level configurations directly, fulfilling Feature 7 (Strict RAM Allocation) and Feature 9 (Dynamic Classpath Assembly).

---

## 8. Conclusion & Implementation Recommendations for Implementer

1. **Enhance `NativeMinecraftRunner` (`native_runner.py`)**:
   - Implement `extract_natives()` with active DLL validation, architecture matching (`x64`), and locked-file error recovery.
   - Implement `inspect_instance_config()` to dynamically read `mmc-pack.json` and `instance.cfg`.
   - Implement `evaluate_library_rules()` to filter libraries using Mojang OS rules.
   - Implement multi-root library discovery in `build_classpath()`.
   - Support modern JVM flags: `-Djava.library.path`, `-Dorg.lwjgl.system.SharedLibraryExtractPath`, `-Djna.tmpdir`, `-Dio.netty.native.workdir`.
2. **Harmonize with `InstanceService` (`instance_service.py`)**:
   - Ensure `InstanceService.launch_instance()` passes the instance directory to `NativeMinecraftRunner.launch()`, allowing dynamic metadata extraction.
3. **Expand Test Coverage (`tests/test_native_runner.py`)**:
   - Implement the complete Tier 1-4 test suite (>15 discrete tests) covering all boundary conditions and profile permutations.
