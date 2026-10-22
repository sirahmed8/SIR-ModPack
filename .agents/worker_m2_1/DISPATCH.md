## 2026-08-29T21:54:16Z
You are Worker M2 for Milestone 2 (Native JVM Launch Pipeline & Compatibility).
Your working directory is: D:\Projects\SIR ModPack\.agents\worker_m2_1\

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Mandatory Reading:
1. Authoritative Request: D:\Projects\SIR ModPack\.agents\ORIGINAL_REQUEST.md
2. Master Roadmap: D:\Projects\SIR ModPack\PROJECT.md
3. Test Infrastructure: D:\Projects\SIR ModPack\TEST_INFRA.md
4. Explorer 1 Report: D:\Projects\SIR ModPack\.agents\explorer_m2_1\analysis.md (Natives Extraction & Dynamic Classpath)
5. Explorer 2 Report: D:\Projects\SIR ModPack\.agents\explorer_m2_2\analysis.md (Strict RAM & JRE Locator)
6. Explorer 3 Report: D:\Projects\SIR ModPack\.agents\explorer_m2_3\analysis.md (Dual Keybindings & Log Tailer)

Files You Own Exclusively:
- `development/launcher_core/native_runner.py`
- `development/launcher_core/java_service.py`
- `development/launcher_core/controls_service.py`
- `development/launcher_core/log_service.py`
- `tests/test_native_runner.py`

Mission:
Implement all Milestone 2 features (Features 7, 8, 9, 10, 11, 12 in PROJECT.md) strictly following the architecture and findings from Explorers 1, 2, and 3:
1. **Feature 7 (Strict RAM Parameter Allocation)**: Remove hardcoded clamping (`max(4, ram_gb)`). Implement strict adherence to user-specified RAM (-Xmx/-Xms) with dynamic G1GC region sizing and young gen percentage scaling.
2. **Feature 8 (Pre-Launch Natives Extraction)**: Implement dynamic extraction of LWJGL 2 / 3 DLLs before process launch into version natives directory (with fallback to temp dir on file locks). Set `-Djava.library.path` and `-Dorg.lwjgl.system.SharedLibraryExtractPath`.
3. **Feature 9 (Dynamic Classpath Assembly)**: Dynamically resolve libraries, components (`mmc-pack.json`, `instance.cfg`, `version.json`), and JAR paths for both Modern Fabric 26.2 and Legacy Forge 1.8.9. Evaluate Mojang OS rules properly.
4. **Feature 10 (Stable JRE Runtime Locator)**: Implement PE header bitness inspection (x64/x86/ARM64), semver parsing for Java 8 through 25, deduplication, registry probing, and prioritization of Temurin 21 LTS x64 for 26.2 and JRE 8 x64 for 1.8.9.
5. **Feature 11 (Dual-Mode Keybinding Injection)**: Implement bidirectional GLFW string <-> LWJGL 2 scancode conversion in `ControlsService` so options.txt for 1.8.9 receives numeric scancodes and 26.2 receives GLFW token strings.
6. **Feature 12 (Non-blocking stdout/stderr Tailer)**: Implement `ProcessLogStreamer` background daemon with thread-safe ring buffer, real-time crash pattern matching, and non-blocking event emission.
7. **Comprehensive Test Suite in `tests/test_native_runner.py`**:
   Write and execute comprehensive tests across Tiers 1-4 covering all M2 features.
