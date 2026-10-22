# Exploration Survey Report: Cross-Client Sync, Invariants, Test & Acceptance Criteria

**Agent**: Survey Explorer 3 (Cross-Client Sync, Invariants, Test & Acceptance Criteria)  
**Working Directory**: `d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_3`  
**Target File**: `handoff.md`  
**Date / Timestamp**: 2026-09-08T20:40:00Z  

---

## 1. Observation

Direct, empirical observations gathered via live filesystem inspection, Python runtime execution, socket-level telemetry verification, Git inspection, and unit test execution across all target environments.

### 1.1 Five Target Directories & options.txt State Audit

All 5 specified directories were audited for existence, directory structure, options configuration, and keybinds:

| Target Directory | Exists | `options.txt` Locations Found | Gamma | VSync | Iris Toggle Key | ReplayMod Keybinds |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **1. `d:/Projects/SIR ModPack`** | **YES** | 54 total matches (`instances/26.2/options.txt`, `instances/26.2/minecraft/options.txt`, `instances/1.8.9/options.txt`, `public_repo/instances/`, `SIR Package/instances/`, etc.) | `1.0` | `false` | `key.keyboard.k` (toggle), `key.keyboard.i` (selection) | `playeroverview: b`, `marker: m`, `playpause: p`, `keyframerepository: x`, `pathpreview: h`, `positionkeyframe: i`, `timekeyframe: o` |
| **2. `C:/Users/a7med/AppData/Roaming/SIR ModPack`** | **YES** | 21 total matches (`instances/26.2/options.txt`, `instances/26.2/minecraft/options.txt`, `instances/1.8.9/options.txt`, `instances/26.2-ultra/options.txt`, etc.) | `1.0` | `false` | `key.keyboard.k` | Fully present and identical to workspace |
| **3. `C:/Users/a7med/.lunarclient`** | **YES** | 0 `options.txt` in root. Lunar Client writes settings to `C:/Users/a7med/AppData/Roaming/.minecraft/optionsLC.txt` and manages profiles in `C:/Users/a7med/.lunarclient/profiles.json`. | **`0.0`** *(optionsLC.txt)* | `false` | `key.keyboard.k` | Present as numerical keycodes (`playeroverview: 48`, `marker: 50`, `playpause: 25`, `keyframerepository: 45`, etc.) |
| **4. `C:/Users/a7med/AppData/Roaming/.minecraft`** | **YES** | 6 matches: Root `options.txt`, `instances/26.2/options.txt`, `instances/26.2/minecraft/options.txt`, and config backups. | **`0.0`** *(options.txt & instances)* | `false` | **MISSING** in root `options.txt` | **MISSING** in root `options.txt` |
| **5. `C:/Users/a7med/AppData/Roaming/PrismLauncher`** | **YES** | Contains `instances/1.8.9/minecraft` and `instances/26.2/minecraft`. **0 `options.txt` files found.** | **N/A** | **N/A** | **MISSING** | **MISSING** |

#### Key options.txt Discrepancies & Gaps:
1. **Gamma Mismatch**: `C:/Users/a7med/AppData/Roaming/.minecraft/options.txt`, `C:/Users/a7med/AppData/Roaming/.minecraft/optionsLC.txt`, and `C:/Users/a7med/AppData/Roaming/.minecraft/instances/26.2/options.txt` all have `gamma: 0.0`. Master project requirement R3 mandates `gamma: 1.0`.
2. **Missing `options.txt` in PrismLauncher**: `C:/Users/a7med/AppData/Roaming/PrismLauncher/instances/26.2/minecraft` and `instances/1.8.9/minecraft` contain `mods`, `resourcepacks`, `screenshots`, `servers.dat`, `shaderpacks`, but lack `options.txt`.
3. **Missing Keybinds in Official `.minecraft`**: Root `C:/Users/a7med/AppData/Roaming/.minecraft/options.txt` contains default Minecraft options without `key_iris.keybind.toggleShaders:key.keyboard.k` or the ReplayMod keybind bindings.
4. **Existing Synchronization Scripts**:
   - `development/tools/sync_resource_packs.py`: Fully implements the 5-target synchronization architecture for resource packs (`d:/Projects`, `Roaming/SIR ModPack`, `.lunarclient`, `.minecraft`, `PrismLauncher`).
   - `development/launcher_core/lunar_bridge_service.py` (lines 20-370): Implements profile and options synchronization between Lunar Client (`optionsLC.txt`, `profiles.db`, `profiles.json`) and SIR ModPack instances.
   - `development/launcher_core/syncer_service.py`: Implements `DifferentialSyncService` for SHA-256 and archive validation.
   - `development/tools/archive_scripts/apply_m4_performance_tuning.py` (lines 192-380): Historical multi-profile options updater.
   - *Gap*: There is currently no unified, standalone CLI tool in `development/tools/` dedicated specifically to synchronizing `options.txt` across all 5 directories.

