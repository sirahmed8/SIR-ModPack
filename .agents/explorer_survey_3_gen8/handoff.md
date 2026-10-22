# Handoff Report: R4 Technical Survey & Test Harness Status

**Agent**: `explorer_survey_3_gen8`  
**Working Directory**: `d:/Projects/SIR ModPack/.agents/explorer_survey_3_gen8/`  
**Handoff Type**: Hard (Investigation & Technical Survey Complete)  
**Parent / Caller**: `ea599214-f527-4f9a-8f66-cdc1288aa4b2`  

---

## 1. Observation

1. **PyInstaller Packaging Infrastructure**:
   - `build_ecosystem.py`: Valid orchestrator located at `d:/Projects/SIR ModPack/build_ecosystem.py`. Compiles 3 spec files: `SIR Launcher.spec`, `SIR Server Manager.spec`, `SIR Installer.spec` using `py -3.13 -m PyInstaller --clean --noconfirm <spec> --distpath dist_apps --workpath build_apps`.
   - `SIR Launcher.spec` (lines 8-10): Analyses `development/launcher_source/SIR_Launcher_Modern.py`, bundles `launcher_ui`, `launcher_core`, `shared_core`, and imports `webview`, `clr`, `pystray`, `PIL`.
   - All 3 spec files use hardcoded paths pointing to `D:/Projects/SIR ModPack/development/...`.
   - Output sync targets: 8 directories (`ROOT`, `public_repo`, `SIR Package`, `SIR Launcher`, `%APPDATA%\SIR ModPack`, `%APPDATA%\SIR ModPack\SIR Launcher`, `website-next\public\share`, `website-next\out\share`).
   - PyInstaller version: `6.22.2` verified under Python 3.13. All required packages (`webview`, `pystray`, `PIL`, `clr`) import cleanly.

2. **Master Test Suite (`tests/`) Execution**:
   - Total discovered unit tests: **368 tests** across 31 test files via `py -3.13 -m unittest discover -s tests -p "test_*.py"`.
   - Runtime: 97.316s.
   - Result: 366 passed, **2 failed**, 0 errors.
   - **Failure 1**:
     ```
     FAIL: test_bridge_all_new_alias_methods (test_challenger_m3_accounts_sync_bridge.TestChallengerM3AccountsSyncBridge.test_bridge_all_new_alias_methods)
     Traceback (most recent call last):
       File "D:\Projects\SIR ModPack\tests\test_challenger_m3_accounts_sync_bridge.py", line 494, in test_bridge_all_new_alias_methods
         self.assertTrue(mock_startfile.called)
     AssertionError: False is not true
     ```
   - **Failure 2**:
     ```
     FAIL: test_drive_d_free_space_threshold (test_system_audit_invariants.TestSystemAuditInvariants.test_drive_d_free_space_threshold)
     Traceback (most recent call last):
       File "D:\Projects\SIR ModPack\tests\test_system_audit_invariants.py", line 91, in test_drive_d_free_space_threshold
         self.assertGreaterEqual(free_gb, min_free, f"Drive D free space must be >= {min_free} GB, currently {free_gb:.2f} GB")
     AssertionError: 15.911125183105469 not greater than or equal to 16.0 : Drive D free space must be >= 16.0 GB, currently 15.91 GB
     ```

3. **E2E Test Suite (`tests_e2e/`) Execution**:
   - Total discovered E2E tests: **39 tests** in `tests_e2e/test_e2e_suite.py`.
   - Runtime: 1.149s.
   - Result: 38 passed, **1 failed**, 0 errors.
   - **Failure**:
     ```
     FAIL: test_f17_drive_d_storage_invariant (test_e2e_suite.TestTier1FeatureCoverage.test_f17_drive_d_storage_invariant)
     Traceback (most recent call last):
       File "D:\Projects\SIR ModPack\tests_e2e\test_e2e_suite.py", line 357, in test_f17_drive_d_storage_invariant
         self.assertGreaterEqual(free_gb, 18.00, f"Drive D free space {free_gb:.2f} GB is below required 18.00 GB invariant!")
     AssertionError: 15.126705169677734 not greater than or equal to 18.0 : Drive D free space 15.13 GB is below required 18.00 GB invariant!
     ```

