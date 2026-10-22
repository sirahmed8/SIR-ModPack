# Dispatch: Worker M1 (Desktop Applications & PyInstaller Packaging)

## Identity
- Role: Implementation Worker (Milestone 1)
- Working Directory: `d:/Projects/SIR ModPack/.agents/worker_m1/`
- Parent Conversation ID: `e6854040-b2f7-4215-a3ca-09a5a910d136`

## Mandatory Inputs (Read These First!)
- `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`
- `d:/Projects/SIR ModPack/PROJECT.md`
- `d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_1/handoff.md`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Exclusive Write Ownership
You own the following files exclusively:
- `d:/Projects/SIR ModPack/development/launcher_ui/js/navigation.js`
- `d:/Projects/SIR ModPack/build_ecosystem.py`
- `d:/Projects/SIR ModPack/website-next/public/share/` (binary synchronization only)
- `d:/Projects/SIR ModPack/dist_apps/`

## Detailed Implementation Tasks
1. **Extend Deep-Link Protocol Routing in `development/launcher_ui/js/navigation.js`**:
   - In `handleIncomingDeepLink(dl)` (lines 334–383):
     - Add route for `mod/install`:
       ```javascript
       else if (action === 'mod/install' || action.startsWith('mod')) {
         const modId = params.id || params.modId || '';
         if (modId) {
           if (typeof showToast === 'function') {
             showToast(`⚡ Deep-link installing mod: ${modId}`, 'info');
           }
           switchTab('mods');
           if (typeof installOnlineModById === 'function') {
             installOnlineModById(modId);
           }
         }
       }
       ```
     - Add route for `profile`:
       ```javascript
       else if (action === 'profile' || params.name) {
         const profName = params.name || params.profile || '';
         if (profName) {
           if (typeof showToast === 'function') {
             showToast(`✨ Switched to profile: ${profName}`, 'info');
           }
           if (typeof selectInstance === 'function') {
             selectInstance(profName);
           }
         }
       }
       ```
2. **Update Master Packaging Synchronization (`build_ecosystem.py`)**:
   - Ensure the distribution target list synchronizes compiled executables to:
     - `ROOT`
     - `public_repo`
     - `SIR Package`
     - `SIR Launcher`
     - `%APPDATA%\SIR ModPack`
     - `website-next/public/share`
     - `website-next/out/share` (if directory exists)
   - Synchronize the fresh 35.4 MB `SIR Launcher.exe` into `website-next/public/share/SIR Launcher.exe` so the web platform distributes the modern binary.
3. **Packaging & Binary Verification**:
   - Verify all 3 executables exist and are valid:
     - `SIR Launcher.exe` (~35.4 MB)
     - `SIR Server Manager.exe` (~34.4 MB)
     - `SIR Installer.exe` (~18.7 MB)
   - Verify PyInstaller build configuration for all 3 spec files (`SIR Launcher.spec`, `SIR Server Manager.spec`, `SIR Installer.spec`).
4. **Verification Commands**:
   - `python -m unittest tests/test_native_runner.py tests/test_tray_and_window_lifecycle.py -v`
   - `python ecosystem_doctor.py`

## Handoff Requirements
Write complete results and command outputs to:
`d:/Projects/SIR ModPack/.agents/worker_m1/handoff.md`

## 2026-09-08T17:49:15Z
You are Worker M1 for Milestone 1 (Desktop Applications & PyInstaller Packaging) of the SIR ModPack Project.
Your working directory is: d:/Projects/SIR ModPack/.agents/worker_m1/
The project workspace root is: d:/Projects/SIR ModPack

MANDATORY FIRST STEP:
Read your dispatch file at `d:/Projects/SIR ModPack/.agents/worker_m1/DISPATCH.md`, read `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`, and read `d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_1/handoff.md`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE WRITE OWNERSHIP:
You own: `development/launcher_ui/js/navigation.js`, `build_ecosystem.py`, `website-next/public/share/`, `dist_apps/`.

MISSION:
1. Extend `handleIncomingDeepLink(dl)` in `development/launcher_ui/js/navigation.js` to handle `mod/install?id=...` and `profile?name=...`.
2. Update `build_ecosystem.py` distribution sync targets to include `website-next/public/share` and `website-next/out/share`. Synchronize the fresh 35.4 MB `SIR Launcher.exe` into `website-next/public/share/`.
3. Verify all 3 standalone executables (`SIR Launcher.exe`, `SIR Server Manager.exe`, `SIR Installer.exe`) exist, are valid, and compile cleanly.
4. Run verification tests: `python -m unittest tests/test_native_runner.py tests/test_tray_and_window_lifecycle.py -v` and `python ecosystem_doctor.py`.

OUTPUT:
Write detailed completion report to `d:/Projects/SIR ModPack/.agents/worker_m1/handoff.md` and send message to parent (e6854040-b2f7-4215-a3ca-09a5a910d136).