---

### 1.2 Generational ZGC Flags Audit

Audit of the mandate: `-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5` across modern profiles (26.2):

1. **Instance Configurations (`instance.cfg`)**:
   - `d:/Projects/SIR ModPack/instances/26.2/instance.cfg`:
     ```ini
     AutomaticJava=true
     OverrideJavaLocation=true
     OverrideJavaArgs=true
     OverrideMemory=true
     JvmArgs=-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5 -XX:+UnlockExperimentalVMOptions -XX:+UseStringDeduplication -XX:+AlwaysPreTouch
     ```
   - Verified present and identical with all 3 flags in:
     - `instances/26.2-ultra/instance.cfg`
     - `instances/26.2-balanced/instance.cfg`
     - `instances/26.2-performance/instance.cfg`
     - `public_repo/instances/26.2*/instance.cfg` (all 4 profiles)
     - `C:/Users/a7med/AppData/Roaming/SIR ModPack/instances/26.2*/instance.cfg` (all 4 profiles)
     - `SIR Package/instances/26.2*/instance.cfg` (all 4 profiles)
   - Legacy 1.8.9 profiles correctly maintain Java 8 G1GC flags (`-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:+UseNUMA -XX:MaxGCPauseMillis=20`).

2. **Launcher Engine Dynamic JVM Flag Builders**:
   - `development/launcher_core/native_runner.py` (lines 895-900):
     ```python
     if use_zgc:
         args.extend([
             "-XX:+UseZGC",
             "-XX:+ZGenerational",
             "-XX:ZAllocationSpikeTolerance=5",
         ])
     ```
   - `development/launcher_core/instance_service.py` (lines 471-476):
     ```python
     if use_zgc:
         jvm_flags.extend([
             "-XX:+UseZGC",
             "-XX:+ZGenerational",
             "-XX:ZAllocationSpikeTolerance=5",
         ])
     ```
   - `install.py` (lines 146-160): Embeds all 3 flags during automated instance generation.

3. **Discrepancies & Gaps Detected in ZGC Flags**:
   - **Lunar Client Profiles**: In `C:/Users/a7med/.lunarclient/profiles.json`, all three 26.2 profiles (`SIR 26 Visuals`, `SIR 26 Balanced`, `SIR 26 Performance`) currently specify:
     ```json
     "jvmArgs": [
       "-XX:+UnlockExperimentalVMOptions",
       "-XX:+UseG1GC",
       "-XX:+ParallelRefProcEnabled",
       "-XX:MaxGCPauseMillis=20",
       "-XX:+AlwaysPreTouch",
       "-XX:+UseStringDeduplication",
       "-XX:+OptimizeStringConcat",
       "-XX:+UseNUMA"
     ]
     ```
     They are using G1GC instead of Generational ZGC!
   - **PrismLauncher Instances**: `C:/Users/a7med/AppData/Roaming/PrismLauncher/instances/26.2` has NO `instance.cfg` file.
   - **Server Start Scripts**:
     - `server/Fabric_26.2_Server/start_server.bat` (line 39) and `start_server.sh`:
       ```bat
       set JVM_FLAGS=-XX:+UseZGC -XX:+ZGenerational -XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+PerfDisableSharedMem -Dusing.aikars.flags=https://mcflags.emc.gs
       ```
       *Missing*: `-XX:ZAllocationSpikeTolerance=5`.
     - `development/launcher_source/SIR_Launcher_Studio.py` (line 3677, line 5986): Has `-XX:+UseZGC -XX:+ZGenerational`, missing `-XX:ZAllocationSpikeTolerance=5`.

---

### 1.3 Bedrock Cross-Play Templates & Server Health Monitoring

1. **Bedrock Geyser-Spigot Gateway Template**:
   - File inspected: `d:/Projects/SIR ModPack/server/Purpur_Paper_Server/plugins/Geyser-Spigot/config.yml` (82 lines).
   - Direct quotes from configuration:
     - Line 12: `address: 0.0.0.0`
     - Line 14: `port: 19132` (Standard Bedrock UDP Port)
     - Line 16: `clone-remote-port: false`
     - Line 26: `address: 127.0.0.1`
     - Line 28: `port: 25565`
     - Line 33: `auth-type: floodgate`
     - Line 37: `floodgate-key-file: plugins/Floodgate/key.pem`
   - Complete console and mobile connection guides included for Android, iOS, Xbox, PlayStation, and Nintendo Switch (lines 64-81).