4. **Resource / Handle Leaks Observed**:
   - Sockets: `D:\Projects\SIR ModPack\tests\test_challenger_m3_accounts_sync_bridge.py:280: ResourceWarning: unclosed <socket.socket fd=2696, family=2, type=1, proto=0>` during `test_microsoft_loopback_port_fallback_when_ports_occupied`.
   - Subprocesses: `C:\...\subprocess.py:1140: ResourceWarning: subprocess 11184 is still running` from child processes spawned during telemetry churn tests in `tests/test_challenger_m1_r2_empirical.py`.
   - File Handles: `threading.py:999: ResourceWarning: unclosed file <_io.TextIOWrapper name=... encoding='cp65001'>`.

5. **Drive D Free Space Invariant**:
   - Drive D Capacity: 260.00 GB total, 244.63 GB used, **15.37 GB free**.
   - Deficit to required $\ge 18.00\text{ GB}$ invariant: **2.63 GB**.

6. **Web Platform & Firebase Hosting**:
   - `website-next/` uses Next.js 16.3.2 with `output: "export"`, exporting 35 routes to `out/`.
   - `firebase.json` has `hosting.public: "out"`, ignoring `**/*.exe` and `**/*.zip` to comply with Firebase's 32 MB file upload limit.
   - Firebase CLI is v15.12.0, logged in as `a7medorabe7@gmail.com`. Project `sir-modpack` is verified and active.

7. **Git Repositories State**:
   - `d:/Projects/SIR ModPack` is the monorepo root (not a git repo).
   - `d:/Projects/SIR ModPack/public_repo`: Branch `main`, in sync with `origin/main` (`0a18824a`), but has uncommitted working copy changes:
     - 7 modified files: `bridge.py`, `hardware_monitor_service.py`, `instance_service.py`, `mods_service.py`, `index.html`, `servers.js`, `test_challenger_m1_r2_empirical.py`.
     - 1 untracked file: `development/launcher_ui/js/downloads_manager.js`.
   - `d:/Projects/SIR ModPack/website-next`: Branch `main`, in sync with `origin/main` (`c70f9df2`), working tree clean.

8. **Root vs `public_repo` Desynchronization**:
   - `public_repo/development/launcher_core/bridge.py` contains `get_hardware_telemetry()` and `get_servers(category="All")`, which were absent from `d:/Projects/SIR ModPack/development/launcher_core/bridge.py`.
   - `d:/Projects/SIR ModPack/development/launcher_core/instance_service.py` contains Generational ZGC flags (`-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5`), whereas `public_repo` had G1GC flags.
   - Because PyInstaller spec files compile from `D:/Projects/SIR ModPack/development/`, building without first syncing these changes will omit the latest R1-R3 bridge methods from the standalone executables.

---

## 2. Logic Chain

1. **Test Failure 1 Reason**: In R3, `instance_service.open_instance_mods_folder` was upgraded to use `subprocess.Popen(['explorer.exe', target_dir])` along with Win32 `AllowSetForegroundWindow(-1)` to satisfy foregrounding requirements. In `test_challenger_m3_accounts_sync_bridge.py:490`, the test mocked `os.startfile` and asserted `mock_startfile.called`. Because `subprocess.Popen` succeeded, `os.startfile` was never called, causing the assertion to fail and launching actual Explorer windows during test execution.
2. **Test Failure 2 & E2E Failure Reason**: Both `test_system_audit_invariants.py` (line 91) and `test_e2e_suite.py` (line 357) assert Drive D free space against $\ge 16.0\text{ GB}$ and $\ge 18.00\text{ GB}$ respectively. Real disk metrics show 15.37 GB free space, causing both tests to fail with clean `AssertionError`s.
3. **Packaging Integrity**: Because `build_ecosystem.py` compiles from `D:/Projects/SIR ModPack/development/`, and recent edits exist in `public_repo/`, compiling without merging `public_repo` into `development/` would create outdated executables.
4. **Firebase Readiness**: Firebase CLI is already authenticated to the correct user account and default project (`sir-modpack`). The ignore patterns in `firebase.json` properly exclude `.exe` and `.zip` files from `out/share`, preventing deployment quota failures.
5. **Executable Synchronization**: The 8 target sync directories exist and are verified. No processes are currently locking `SIR Launcher.exe`, ensuring `shutil.copy2` will succeed when the build script is invoked.

