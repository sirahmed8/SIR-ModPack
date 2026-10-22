## 2026-09-10T21:00:00Z
Objective: Conduct a technical survey of R3 (Launcher UI/UX & Native Bridge Engineering).
Tasks:
1. Inspect `development/launcher_core/`, `development/launcher_ui/`, and `development/launcher_source/`:
   - Hardware telemetry: examine how CPU, RAM, and GPU are currently detected in `hardware_service.py` / `bridge.py` and UI display in `index.html` / `navigation.js`. Identify why it gets stuck on "Detecting..." and how to implement real-time Win32 kernel CPU load %, physical RAM load %, GPU adapter detection, and 1-second Task Manager style dynamic fluctuation.
   - Folder opening / Win32 foregrounding: check how "Open Folder" / mods/instance directory actions are implemented in `bridge.py`. Determine how to add `AllowSetForegroundWindow(-1)` via ctypes and `subprocess.Popen(['explorer.exe', ...])` for robust Windows 10/11 foregrounding.
   - Welcome Modal: inspect `index.html` / `welcome.js` / modal logic. Determine how to implement the interactive engine selector (Fabric 26.2 vs Forge 1.8.9) and quick-start tour.
   - Top navbar Download Manager & Announcements tray: check existing navbar structure. Determine how to add live progress bars, speed, and functional Cancel action.
   - Servers page refresh: inspect `servers.js` and server ping logic in `server_service.py`. Find root cause of the infinite spin loop on refresh and how to guarantee latency/player count updates within 5 seconds.
   - Google OAuth authentication: inspect `auth_service.py` and frontend account switcher. Identify why 1-click auth does not instantly reflect in navbar and account switcher without launcher restart, and design instant UI state update.
   - Application startup: analyze initialization flow in `SIR_Launcher_Modern.py` and UI scripts for thread blocking, unresponsiveness, or early interaction freezes.
   - Launchpad view: locate and verify exact removal of the Multiplayer Latency Radar widget from the main launchpad view.
2. Document exact file locations, line numbers, function signatures, and implementation specifications.
Boundaries:
- You are strictly read-only. Do NOT modify source code files.
- Write your findings to `d:/Projects/SIR ModPack/.agents/explorer_survey_2_gen8/analysis.md` and `handoff.md`.
- Send a completion message back when finished with the path to your handoff.