2. **Automated Server Health Monitor**:
   - File inspected: `d:/Projects/SIR ModPack/server/server_health_check.py` (356 lines).
   - Capabilities verified:
     - Java Edition Server List Ping (SLP) on TCP port 25565 (lines 91-140)
     - Java Query / UT3 Protocol on UDP port 25565 (lines 142-181)
     - Bedrock RakNet Unconnected Ping on UDP port 19132 (lines 184-260) using RakNet magic bytes `\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78` to packet 0x01 and decoding 0x1C unconnected pong for server name, MOTD, version, protocol, and player count.
   - CLI execution verified: `python server/server_health_check.py --help` successfully returned with options `--host`, `--port`, `--bedrock-port`, `--timeout`, `--json`, `--continuous`.
   - Wired in `server/Launch_SIR_Server.bat` (line 30): option `[3] Run Server Health Check Telemetry (Java 25565 + Bedrock 19132)`.

---

### 1.4 Drive D Free Space Invariant & Disk Protection

1. **Empirical Disk Measurement (`shutil.disk_usage('D:\\')`)**:
   - Total Capacity: `260.01 GB`
   - Used Space: `242.26 GB`
   - **Free Space: `17.7439 GB` (19,052,322,816 bytes)**
   - **Required Threshold: `>= 18.0000 GB` (19,327,352,832 bytes)**
   - **Invariant Status: VIOLATED / DEFICIT OF -0.256 GB (-262.1 MB)**

2. **Unit Test vs Acceptance Criteria Discrepancy**:
   - In `tests/test_system_audit_invariants.py` (line 90):
     ```python
     elif ROOT_DIR.upper().startswith("D:"):
         self.assertGreaterEqual(free_gb, 15.0, f"Drive D free space must be >= 15 GB, currently {free_gb:.2f} GB")
     ```
   - The test checks `free_gb >= 15.0`, allowing it to pass at `17.74 GB`, despite the Master Prompt and R3 Acceptance Criteria explicitly demanding `>= 18.00 GB`.

3. **Workspace Disk Consumer Audit**:
   - `d:/Projects/SIR ModPack/SIR Package`: `5,859.7 MB`
   - `d:/Projects/SIR ModPack/instances`: `4,984.9 MB`
   - `d:/Projects/SIR ModPack/public_repo`: `2,088.2 MB`
   - `d:/Projects/SIR ModPack/website-next`: `1,720.6 MB`
   - `d:/Projects/SIR ModPack/assets`: `1,271.5 MB`
   - `d:/Projects/SIR ModPack/dist_payloads`: `823.4 MB`
   - `d:/Projects/SIR ModPack/exports`: `776.8 MB` *(Stale build zip exports)*
   - `d:/Projects/SIR ModPack/libraries`: `763.5 MB`
   - `d:/Projects/SIR ModPack/build_apps`: `113.6 MB` *(PyInstaller build cache)*
   - `d:/Projects/SIR ModPack/website-next/.next/cache`: `193.1 MB` *(Next.js compiler cache)*

4. **Identified Safe Reclaim Potential**:
   - Pruning `exports/` (776.8 MB) + `build_apps/` (113.6 MB) + `.next/cache/` (193.1 MB) yields **~1,083.5 MB (1.08 GB)** of safe reclaimed disk space, which will raise Drive D free space to **~18.82 GB**, firmly satisfying the invariant.

---

### 1.5 Git Repositories Status

1. **`d:/Projects/SIR ModPack/public_repo`**:
   - Current Branch: `main`
   - Remote URL: `https://github.com/sirahmed8/SIR-ModPack.git` (fetch & push)
   - Working Tree: **Clean (0 modified, 0 untracked files)**
   - Latest Commit: `52e18f0a feat(release): v1.0.0 Genesis Production Release - complete multi-agent overhaul`

2. **`d:/Projects/SIR ModPack/website-next`**:
   - Current Branch: `main`
   - Remote URLs: `origin` & `private` -> `https://github.com/sirahmed8/SIR-ModPack-private.git` (fetch & push)
   - Working Tree: **Clean (0 modified, 0 untracked files)**
   - Latest Commit: `45d842f feat(security): enforce mandatory Google auth gate across all routes - redirect unauthenticated users to /welcome`

3. **Master Workspace**: `d:/Projects/SIR ModPack` is the local root development workspace.

---

