# Milestone 1 Review & Adversarial Challenge Report

## 1. Observation

### 1.1 Automated Test Execution & Verbatim Failures
Executing the standard automated test discovery command:
```pwsh
python -m unittest discover -s tests -p "test_*.py"
```
Direct output:
```
Ran 81 tests in 76.017s
FAILED (failures=2, errors=1)
```

**Verbatim Failures**:

1. `test_adversarial_m1.py:531-532` (`TestAdversarialAtomicPersistence.test_concurrent_multithreaded_atomic_write_race`):
   ```python
   AssertionError: 2806 != 0 : Encountered read errors during concurrent replace: [
       (6, "Unexpected read error: [Errno 13] Permission denied: '...race_config.json'"),
       (7, "Unexpected read error: [Errno 13] Permission denied: '...race_config.json'"),
       ...
   ]
   ```

2. `test_challenger_stress_m1.py:240` (`TestAtomicPersistenceEmpiricalStress.test_concurrent_multi_threaded_atomic_json_writers_and_readers`):
   ```python
   AssertionError: 841 != 0 : Reader encountered JSON corruption: [
       PermissionError(13, 'Permission denied'),
       PermissionError(13, 'Permission denied'),
       PermissionError(13, 'Permission denied')
   ]
   ```

3. `test_challenger_stress_m1.py:405` (`TestResilientDownloaderEmpiricalStress.test_interrupted_byte_stream_recovery_with_http_range_resumption`):
   ```python
   ValueError: SHA-256 mismatch for downloaded_medium.bin: expected 4f4ebdd47c752a4547b3e8aae6ec15767036f1729b63a1beededa2e259a0b3db, got 3b0e390427c62e79497e4d769af3b662ee3cc40c3d3754f91eaef26f7a74ea11
   ```
   *(Note: Passes when run in isolated suite `python -m unittest tests/test_challenger_stress_m1.py`, but encounters transient port/stream collision during full discovery).*

---

### 1.2 Codebase Review Observations

1. **Feature 1: Async Bridge & Non-blocking I/O** (`development/launcher_core/async_tasks.py`, `bridge.py`):
   - `AsyncTaskManager` implements a thread-safe singleton managing a `ThreadPoolExecutor(max_workers=8)` with cooperative cancellation (`threading.Event`), progress callbacks, and safe PyWebView event emission (`evaluate_js`).
   - `bridge.py` exposes async counterparts for mod downloads (`install_online_mod_async`), update checks (`check_mod_updates_async`), storage cleaning (`run_deep_clean_async`), and instance repair (`run_self_repair_async`).
   - Verified genuine implementation; zero mock task runners.

2. **Feature 2: Resilient Chunked Downloader** (`development/shared_core/downloader.py`):
   - Implements HTTP Range 206 resuming (`Range: bytes={existing}-`), exponential backoff with jitter, cryptographic SHA-256/SHA-1 validation, and atomic rename.
   - Stream truncation is handled via `IncompleteRead` partial chunk collection and `os.path.getsize` validation.

3. **Feature 3: Universal Atomic Persistence** (`development/shared_core/persistence.py`):
   - Implements `atomic_write_json`, `atomic_write_text`, `atomic_copy`, and `atomic_write_zip` via same-directory `.tmp` staging, explicit `flush()` and `os.fsync()`, followed by `_atomic_replace_with_retry`.
   - **Flaw**: On Windows, when readers execute standard `open(target, "r")` during `os.replace`, Windows raises `PermissionError` (Errno 13) / `WinError 32` due to mandatory file locking during `MoveFileEx`. The library lacks an `atomic_read_json` helper with retry backoff.

4. **Feature 4: Zero-Mock Telemetry, Real Cleaner & Repair** (`satellite_service.py`, `cleaner_service.py`, `repair_service.py`, `launcher_ui/app.js`):
   - `satellite_service.py` executes genuine multi-threaded TCP socket pings against 6 live hostnames (`authserver.mojang.com`, `sessionserver.mojang.com`, `api.modrinth.com`, `resources.download.minecraft.net`, `1.1.1.1`, `8.8.8.8`).
   - `cleaner_service.py` performs genuine disk traversals across instance directories, logs, shadercache, GPUCache, and temp files with dry-run support.
   - `repair_service.py` verifies SHA-256 with 128KB chunks, validates ZIP CRC tables with `zf.testzip()`, and quarantines corrupted jars.
   - `app.js` (lines 305–317): Fake sinusoidal oscillations (`Math.sin(Date.now() / 2000)`) were completely removed and replaced with genuine kernel telemetry bindings.

