# Technical Investigation & Architectural Specification: Features 11 & 12 (Milestone 2)

**Author:** Explorer 3 (Milestone 2: Native JVM Launch Pipeline & Compatibility)  
**Target Subsystems:** `development/launcher_core/controls_service.py`, `development/launcher_core/logs_service.py`, `development/launcher_core/native_runner.py`, `tests/test_native_runner.py`  
**Date:** 2026-08-30  

---

## 1. Executive Summary

This report provides a comprehensive technical analysis, bidirectional conversion specifications, and architectural design for **Feature 11 (Dual-Mode Keybinding Injection)** and **Feature 12 (Non-blocking stdout/stderr Tailer & Crash Detection)** within the SIR Minecraft Ecosystem. In addition, it provides a comprehensive **Tier 1-4 Test Matrix** covering Features 7 through 12 to harden `tests/test_native_runner.py`.

### Key Discoveries & Architectural Gaps:
1. **Feature 11 (Dual-Mode Keybinding Injection)**:
   - **Current Flaw**: `ControlsService.apply_control_profile()` unconditionally writes modern GLFW token strings (e.g. `key.keyboard.f`, `key.keyboard.left.shift`) to all instance configurations—including Legacy 1.8.9 Forge (`instances/1.8.9/minecraft/options.txt`).
   - **Impact**: In Minecraft 1.8.9 (LWJGL 2), `GameSettings.java` calls `Integer.parseInt(val)` on key lines starting with `key_`. When 1.8.9 encounters string tokens, `Integer.parseInt` throws `NumberFormatException`, causing all injected keybindings to be lost or reset to default `0`.
   - **Solution**: Implement a version-aware `KeybindingTranslator` with bidirectional mapping between modern GLFW tokens and legacy LWJGL 2 integer scancodes, including negative-indexed mouse buttons (`button - 100`), key aliases (`togglePerspective` vs `perspective`), and atomic options preservation.
2. **Feature 12 (Non-blocking stdout/stderr Tailer & Real-Time Crash Trigger)**:
   - **Current Flaw**: `NativeMinecraftRunner.launch()` executes Minecraft by redirecting stdout/stderr directly to a file handle on disk without an active reader daemon or live event streaming.
   - **Impact**: UI has no real-time console feedback without polling disk files. Immediate JVM boot failures or runtime access violations do not trigger immediate UI alerts, leaving processes in ambiguous states.
   - **Solution**: Architect a non-blocking `ProcessLogStreamer` daemon featuring a thread-safe circular ring buffer (`collections.deque(maxlen=2000)`), real-time regex crash pattern scanner, automatic `CrashAnalyzer` diagnostics upon non-zero exit codes, and non-blocking `_emit_ui_event` dispatching.
3. **Comprehensive Test Coverage**:
   - `tests/test_native_runner.py` currently contains only 3 unit tests. A full Tier 1-4 test harness with >30 assertions covering RAM bounds, pre-launch native DLL resolution, dynamic classpath assembly, JRE detection, keybinding translation, and process log tailing is designed.

---

## 2. Feature 11 Investigation: Dual-Mode Keybinding Injection

### 2.1 Codebase Analysis (`development/launcher_core/controls_service.py`)
In `ControlsService`:
```python
# controls_service.py (lines 61-89)
target_options_files = [
    os.path.join(self.root_dir, "instances", instance_id, "minecraft", "options.txt"),
    os.path.join(self.root_dir, "instances", "26.2", "minecraft", "options.txt"),
    os.path.join(self.root_dir, "instances", "1.8.9", "minecraft", "options.txt")
]
for opt_path in target_options_files:
    if os.path.exists(opt_path):
        # Injects raw profile["keys"], which are strings like "key.keyboard.f"
```
**Deficiencies Identified**:
1. It loops over hardcoded paths rather than resolving the specific target instance directory.
2. It assumes uniform GLFW token syntax across all Minecraft versions.
3. In Legacy 1.8.9, key names differ (e.g. `key_key.togglePerspective` vs `key_key.perspective`, `key_of.key.zoom` vs `key_key.zoom`).

---

