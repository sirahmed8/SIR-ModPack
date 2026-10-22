# Technical Survey Report: R4 Distribution Packaging, Verification & Deployment

**Survey Agent**: `explorer_survey_3_gen8`  
**Date**: 2026-09-11  
**Project Root**: `d:/Projects/SIR ModPack`  
**Working Directory**: `d:/Projects/SIR ModPack/.agents/explorer_survey_3_gen8/`  
**Authoritative Reference**: `ORIGINAL_REQUEST.md` (Request `## 2026-09-10T20:57:12Z`)

---

## Executive Summary

This technical survey evaluates the end-to-end readiness of Requirement 4 (**Distribution Packaging, Verification & Deployment**) across the SIR ModPack ecosystem.

Key Findings:
1. **PyInstaller Packaging**: `build_ecosystem.py` and the 3 spec files (`SIR Launcher.spec`, `SIR Server Manager.spec`, `SIR Installer.spec`) are structurally complete and target PyInstaller 6.22.2 on Python 3.13. However, all spec files compile strictly from `D:/Projects/SIR ModPack/development/`, while recent R1-R3 changes were edited partially in `public_repo/development/`, creating a code divergence risk.
2. **Master Test Suite (368 Tests)**: 366 tests pass cleanly. Exactly 2 tests fail:
   - `test_bridge_all_new_alias_methods` in `tests/test_challenger_m3_accounts_sync_bridge.py:494`: failed because `open_mods_folder` was upgraded to `subprocess.Popen(['explorer.exe', ...])` for Windows 11 foregrounding (R3), but the test still expects `os.startfile` to be called.
   - `test_drive_d_free_space_threshold` in `tests/test_system_audit_invariants.py:91`: failed because Drive D has ~15.37 GB free space, whereas the test requires $\ge 16.0\text{ GB}$ (and Acceptance Criteria requires $\ge 18.00\text{ GB}$).
3. **E2E Test Suite (39 Tests)**: 38 tests pass cleanly. Exactly 1 test fails (`test_f17_drive_d_storage_invariant`) due to the same Drive D free space invariant ($< 18.00\text{ GB}$).
4. **Resource / Handle Leaks**: Unclosed socket warnings in `test_challenger_m3_accounts_sync_bridge.py:280` during port contention testing, unclosed subprocess warning in `test_challenger_m1_r2_empirical.py`, and unclosed file handles in threading loggers.
5. **Web Platform & Firebase Hosting**: `website-next` builds cleanly via Next.js 16 static export (`output: "export"`). Firebase CLI (v15.12.0) is authenticated as `a7medorabe7@gmail.com` with direct access to project `sir-modpack`. `firebase.json` properly ignores `**/*.exe` and `**/*.zip` to respect Firebase Hosting limits.
6. **Git Repositories Status**: `website-next` is clean and fully pushed to `origin/main` (`c70f9df2`). `public_repo` has 7 modified files and 1 untracked file (`development/launcher_ui/js/downloads_manager.js`) reflecting R1-R3 in-progress implementations.

---

## 1. Distribution Packaging & PyInstaller Analysis

### 1.1 Orchestrator: `build_ecosystem.py`
- **Location**: `d:/Projects/SIR ModPack/build_ecosystem.py`
- **Pipeline Flow**:
  1. Creates output directories: `dist_apps/` and `build_apps/`.
  2. Compiles the 3 standalone Windows executables sequentially:
     - `py -3.13 -m PyInstaller --clean --noconfirm "SIR Launcher.spec" --distpath dist_apps --workpath build_apps`
     - `py -3.13 -m PyInstaller --clean --noconfirm "SIR Server Manager.spec" --distpath dist_apps --workpath build_apps`
     - `py -3.13 -m PyInstaller --clean --noconfirm "SIR Installer.spec" --distpath dist_apps --workpath build_apps`
  3. Synchronizes compiled binaries (`SIR Launcher.exe`, `SIR Server Manager.exe`, `SIR Installer.exe`, `SIR_Icon.ico`) across 8 distribution targets:
     - `d:/Projects/SIR ModPack` (ROOT)
     - `d:/Projects/SIR ModPack/public_repo`
     - `d:/Projects/SIR ModPack/SIR Package`
     - `d:/Projects/SIR ModPack/SIR Launcher`
     - `%APPDATA%/SIR ModPack`
     - `%APPDATA%/SIR ModPack/SIR Launcher`
     - `d:/Projects/SIR ModPack/website-next/public/share`
     - `d:/Projects/SIR ModPack/website-next/out/share`
  4. Cleans up scratch directory `build_apps/`.

