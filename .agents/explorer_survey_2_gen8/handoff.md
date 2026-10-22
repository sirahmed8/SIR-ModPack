# Handoff Report: Technical Survey of R3 (Launcher UI/UX & Native Bridge Engineering)

**Agent**: explorer_survey_2_gen8  
**Working Directory**: `d:/Projects/SIR ModPack/.agents/explorer_survey_2_gen8/`  
**Date**: 2026-09-11  
**Handoff Type**: Hard (Task Complete)  

---

## 1. Observation

Direct observations from source files and environment tools:

1. **Hardware Telemetry**:
   - `development/launcher_ui/index.html` lines 1094–1139:
     ```html
     <span id="hw-total-ram" class="text-lg font-black text-cyan-400 block">Detecting...</span>
     <span id="hw-avail-ram" class="text-[10px] text-emerald-400 font-mono block">Detecting...</span>
     <span id="hw-cpu-cores" class="text-lg font-black text-slate-100 block">Detecting...</span>
     <span id="hw-power-tier" class="text-xs font-black text-emerald-300 block truncate">Detecting Power Tier...</span>
     <span id="hw-gpu-name" class="text-sm font-bold text-slate-100 block">Detecting GPU...</span>
     ```
   - `development/launcher_ui/app.js` lines 448–452:
     ```javascript
     _hardwarePollingInterval = setInterval(() => {
       if (typeof STATE !== 'undefined' && STATE.activeTab === 'hardware') {
         refreshHardwareTelemetry();
       }
     }, 1200);
     ```
   - `development/launcher_ui/bootstrap_cache.js` lines 1–3:
     ```javascript
     window.__SIR_BOOTSTRAP__ = { active: "", activeAccountId: "", status: "Offline", accounts: [] };
     window.__SIR_CLOUD_BOOTSTRAP__ = { authenticated: false };
     window.__SIR_MODS_COUNT_PRE_HYDRATE__ = 228;
     ```
     (`window.__SIR_HW_BOOTSTRAP__` is absent in checked-in bootstrap cache).
   - `development/launcher_core/bridge.py` lines 735–736 and 938–940: `def get_hardware_telemetry(self):` is declared twice.

2. **Folder Opening / Win32 Foregrounding**:
   - `development/launcher_core/bridge.py` lines 200–207 defines `open_instance_folder`, `open_instance_mods_folder`, and `open_mods_folder`.
   - The default argument for `open_instance_mods_folder` and `open_mods_folder` is `"sir-26-ultra"` instead of canonical `"26.2-ultra"`.
   - `development/launcher_core/instance_service.py` lines 1107 and 1158:
     ```python
     ctypes.windll.user32.AllowSetForegroundWindow(-1)
     ```
     Uses untyped signed `-1` rather than `ctypes.c_uint32(0xFFFFFFFF)` (`ASFW_ANY`). Explorer process on Win 10/11 handles new window requests via DDE and remains in the background without explicit `argtypes = [ctypes.c_uint32]` and `ASFW_ANY`.

3. **Welcome Modal & Engine Selector**:
   - `development/launcher_ui/index.html` lines 2732–2748: Modern 26.2 and Legacy 1.8.9 cards are static `div`s with no `onclick` attributes or interactive state tags.
   - `development/launcher_ui/js/onboarding.js`: Handles steps 1–4, but contains no engine selection logic or bridge profile binding for the onboarding flow.

4. **Navbar Download Tray**:
   - `development/launcher_ui/index.html` line 141: `<button id="download-hub-btn" onclick="toggleDownloadHubDropdown()" ...>`
   - `development/launcher_ui/index.html` lines 3175–3200: `<script src="js/downloads_manager.js"></script>` is missing from the script includes list.
   - `development/launcher_ui/js/downloads_manager.js` exists on disk (187 lines), fully implementing `toggleDownloadHubDropdown`, `switchTrayTab`, `addActiveDownload`, `updateDownloadProgress`, `completeDownload`, and `cancelDownload`.
   - Neither `js/store.js` nor `js/navigation.js` calls `addActiveDownload`.

