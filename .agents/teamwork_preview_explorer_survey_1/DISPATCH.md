# Dispatch: Survey Explorer 1 (Desktop Applications & Ecosystem Diagnostics)

## Identity
- Role: Explorer (Survey 1 - Desktop Applications & Ecosystem Diagnostics)
- Working Directory: d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_1/
- Parent Conversation ID: e6854040-b2f7-4215-a3ca-09a5a910d136

## Mandatory Inputs
- Original Request: `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md` (Read this first!)

## Mission & Objectives
Investigate the desktop applications and ecosystem diagnostic infrastructure in `d:/Projects/SIR ModPack`:
1. **SIR Launcher Pro (`SIR Launcher.exe`)**:
   - Inspect existing launcher code (Python/PyQt/PySide or similar desktop framework).
   - Check Windows deep-link protocol handler registration `sirlauncher://` (`sirlauncher://auth`, `sirlauncher://mod/install?id=...`, `sirlauncher://join?ip=...`, `sirlauncher://profile?name=...`).
   - Check Multiplayer Latency Radar integration with live server query caches.
   - Check Game Integrity Doctor with live checksum progress against `delta_manifest.json`.
   - Check Win32 RAM Compactor (`psapi.dll` memory trimming) in header navigation.
   - Check 3D Skin Studio with OrbitControls and 4px Steve / 3px Alex switching.
2. **SIR Server Manager Pro (`SIR Server Manager.exe`)**:
   - Check `ServerRestartScheduler` countdown alerts to in-game chat and Discord Webhook Bot.
   - Check automated world snapshots with retention pruning (`prune_world_snapshots`, keep 5 most recent).
   - Check 60-second historical canvas sparklines for TPS (msPT) and dynamic heap RAM.
3. **SIR Installer Pro (`SIR Installer.exe`)**:
   - Check pre-flight hardware diagnostic matrix (RAM, disk space, CPU AVX2, Java 21 LTS).
   - Check Adoptium OpenJDK 21 LTS detector & 1-click silent background downloader.
   - Check custom drive selection across Windows logical volumes (`C:`, `D:`, `E:`) with free space validation.
4. **Diagnostics, Tests & Packaging**:
   - Inspect `ecosystem_doctor.py` (all 6 diagnostic layers).
   - Inspect existing unit test suite in `tests/` (current passing count, structure).
   - Inspect PyInstaller spec files and build scripts for the 3 executables.

## Output Requirements
Produce a comprehensive, structured report in:
`d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_1/handoff.md`
Detailing:
- Exact inventory of files, modules, classes, and entry points.
- Current state of each R1 requirement (what is working, what is partial, what is missing).
- Current status of unit tests and PyInstaller packaging.
- Dependencies, constraints, and proposed work items.

## 2026-09-08T17:31:04Z
You are Survey Explorer 1 for the SIR ModPack Project.
Your working directory is: d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_1/
The project workspace root is: d:/Projects/SIR ModPack

MANDATORY FIRST STEP:
Read your dispatch file at `d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_1/DISPATCH.md` and read `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`.

YOUR ROLE & MISSION:
You are a READ-ONLY explorer. DO NOT modify any source code files.
Investigate the desktop applications and diagnostic systems in `d:/Projects/SIR ModPack`:
1. SIR Launcher Pro (`SIR Launcher.exe`) - deep link `sirlauncher://`, multiplayer latency radar, game integrity doctor checksums, Win32 RAM compactor `psapi.dll`, 3D Skin Studio.
2. SIR Server Manager Pro (`SIR Server Manager.exe`) - ServerRestartScheduler alerts (chat + Discord Webhook Bot), automated world snapshots with retention pruning (keep 5), 60s sparklines (TPS & heap).
3. SIR Installer Pro (`SIR Installer.exe`) - Pre-flight hardware diagnostic matrix (RAM, disk, AVX2, Java 21 LTS), Adoptium OpenJDK 21 LTS detector & silent background downloader, custom drive selection across logical volumes (C:, D:, E:).
4. Ecosystem Doctor (`ecosystem_doctor.py`) - all 6 diagnostic layers.
5. Test suite in `tests/` and PyInstaller build configuration.

OUTPUT:
Write your complete, structured survey report to:
`d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_1/handoff.md`
Then call `send_message` to your parent (e6854040-b2f7-4215-a3ca-09a5a910d136) notifying that your survey handoff is complete.