### 1.2 Spec Files Comparison Matrix

| Property | `SIR Launcher.spec` | `SIR Server Manager.spec` | `SIR Installer.spec` |
|---|---|---|---|
| **Entry Point** | `development/launcher_source/SIR_Launcher_Modern.py` | `development/server_source/SIR_Server_Manager_Modern.py` | `development/installer_source/SIR_Installer_Modern.py` |
| **Analysis Pathex** | `development` | `development` | `development` |
| **Bundled Data** | `launcher_ui`, `launcher_core`, `shared_core`, `webview`, `pystray`, `PIL` | `server_ui`, `server_core`, `shared_core`, `webview`, `pystray`, `PIL` | `installer_ui`, `installer_core`, `shared_core`, `webview` |
| **Hidden Imports** | `webview`, `clr`, `webview.platforms.winforms`, `webview.platforms.edgechromium`, `pystray`, `pystray._win32`, `PIL`, `PIL.Image`, `shared_core`, `shared_core.runtime`, `shared_core.cloud_sync` | Same as Launcher | `webview`, `clr`, `webview.platforms.winforms`, `webview.platforms.edgechromium`, `shared_core`, `shared_core.runtime` |
| **Icon** | `SIR_Icon.ico` | `SIR_Icon.ico` | `SIR_Icon.ico` |
| **Version File** | `version_launcher.txt` | `version_server.txt` | `version_installer.txt` |
| **Target Mode** | Windowed (`console=False`, `upx=False`, `strip=False`) | Windowed (`console=False`, `upx=False`, `strip=False`) | Windowed (`console=False`, `upx=False`, `strip=False`) |
| **Binary Output** | `dist_apps/SIR Launcher.exe` (~35.5 MB) | `dist_apps/SIR Server Manager.exe` (~34.4 MB) | `dist_apps/SIR Installer.exe` (~18.7 MB) |

### 1.3 Critical PyInstaller Compilation Risks & Failure Points

1. **Source Desynchronization (Root vs `public_repo`)**:
   - The PyInstaller spec files hardcode paths to `D:/Projects/SIR ModPack/development/...`.
   - Recent modifications for R1-R3 (such as `downloads_manager.js`, `bridge.py`, `mods_service.py`, and `servers.js`) exist in `public_repo/` and must be fully synchronized with `d:/Projects/SIR ModPack/development/` before building. Otherwise, the generated `.exe` binaries will contain stale logic.
2. **File Lock Contention (`[WinError 5] Access is denied`)**:
   - If any instance of `SIR Launcher.exe`, `SIR Server Manager.exe`, or `SIR Installer.exe` is running from Root, `SIR Package/`, or `%APPDATA%/SIR ModPack`, the copy step in `build_ecosystem.py` will fail with an OS file-lock error.
   - *Mitigation*: Ensure all SIR processes are terminated via PowerShell before compilation.
3. **Hardcoded Drive Path Dependency**:
   - All 3 spec files use absolute `D:/Projects/SIR ModPack/...` paths. This works on this host machine, but any portable build requires dynamic path resolution relative to `SPECPATH`.

---

## 2. Test Harness Status & Leak Investigation

### 2.1 Test Suite Inventory
- **Unit Test Discovery**: `py -3.13 -m unittest discover -s tests -p "test_*.py"`
  - Total unit test files: 31 files
  - Total discovered unit test cases: **368 tests**
- **E2E Test Discovery**: `py -3.13 -m unittest discover -s tests_e2e -p "test_*.py"`
  - Total E2E test files: 1 file (`test_e2e_suite.py`)
  - Total discovered E2E test cases: **39 tests**

### 2.2 Test Run Results & Failures Breakdown

#### A. Unit Test Suite Execution
- **Command**: `py -3.13 -m unittest discover -s tests -p "test_*.py"`
- **Total Runtime**: 97.316 seconds
- **Outcome**: `FAILED (failures=2, errors=0, passed=366)`