### 2.2 Complete GLFW Token String <-> LWJGL 2 Scancode Bidirectional Mapping

#### A. Keyboard Scancode Table
| Key Description | Modern GLFW Token (26.2 / 1.21.4) | Legacy LWJGL 2 Scancode (1.8.9) |
|---|---|:---:|
| **Escape** | `key.keyboard.escape` | `1` |
| **1 - 9, 0** | `key.keyboard.1` ... `key.keyboard.9`, `key.keyboard.0` | `2` to `10`, `11` |
| **Minus / Equal / Backspace** | `key.keyboard.minus`, `key.keyboard.equal`, `key.keyboard.backspace` | `12`, `13`, `14` |
| **Tab** | `key.keyboard.tab` | `15` |
| **Q, W, E, R, T, Y, U, I, O, P** | `key.keyboard.q`, `key.keyboard.w`, `key.keyboard.e`, `key.keyboard.r`, `key.keyboard.t`, `key.keyboard.y`, `key.keyboard.u`, `key.keyboard.i`, `key.keyboard.o`, `key.keyboard.p` | `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`, `24`, `25` |
| **Left Bracket / Right Bracket** | `key.keyboard.left.bracket`, `key.keyboard.right.bracket` | `26`, `27` |
| **Enter** | `key.keyboard.enter` | `28` |
| **Left Control** | `key.keyboard.left.control` | `29` |
| **A, S, D, F, G, H, J, K, L** | `key.keyboard.a`, `key.keyboard.s`, `key.keyboard.d`, `key.keyboard.f`, `key.keyboard.g`, `key.keyboard.h`, `key.keyboard.j`, `key.keyboard.k`, `key.keyboard.l` | `30`, `31`, `32`, `33`, `34`, `35`, `36`, `37`, `38` |
| **Semicolon / Apostrophe / Grave** | `key.keyboard.semicolon`, `key.keyboard.apostrophe`, `key.keyboard.grave.accent` | `39`, `40`, `41` |
| **Left Shift** | `key.keyboard.left.shift` | `42` |
| **Backslash** | `key.keyboard.backslash` | `43` |
| **Z, X, C, V, B, N, M** | `key.keyboard.z`, `key.keyboard.x`, `key.keyboard.c`, `key.keyboard.v`, `key.keyboard.b`, `key.keyboard.n`, `key.keyboard.m` | `44`, `45`, `46`, `47`, `48`, `49`, `50` |
| **Comma / Period / Slash** | `key.keyboard.comma`, `key.keyboard.period`, `key.keyboard.slash` | `51`, `52`, `53` |
| **Right Shift** | `key.keyboard.right.shift` | `54` |
| **Left Alt / Space / Caps Lock** | `key.keyboard.left.alt`, `key.keyboard.space`, `key.keyboard.caps.lock` | `56`, `57`, `58` |
| **F1 – F10** | `key.keyboard.f1` ... `key.keyboard.f10` | `59` to `68` |
| **F11 / F12** | `key.keyboard.f11`, `key.keyboard.f12` | `87`, `88` |
| **Numpad 0 – 9** | `key.keyboard.keypad.0` ... `key.keyboard.keypad.9` | `82`, `79`, `80`, `81`, `75`, `76`, `77`, `71`, `72`, `73` |
| **Right Control / Right Alt** | `key.keyboard.right.control`, `key.keyboard.right.alt` | `157`, `184` |
| **Arrow Up / Left / Right / Down**| `key.keyboard.up`, `key.keyboard.left`, `key.keyboard.right`, `key.keyboard.down` | `200`, `203`, `205`, `208` |
| **Home / Page Up / End / Page Down** | `key.keyboard.home`, `key.keyboard.page.up`, `key.keyboard.end`, `key.keyboard.page.down` | `199`, `201`, `207`, `209` |
| **Insert / Delete** | `key.keyboard.insert`, `key.keyboard.delete` | `210`, `211` |

#### B. Mouse Buttons Negative-Offset Indexing
In LWJGL 2 (Minecraft 1.8.9), mouse buttons are stored as negative integers using the standard formula:
$$\text{LWJGL2 Keycode} = \text{Button Index} - 100$$

