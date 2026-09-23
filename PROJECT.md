# Project: SIR ModPack Master Ecosystem Stabilization & Overhaul (Gen 9 - v1.0.0)

## Architecture
The SIR ModPack ecosystem consists of five interconnected core subsystems:
1. **Game Instances & Modpack Runtimes** (`instances/`, `C:/Users/a7med/.lunarclient`):
   - Modern 26.2 Runtimes: `26.2-ultra` (high-end visual), `26.2-balanced` (optimized daily driver), `26.2-performance` (lightweight competitive esports).
   - Legacy 1.8.9 Runtimes: Forge 1.8.9 PvP profiles (`1.8.9-ultra`, `1.8.9-balanced`, `1.8.9-performance`).
   - Lunar Client Bridge: Bi-directional synchronization profiles linking launcher instances with Lunar Client's Ichor engine.
   - Clean modsets, strictly preserving user configuration files (`options.txt`, `optionsof.txt`, shaderpacks).
   - Automated Options Sanitizer: Launch-time enforcement of windowed mode preventing DWM deadlocks on Intel/NVIDIA hybrid graphics.
2. **Desktop Applications Tier** (`development/`):
   - `SIR Launcher` (`development/launcher_source/`, `development/launcher_core/`, `development/launcher_ui/`): PyWebView native desktop client with Win32 kernel Task Manager telemetry, folder foregrounding, interactive welcome engine selector, download manager tray, instant Google OAuth, window lifecycle controller, and GitHub Single-File Delta Fetcher.
   - `SIR Server Manager` (`development/server_source/`, `development/server_core/`, `development/server_ui/`): Background server supervisor with CSS spring animations, persistent lifecycle configuration, automated world snapshots, and live TPS/RAM metrics.
   - `SIR Installer` (`development/installer_source/`, `development/installer_core/`, `development/installer_ui/`): Multi-stage setup wizard with fluid spring transitions, pre-flight hardware matrix, Adoptium OpenJDK 25/8 silent downloader, and GitHub Single-File Delta Auto-Healer.
3. **In-Game Client Engine & Optics Tier**:
   - `sir-mod-26.2-1.0.0.jar`: Native Fabric client mod bound to Right-Shift (`RSHIFT`) with 9 competitive toggles (FPS, CPS, Ping, Armor/Status, Keystrokes, 1.7 Block-Hitting, Dynamic C-Zoom, Toggle Sprint/Sneak, 0ms Hit Registration).
   - Dedicated Shaders (`SIR Modern Shader.zip` with unbloomed sharp nametags & `SIR Legacy Shader.zip`).
   - Dedicated Resource Packs (`SIR Modern.zip` with 26.2 pack format 88 & `SIR Legacy.zip` with authentic PNG pack icon).
4. **Web Platform Tier** (`website-next/`):
   - Next.js 16.3 App Router (38 static routes) deployed to Firebase Hosting (`sir-modpack.web.app`).
   - SIR Diagnostic & Configuration Assistant for configuration telemetry and crash analysis.
   - Deep-linking (`sirlauncher://`) connecting web catalog to native desktop client.
   - Cryptographic SHA-256 gated administrative cockpit (`/admin`).
   - Dedicated Statutory 14-Day EU/UK Digital Refund & Withdrawal Policy (`/refund`).
5. **Packaging, Invariants & Verification Tier**:
   - Master test suite (406 unit tests in `tests/`, 394 in `public_repo/tests/`) with 100% green status.
   - System Invariants: options.txt GLFW key standards, zero unclosed handles/sockets, 100% manifest cryptographic SHA-256 verification.
   - PyInstaller compilation via `build_ecosystem.py` targeting synchronized distribution paths.

---