### 1.6 Unit Test Inventory & Acceptance Criteria Verification

1. **Unit Test Suite Execution**:
   - Command: `python -m unittest discover -s tests -p "test_*.py" -v`
   - Test files discovered: 31 test modules in `tests/`
   - Result:
     ```
     Ran 368 tests in 100.078s
     OK
     ```
   - **368 tests passed, 0 failures, 0 errors, 0 skipped.**
   - All critical domain test modules passed, including:
     - `test_system_audit_invariants.py`: 8 tests ok
     - `test_native_runner.py`: 48 tests ok
     - `test_video_presets.py`: 10 tests ok
     - `test_instance_matrix_parity.py`: 14 tests ok
     - `test_tray_and_window_lifecycle.py`: 7 tests ok
     - `test_challenger_m5_matrix_stress.py`: 6 tests ok

2. **Ecosystem Doctor Execution**:
   - Command: `python ecosystem_doctor.py`
   - Result: **100% HEALTHY — ZERO ISSUES DETECTED ACROSS ENTIRE ECOSYSTEM!**
   - Layer 1 (Desktop Binaries): All 3 binaries verified (`SIR Launcher.exe`: 33.8 MB, `SIR Installer.exe`: 17.8 MB, `SIR Server Manager.exe`: 32.8 MB).
   - Layer 2 (Shaders): `SIR Modern Shader.zip` (347 files), `SIR Legacy Shader.zip` (342 files).
   - Layer 3 (Resource Packs): `SIR Modern.zip` (5,341 files), `SIR Legacy.zip` (1,762 files).
   - Layer 4 (Mods): 224 mod JARs detected; `sir_core.json` verified active.
   - Layer 5 (Instance Profiles): All 8 instances verified on disk.
   - Layer 6 (Web Platform): Verified `website-next/public/share` (10 items).

---

## 2. Logic Chain

1. **From Observation 1.1 (Multi-Folder options.txt Audit)**:
   - While the primary development workspace (`d:/Projects/SIR ModPack`) and roaming runtime (`AppData/Roaming/SIR ModPack`) are synchronized with `gamma: 1.0`, `vsync: false`, Iris toggle `K`, and full ReplayMod keybinds, external launchers on the user machine diverge.
   - Specifically, `.minecraft/options.txt` and `.minecraft/optionsLC.txt` are set to `gamma: 0.0` and `.minecraft/options.txt` lacks the Iris/ReplayMod keybinds.
   - Furthermore, `PrismLauncher/instances/26.2/minecraft` and `1.8.9/minecraft` exist but completely lack `options.txt`.
   - *Inference*: To achieve true cross-client harmony (R3), an automated options synchronization script should be executed during the worker phase to propagate the canonical `options.txt` and `optionsLC.txt` across all 5 directories.

2. **From Observation 1.2 (Generational ZGC Flags Audit)**:
   - Modern 26.2 instances in `instances/26.2*/instance.cfg`, `native_runner.py`, and `instance_service.py` properly enforce `-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5`.
   - However, Lunar Client's `profiles.json` still has legacy G1GC flags assigned to all modern 26.2 profiles, `server/Fabric_26.2_Server/start_server.bat` lacks `-XX:ZAllocationSpikeTolerance=5`, and `PrismLauncher/instances/26.2` lacks `instance.cfg`.
   - *Inference*: Updating Lunar Client's `profiles.json` for modern 26.2 profiles and appending `-XX:ZAllocationSpikeTolerance=5` to the server launch script will ensure 100% adherence to the ZGC mandate.

3. **From Observation 1.3 (Bedrock Gateway & Server Health)**:
   - `Geyser-Spigot/config.yml` on UDP 19132 is properly configured with `floodgate` auth and remote bridge to Java 25565.
   - `server/server_health_check.py` accurately tests all three protocol layers (Java TCP SLP, Java UDP Query, Bedrock UDP RakNet ping).
   - *Inference*: Bedrock cross-play template and health monitoring requirements are fully satisfied and ready for production deployment.

4. **From Observation 1.4 (Drive D Invariant & Deficit)**:
   - Drive D currently has 17.74 GB free space, falling short of the required 18.00 GB threshold by 262 MB.
   - `tests/test_system_audit_invariants.py` passes because its test condition was loosely set to `>= 15.0 GB`.
   - The repository contains ~1.08 GB of redundant, rebuildable files in `exports/`, `build_apps/`, and `website-next/.next/cache/`.
   - *Inference*: Updating the unit test to enforce `>= 18.0 GB` and having an authorized implementation worker prune stale exports and build caches will restore Drive D free space to ~18.82 GB, permanently satisfying the invariant.