#### Detailed Failure 1: Missing Mock for Subprocess Explorer Spawn
- **Test File**: `tests/test_challenger_m3_accounts_sync_bridge.py:494`
- **Test Name**: `test_bridge_all_new_alias_methods`
- **Failure Trace**:
  ```
  FAIL: test_bridge_all_new_alias_methods (test_challenger_m3_accounts_sync_bridge.TestChallengerM3AccountsSyncBridge.test_bridge_all_new_alias_methods)
  Traceback (most recent call last):
    File "D:\Projects\SIR ModPack\tests\test_challenger_m3_accounts_sync_bridge.py", line 494, in test_bridge_all_new_alias_methods
      self.assertTrue(mock_startfile.called)
  AssertionError: False is not true
  ```
- **Root Cause**:
  In `development/launcher_core/instance_service.py:1155-1167`, `open_instance_mods_folder` was upgraded for R3 to bring File Explorer to the foreground using Windows Win32 API and `subprocess.Popen`:
  ```python
  if sys.platform == "win32":
      try:
          import ctypes
          ctypes.windll.user32.AllowSetForegroundWindow(-1)
      except Exception:
          pass
      try:
          subprocess.Popen(['explorer.exe', os.path.normpath(target_dir)])
      except Exception:
          ...
  ```
  However, `test_challenger_m3_accounts_sync_bridge.py:490` only patches `os.startfile`:
  ```python
  with patch('os.startfile', create=True) as mock_startfile:
      res_open_mods = bridge.open_mods_folder("26.2")
      self.assertTrue(res_open_mods.get("success"))
      if sys.platform == "win32":
          self.assertTrue(mock_startfile.called) # <--- FAILS!
  ```
  Because `subprocess.Popen` succeeded, `os.startfile` was never reached. Furthermore, because `subprocess.Popen` was not mocked, real Windows Explorer windows were spawned during test runs.
- **Remediation**:
  In `test_challenger_m3_accounts_sync_bridge.py`, patch both `subprocess.Popen` and `os.startfile`:
  ```python
  with patch('subprocess.Popen') as mock_popen, patch('os.startfile', create=True) as mock_startfile:
      res_open_mods = bridge.open_mods_folder("26.2")
      self.assertTrue(res_open_mods.get("success"))
      if sys.platform == "win32":
          self.assertTrue(mock_popen.called or mock_startfile.called)
  ```

#### Detailed Failure 2: Drive D Free Space Invariant Violation
- **Test File**: `tests/test_system_audit_invariants.py:91`
- **Test Name**: `test_drive_d_free_space_threshold`
- **Failure Trace**:
  ```
  FAIL: test_drive_d_free_space_threshold (test_system_audit_invariants.TestSystemAuditInvariants.test_drive_d_free_space_threshold)
  Traceback (most recent call last):
    File "D:\Projects\SIR ModPack\tests\test_system_audit_invariants.py", line 91, in test_drive_d_free_space_threshold
      self.assertGreaterEqual(free_gb, min_free, f"Drive D free space must be >= {min_free} GB, currently {free_gb:.2f} GB")
  AssertionError: 15.911125183105469 not greater than or equal to 16.0 : Drive D free space must be >= 16.0 GB, currently 15.91 GB
  ```
- **Root Cause**:
  `shutil.disk_usage("D:/Projects/SIR ModPack")` reports 15.37 GB – 15.91 GB free space. The unit test enforces $\ge 16.0\text{ GB}$, and the E2E test / project criteria enforce $\ge 18.00\text{ GB}$.
- **Storage Profile of Drive D**:
  - Drive Total: 260.00 GB
  - Drive Used: 244.63 GB
  - Drive Free: 15.37 GB (Deficit to 18.00 GB: **2.63 GB**)
  - Major folders in `d:/Projects/SIR ModPack`:
    - `SIR Package`: 5.72 GB
    - `instances`: 5.51 GB
    - `public_repo`: 2.39 GB
    - `website-next`: 1.57 GB
    - `assets`: 1.24 GB
    - `exports`: 0.85 GB
    - `dist_payloads`: 0.80 GB
    - `libraries`: 0.75 GB