---

## 3. Caveats

1. **No Destructive File Purges Performed**: In strict adherence to read-only constraints and the `accidental-data-loss-prevention` rule, no large files were deleted to reclaim the 2.63 GB needed on Drive D. The orchestrator or user must approve which temporary directories (e.g. `exports/`, `dist_payloads/`, or local caches) to prune.
2. **Source Code Modifications Not Applied**: The patch to `test_challenger_m3_accounts_sync_bridge.py` and the source sync between `public_repo` and root were documented but not written to source files.
3. **No Network Push Executed**: Git commits and pushes to remote repositories were surveyed and verified, but not triggered.

---

## 4. Conclusion

1. **Master Test Suite**: 366/368 unit tests and 38/39 E2E tests are already fully passing. Achieving 100% (368/368 and 39/39) requires only:
   - Patching `subprocess.Popen` in `tests/test_challenger_m3_accounts_sync_bridge.py:490`.
   - Freeing $\ge 2.63\text{ GB}$ on Drive D to satisfy the 18.00 GB invariant.
2. **Packaging (`build_ecosystem.py`)**: All prerequisites (PyInstaller 6.22.2, pywebview, clr, pystray, PIL) are operational. Before compilation, source changes in `public_repo/` must be synchronized into `d:/Projects/SIR ModPack/development/`.
3. **Deployment**: Firebase Hosting is 100% pre-configured and authenticated to `sir-modpack`. `firebase deploy --only hosting` will deploy cleanly once `npm run build` is executed.
4. **Git State**: `website-next` is clean and pushed. `public_repo` has 7 modified files and 1 untracked file ready to be committed and pushed once R1-R3 tasks are sealed.

---

## 5. Verification Method

To independently verify these findings:

1. **Verify Test Failures & Count**:
   ```powershell
   py -3.13 -m unittest discover -s tests -p "test_*.py"
   ```
   *Expected*: Discovers 368 tests; runs with 366 passes and exactly 2 failures (`test_bridge_all_new_alias_methods` and `test_drive_d_free_space_threshold`).

2. **Verify E2E Test Failure & Count**:
   ```powershell
   py -3.13 -m unittest discover -s tests_e2e -p "test_*.py"
   ```
   *Expected*: Discovers 39 tests; runs with 38 passes and exactly 1 failure (`test_f17_drive_d_storage_invariant`).

3. **Verify Drive D Capacity Deficit**:
   ```powershell
   Get-PSDrive D | Select-Object Name, @{N="FreeGB";E={[math]::Round($_.Free/1GB,2)}}
   ```
   *Expected*: Reports ~15.37 GB free space ($< 18.00\text{ GB}$).

4. **Verify Ecosystem Doctor**:
   ```powershell
   py -3.13 ecosystem_doctor.py
   ```
   *Expected*: Passes 100% healthy across all 6 diagnostic layers.

5. **Verify Firebase CLI & Project Access**:
   ```powershell
   cd "d:\Projects\SIR ModPack\website-next"
   firebase login:list
   firebase projects:list
   ```
   *Expected*: Shows logged in as `a7medorabe7@gmail.com` with `sir-modpack (current)`.

6. **Verify Git Working Copies**:
   ```powershell
   git -C "d:\Projects\SIR ModPack\public_repo" status -sb
   git -C "d:\Projects\SIR ModPack\website-next" status -sb
   ```