| Mouse Button | Modern GLFW Token | Legacy LWJGL 2 Scancode | Formula Calculation |
|---|---|:---:|:---:|
| **Left Mouse Button** | `key.mouse.left` | `-100` | $0 - 100 = -100$ |
| **Right Mouse Button** | `key.mouse.right` | `-99` | $1 - 100 = -99$ |
| **Middle Mouse Button** | `key.mouse.middle` | `-98` | $2 - 100 = -98$ |
| **Mouse 4 (Back Button)** | `key.mouse.4` or `key.mouse.button.4` | `-97` | $3 - 100 = -97$ |
| **Mouse 5 (Forward Button)** | `key.mouse.5` or `key.mouse.button.5` | `-96` | $4 - 100 = -96$ |
| **Mouse 6 / 7 / 8** | `key.mouse.6`, `key.mouse.7`, `key.mouse.8` | `-95`, `-94`, `-93` | $5 - 100$, etc. |

---

### 2.3 Key Names & Aliases Across Minecraft Versions
| Logical Control Action | Modern 26.2 (1.21.4) Option Key | Legacy 1.8.9 Option Key |
|---|---|---|
| **Toggle Perspective (3rd Person)** | `key_key.perspective` | `key_key.togglePerspective` |
| **Zoom (OptiFine / Zoomify)** | `key_key.zoom` | `key_of.key.zoom` and `key_key.zoom` |
| **Player List (Tab HUD)** | `key_key.playerlist` | `key_key.playerlist` |
| **Sprint** | `key_key.sprint` | `key_key.sprint` |
| **Sneak** | `key_key.sneak` | `key_key.sneak` |
| **Attack / Destroy** | `key_key.attack` | `key_key.attack` |
| **Use Item / Place Block** | `key_key.use` | `key_key.use` |
| **Pick Block** | `key_key.pickItem` | `key_key.pickItem` |

---

### 2.4 Recommended Refactored Implementation Strategy for `ControlsService`

```python
class KeybindingMode:
    MODERN_GLFW = "glfw"
    LEGACY_LWJGL2 = "lwjgl2"

class ControlsService:
    # 1. Provide bidirectional GLFW <-> LWJGL2 lookup tables
    # 2. Implement detect_instance_mode(instance_dir, instance_id)
    #    - Inspects mmc-pack.json, instance.cfg, or options.txt header (version:xxxx)
    #    - If version < 1444 or instance_id in ["1.8.9", "1.8.9-ultra", "1.8.9-performance"] -> LEGACY_LWJGL2
    # 3. Implement translate_keys(keys_dict, mode)
    #    - Translates values and handles key aliases (e.g. perspective <-> togglePerspective)
    # 4. Implement apply_control_profile(profile_id, instance_id)
    #    - Reads options.txt
    #    - Preserves existing non-key options and comments
    #    - Writes translated keys using atomic_write_text
```

---

## 3. Feature 12 Investigation: Non-blocking stdout/stderr Tailer & Crash Detection

### 3.1 Architectural Deficiencies in Existing Runner
In `development/launcher_core/native_runner.py` (lines 704-715):
- The process is spawned with stdout/stderr piped directly to an OS file handle on disk.
- There is no live thread reading stdout, meaning:
  1. Frontend UI cannot stream live logs without polling disk files.
  2. Crash events are not detected in real time.
  3. When Minecraft exits with exit code > 0 (e.g. JVM exit code 1 or -1073740791), no diagnostic event is triggered to the user.

---

### 3.2 Async Real-Time Log Streaming & Ring Buffer Architecture