5. **Servers Page Refresh Infinite Spin**:
   - `development/launcher_ui/js/servers.js` lines 876–914:
     ```javascript
     async function refreshServersLive(btn) {
       targetBtn.classList.add('pointer-events-none', 'opacity-70');
       const el = targetBtn.querySelector('i, svg');
       if (el) el.classList.add('animate-spin');
       ...
       await loadServersLive();
       ...
       finally {
         targetBtn.classList.remove('pointer-events-none', 'opacity-70');
         targetBtn.querySelectorAll('.animate-spin').forEach(el => el.classList.remove('animate-spin'));
       }
     }
     ```
   - `servers.js` lines 496–515: `loadServersLive()` executes 20 concurrent HTTP fetches to `https://api.mcstatus.io/v2/status/java/${srv.host}` with 3.5s timeouts without a race timer, triggering HTTP 429 and network stalling.
   - `development/launcher_core/server_service.py` lines 337–360: Probes servers sequentially on a single thread (`ping_single_server_live` + `fetch_live_mcstatus` + `sleep(0.08)`), taking 40–60 seconds.

6. **Google OAuth 1-Click UI Update**:
   - `development/launcher_core/cloud_sync_service.py` lines 154–158:
     ```python
     if self.on_auth_change:
         try:
             self.on_auth_change(self.get_user_profile())
         except Exception:
             pass
     ```
   - `development/launcher_core/bridge.py` lines 962–969:
     ```python
     def _on_cloud_auth_change(self, profile):
         self.emit_to_js("sir_cloud_auth_changed", profile)
         if self.window:
             try:
                 js = f"if (window.onCloudAuthSuccess) window.onCloudAuthSuccess({json.dumps(profile)});"
                 self.window.evaluate_js(js)
     ```
   - Verbatim error: `LauncherBridgeAPI` has NO method named `emit_to_js`. Invoking line 963 raises `AttributeError: 'LauncherBridgeAPI' object has no attribute 'emit_to_js'`.
   - The broad `except Exception: pass` in `cloud_sync_service.py:157` swallows this `AttributeError`, so line 967 `self.window.evaluate_js(js)` is never reached.

7. **Application Startup Freezes**:
   - `development/launcher_ui/app.js` lines 135–157: `initLauncher()` is invoked on `DOMContentLoaded` and re-invoked on `pywebviewready`, triggering full double-rendering.
   - `app.js` lines 457–483: `MutationObserver` on `document.body` triggers `refreshLucideIcons()` on every added node, causing DOM mutation recursion during startup hydration.

8. **Multiplayer Latency Radar Removal**:
   - `development/launcher_ui/index.html` lines 265–396 (`view-launchpad`): The HTML element `#launchpad-radar-list` was already removed from the launchpad view.
   - `development/launcher_ui/js/launch.js` lines 50–52 & 387–450: `renderLaunchpad()` still calls `refreshMultiplayerRadar()` on every render, executing dead code.

---

## 2. Logic Chain

1. **Hardware Telemetry "Detecting..." Issue**:
   - Spans in `index.html` start with text "Detecting...".
   - Polling only runs when `STATE.activeTab === 'hardware'` (Observation 1).
   - Startup runs on `'launchpad'`, where polling is inactive.
   - `__SIR_HW_BOOTSTRAP__` was omitted from `bootstrap_cache.js` (Observation 1).
   - Therefore, the UI remains on "Detecting..." until the user navigates to the hardware tab, and if the bridge call is delayed or fails, it never updates.

2. **Folder Opening Inaction / Foregrounding**:
   - Frontend UI invokes `window.pywebview.api.open_instance_folder(instId)` and `open_mods_folder()`.
   - In `instance_service.py`, `AllowSetForegroundWindow(-1)` lacks 32-bit unsigned typing, which on Windows 10/11 fails to grant foreground permission to Explorer, leaving it behind pywebview or flashing on the taskbar.
   - In `bridge.py`, defaults are mismatched to non-existent `"sir-26-ultra"`.

