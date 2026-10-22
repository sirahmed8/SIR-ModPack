# Original User Request

## 2026-09-08T17:29:26Z

# Teamwork Project Prompt — Master Interconnected Ecosystem Overhaul

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: Full multi-agent engineering team under central control

Execute an exhaustive, grand-scale, page-by-page, file-by-file, and app-by-app multi-agent engineering overhaul across every subsystem, application, page, and directory of the SIR ModPack ecosystem, operating across the complete multi-folder environment on the user's computer:
1. `d:/Projects/SIR ModPack` (Main Development Workspace)
2. `C:/Users/a7med/AppData/Roaming/SIR ModPack` (Installed Live User Runtime)
3. `C:/Users/a7med/.lunarclient` (Lunar Client Ecosystem)
4. `C:/Users/a7med/AppData/Roaming/.minecraft` (Official Minecraft Roaming & Caches)
5. `C:/Users/a7med/AppData/Roaming/PrismLauncher` (Prism Launcher Ecosystem)

Working directory: d:/Projects/SIR ModPack
Integrity mode: development

---

## 🏛️ Requirements

### R1. App-by-App Deep Modernization & Interconnection
- **SIR Launcher Pro (`SIR Launcher.exe`)**:
  - Implement and register native Windows deep-link protocol handler `sirlauncher://` (`sirlauncher://auth`, `sirlauncher://mod/install?id=...`, `sirlauncher://join?ip=...`, `sirlauncher://profile?name=...`).
  - Wire Multiplayer Latency Radar directly to live server query caches for instant home screen ping display.
  - Wire Game Integrity Doctor with live checksum progress against `delta_manifest.json`.
  - Wire Win32 RAM Compactor (`psapi.dll` memory trimming) in the header navigation.
  - Ensure 3D Skin Studio with OrbitControls and 4px Steve / 3px Alex switching connects to local and cloud skins.
- **SIR Server Manager Pro (`SIR Server Manager.exe`)**:
  - Wire `ServerRestartScheduler` countdown alerts to in-game chat broadcasts and Discord Webhook Bot.
  - Wire automated world snapshots with retention pruning (`prune_world_snapshots`, keep 5 most recent).
  - Ensure 60-second historical canvas sparklines for TPS (msPT) and dynamic heap RAM render smoothly.
- **SIR Installer Pro (`SIR Installer.exe`)**:
  - Pre-flight hardware diagnostic matrix (RAM, disk space, CPU AVX2 instructions, Java 21 LTS).
  - Pre-flight Adoptium OpenJDK 21 LTS detector & 1-click silent background downloader.
  - Custom drive selection across all Windows logical volumes (`C:`, `D:`, `E:`) with free space validation.

### R2. Page-by-Page Web Platform Elevation (All 35 Routes in `website-next`)
- **Strict Welcome & Google Authentication Gate**:
  - Ensure `/welcome` is the mandatory entry gateway for non-logged-in visitors; unauthenticated visitors cannot access any protected routes and are directed to `/welcome`.
  - Upon Google login, grant full access and synchronize user profile with Firestore and local storage.
- **Interconnected Feature Pages**:
  - `/` (Home): Unified dashboard with deep-link quick launch buttons and live announcements.
  - `/download`: 3 download tiers with interactive SHA-256 cards, PowerShell check commands, and direct `sirlauncher://` install actions.
  - `/mods`: 221+ mod catalog with loader filters and 1-click "Install to Launcher" deep links.
  - `/shaders`: Interactive 3D RTX/POM slider with dynamic sun angles and water caustics controls.
  - `/skins`: 3D Skin & Cape Studio featuring all 6 official preset capes and 6 dual-layer skins with 1-click cloud sync.
  - `/servers`: 360° Live Radar widget with direct-connect `sirlauncher://join?ip=...` action.
  - `/crash-analyzer`: Automated diagnostic tool with 1-click recommended fix exporter.
  - `/benchmarks`: Public hardware rig simulator comparing 120+ GPUs and CPUs.
  - `/changelog`: Filterable v1.0.0 Genesis timeline with category badges.
  - `/faq`: Comprehensive legal, server safety, and shader FAQ.
  - `/trainer`: In-browser Aim & CPS trainer with leaderboard submission.
  - All remaining routes (`/builder`, `/leaderboards`, `/seeds`, `/server-guide`, `/admin`, etc.) cleanly styled and interlinked.

### R3. File-by-File Cross-Client Synchronization & Invariants
- Harmonize `options.txt` (gamma: 1.0, vsync: false, Iris toggle: K, ReplayMod keybinds) across all 5 directories on the computer.
- Enforce Generational ZGC flags (`-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5`) across all 26.2 modern profiles.
- Verify Bedrock Cross-Play templates (`Geyser-Spigot/config.yml` on UDP 19132) and automated server health monitor (`server/server_health_check.py`).
- Maintain Drive D free space invariant $\ge$ 18.00 GB at all times.

---

## 🎯 Acceptance Criteria