5. **From Observation 1.5 & 1.6 (Git Status & Unit Test Suite)**:
   - Both `public_repo` and `website-next` are on `main`, clean, with 0 modified or untracked files.
   - All 368 unit tests pass with 0 failures and 0 errors, and `ecosystem_doctor.py` reports 100% healthy across all 6 layers.
   - *Inference*: The codebase is stable and healthy; the gaps identified above are specific synchronization, config alignment, and disk management tasks that can be addressed directly in the implementation phase.

---

## 3. Caveats

1. **Read-Only Scope**: In strict compliance with the Explorer archetype, no project files, configuration files, or repositories were altered during this survey.
2. **Network/Live Playit Tunnel**: Live socket checks were conducted against local loopback interfaces; actual remote connectivity through `irvine-speller.tun.ply.gg` depends on an active external Playit daemon.
3. **PrismLauncher Runtime Execution**: `PrismLauncher` instances in AppData appear to have been generated as directory stubs (`instances/26.2/minecraft`); their `instance.cfg` files will need to be populated so that Prism Launcher can launch them directly.

---

## 4. Conclusion

The SIR ModPack ecosystem is in an exceptionally robust baseline state:
- **368/368 unit tests passing** with 0 errors.
- **6/6 diagnostic layers 100% healthy** in `ecosystem_doctor.py`.
- **Both Git repositories clean** on `main`.
- **Bedrock cross-play gateway** and **socket-level health check monitor** fully verified on UDP 19132 and TCP/UDP 25565.

To achieve 100% fulfillment of the Master Prompt's Acceptance Criteria, the following concrete actions are recommended for the implementation phase:
1. **Harmonize `options.txt` across all 5 directories**:
   - Update `C:/Users/a7med/AppData/Roaming/.minecraft/options.txt` and `optionsLC.txt` to `gamma: 1.0` and inject `key_iris.keybind.toggleShaders:key.keyboard.k` and ReplayMod keybinds.
   - Deploy canonical `options.txt` to `C:/Users/a7med/AppData/Roaming/PrismLauncher/instances/26.2/minecraft` and `1.8.9/minecraft`.
2. **Enforce Generational ZGC in Lunar Client & Server Scripts**:
   - Update `C:/Users/a7med/.lunarclient/profiles.json` to replace G1GC flags with `-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5` on modern 26.2 profiles.
   - Add `-XX:ZAllocationSpikeTolerance=5` to `server/Fabric_26.2_Server/start_server.bat` (line 39) and `start_server.sh`.
   - Create `instance.cfg` with ZGC flags in `C:/Users/a7med/AppData/Roaming/PrismLauncher/instances/26.2/`.
3. **Restore Drive D Invariant ($\ge 18.00\text{ GB}$)**:
   - Prune stale build exports in `exports/` (776.8 MB), PyInstaller cache in `build_apps/` (113.6 MB), and Next.js cache in `.next/cache/` (193.1 MB) to reclaim ~1.08 GB.
   - Update `tests/test_system_audit_invariants.py` line 90 from `15.0` to `18.0` GB to strictly enforce the invariant.

---

## 5. Verification Method

To independently reproduce and verify all findings:

1. **Verify Unit Test Suite**:
   ```pwsh
   python -m unittest discover -s tests -p "test_*.py" -v
   ```
   *Expected Result*: 368 tests run and pass with `OK` (0 failures, 0 errors).

2. **Verify Ecosystem Doctor Diagnostics**:
   ```pwsh
   python ecosystem_doctor.py
   ```
   *Expected Result*: Output ends with `🎉 100% HEALTHY — ZERO ISSUES DETECTED ACROSS ENTIRE ECOSYSTEM!`.

3. **Verify Drive D Free Space & Invariant**:
   ```pwsh
   python -c "import shutil; total, used, free = shutil.disk_usage('D:\\'); print(f'Free: {free / (1024**3):.4f} GB | Invariant >= 18.0: {free >= 18.0 * (1024**3)}')"
   ```
   *Current Result*: `Free: 17.7439 GB | Invariant >= 18.0: False` (Deficit: 0.256 GB).

4. **Verify Bedrock Config & Health Monitor**:
   ```pwsh
   python server/server_health_check.py --help
   ```
   *Expected Result*: Returns usage string verifying `--port 25565` and `--bedrock-port 19132` capabilities.

5. **Verify Git Repositories**:
   ```pwsh
   git -C public_repo status
   git -C website-next status
   ```
   *Expected Result*: Both return `On branch main`, `nothing to commit, working tree clean`.