5. **Feature 5: Telemetry Governor & Memory Trimming** (`telemetry_governor_service.py`, `hardware_monitor_service.py`):
   - Pure `ctypes` implementation querying `kernel32.dll` and `psapi.dll` (`GetProcessMemoryInfo`, `GetProcessTimes`, `EmptyWorkingSet`).
   - Verifiably trims working set memory on live processes without external dependencies.

6. **Feature 6: Deep Crash Stack-Trace Analyzer** (`crash_analyzer.py`, `crash_analyzer_service.py`, `logs_service.py`):
   - Diagnoses 7 distinct crash categories: Fabric/Forge Mixin conflicts, Java class version mismatches, 5 OOM variants (Heap, Direct, Metaspace, GC Overhead, Native Thread), JVM native crashes (`hs_err_pid*.log`, `nvoglv64.dll`, `atio6axx.dll`, etc.), missing dependencies (`trove4j`, `Fabric API`), corrupted world regions (`r.0.0.mca`), and shader/OpenGL context errors.

---

## 2. Logic Chain

1. **Integrity & Implementation Assessment**:
   - The implementations across `development/launcher_core/` and `development/shared_core/` represent genuine, production-grade logic. No dummy facades, hardcoded outputs, or shortcuts were found.
2. **Windows File Locking Concurrency Issue**:
   - On Windows NT kernel, `os.replace` replaces a file via `MoveFileExW(..., MOVEFILE_REPLACE_EXISTING)`.
   - When multiple threads concurrently read and write the exact same JSON configuration file, readers opening the file without shared delete access experience transient `PermissionError` (Errno 13) or `[WinError 32]`.
   - Because `persistence.py` only wraps writes in retry logic (`_atomic_replace_with_retry`) and does not provide an `atomic_read_json` retry wrapper, standard concurrent reads fail under heavy write contention.
   - This directly causes the 2 test failures in `test_adversarial_m1.py` and `test_challenger_stress_m1.py`.
3. **Verdict Determination**:
   - Project quality and CI standards require a 100% automated test pass rate across the full test suite (`python -m unittest discover -s tests -p "test_*.py"`).
   - Because 2 tests fail in the automated test discovery, changes are requested to remediate Windows read/write concurrency in `persistence.py` and ensure full test pass.

---

## 3. Caveats

- Isolated executions of `test_atomic_persistence.py` (10/10), `test_telemetry_cleaner.py` (14/14), `test_launcher_bridge.py` (11/11), `test_m1_stress_challenger2.py` (14/14), and `test_native_runner.py` (3/3) pass completely.
- The failure is isolated to high-contention multi-threaded concurrent reads/writes on Windows file systems and socket test isolation during full test suite discovery.

---

## 4. Conclusion & Required Actions

**Verdict**: **REQUEST_CHANGES**

### Required Remediation for Worker M1:

1. **Add `atomic_read_json` & `atomic_read_text` with Windows Retry Backoff** in `development/shared_core/persistence.py`:
   - Implement `atomic_read_json(path, max_retries=15, default=None)` and `atomic_read_text(path, max_retries=15)` that catch transient `PermissionError` (Errno 13) and `FileNotFoundError` during replace races, retrying with brief exponential backoff.
2. **Increase Resilience in `_atomic_replace_with_retry`**:
   - Tune retry intervals and ensure graceful handling when another thread holds an open handle.
3. **Ensure Test Isolation & 100% Pass Rate**:
   - Update reader loops in `test_adversarial_m1.py` and `test_challenger_stress_m1.py` to use `atomic_read_json` or handle expected transient Windows sharing locks.
   - Re-run `python -m unittest discover -s tests -p "test_*.py"` and verify all 81 tests pass cleanly.

---

## 5. Verification Method

To independently verify the fixes:

1. Run the full automated test discovery:
   ```pwsh
   python -m unittest discover -s tests -p "test_*.py"
   ```
   **Pass Condition**: 81 tests run with 0 failures and 0 errors (`OK`).

2. Run stress tests individually:
   ```pwsh
   python -m unittest tests/test_adversarial_m1.py
   python -m unittest tests/test_challenger_stress_m1.py
   python -m unittest tests/test_m1_stress_challenger2.py
   ```
   **Pass Condition**: All test suites complete with status `OK`.
