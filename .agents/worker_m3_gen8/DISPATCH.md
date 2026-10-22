## 2026-09-10T21:13:28Z
You are worker_m3_gen8.
Your working directory is: d:/Projects/SIR ModPack/.agents/worker_m3_gen8/
Authoritative Request: d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md (specifically request ## 2026-09-10T20:57:12Z)
Master Project Spec: d:/Projects/SIR ModPack/PROJECT.md
Explorer Survey 2 Findings: d:/Projects/SIR ModPack/.agents/explorer_survey_2_gen8/handoff.md and d:/Projects/SIR ModPack/.agents/explorer_survey_2_gen8/analysis.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & Write Ownership:
You have exclusive write ownership of:
- `development/launcher_core/bridge.py`
- `development/launcher_core/hardware_monitor_service.py`
- `development/launcher_core/cloud_sync_service.py`
- `development/launcher_core/server_service.py`
- `development/launcher_ui/` files (`index.html`, `app.js`, `bootstrap_cache.js`, `js/navigation.js`, `js/servers.js`, `js/launch.js`, `js/onboarding.js`, `js/downloads_manager.js`, `js/instances.js`, `js/mods.js`, `js/packs.js`, `js/gallery.js`, `js/command_palette.js`)
- `public_repo/development/` counterparts

Milestone 3 Objectives:
1. Live Dynamic Hardware Telemetry:
   - Implement 1-second continuous telemetry daemon in `hardware_monitor_service.py` (CPU % via `GetSystemTimes` deltas over 1000ms, physical RAM % via `GlobalMemoryStatusEx`, GPU detection).
   - Wire `LauncherBridgeAPI.get_hardware_telemetry()` and stream `hardware_telemetry_update` event via `_emit_ui_event`.
   - In `app.js` and `index.html`, listen for events and update UI elements dynamically across all tabs. Populate `__SIR_HW_BOOTSTRAP__` in `bootstrap_cache.js` to eliminate "Detecting..." on launch.
2. Windows Folder Opening & Win32 Foregrounding:
   - Add `open_instance_folder(inst_id)` and `open_mods_folder(inst_id)` to `LauncherBridgeAPI` in `bridge.py`.
   - Use `ctypes.windll.user32.AllowSetForegroundWindow(ctypes.c_uint32(0xFFFFFFFF))` and `subprocess.Popen(['explorer.exe', target_path])` so Windows File Explorer activates in the foreground on Windows 10/11.
3. Welcome Modal Engine Selector & Tour:
   - In `index.html` (lines 2732-2748) and `onboarding.js`, make the Modern 26.2 (Fabric) vs Legacy 1.8.9 (Forge) engine cards interactive, setting the active profile on click and providing a smooth quick-start tour.
4. Navbar Download Manager & Announcements Tray:
   - Add `<script src="js/downloads_manager.js"></script>` to `index.html`.
   - Wire `toggleDownloadHubDropdown()` and connect active downloads from `store.js`/`mods.js` to `addActiveDownload()`, displaying live progress bar, speed, and functional Cancel action.
5. Servers Page Refresh:
   - In `servers.js`, wrap `loadServersLive()` in a 5-second `Promise.race` timeout, throttle concurrency (max 5 simultaneous fetches), and guarantee `.animate-spin` removal in `finally`.
6. Google OAuth Instant UI Reflection:
   - In `bridge.py`, fix `_on_cloud_auth_change` to call `self._emit_ui_event("sir_cloud_auth_changed", profile)` and `self.window.evaluate_js(f"window.onCloudAuthSuccess({json.dumps(profile)})")`, updating navbar and account switcher immediately without restart.
7. Application Startup Responsiveness:
   - Deduplicate `initLauncher()`, debounce Lucide icon refreshes, and scope `MutationObserver` to prevent startup freezes and UI locking.
8. Multiplayer Latency Radar Removal:
   - Cleanly remove all remaining calls (`refreshMultiplayerRadar()`) and mock server definitions from `launch.js` and `renderLaunchpad()`.
9. Verify your implementation:
   - Run: `py -3.13 -m unittest discover -s tests -p "test_*bridge*.py"`
   - Run: `py -3.13 -m unittest discover -s tests -p "test_*server*.py"`
10. Write your structured handoff report to `d:/Projects/SIR ModPack/.agents/worker_m3_gen8/handoff.md` with Observation, Logic Chain, Caveats, Conclusion, and Verification results.
11. Send a completion message to parent when done.