- **Remediation**:
  Purge unnecessary temporary zip exports or old build artifacts on Drive D (e.g. `dist_apps`, temporary `.next` caches, or user temp folders) to restore $\ge 18.00\text{ GB}$ free space.

#### B. E2E Test Suite Execution
- **Command**: `py -3.13 -m unittest discover -s tests_e2e -p "test_*.py"`
- **Total Runtime**: 1.149 seconds
- **Outcome**: `FAILED (failures=1, errors=0, passed=38)`
- **Failure**: `test_f17_drive_d_storage_invariant` at `tests_e2e/test_e2e_suite.py:357`:
  `AssertionError: 15.13 not greater than or equal to 18.0 : Drive D free space 15.13 GB is below required 18.00 GB invariant!`
  (Directly caused by the same disk capacity deficit).

### 2.3 Leaks & Resource Warnings Identified

1. **Unclosed Socket Leak in Port Contention Test**:
   - **Warning**: `ResourceWarning: unclosed <socket.socket fd=2696, family=2, type=1, proto=0>`
   - **Location**: `tests/test_challenger_m3_accounts_sync_bridge.py:280` in `test_microsoft_loopback_port_fallback_when_ports_occupied`:
   - **Cause**: Sockets created in the `for p in [52135, 52136]:` loop that fail to bind or encounter exceptions are not closed, and sockets appended to `occupied_socks` remain open until cleanup without a guaranteed context manager.
   - **Fix**: Wrap socket allocations in a try/finally block ensuring `s.close()` on every socket created.
2. **Subprocess Leak**:
   - **Warning**: `ResourceWarning: subprocess 11184 is still running` at `subprocess.py:1140`.
   - **Location**: `tests/test_challenger_m1_r2_empirical.py:409-488` in `test_ephemeral_rapid_spawn_and_churn` and `test_multi_process_concurrency_and_lifecycle_transitions`.
   - **Cause**: Some ephemeral child processes were killed or waited on without calling `p.poll()` / `p.communicate()`, leaving the Python handle registered in `subprocess._active`.
3. **Unclosed File Handles in Worker Threads**:
   - **Warning**: `ResourceWarning: unclosed file <_io.TextIOWrapper name=... encoding='cp65001'>` at `threading.py:999`.
   - **Cause**: Captured process stdout/stderr pipes in tests that were not closed before thread exit.

---

## 3. Web Platform & Firebase Hosting Verification

### 3.1 Next.js 16 Static Export Architecture
- **Directory**: `d:/Projects/SIR ModPack/website-next/`
- **Framework**: Next.js 16.3.2 App Router with React 19.2.8.
- **Export Config (`next.config.ts`)**:
  ```ts
  const nextConfig: NextConfig = {
    output: "export",
    trailingSlash: true,
    images: { unoptimized: true },
    experimental: {
      optimizePackageImports: ["lucide-react", "framer-motion"]
    }
  };
  ```
- **Export Target**: `website-next/out/` containing 35 static HTML routes matching requirements.

### 3.2 Firebase Hosting Configuration (`firebase.json`)
```json
{
  "database": { "rules": "database.rules.json" },
  "firestore": { "rules": "firestore.rules" },
  "hosting": {
    "public": "out",
    "cleanUrls": true,
    "trailingSlash": true,
    "headers": [
      {
        "source": "**",
        "headers": [
          { "key": "X-Content-Type-Options", "value": "nosniff" },
          { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
          { "key": "X-XSS-Protection", "value": "1; mode=block" },
          { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
          { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" }
        ]
      }
    ],
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**",
      "**/*.exe",
      "**/*.zip"
    ]
  }
}
```
- **Key Observation**:
  - `website-next/out/share` holds `SIR Launcher.exe` (35.5 MB), `SIR Server Manager.exe` (34.4 MB), and `SIR_Apps_Suite.zip` (86.3 MB).
  - Firebase Hosting enforces a **32 MB per-file upload ceiling**.
  - The `"ignore": ["**/*.exe", "**/*.zip"]` rule in `firebase.json` intentionally prevents large binary uploads, ensuring that `firebase deploy --only hosting` deploys only web assets without hitting size quota rejections.