### Execution & Interconnection
- [ ] Deep-link protocol `sirlauncher://` registered and verified in Launcher.
- [ ] Web platform (`website-next`) builds cleanly across all 35 static routes and is deployed to Firebase Hosting (`sir-modpack.web.app`).
- [ ] Non-logged-in users cannot access any protected page and are redirected to `/welcome`.
- [ ] All 3 standalone executables (`SIR Launcher.exe`, `SIR Server Manager.exe`, `SIR Installer.exe`) compile cleanly via PyInstaller.
- [ ] All 368+ Python unit tests pass with 0 failures and 0 errors.
- [ ] `python ecosystem_doctor.py` reports 100% healthy across all 6 diagnostic layers.
- [ ] Drive D maintains $\ge 18.00\text{ GB}$ free space.
- [ ] Both Git repositories (`public_repo` on `main` and `website-next` on `main`) committed and pushed cleanly.

## Verification Resources
- Unit test suite: `python -m unittest discover -s tests -p "test_*.py" -v`
- Ecosystem doctor: `python ecosystem_doctor.py`
- Static build: `npm run build` in `website-next`
- Live audit: Chrome DevTools MCP on `https://sir-modpack.web.app`

## 2026-09-10T20:57:12Z

Comprehensive stabilization, modpack synchronization, crash elimination, and engineering overhaul of the SIR ModPack launcher and game runtime ecosystem across Modern (Fabric 26.2), Legacy (Forge 1.8.9), and Lunar Client bridge profiles.

Working directory: d:/Projects/SIR ModPack
Integrity mode: development

## Requirements

### R1. Modpack Instance Audit, Harmonization & Reset
- Audit and reset active mods across all game instance profiles (`26.2-ultra`, `26.2-balanced`, `26.2-performance`, `26.2` vanilla, and `1.8.9` legacy variants) so each tier possesses a validated, coherent mod set without duplicates, broken dependencies, or conflicting bytecode transformers.
- Reset the mods directories cleanly to working baseline states while strictly preserving user options and video game configuration files (`options.txt`, `optionsof.txt`, shader configs).

### R2. Crash Remediation (World Creation, Loading & Lunar Profiles)
- Diagnose and eliminate runtime crashes occurring during singleplayer world creation, world loading, and Lunar Client profile execution.
- Fix ASM/Mixin incompatibilities, memory allocation flags, and Lunar Client bi-directional synchronization bridge errors.
- Ensure worlds can be created, saved, and re-opened without errors or JVM crashes.

### R3. Launcher UI/UX & Native Bridge Engineering
- Deliver live dynamic hardware telemetry (Win32 kernel CPU load %, physical RAM load %, GPU adapter detection, real-time Task Manager style fluctuation).
- Implement robust foregrounding for Windows File Explorer when opening mods/instance folders on Windows 10/11 (`AllowSetForegroundWindow(-1)` + `subprocess.Popen(['explorer.exe', ...])`).
- Modernize the Welcome Modal with an interactive engine selector (Fabric 26.2 vs Forge 1.8.9) and quick-start tour.
- Add a top navbar Download Manager & Announcements tray with live progress bars, speed, and functional Cancel action.
- Fix the servers page refresh button infinite spin loop and ensure server latency/player counts update.
- Ensure 1-click Google OAuth authentication instantly reflects in the navbar and account switcher without requiring launcher restart.
- Prevent application startup freezes and unresponsiveness on early user interaction.
- Completely remove the Multiplayer Latency Radar widget from the main launchpad view.

### R4. Distribution Packaging, Verification & Deployment
- Recompile all 3 standalone Windows executables (`SIR Launcher`, `SIR Server Manager`, `SIR Installer`) using `build_ecosystem.py`.
- Execute master test suite (`py -3.13 -m unittest discover -s tests -p "test_*.py"`) to verify 100% passing tests with zero handle leaks and zero regressions.
- Deploy frontend updates to Firebase Hosting and synchronize both public and private git repositories.

## Acceptance Criteria

### Instance & Mod Stability
- [ ] Singleplayer world creation and loading succeeds on all 26.2 and 1.8.9 profiles without JVM crash or fatal Mixin error.
- [ ] Lunar Client synchronized profiles launch cleanly without configuration corruption.
- [ ] Mods folders are clean, organized, and free of obsolete, duplicate, or incompatible JAR files.

### Launcher Native Subsystems
- [ ] Hardware telemetry displays live physical metrics (RAM, Cores, GPU) and dynamically fluctuates every second without remaining stuck on "Detecting...".
- [ ] "Open Folder" brings Windows File Explorer to the active foreground on Windows 11.
- [ ] Top navbar download tray displays active download progress and supports cancellation.
- [ ] Servers refresh completes within 5 seconds and removes spinning animation upon finish.
- [ ] Google authentication immediately adds the account to the active UI state without application restart.
- [ ] Main launchpad view is free of the multiplayer latency radar widget.

### Verification & Build Artifacts
- [ ] `py -3.13 -m unittest discover -s tests -p "test_*.py"` passes 100% clean.
- [ ] All 3 standalone `.exe` binaries compile successfully without PyInstaller errors.
- [ ] Firebase deployment succeeds and git commits are pushed to remote repositories.