```
                    ┌────────────────────────┐
                    │ Minecraft JVM Process  │
                    └───────────┬────────────┘
                                │ stdout & stderr (PIPE)
                                ▼
                    ┌────────────────────────┐
                    │  AsyncLogTailer Daemon │ (Background Thread)
                    └───────────┬────────────┘
                                │
        ┌───────────────────────┼────────────────────────┐
        ▼                       ▼                        ▼
┌───────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Disk Log File │      │  Ring Buffer    │      │ Real-Time Crash │
│ (Launches/)   │      │ (deque max 2000)│      │ Pattern Scanner │
└───────────────┘      └────────┬────────┘      └────────┬────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐      ┌─────────────────┐
                       │  Live UI Events │      │  CrashAnalyzer  │
                       │ (game_log_line) │      │  & Diagnostics  │
                       └─────────────────┘      └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   UI Event      │
                                                │  (game_crashed) │
                                                └─────────────────┘
```

### 3.3 Real-Time Crash Signatures & Regex Matchers
The streamer scans every incoming line in real time against known fatal crash signatures:
1. **Out-of-Memory (OOM)**: `r"java\.lang\.OutOfMemoryError"` -> Immediate Heap/Metaspace exhaustion flag.
2. **Fabric/Forge Mixin Conflicts**: `r"(?:MixinTransformerError|MixinApplyError|InvalidMixinException).*from mod ([a-zA-Z0-9_\-]+)"` -> Offending mod identification.
3. **Class/Method Incompatibility**: `r"java\.lang\.(?:NoSuchMethodError|NoSuchFieldError|ClassNotFoundException|NoClassDefFoundError): (.*)"`.
4. **Native Driver Fault**: `r"(?:EXCEPTION_ACCESS_VIOLATION|# Problematic frame:.*(?:nvoglv64|atio6axx|ig9icd64|jvm\.dll))"`.
5. **Display / OpenGL Failure**: `r"(?:GLFW error 65542|No OpenGL context found|WGL:)"`.
6. **Forge Loader Abort**: `r"\[FML\]: Fatal errors were detected during the transition from"`

### 3.4 Process Exit Status Propagation & Lifecycle
When the JVM terminates (`proc.poll()` is not None):
- **Exit Code == 0**: Emit `game_exited` event with clean status.
- **Exit Code != 0** (or crash signature detected):
  1. Capture the last 200 lines from the circular ring buffer.
  2. Inspect `instances/<id>/minecraft/crash-reports/` for crash files created within the last 15 seconds.
  3. Execute `CrashAnalyzer.diagnose_crash(crash_text, filename)`.
  4. Dispatch `game_crashed` event with `{pid, exit_code, cause, offending_mod, fix, report_path}` to the frontend UI.
  5. Clean up process registries in `InstanceService.running_processes` and `TelemetryGovernorService`.

---

## 4. Comprehensive Test Infrastructure Specification (Features 7–12)

To ensure 100% test coverage and zero regression in `tests/test_native_runner.py`, the following four-tier test suite is specified:

### Test Suite Structure (`tests/test_native_runner.py`)

```
TestNativeRunner (unittest.TestCase)
├── Tier 1: Core Feature Verification (≥5 tests per feature)
│   ├── Feature 7 (Strict RAM): test_ram_allocation_bounds, test_ram_aikar_g1gc_flags, test_power_mode_thread_governor
│   ├── Feature 8 (Natives): test_natives_resolution_lwjgl3_modern, test_natives_resolution_lwjgl2_legacy, test_natives_jar_extraction
│   ├── Feature 9 (Classpath): test_dynamic_classpath_fabric_asm9, test_dynamic_classpath_forge_launchwrapper, test_classpath_deduplication
│   ├── Feature 10 (JRE Locator): test_jre_locator_java25_priority, test_jre_locator_java8_legacy, test_jre_search_roots_hierarchy
│   ├── Feature 11 (Keybindings): test_keybinding_translation_glfw_modern, test_keybinding_translation_scancode_legacy, test_mouse_button_negative_offset, test_options_txt_roundtrip_preservation
│   └── Feature 12 (Log Tailer): test_log_tailer_ring_buffer, test_log_tailer_realtime_line_callbacks, test_crash_signature_trigger_oom, test_crash_signature_trigger_mixin
│
├── Tier 2: Boundary & Corner Cases
│   ├── test_ram_boundary_1gb_floor_and_128gb_extreme
│   ├── test_unknown_keybinding_fallback_to_zero
│   ├── test_missing_version_json_graceful_recovery
│   ├── test_non_zero_exit_code_propagation_without_hang
│   └── test_corrupted_options_txt_recovery
│
├── Tier 3: Cross-Feature Integration Combinations
│   ├── test_modern_fabric_full_pipeline_synthesis (F7 + F8 + F9 + F10 + F11 + F12)
│   └── test_legacy_forge_full_pipeline_synthesis (F7 + F8 + F9 + F10 + F11 + F12)
│
└── Tier 4: Real-World Launch & Stress Scenarios
    ├── test_scenario_high_throughput_log_streaming_stress (1000 lines/sec)
    └── test_scenario_simulated_instant_jvm_crash_diagnostics
```