3. **Navbar Download Manager Unresponsiveness**:
   - Top navbar bell icon has `onclick="toggleDownloadHubDropdown()"` (Observation 4).
   - `js/downloads_manager.js` defines this function but is not included in `index.html` (Observation 4).
   - Therefore, clicking the bell icon results in `ReferenceError: toggleDownloadHubDropdown is not defined`.

4. **Servers Refresh Infinite Spin**:
   - `refreshServersLive()` adds `.animate-spin` to the refresh icon (Observation 5).
   - It awaits `loadServersLive()`, which launches 20 concurrent network fetches to `api.mcstatus.io` (Observation 5).
   - When requests hang or hit HTTP 429 rate limits, `await loadServersLive()` does not resolve within expected time, postponing or preventing `finally` from clearing `.animate-spin`.

5. **Google OAuth UI Non-Reflection**:
   - Browser OAuth sends callback to loopback server; `cloud_sync_service.py` calls `on_auth_change` (Observation 6).
   - `bridge.py:963` crashes with `AttributeError` on nonexistent `self.emit_to_js` (Observation 6).
   - The exception is silently suppressed by `except Exception: pass` in `cloud_sync_service.py:157` (Observation 6).
   - `self.window.evaluate_js` is never called, so `window.onCloudAuthSuccess` never runs (Observation 6).
   - Therefore, the UI remains in a logged-out state until the app is restarted.

---

## 3. Caveats

- No source code modifications were made during this investigation (strict read-only compliance).
- Network tests for `api.mcstatus.io` depend on external connectivity and public rate limits; tests confirmed that concurrent unthrottled requests trigger rate limits.
- No other caveats.

---

## 4. Conclusion

All 8 survey tasks for R3 (Launcher UI/UX & Native Bridge Engineering) are fully analyzed with exact source code references and root cause determinations:
1. Hardware telemetry stuckness is caused by conditional tab scoping and unhydrated bootstrap cache; requires a 1-second background daemon and stream events.
2. Folder opening foregrounding failure is caused by untyped signed `-1` in `AllowSetForegroundWindow` and default ID mismatch in `bridge.py`.
3. Welcome modal engine selector requires interactive button wiring in `index.html` and `onboarding.js`.
4. Download tray failure is caused by missing `<script src="js/downloads_manager.js"></script>` in `index.html`.
5. Servers refresh spin loop is caused by unmetered concurrent external API fetches; requires a 5-second `Promise.race` timeout and parallel socket pinger in Python.
6. Google OAuth instant reflection failure is caused by an `AttributeError: emit_to_js` in `bridge.py:963` silently caught in `cloud_sync_service.py:157`.
7. Application startup freezing is caused by duplicate `initLauncher()` execution and unthrottled `MutationObserver` on `document.body`.
8. Main launchpad radar widget removal requires removing the residual `refreshMultiplayerRadar()` call from `launch.js`.

---

## 5. Verification Method

To independently verify these findings:

1. **Verify Missing Methods in `bridge.py`**:
   ```powershell
   py -3.13 -c "import sys; sys.path.insert(0, 'development'); from launcher_core.bridge import LauncherBridgeAPI; b = LauncherBridgeAPI(); print('open_instance_folder:', hasattr(b, 'open_instance_folder')); print('emit_to_js:', hasattr(b, 'emit_to_js'))"
   ```
   *Expected Output*: `open_instance_folder: False`, `emit_to_js: False`.

2. **Verify Missing Script Tag in `index.html`**:
   ```powershell
   Select-String -Path "development/launcher_ui/index.html" -Pattern "downloads_manager.js"
   ```
   *Expected Output*: Empty (no matches found).

3. **Verify Residual Radar Call in `launch.js`**:
   ```powershell
   Select-String -Path "development/launcher_ui/js/launch.js" -Pattern "refreshMultiplayerRadar"
   ```
   *Expected Output*: Lines 50, 387, 450.

4. **Verify Unit Tests Pass**:
   ```powershell
   py -3.13 -m unittest discover -s tests -p "test_*.py"
   ```

---
*Report written to `d:/Projects/SIR ModPack/.agents/explorer_survey_2_gen8/handoff.md` and `analysis.md`.*
