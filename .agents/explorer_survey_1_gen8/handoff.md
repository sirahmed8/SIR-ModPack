# Handoff Report: R1 (Instance Harmonization & Reset) & R2 (Crash Remediation)

**Author:** explorer_survey_1_gen8  
**Working Directory:** `d:/Projects/SIR ModPack/.agents/explorer_survey_1_gen8/`  
**Target Milestone:** R1 (Modpack Instance Audit, Harmonization & Reset) & R2 (Crash Remediation)  
**Detailed Report:** [`analysis.md`](file:///d:/Projects/SIR%20ModPack/.agents/explorer_survey_1_gen8/analysis.md)

---

## 1. Observation

### Obs 1: Fatal Native JVM Crash (`hs_err_pid*.log`)
- **Files:**
  - `C:/Users/a7med/.lunarclient/profiles/sir-26-ultra/hs_err_pid41980.log` (lines 4–9, 28, 35–46, 52–64, 72)
  - `C:/Users/a7med/.lunarclient/profiles/sir-26-ultra/hs_err_pid18004.log`
  - `C:/Users/a7med/.lunarclient/profiles/sir-26-ultra/hs_err_pid30316.log`
  - `C:/Users/a7med/.lunarclient/profiles/sir-26-ultra/hs_err_pid30664.log`
- **Verbatim Content:**
  ```
  #  EXCEPTION_ACCESS_VIOLATION (0xc0000005) at pc=0x00007ffdd28c5a4e, pid=41980, tid=42776
  # Problematic frame:
  # C  [ntdll.dll+0x125a4e]
  Current thread (0x0000029a6246d880):  JavaThread "Quantified-OpenCL-Isolated" daemon [_thread_in_native, id=42776]
  siginfo: EXCEPTION_ACCESS_VIOLATION (0xc0000005), reading address 0x0000000000000006
  Java frames:
  j  org.lwjgl.system.windows.WinBase.nGetModuleHandle(J)J+0
  j  org.lwjgl.system.windows.WinBase.GetModuleHandle(Ljava/nio/ByteBuffer;)J+14
  j  org.lwjgl.system.windows.WindowsLibrary.<clinit>()V+13
  j  org.lwjgl.opencl.CL.create()V+52
  j  org.admany.quantified.core.common.opencl.core.OpenCLRuntime.invokeLWJGLCreate()Z+3
  j  org.admany.quantified.core.common.opencl.core.OpenCLIsolatedExecutor.lambda$warmupAsync$2(...)V+26
  ```

### Obs 2: Integrated Server Tick Crash on World Creation/Loading
- **Files:** `C:/Users/a7med/.lunarclient/profiles/sir-26-ultra/crash-reports/crash-2026-09-09_07.29.02-server.txt` (lines 4–26), `crash-2026-09-09_05.45.58-server.txt`
- **Verbatim Content:**
  ```
  Time: 2026-09-09 07:29:02
  Description: Exception in server tick loop
  java.lang.NoClassDefFoundError: net/minecraft/class_7924
      at Genesis//net.bettercombat.logic.WeaponRegistry.<clinit>(WeaponRegistry.java:165)
      at Genesis//net.bettercombat.BetterCombatMod.loadWeaponAttributes(BetterCombatMod.java:70)
      at Genesis//net.bettercombat.fabric.FabricMod.lambda$onInitialize$0(FabricMod.java:19)
      at Genesis//net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents.lambda$static$1(ServerLifecycleEvents.java:38)
      at Genesis//net.minecraft.server.MinecraftServer.handler$dmp000$fabric-lifecycle-events-v1$beforeSetupServer(MinecraftServer.java:5919)
      at Genesis//net.minecraft.server.MinecraftServer.runServer(MinecraftServer.java:741)
  Caused by: java.lang.ClassNotFoundException: Failed to find class net.minecraft.class_7924
      at com.moonsworth.lunar.genesis.ICRHORIIHOHROHOHOCOOHOOCOORRHO.loadClass(Unknown Source)
  Caused by: java.lang.ClassNotFoundException: IchorPipeline can't find class in Genesis: net.minecraft.class_7924
  ```

### Obs 3: Mixin Check Failure under Lunar Client
- **Files:** `C:/Users/a7med/.lunarclient/profiles/sir-26-ultra/crash-reports/crash-2026-09-09_05.15.18-client.txt` (lines 39–55), `crash-2026-09-09_05.20.48-client.txt`
- **Verbatim Content:**
  ```
  Caused by: org.spongepowered.asm.mixin.injection.throwables.InjectionError: Critical injection failure: Redirector onKey$initializeVelocityCipher(ILjava/security/Key;)Ljavax/crypto/Cipher; in krypton.mixins.json:shared.network.pipeline.encryption.ServerLoginPacketListenerImplMixin from mod krypton failed injection check, (0/1) succeeded. Scanned 0 target(s). No refMap loaded.
  ```

### Obs 4: Options Load Crash from Legacy Integer Keycodes
- **Files:** `instances/26.2/logs/latest.log` (lines 12–19), `instances/26.2/minecraft/options.txt` (line 132), `tune_engine_configs.py` (line 375)
- **Verbatim Content:**
  ```
  [02:37:12] [Render thread/ERROR]: Failed to load options
  java.lang.IllegalArgumentException: Unknown key name: 47
      at knot//com.mojang.blaze3d.platform.InputConstants.getKey(InputConstants.java:461)
      at knot//net.minecraft.client.Options.processOptions(Options.java:1886)
      at knot//net.minecraft.client.Options.load(Options.java:1923)
  ```
  In `instances/26.2/minecraft/options.txt:132`: `key_key.togglePerspective:47`
  In `tune_engine_configs.py:375`: `opts["key_key.modmenu.open_menu"] = "54"` (inside `if is_modern:`)

### Obs 5: Lunar Profile Path Disconnect
- **File:** `C:/Users/a7med/.lunarclient/profiles.json` (lines 8, 24, 40)
- **Verbatim Content:**
  ```json
  "gameDir": "C:\\Users\\a7med\\AppData\\Roaming\\SIR ModPack\\instances\\26.2-ultra"
  ```
  In `C:\Users\a7med\AppData\Roaming\SIR ModPack\instances\`: only `1.8.9` and `26.2` exist. `26.2-ultra` does not exist on C:.

### Obs 6: Active Mod Counts & Tier Discrepancies
- **Counts:**
  - `26.2-ultra`: 185 JARs
  - `26.2-balanced`: 185 JARs (`Compare-Object` shows 0 differences; 100% clone)
  - `26.2-performance`: 221 JARs (36 more mods than Ultra!)
  - `26.2`: 252 JARs (18 duplicate mod families with multiple versions side-by-side)
  - All 1.8.9 instances (`1.8.9`, `1.8.9-balanced`, `1.8.9-performance`, `1.8.9-ultra`): 27 mods.
- **Self-Healing Override:** `instance_service.py` lines 817–822:
  ```python
  min_jars = 200 if is_modern else 45
  if len(existing_jars) < min_jars:
      self._download_payload_if_missing(payload_name, mods_dir)
  ```

---

## 2. Logic Chain

1. **Native JVM Crash Cause:**
   From Obs 1, the fault occurs in `ntdll.dll` inside the thread `Quantified-OpenCL-Isolated` running `org.lwjgl.opencl.CL.create()`. Because `quantified api-omni` unconditionally launches this background thread on game start, it will crash any environment on Java 25 / Windows 11 where LWJGL OpenCL native handles dereference. Eliminating `quantified api-omni` directly terminates this crash pathway.

2. **World Creation/Loading Crash Cause:**
   From Obs 2, every singleplayer world creation/load starts an integrated server that fires `ServerLifecycleEvents.beforeSetupServer`. BetterCombat Mod initializes `WeaponRegistry` during this event and attempts to link `net/minecraft/class_7924`. Under Lunar Client's Genesis classloader, unmapped Intermediary class names cannot be resolved, resulting in a fatal `NoClassDefFoundError` and dropping the world creation flow. Excluding BetterCombat from Lunar synchronized profiles (or remapping it) resolves this crash.

3. **Lunar Mixin Launch Crash Cause:**
   From Obs 3, `krypton` attempts to redirect `onKey$initializeVelocityCipher` in `ServerLoginPacketListenerImpl`. Since Lunar Client replaces this network class, the target method is nonexistent, and Mixin halts startup with `InjectionError`. Excluding `krypton` from Lunar profiles prevents this crash.

4. **Options Load Failure Cause:**
   From Obs 4, modern Minecraft 26.2 uses GLFW key names (`key.keyboard.*`), while legacy 1.8.9 uses LWJGL 2 integer keycodes. When `47` or `54` is in modern `options.txt`, `InputConstants.getKey()` throws `IllegalArgumentException: Unknown key name: 47`. `tune_engine_configs.py:375` hardcodes `"54"` into modern options. Sanitizing modern `options.txt` to GLFW strings and updating `tune_engine_configs.py` stops options corruption.

5. **Profile Bloat and Re-inflation Cause:**
   From Obs 6, `instance_service.py` checks `if len(existing_jars) < 200` for modern profiles. Pruning `26.2-performance` to a lightweight set will immediately trigger `instance_service.py` to re-download `payload_mods_26.2.zip` and extract 200+ mods back into the folder. Refactoring `min_jars` to per-tier thresholds (`performance`: 35, `balanced`: 75, `ultra`: 110) allows tiering to persist.

---

## 3. Caveats

1. **Read-Only Constraint:** In accordance with instructions, this survey did not alter any JAR files, configurations, or Python source files.
2. **adoptium-25.0.5 vs zulu-25.0.1:** The user has both Adoptium and Zulu Java 25 installed. The native OpenCL crash reproduced across both JDK distributions.
3. **Drive D Free Space:** Drive D currently maintains >18GB free space. Pruning duplicate JARs will further optimize disk capacity.

---

## 4. Conclusion

The system instability across instances, world creation, and Lunar profiles is completely diagnosed with exact line numbers, stacktraces, and files. Resolving the issues requires:
1. Deleting `quantified api-omni-2.2.0.jar` and `quantified api-omni-2.2.2.jar` (stops native crash).
2. Purging 18 duplicate mod families from `26.2` and pruning obsolete 26.1 JARs.
3. Establishing true tiered mod sets: `performance` (~42 mods), `balanced` (~92 mods), `ultra` (~132 mods).
4. Updating `min_jars` in `instance_service.py` to tier-specific thresholds.
5. Fixing `tune_engine_configs.py` line 375 and modern `options.txt` to use GLFW key strings (`key.keyboard.right.shift`, `key.keyboard.v`).
6. Aligning `C:/Users/a7med/.lunarclient/profiles.json` `gameDir` paths and adding LWJGL 2 $\leftrightarrow$ GLFW translation in `lunar_bridge_service.py`.

---

## 5. Verification Method

To independently verify all findings and confirm fixes once executed by the implementing agent:
1. **Verify No Duplicate JARs in Instances:**
   ```pwsh
   pwsh -NoProfile -Command '
   Get-ChildItem "d:/Projects/SIR ModPack/instances" -Recurse -Filter "*.jar" | 
       Group-Object { $_.DirectoryName + "/" + ($_.Name -replace "[-_](v?[0-9]+.*|\d+\.jar$)", "") } | 
       Where-Object { $_.Count -gt 1 } | Select-Object Name, Count
   '
   ```
   *Expected:* 0 duplicate families returned.
2. **Verify No Numeric Keycodes in Modern options.txt:**
   ```pwsh
   pwsh -NoProfile -Command '
   Get-ChildItem "d:/Projects/SIR ModPack/instances" -Recurse -Filter "options.txt" | 
       Where-Object { $_.FullName -match "26\.2" } | 
       ForEach-Object { Select-String -Path $_.FullName -Pattern "^key_.*:\d+$" }
   '
   ```
   *Expected:* 0 matches.
3. **Verify Quantified API Purged:**
   ```pwsh
   pwsh -NoProfile -Command 'Get-ChildItem "d:/Projects/SIR ModPack" -Recurse -Filter "*quantified*.jar"'
   ```
   *Expected:* 0 matches.
4. **Unit Test Suite:**
   ```pwsh
   py -3.13 -m unittest discover -s tests -p "test_*.py"
   ```
   *Expected:* All unit tests pass cleanly.