## Feature Inventory
| # | Feature | Description | Milestone | Status |
|---|---------|-------------|-----------|--------|
| 1 | OpenCL Crash Termination | Purge `quantified api-omni` JARs from all instances and payloads | M1 | COMPLETED |
| 2 | Duplicate Mod Families Cleanup | Purge duplicate mod families and remove obsolete JARs | M1 | COMPLETED |
| 3 | Instance Tier Harmonization | Establish validated, coherent mod sets across 6 tiers | M1 | COMPLETED |
| 4 | Self-Healing Inflation Fix | Per-tier thresholds in `instance_service.py` to prevent mod re-inflation | M1 | COMPLETED |
| 5 | Options & Keycode Harmonization | Cleanse modern `options.txt` of legacy keycodes, enforcing GLFW strings | M1 | COMPLETED |
| 6 | BetterCombat Lunar Crash Fix | Decouple/remap classloading under Lunar Client | M2 | COMPLETED |
| 7 | Lunar Mixin Injection Fix | Eliminate Mixin injection errors in Lunar profiles | M2 | COMPLETED |
| 8 | Lunar Profile Path Alignment | Synchronize gameDir paths and keycodes in bridge | M2 | COMPLETED |
| 9 | Singleplayer World Creation Pass | Verify world creation, saving, and reopening across all tiers | M2 | COMPLETED |
| 10 | Live Dynamic Hardware Telemetry | 1s continuous telemetry daemon (CPU %, RAM %, GPU) with Win32 Task Manager parity | M3 | COMPLETED |
| 11 | Explorer Folder Foregrounding | Add `open_instance_folder`/`open_mods_folder` with win32 foreground elevation | M3 | COMPLETED |
| 12 | Welcome Modal Engine Selector | Interactive Modern 26.2 vs Legacy 1.8.9 engine selector | M3 | COMPLETED |
| 13 | Navbar Download Manager Tray | Interactive download progress and cancel in desktop navbar | M3 | COMPLETED |
| 14 | Servers Refresh Timeout Fix | Race timeout and guaranteed animation reset in server browser | M3 | COMPLETED |
| 15 | 1-Click Google OAuth Instant Sync | Seamless real-time UI synchronization without restart | M3 | COMPLETED |
| 16 | Startup Freeze & Mutation Fix | Deduplicate initialization and scope MutationObserver | M3 | COMPLETED |
| 17 | Latency Radar Widget Removal | Cleanly eliminate unused mock polling loops | M3 | COMPLETED |
| 18 | Hybrid GPU Black Screen Resolution | Integrated launch-time options sanitization preventing DWM deadlocks | M5 | COMPLETED |
| 19 | Ghost Window Elimination | Win32 class suppression loop eliminating GDI+ taskbar ghost artifacts | M5 | COMPLETED |
| 20 | Launcher Auto-Restore Watchdog | Dual-hook recovery bringing launcher to foreground upon game termination | M5 | COMPLETED |
| 21 | Anti-"Vibe Coded" Design Standard | Obsidian/slate palette, cyan/emerald accents, zero pill buttons, zero emojis | M5 | COMPLETED |
| 22 | Diagnostic Assistant Rebranding | Rebrand intelligence features to "SIR Diagnostic & Configuration Assistant" | M5 | COMPLETED |
| 23 | Master Test Suite 100% Pass | 406/406 root tests and 394/394 public_repo tests passing | M5 | COMPLETED |
| 24 | Firebase Deploy & Dual Git Push | Deploy web platform and push public apps / private web repos | M5 | COMPLETED |

---

## Milestones
| # | Name | Scope | Status |
|---|------|-------|--------|
| M1 | Modpack Instance Audit, Harmonization & Reset | Clean modsets, eliminate quantified api-omni, fix options keycodes | COMPLETED |
| M2 | Crash Remediation (World Creation, Loading & Lunar) | Decouple Lunar BetterCombat, fix Mixins, verify world saves | COMPLETED |
| M3 | Launcher UI/UX & Native Bridge Engineering | Dynamic telemetry, folder foregrounding, welcome modal, OAuth sync | COMPLETED |
| M4 | Packaging & Verification Pipeline | Ecosystem doctor, manifest delta validator, PyInstaller apps | COMPLETED |
| M5 | Anti-Vibe Overhaul, Window Lifecycle & Legal Hardening | Hybrid GPU fix, window lifecycle, anti-vibe design, GDPR refund route | COMPLETED |

---

## Interface Contracts
### Launcher Bridge <-> Windows Native Explorer
- `open_instance_folder(inst_id)`:
  - Invokes `ctypes.windll.user32.AllowSetForegroundWindow(ctypes.c_uint32(0xFFFFFFFF))`
  - Resolves target directory path from `instance_service.get_instance_path(inst_id)`
  - Spawns `subprocess.Popen(['explorer.exe', target_path])`
  - Returns `{"success": True, "path": target_path}`

### Hardware Monitor <-> UI Event Stream
- Event: `hardware_telemetry_update`
- Payload: `{"cpu_percent": float, "ram_percent": float, "ram_total_gb": float, "ram_avail_gb": float, "gpu_name": str, "power_tier": str}`
- Frequency: 1000ms steady-state fluctuation

### Options Invariant Contract (`options.txt`)
- Modern 26.2 instances MUST strictly use GLFW key naming conventions (e.g. `key.keyboard.*`, `key.mouse.*`).
- Numeric integer keycodes (e.g. `47`, `54`) are strictly forbidden in modern profiles.
- Pre-launch sanitizer automatically verifies and resets `fullscreen:false` to prevent dual-GPU display deadlocks.

---

## Code Layout
- `development/launcher_source/`: Launcher entry point scripts (`SIR_Launcher_Modern.py`)
- `development/launcher_core/`: Launcher backend services (`bridge.py`, `hardware_monitor_service.py`, `instance_service.py`, `cloud_sync_service.py`, `server_service.py`, `lunar_bridge_service.py`, `native_runner.py`, `tray_service.py`)
- `development/launcher_ui/`: Launcher UI assets (`index.html`, `app.css`, `app.js`, `js/navigation.js`, `js/instances.js`, `js/mods.js`, `js/servers.js`, `js/launch.js`, `js/downloads_manager.js`, `js/onboarding.js`, `js/settings.js`, `js/skins.js`)
- `development/server_source/`, `development/server_core/`, `development/server_ui/`: Server Manager components
- `development/installer_source/`, `development/installer_core/`, `development/installer_ui/`: Installer components
- `instances/`: Minecraft instance profiles (`26.2-ultra`, `26.2-balanced`, `26.2-performance`, `1.8.9-ultra`, `1.8.9-balanced`, `1.8.9-performance`)
- `tests/`: Automated unit test suite (406 tests)
- `public_repo/`: Mirrored public distribution repository for desktop applications
- `website-next/`: Next.js 16 web platform repository (38 static routes)
- `build_ecosystem.py`: Release compilation and distribution synchronization orchestrator

