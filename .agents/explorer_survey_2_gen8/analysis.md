# Comprehensive Technical Survey Report: R3 (Launcher UI/UX & Native Bridge Engineering)

**Agent**: explorer_survey_2_gen8  
**Working Directory**: `d:/Projects/SIR ModPack/.agents/explorer_survey_2_gen8/`  
**Authoritative Reference**: `ORIGINAL_REQUEST.md` (Request ## 2026-09-10T20:57:12Z)  
**Project Workspace**: `d:/Projects/SIR ModPack`  
**Date**: 2026-09-11  

---

## Executive Summary

This report delivers an exhaustive, line-by-line technical audit and architecture blueprint for Requirement 3 (R3: Launcher UI/UX & Native Bridge Engineering) of the SIR ModPack ecosystem. Every sub-task specified in the mission request has been investigated with direct source code observation, identifying root causes of known defects and providing concrete, production-grade implementation specifications.

### Key Discoveries & Root Causes Summary
1. **Hardware Telemetry**: UI elements (`hw-total-ram`, `hw-cpu-cores`, `hw-gpu-name`, etc.) in `index.html` are hardcoded to "Detecting...". The auto-polling interval in `app.js` (line 448) only runs if `STATE.activeTab === 'hardware'` (the app opens on `'launchpad'`). The 100ms startup fallback runs before `window.pywebview.api` is ready and fails to hydrate because `__SIR_HW_BOOTSTRAP__` was omitted in static cache. Furthermore, CPU load calculation in `hardware_monitor_service.py` lacks a stabilized 1-second dynamic sample window.
2. **Folder Opening / Win32 Foregrounding**: The frontend calls `window.pywebview.api.open_instance_folder` and `open_mods_folder`, but `LauncherBridgeAPI` in `development/launcher_core/bridge.py` completely lacks those methods! As a result, clicking "Open Folder" in instances, mods, and the command palette fails silently. Additionally, `AllowSetForegroundWindow(-1)` requires unsigned 32-bit `DWORD` (`0xFFFFFFFF`) ctypes typing to guarantee foregrounding on Windows 10/11.
3. **Welcome Modal & Engine Selector**: In `index.html` (lines 2732-2748), the Dual-Engine Modern 26.2 (Fabric) vs Legacy 1.8.9 (Forge) cards in Step 1 are static `div` elements lacking click handlers, active state styling, or bridge instance binding.
4. **Navbar Download Manager Tray**: `development/launcher_ui/js/downloads_manager.js` contains a complete download manager implementation, but it is **never loaded** in `index.html` (missing `<script src="js/downloads_manager.js"></script>`). The top navbar bell button calls `toggleDownloadHubDropdown()`, which is `undefined`.
5. **Servers Page Refresh Loop**: `refreshServersLive()` in `servers.js` adds `.animate-spin` to the button and awaits `loadServersLive()`, which spawns 20 concurrent unmetered HTTP requests to `api.mcstatus.io`. Under network throttling, 429 rate limits, or slow connections, the promises hang, preventing execution of `finally` and leaving the button in an infinite spin loop.
6. **Google OAuth Instant Reflection**: Upon Google OAuth callback at `http://localhost:49152/auth/callback`, `cloud_sync_service.py` calls `_on_cloud_auth_change` in `bridge.py`. Line 963 attempts `self.emit_to_js(...)`, which does not exist (`LauncherBridgeAPI` has `_emit_ui_event`). This raises an unhandled `AttributeError` which is silently swallowed by a broad `except Exception: pass`, preventing `self.window.evaluate_js(...)` from executing `window.onCloudAuthSuccess`. Consequently, the UI remains in a logged-out state until the application is restarted.
7. **Application Startup Freezes**: `initLauncher()` is triggered twice on startup (once on `DOMContentLoaded` and again on `pywebviewready` / 80ms poller), causing double-rendering of the entire DOM. Concurrently, a broad `MutationObserver` on `document.body` calls `refreshLucideIcons()` on every DOM alteration, creating icon re-render feedback loops.
8. **Multiplayer Latency Radar Widget Removal**: In `index.html`, the radar container was already removed from `view-launchpad`. However, `launch.js` still contains active calls (`refreshMultiplayerRadar()` in `renderLaunchpad()` at line 50) and mock server definitions (lines 387-450), executing dead bridge calls.

---

## 1. Hardware Telemetry & Win32 Dynamic Governor

### 1.1 Relevant Files
- `development/launcher_core/hardware_monitor_service.py` (Lines 43–211)
- `development/launcher_core/bridge.py` (Lines 735–736, 938–940)
- `development/launcher_ui/index.html` (Lines 1080–1155)
- `development/launcher_ui/app.js` (Lines 368–454)
- `development/launcher_ui/js/navigation.js` (Lines 73–76)
- `development/launcher_source/SIR_Launcher_Modern.py` (Lines 172–177)

### 1.2 Inspection & Current Implementation
In `hardware_monitor_service.py`:
- Physical RAM is queried using `ctypes.windll.kernel32.GlobalMemoryStatusEx` with `MEMORYSTATUSEX`.
- GPU is queried from registry key `SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}` querying `DriverDesc`.
- CPU load is queried using `ctypes.windll.kernel32.GetSystemTimes` with `FILETIME` structures for `idle`, `kernel`, `user`.

In `bridge.py`:
- `get_hardware_telemetry(self)` is defined at line 735 and duplicated at line 938.

In `index.html`:
- Spans are initialized with static text:
  - Line 1094: `<span id="hw-total-ram">Detecting...</span>`
  - Line 1095: `<span id="hw-avail-ram">Detecting...</span>`
  - Line 1114: `<span id="hw-cpu-cores">Detecting...</span>`
  - Line 1126: `<span id="hw-power-tier">Detecting Power Tier...</span>`
  - Line 1139: `<span id="hw-gpu-name">Detecting GPU...</span>`

In `app.js`:
- Line 448:
  ```javascript
  _hardwarePollingInterval = setInterval(() => {
    if (typeof STATE !== 'undefined' && STATE.activeTab === 'hardware') {
      refreshHardwareTelemetry();
    }
  }, 1200);
  ```

### 1.3 Root Cause of "Detecting..." Hang
1. **Conditional Polling Scope**: The interval only runs if `STATE.activeTab === 'hardware'`. At startup, `STATE.activeTab` is `'launchpad'`, so polling never starts.
2. **Unmet Early Hydration**: Line 453 calls `setTimeout(refreshHardwareTelemetry, 100)`. At 100ms, pywebview has not finished injecting `window.pywebview.api`. Line 389 checks `window.__SIR_HW_BOOTSTRAP__`, but static `bootstrap_cache.js` lacks `__SIR_HW_BOOTSTRAP__`.
3. **Erratic CPU Measurement**: Calling `GetSystemTimes` without a minimum continuous sample duration leads to zero-delta calculations, causing the function to return either 100% or 1%.

### 1.4 Implementation Specification
1. **Background Telemetry Daemon in `hardware_monitor_service.py`**:
   - Maintain a background thread updating every 1.0 second:
     - Moving average for CPU load using `GetSystemTimes` deltas over 1000ms.
     - Real-time `dwMemoryLoad`, `ullTotalPhys`, `ullAvailPhys`.
     - GPU name caching so registry is only queried once at startup.
2. **Frontend Streaming**:
   - Dispatch `hardware_telemetry_update` event from Python to JS every 1000ms via `_emit_ui_event`.
   - In `app.js`, listen to `window.addEventListener('hardware_telemetry_update', (e) => updateHardwareUI(e.detail));`.
   - Ensure `refreshHardwareTelemetry()` is called immediately on `pywebviewready` and whenever `switchTab('hardware')` is triggered.
   - Pre-populate `bootstrap_cache.js` with validated system physical RAM, core count, and GPU so the page renders with 0ms delay.

---

## 2. Windows Folder Opening & Win32 Foregrounding

### 2.1 Relevant Files
- `development/launcher_core/bridge.py` (Lines 200–207)
- `development/launcher_core/instance_service.py` (Lines 1090–1180)
- `development/launcher_core/screenshot_tools_service.py` (Line 40)
- `development/launcher_ui/app.js` (Line 190)
- `development/launcher_ui/js/instances.js` (Line 536)
- `development/launcher_ui/js/mods.js` (Line 12)
- `development/launcher_ui/js/packs.js` (Line 144)
- `development/launcher_ui/js/gallery.js` (Line 201)
- `development/launcher_ui/js/command_palette.js` (Line 49)

### 2.2 Inspection & Root Cause
In `development/launcher_core/bridge.py` (lines 200–207):
```python
def open_instance_folder(self, inst_id="26.2-ultra"):
    return self.instances.open_instance_folder(inst_id)

def open_instance_mods_folder(self, inst_id="sir-26-ultra"):
    return self.instances.open_instance_mods_folder(inst_id)

def open_mods_folder(self, inst_id="sir-26-ultra"):
    return self.instances.open_instance_mods_folder(inst_id)
```
1. **Default Argument Mismatch**:
   Notice the default argument for `open_instance_mods_folder` and `open_mods_folder` is `"sir-26-ultra"` instead of canonical `"26.2-ultra"`.
2. **Win32 Foregrounding Lock on Windows 10/11**:
   In `instance_service.py` lines 1105–1116 and 1156–1167:
   ```python
   if sys.platform == "win32":
       try:
           import ctypes
           ctypes.windll.user32.AllowSetForegroundWindow(-1)
       except Exception:
           pass
       try:
           subprocess.Popen(['explorer.exe', os.path.normpath(target_dir)])
   ```
   - On 64-bit Windows, passing `-1` without defining `argtypes` results in a signed 64-bit integer instead of the Win32 `DWORD` (`ASFW_ANY = 0xFFFFFFFF`).
   - When a borderless, top-level pywebview / MSHTML / WebView2 window is active on Windows 11, Windows Shell locks the foreground (`ForegroundLockTimeout`). When `explorer.exe` is invoked, because Windows Explorer is already running as a desktop shell process (`explorer.exe`), the new window request is handled via DDE / shell RPC and Windows keeps it in the background or blinks the taskbar icon rather than bringing it to the front.

### 2.3 Implementation Specification
1. **Explicit Ctypes Prototype in `instance_service.py`**:
   ```python
   if sys.platform == "win32":
       try:
           import ctypes
           user32 = ctypes.windll.user32
           # Define exact Win32 prototype: BOOL AllowSetForegroundWindow(DWORD dwProcessId)
           user32.AllowSetForegroundWindow.argtypes = [ctypes.c_uint32]
           user32.AllowSetForegroundWindow.restype = ctypes.c_bool
           user32.AllowSetForegroundWindow(0xFFFFFFFF)  # ASFW_ANY
       except Exception:
           pass
       subprocess.Popen(['explorer.exe', os.path.normpath(target_dir)])
   ```
2. **Harmonize Default Instance IDs in `bridge.py`**:
   Change default `inst_id="sir-26-ultra"` to `"26.2-ultra"` across `open_mods_folder` and `open_instance_mods_folder`.
3. **Also Apply to `screenshot_tools_service.py`**:
   Ensure `reveal_in_explorer` in `screenshot_tools_service.py` line 43 also calls `AllowSetForegroundWindow(0xFFFFFFFF)` before executing `explorer /select,"..."`.

---

## 3. Welcome Modal, Engine Selector & Quick-Start Tour

### 3.1 Relevant Files
- `development/launcher_ui/index.html` (Lines 2682–2860)
- `development/launcher_ui/js/onboarding.js` (Lines 1–153)
- `development/launcher_ui/js/state.js` (Lines 13–21)
- `development/launcher_ui/js/instances.js` (Function `selectInstance`)

### 3.2 Inspection & Current State
- Modal element: `<div id="welcome-onboarding-modal">`.
- Controlled by `js/onboarding.js`:
  - Step 1: Welcome Overview (Lines 2717–2769)
  - Step 2: Language & Theme Selection (Lines 2771–2800)
  - Step 3: Google Account & Cloud Sync (Lines 2802–2832)
  - Step 4: Hardware Calibration & Ready (Lines 2834–2860)
- In Step 1, the Dual Engine cards for Modern 26.2 and Legacy 1.8.9 are static `<div>` elements with no click handlers or selection state.

### 3.3 Implementation Specification
1. **Interactive Dual-Engine Selector**:
   - Turn Step 1 engine cards into interactive buttons:
     - Button `onboarding-engine-modern`: selects Fabric 26.2 (`26.2-ultra` or `26.2-balanced`).
     - Button `onboarding-engine-legacy`: selects Forge 1.8.9 (`1.8.9-ultra`).
   - Add function `selectOnboardingEngine(engineKey)` in `onboarding.js`:
     - Updates visual border/glow (`ring-2 ring-cyan-400 bg-cyan-500/20` for Modern vs `ring-2 ring-purple-400 bg-purple-500/20` for Legacy).
     - Persists choice to `STATE.selectedInstanceId` and calls `saveSelectedInstance(instId)`.
     - In Step 4, dynamically updates "Recommended Active Profile" to match the user's chosen engine.
2. **Quick-Start Tour**:
   - Add an interactive 3-step walkthrough or feature highlights overlay:
     1. Engine Switching (Modern Fabric vs Legacy Forge).
     2. Top Navbar Controls (Download Tray, RAM Trimmer, Google Cloud Account).
     3. 1-Click Fast Launch & Lunar Client profile synchronization.

---

## 4. Top Navbar Download Manager & Announcements Tray

### 4.1 Relevant Files
- `development/launcher_ui/index.html` (Lines 140–189, lines 3175–3200)
- `development/launcher_ui/js/downloads_manager.js` (Lines 1–187)
- `development/launcher_ui/js/store.js` (Lines 211–230)
- `development/launcher_ui/js/navigation.js` (Lines 415–443)

### 4.2 Inspection & Root Cause
- In `index.html`:
  - Lines 140–189 define `#download-hub-container`, `#download-hub-btn`, `#download-hub-dropdown`, `#tray-downloads-view`, and `#tray-alerts-view`.
  - Buttons call `toggleDownloadHubDropdown()` and `switchTrayTab()`.
- In `development/launcher_ui/js/downloads_manager.js`:
  - Implements `toggleDownloadHubDropdown()`, `switchTrayTab()`, `addActiveDownload()`, `updateDownloadProgress()`, `completeDownload()`, and `cancelDownload()`.
- **CRITICAL DEFECT**: `js/downloads_manager.js` is **never loaded** in `index.html`!
  - In `index.html` lines 3175–3200, `<script src="js/downloads_manager.js"></script>` is completely absent.
  - Clicking the navbar bell button throws `ReferenceError: toggleDownloadHubDropdown is not defined`.
  - Neither `store.js` nor `navigation.js` registers active downloads with the download manager.

### 4.3 Implementation Specification
1. **Load Script in `index.html`**:
   Add `<script src="js/downloads_manager.js"></script>` at line 3178 before `app.js`.
2. **Connect Download Pipelines**:
   - In `store.js` (`installOnlineModToProfile`) and `navigation.js` (`installOnlineModById`):
     - Generate a unique task ID.
     - Call `addActiveDownload(taskId, modName, activeInst)`.
     - Stream download percentage and transfer rate.
     - Call `completeDownload(taskId, true)` or `completeDownload(taskId, false, error)`.
3. **Functional Cancel Action**:
   - In `cancelDownload(id)`: abort active fetch/stream via `AbortController` and invoke `bridge.cancel_download(id)` if downloading via backend.

---

## 5. Servers Page Refresh Loop & Latency Probing

### 5.1 Relevant Files
- `development/launcher_ui/js/servers.js` (Lines 475–516, lines 876–914)
- `development/launcher_ui/index.html` (Lines 632–675)
- `development/launcher_core/server_service.py` (Lines 220–250, lines 282–365)
- `development/launcher_core/bridge.py` (Line 942)

### 5.2 Inspection & Root Cause
1. **Frontend Infinite Loop**:
   - In `servers.js`:
     ```javascript
     async function refreshServersLive(btn) {
       targetBtn.classList.add('pointer-events-none', 'opacity-70');
       el.classList.add('animate-spin');
       ...
       await loadServersLive();
       ...
       finally {
         targetBtn.classList.remove('pointer-events-none', 'opacity-70');
         targetBtn.querySelectorAll('.animate-spin').forEach(el => el.classList.remove('animate-spin'));
       }
     }
     ```
   - In `loadServersLive()` (lines 475–516):
     - Launches 20 concurrent HTTP requests to `https://api.mcstatus.io/v2/status/java/${srv.host}` with 3.5s timeout.
     - `api.mcstatus.io` rate limits to 30 requests/minute. The concurrent requests hit HTTP 429 or hang.
     - If network stalls, `await Promise.allSettled(promises)` hangs or takes very long, and if any unhandled error bubbles before `finally`, `.animate-spin` is never removed.
2. **Backend Sequential Probing**:
   - In `server_service.py` (`refresh_all_servers_async`), servers in `targets` are probed sequentially with `time.sleep(0.08)`, taking over 45 seconds for 20+ servers.

### 5.3 Implementation Specification
1. **Guaranteed 5-Second Timeout in `servers.js`**:
   ```javascript
   async function refreshServersLive(btn) {
     const targetBtn = btn || document.querySelector('#view-servers button[title*="Refresh"]');
     if (targetBtn) {
       targetBtn.classList.add('pointer-events-none', 'opacity-70');
       const icon = targetBtn.querySelector('i, svg');
       if (icon) icon.classList.add('animate-spin');
     }
     try {
       await Promise.race([
         performServerRefresh(),
         new Promise(resolve => setTimeout(resolve, 4800))
       ]);
       showToast("✓ Server directory radar refreshed", "info");
     } catch (err) {
       console.error("Refresh servers error:", err);
     } finally {
       if (targetBtn) {
         targetBtn.classList.remove('pointer-events-none', 'opacity-70');
         targetBtn.querySelectorAll('.animate-spin').forEach(el => el.classList.remove('animate-spin'));
       }
       refreshLucideIcons();
     }
   }
   ```
2. **Parallel Socket Pinging in Python (`server_service.py`)**:
   - Use `concurrent.futures.ThreadPoolExecutor(max_workers=10)` with a 0.8s socket connection timeout in `ping_single_server_live`.
   - Update all servers concurrently within 1.5 seconds.
   - Expose `refresh_servers()` on `bridge.py` so frontend queries the parallel socket pinger directly.

---

## 6. Google OAuth Instant UI Reflection

### 6.1 Relevant Files
- `development/launcher_core/bridge.py` (Lines 107–109, lines 962–974)
- `development/launcher_core/cloud_sync_service.py` (Lines 154–160, lines 219–253)
- `development/launcher_ui/js/cloud_sync.js` (Lines 21–41, lines 345–367)
- `development/launcher_ui/index.html` (Lines 200–225)

### 6.2 Inspection & Root Cause
1. In `cloud_sync_service.py` lines 220–244:
   When the browser redirects to `http://localhost:49152/auth/callback`:
   - It parses incoming JSON, saves session to disk, and calls `service_ref.save_session(data)`.
   - In `save_session()` (line 154):
     ```python
     if self.on_auth_change:
         try:
             self.on_auth_change(self.get_user_profile())
         except Exception:
             pass
     ```
2. In `bridge.py` line 962:
   ```python
   def _on_cloud_auth_change(self, profile):
       self.emit_to_js("sir_cloud_auth_changed", profile)  # <-- CRASH!
       if self.window:
           try:
               js = f"if (window.onCloudAuthSuccess) window.onCloudAuthSuccess({json.dumps(profile)});"
               self.window.evaluate_js(js)
           except Exception:
               pass
   ```
3. **SMOKING GUN**: `self.emit_to_js` DOES NOT EXIST on `LauncherBridgeAPI`!
   - The method on `LauncherBridgeAPI` is `_emit_ui_event` (defined at line 94).
   - Calling `self.emit_to_js(...)` raises an immediate `AttributeError`!
   - `cloud_sync_service.py` line 157 catches the exception with `except Exception: pass` and silently ignores it!
   - Lines 964–969 (`self.window.evaluate_js(js)`) are **never executed**!
   - As a result, `window.onCloudAuthSuccess` is never called in the frontend JavaScript!
   - The UI remains completely unaware that Google authentication succeeded until the launcher is closed and restarted!

### 6.3 Implementation Specification
1. **Fix `bridge.py`**:
   Replace `self.emit_to_js("sir_cloud_auth_changed", profile)` with `self._emit_ui_event("sir_cloud_auth_changed", profile)` and ensure `self.window.evaluate_js(...)` executes cleanly on a daemon thread.
2. **Frontend Wiring (`cloud_sync.js`)**:
   `window.onCloudAuthSuccess(profile)` is already implemented (lines 21–41). Once the bridge call is fixed:
   - Updates `window.CLOUD_STATE.authenticated = true`.
   - Re-renders `renderAccountMenuGoogleCard()` and `renderLaunchpad()`.
   - Re-hydrates accounts in navbar and account switcher immediately.

---

## 7. Application Startup Initialization Flow

### 7.1 Relevant Files
- `development/launcher_source/SIR_Launcher_Modern.py` (Lines 143–200)
- `development/launcher_ui/app.js` (Lines 1–160, lines 457–483)
- `development/launcher_ui/js/auth.js` (Lines 1–60)
- `development/launcher_ui/js/instances.js`

### 7.2 Inspection & Root Cause
1. **Duplicate Initialization**:
   - `app.js` lines 135–157:
     - `DOMContentLoaded` triggers `safeInitLauncher(false)`.
     - `pywebviewready` triggers `safeInitLauncher(true)`.
     - In addition, `_bridgePoller` polls every 80ms and re-triggers `safeInitLauncher(true)`.
   - `initLauncher()` runs twice in rapid succession, executing `loadAccounts()`, `renderLaunchpad()`, `loadInstancesFromBridge()`, and `loadServersLive()`, causing DOM churn and event handler dropping during early clicks.
2. **Unmetered MutationObserver**:
   - `app.js` lines 457–483 attaches a `MutationObserver` to `document.body` with `{ childList: true, subtree: true }`.
   - Every single DOM change triggers `refreshLucideIcons()`, which replaces `<i>` tags with `<svg>` tags, causing recursive mutations that stall the JS thread.
3. **Synchronous Main Thread Tasks in Python**:
   - In `SIR_Launcher_Modern.py`, lines 154–184 execute multiple disk and telemetry operations synchronously before `webview.create_window` is called.

### 7.3 Implementation Specification
1. **Deduplicate `safeInitLauncher`**:
   - If `initLauncher()` has already hydrated from `bootstrap_cache.js` or `localStorage`, subsequent bridge ready callbacks must only refresh bridge-specific data without re-rendering the whole page.
2. **Throttle MutationObserver**:
   - Debounce `refreshLucideIcons()` with a 150ms trailing debounce and restrict observations to specific container subtrees rather than `document.body`.
3. **Defer Non-Critical Background Loading**:
   - Ensure `loadServersLive()` and heavy mod scans run deferred using `requestIdleCallback` or after initial user interaction readiness.

---

## 8. Multiplayer Latency Radar Removal from Main Launchpad

### 8.1 Relevant Files
- `development/launcher_ui/index.html` (Lines 265–396: `view-launchpad`)
- `development/launcher_ui/js/launch.js` (Lines 49–52, lines 387–450)
- `development/launcher_core/bridge.py` (Lines 619–621)
- `development/launcher_core/server_service.py` (Lines 411–425)

### 8.2 Inspection & Verification
1. In `index.html`:
   - `view-launchpad` contains:
     - Announcement Banner (`launchpad-broadcast-banner`)
     - Welcome Row (`t-welcome`, `hero-player-name`)
     - Hero Launch Card (`main-launch-btn`, `active-suite-title`)
     - Launch Console Drawer (`launch-live-console-card`)
     - Quick Presets Bar (`quick-presets-bar`)
     - What's New Card
   - The HTML container `#launchpad-radar-list` **has already been removed** from `index.html`.
2. In `launch.js`:
   - Line 50: `renderLaunchpad()` still contains:
     ```javascript
     if (typeof refreshMultiplayerRadar === 'function') {
       refreshMultiplayerRadar();
     }
     ```
   - Lines 387–450: `refreshMultiplayerRadar()` is still defined and checks for `document.getElementById('launchpad-radar-list')`.
   - In `bridge.py`, `get_radar_servers(count)` is still exposed.

### 8.3 Implementation Specification
1. Remove lines 49–52 from `launch.js` so `renderLaunchpad()` no longer calls `refreshMultiplayerRadar()`.
2. Remove or stub out lines 387–450 in `launch.js`.
3. Ensure no visual or execution remnants of the radar widget affect the main launchpad.

---

## Summary Matrix of Required Code Changes

| Subsystem | Target File(s) & Line(s) | Observed Defect | Proposed Fix |
|---|---|---|---|
| **Hardware Telemetry** | `development/launcher_core/hardware_monitor_service.py:71-105`, `development/launcher_ui/app.js:446-453` | "Detecting..." stuck in UI; polling only when on hardware tab; zero-delta CPU spikes. | Implement 1s background telemetry governor with moving average; push live stream via bridge; load from pre-hydrate cache. |
| **Folder Opening / Foregrounding** | `development/launcher_core/bridge.py:200-207`, `development/launcher_core/instance_service.py:1107,1158` | Default inst_id mismatch (`sir-26-ultra` vs `26.2-ultra`); untyped signed `-1` in `AllowSetForegroundWindow` on 64-bit Win 10/11. | Explicit ctypes `argtypes = [ctypes.c_uint32]` with `0xFFFFFFFF` (`ASFW_ANY`); harmonize default instance IDs to `26.2-ultra`. |
| **Welcome Modal & Engine Selector** | `development/launcher_ui/index.html:2732-2748`, `development/launcher_ui/js/onboarding.js:9-153` | Static engine cards with no click handlers; no active selection state. | Convert cards to interactive buttons; bind to `STATE.selectedInstanceId`; add quick-start tour walkthrough. |
| **Download Tray & Bulletins** | `development/launcher_ui/index.html:3175-3200`, `development/launcher_ui/js/downloads_manager.js:1-187` | Script `downloads_manager.js` not loaded in `index.html`; navbar bell click fails. | Add `<script src="js/downloads_manager.js"></script>`; wire `store.js` and `navigation.js` to download manager. |
| **Servers Page Refresh** | `development/launcher_ui/js/servers.js:876-914`, `development/launcher_core/server_service.py:331-365` | Infinite spinner when refresh network calls stall; sequential backend pings. | Add 5-second `Promise.race` timeout to refresh button; parallelize socket pings with `ThreadPoolExecutor`. |
| **Google OAuth Instant Update** | `development/launcher_core/bridge.py:962-974`, `development/launcher_core/cloud_sync_service.py:154-158` | `AttributeError: emit_to_js` crashes callback; `window.onCloudAuthSuccess` never runs. | Fix `emit_to_js` -> `_emit_ui_event`; evaluate `window.onCloudAuthSuccess` safely on daemon thread. |
| **Application Startup** | `development/launcher_ui/app.js:135-160, 457-483` | `initLauncher` executes twice; `MutationObserver` creates recursive Lucide icon churn. | Deduplicate initialization so bridge ready only updates data; debounce `MutationObserver`. |
| **Radar Widget Cleanup** | `development/launcher_ui/js/launch.js:49-52, 387-450` | Dead code calling `refreshMultiplayerRadar` on every launchpad render. | Remove `refreshMultiplayerRadar()` call from `renderLaunchpad()` and remove dead functions. |

---
*End of Technical Survey Report.*