---

## 5. Concrete Test Matrix & Specifications for Worker

| Test Method Name | Features Exercised | Tier | Verification Invariant / Assertion |
|---|---|:---:|---|
| `test_ram_allocation_bounds` | F7 | T1 | `-Xmx` matches configured RAM; `-Xms` set to $\max(2, \text{ram}//2)$ |
| `test_power_mode_thread_governor` | F7 | T1 | `smooth` -> ParallelGCThreads=4; `turbo` -> matches system CPU cores |
| `test_natives_resolution_modern` | F8 | T1 | Returns path containing LWJGL 3 / GLFW binaries |
| `test_natives_resolution_legacy` | F8 | T1 | Returns path containing `Forge 1.8.9/natives` or `controllable_natives` |
| `test_dynamic_classpath_fabric` | F9 | T1 | ASM 9.10.1 and KnotClient prepended before game jars |
| `test_dynamic_classpath_forge` | F9 | T1 | LaunchWrapper 1.12 and Forge jar included; `FMLTweaker` in game args |
| `test_jre_locator_version_matching` | F10 | T1 | Java 25 detected for Modern 26.2; Java 8 detected for Legacy 1.8.9 |
| `test_keybinding_mode_detection` | F11 | T1 | Correctly identifies `LEGACY_LWJGL2` for 1.8.9 and `MODERN_GLFW` for 26.2 |
| `test_keybinding_scancode_translation` | F11 | T1 | `key.keyboard.w` -> `17`, `key.keyboard.left.shift` -> `42`, `key.mouse.left` -> `-100` |
| `test_keybinding_options_injection` | F11 | T2 | Modifies `options.txt` atomically while retaining existing `fov`, `gamma`, `renderDistance` |
| `test_log_tailer_buffer_streaming` | F12 | T1 | Streamed lines appear in ring buffer with FIFO truncation at max limit |
| `test_log_tailer_crash_detection` | F12 | T2 | `OutOfMemoryError` line triggers crash flag and diagnostic payload |
| `test_log_tailer_exit_propagation` | F12 | T2 | Subprocess exit code `1` triggers `on_crash` callback with `CrashAnalyzer` output |

---

## 6. Implementation Strategy Checklist for Worker

- [ ] **Step 1: Upgrade `ControlsService` (`development/launcher_core/controls_service.py`)**:
  - Add `KeybindingTranslator` dictionary containing complete GLFW <-> LWJGL 2 scancodes and mouse button offsets.
  - Implement instance version/mode detection (`detect_mode(instance_path)`).
  - Update `apply_control_profile` to translate keybindings dynamically based on target instance mode and apply atomic write.
- [ ] **Step 2: Implement Non-blocking Streamer in `NativeMinecraftRunner` (`development/launcher_core/native_runner.py`)**:
  - Add `ProcessLogStreamer` background daemon class with `queue.Queue` / `deque(maxlen=2000)` buffer.
  - Pipe subprocess stdout/stderr and stream lines in real time to both file and callbacks.
  - Scan lines for fatal crash regex signatures and trigger `CrashAnalyzer` on exit.
  - Add exit watcher thread to push exit status events (`game_exited` / `game_crashed`).
- [ ] **Step 3: Implement Comprehensive Test Suite in `tests/test_native_runner.py`**:
  - Expand test suite to implement all specified Tier 1-4 test methods.
  - Run `python -m unittest tests/test_native_runner.py` and verify 100% pass rate.