### 3.3 Firebase Environment Prerequisites
- **Firebase CLI**: v15.12.0 installed globally.
- **Authentication**: Authenticated as `a7medorabe7@gmail.com`.
- **Active Project**: `.firebaserc` designates `sir-modpack` as default project. Confirmed active on Firebase.
- **Target URL**: `https://sir-modpack.web.app` (and `https://sir-modpack.firebaseapp.com`).

---

## 4. Git Repositories Status

### 4.1 Monorepo & Repositories Layout
- `d:/Projects/SIR ModPack`: Monorepo root (contains all raw assets, instances, package payloads, and tools). Not a Git repository directly.
- `d:/Projects/SIR ModPack/public_repo`: Git repository tracking public desktop source, configs, launchers, and tests.
  - Remote: `origin -> https://github.com/sirahmed8/SIR-ModPack.git`
  - Remote: `private -> https://github.com/sirahmed8/SIR-ModPack-private.git`
- `d:/Projects/SIR ModPack/website-next`: Git repository tracking web portal and Firebase rules.
  - Remote: `origin -> https://github.com/sirahmed8/SIR-ModPack-private.git`

### 4.2 Current Git Working Trees

| Repository | Current Branch | Last Commit | Remote Status | Working Tree State |
|---|---|---|---|---|
| `public_repo` | `main` | `0a18824a` | In sync with `origin/main` | **Uncommitted changes**: 7 modified files, 1 untracked file (`development/launcher_ui/js/downloads_manager.js`) |
| `website-next` | `main` | `c70f9df2` | In sync with `origin/main` | **Clean**: `nothing to commit, working tree clean` |

---

## 5. Step-by-Step Build, Verification & Deployment Protocol

When ready to execute Requirement 4, follow this exact sequence:

### Step 1: Code Harmonization & Storage Remediation
1. **Harmonize Source Files**:
   Ensure `development/launcher_core/` in project root receives the latest validated methods from `public_repo/development/launcher_core/` (e.g. `get_hardware_telemetry`, `get_servers`) while preserving root's Generational ZGC configuration (`instance_service.py`).
2. **Fix Test Mock (`test_challenger_m3_accounts_sync_bridge.py:490`)**:
   Update `test_bridge_all_new_alias_methods` to patch `subprocess.Popen` in addition to `os.startfile`.
3. **Free Drive D Space**:
   Clear $\ge 3.0\text{ GB}$ of unnecessary temporary files or caches on Drive D to bring free space $\ge 18.00\text{ GB}$.

### Step 2: Verification Run
```powershell
# 1. Run ecosystem diagnostic layer
py -3.13 ecosystem_doctor.py

# 2. Run master unit test suite
py -3.13 -m unittest discover -s tests -p "test_*.py" -v

# 3. Run E2E test suite
py -3.13 -m unittest discover -s tests_e2e -p "test_*.py" -v
```
*Expected Outcome*: 100% clean passes (0 failures, 0 errors) across all 368 unit tests and 39 E2E tests.

### Step 3: PyInstaller Desktop Compilation
```powershell
# Terminate any existing background SIR processes
Get-Process -Name "*SIR*", "*Launcher*" -ErrorAction SilentlyContinue | Stop-Process -Force

# Execute build ecosystem orchestrator
py -3.13 build_ecosystem.py
```
*Expected Outcome*: Successful build of all 3 executables in `dist_apps/` and synchronization to all 8 targets.

### Step 4: Web Static Export & Firebase Deployment
```powershell
cd "d:\Projects\SIR ModPack\website-next"

# Build static Next.js export
npm run build

# Deploy hosting to Firebase
firebase deploy --only hosting
```
*Expected Outcome*: 35 static routes exported to `out/` and deployed to `https://sir-modpack.web.app`.

### Step 5: Git Commit & Remote Synchronization
```powershell
# 1. Synchronize and commit public_repo
cd "d:\Projects\SIR ModPack\public_repo"
git add .
git commit -m "feat(ecosystem): v1.0.0 stabilization, modpack synchronization, and distribution update"
git push origin main

# 2. Commit and push website-next (if any new export or docs modified)
cd "d:\Projects\SIR ModPack\website-next"
git add .
git commit -m "feat(web): update static export and distribution manifests for v1.0.0"
git push origin main
```
