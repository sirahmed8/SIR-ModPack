# Reviewer 2 Report — Milestone 1: Python Core Engine & Telemetry Hardening

## 1. Observation

### 1.1 Test Suite Execution Results
- **Standard Baseline Test Suite** (`tests/test_launcher_bridge.py`, `tests/test_atomic_persistence.py`, `tests/test_telemetry_cleaner.py`):
  ```pwsh
  python -m unittest tests/test_launcher_bridge.py tests/test_atomic_persistence.py tests/test_telemetry_cleaner.py
  ```
  **Result**: `Ran 35 tests in 41.389s` -> **`OK`** (100% pass rate).

- **Full Ecosystem & Adversarial Test Suite** (`python -m unittest discover -s tests -p "test_*.py"`):
  ```
  Ran 81 tests in 70.872s
  FAILED (failures=2, errors=1)
  ```
  **Failures & Errors Observed**:
  1. `test_interrupted_byte_stream_recovery_with_http_range_resumption` (`tests/test_challenger_stress_m1.py:405`):
     ```
     ValueError: SHA-256 mismatch for C:\Users\a7med\AppData\Local\Temp\sir-stress-download-u_1hg385\downloaded_medium.bin: expected e40bdbda3f9bd6f0360203c58456467eab1e69a4ff81863ebdbbed99246c0cad, got 1b64003ad06b08826c8514c177fdc73085647c7b17164573397b3ab93dfa21a8
     ```
  2. `test_concurrent_multithreaded_atomic_write_race` (`tests/test_adversarial_m1.py:531`):
     ```
     AssertionError: 26 != 0 : Encountered write errors: [(2, 0, "[WinError 32] The process cannot access the file because it is being used by another process: '...\\race_config.json'")]
     ```
  3. `test_concurrent_multi_threaded_atomic_json_writers_and_readers` (`tests/test_challenger_stress_m1.py:240`):
     ```
     AssertionError: 1808 != 0 : Reader encountered JSON corruption: [PermissionError(13, 'Permission denied'), PermissionError(13, 'Permission denied'), PermissionError(13, 'Permission denied')]
     ```

### 1.2 Verification of 14 Un-atomic Write Replacements
Independently inspected all 14 write sites across the codebase:
1. `development/launcher_core/bridge.py:581` -> `atomic_write_json(agree_file, {...})` [VERIFIED]
2. `development/launcher_core/controls_service.py:90` -> `atomic_write_text(opt_path, "".join(new_lines))` [VERIFIED]
3. `development/launcher_core/packs_service.py:139` -> `atomic_write_text(opt_path, "".join(new_lines))` [VERIFIED]
4. `development/launcher_core/shaders_service.py:82` -> `atomic_write_text(target_cfg, content)` [VERIFIED]
5. `development/launcher_core/shaders_service.py:122` -> `atomic_write_text(bliss_cfg, content)` [VERIFIED]
6. `development/launcher_core/skin_studio_service.py:176` -> `atomic_write_json(skin_cfg, {...})` [VERIFIED]
7. `development/launcher_core/export_service.py:34` -> `with atomic_write_zip(target_path) as zipf:` [VERIFIED]
8. `development/launcher_core/export_service.py:68` -> `atomic_write_json(profile_path, data)` [VERIFIED]
9. `development/launcher_core/worlds_service.py:131` -> `with atomic_write_zip(backup_dest) as zf:` [VERIFIED]
10. `development/server_core/server_bridge.py:143` -> `atomic_write_json(self.settings_file, self.settings)` [VERIFIED]
11. `development/server_core/server_bridge.py:158` -> `atomic_write_text(eula_path, ...)` [VERIFIED]
12. `development/server_core/server_bridge.py:175` -> `atomic_write_text(props_path, default_props)` [VERIFIED]
13. `development/launcher_core/native_runner.py:325` -> `atomic_write_text(target_json, v_content)` [VERIFIED]
14. `development/launcher_core/instance_service.py:19,25` & `auth_service.py:28` -> imported `atomic_write_json` / `atomic_write_text` from `shared_core.runtime` [VERIFIED]

### 1.3 Concurrency & Thread Safety Inspection
- `development/launcher_core/async_tasks.py`: `AsyncTaskManager` uses `_tasks_lock = threading.Lock()` for task state manipulation, task listing, and progress reporting. `submit_task` handles callback invocation defensively and catches worker exceptions. PyWebView JavaScript calls via `window.evaluate_js` are protected with `try...except`.
- `development/launcher_core/bridge.py`: Async bridge methods wrap operations via `self.async_tasks.submit_task()`, returning immediate `{success: True, task_id: ...}` without blocking PyWebView.

### 1.4 Zero-Mock Telemetry & Diagnostics Inspection
- `development/launcher_core/hardware_monitor_service.py` & `telemetry_governor_service.py`: Direct Win32 ctypes calls (`GlobalMemoryStatusEx`, `GetProcessMemoryInfo`, `GetProcessTimes`, `EmptyWorkingSet`). No hardcoded mock values.
- `development/launcher_core/satellite_service.py`: 6 live endpoints queried concurrently with socket `try...finally: s.close()`.
- `development/launcher_core/cleaner_service.py` & `repair_service.py`: Real disk scanning, dry-run reports, SHA-256 checking, CRC tests, and `.corrupted` quarantine renames.
- `development/launcher_core/crash_analyzer.py`: 7 comprehensive matchers for real-world crash logs (Fabric/Forge mixin conflicts, Temurin 21 vs Java 8 mismatches, 5 OOM variants, GPU DLL native faults).
- `development/launcher_ui/app.js`: Scanned for `Math.sin`/`Math.cos` mock oscillation loops; zero instances found.

---

## 2. Logic Chain

1. **Downloader Premature EOF Defect**:
   - In `development/shared_core/downloader.py` (lines 176–189):
     ```python
     with open(temp_path, file_mode) as f_out:
         while True:
             chunk = resp.read(chunk_size)
             if not chunk:
                 break
             f_out.write(chunk)
     ```
   - When a remote server or proxy terminates a connection mid-stream without throwing a TCP exception, `resp.read()` returns `b""` (EOF).
   - If `content_len > 0` or `total_bytes > 0`, the read loop exits prematurely without verifying whether the number of bytes written in the current request equals the expected `content_len`.
   - As a result:
     - If `expected_sha256` is supplied: the truncated file fails the cryptographic checksum. In lines 229–235, `isinstance(ex, ValueError)` is classified as a non-retryable error, which immediately deletes the `.part` file and raises `ValueError`, completely breaking the HTTP Range resumption mechanism.
     - If no checksum is supplied: the partial, incomplete file is renamed into the destination path via `_atomic_replace_with_retry`, delivering a corrupted/truncated asset to the user.

2. **Windows NTFS File Lock Contention in `_atomic_replace_with_retry`**:
   - In `development/shared_core/persistence.py` (lines 18–35):
     - When multiple threads perform concurrent atomic writes to the same destination file on Windows, `os.replace(temp_path, target)` throws `[WinError 32] The process cannot access the file because it is being used by another process`.
     - In line 29, the fallback `if os.path.exists(target): os.remove(target)` also fails with `[WinError 32]` because removing a locked file handle is prohibited by Windows NTFS.
     - When concurrent reader threads open the target file with standard `open(target, "r")` during the exact millisecond `os.replace` is modifying directory metadata, readers receive `PermissionError: [WinError 5] Access is denied` or `[WinError 32]`.
     - To ensure 100% resilience under heavy multi-threaded contention on Windows, `_atomic_replace_with_retry` requires adaptive backoff with higher retry thresholds and graceful handling of transient `PermissionError` / `WinError 32` / `WinError 5`.

---

## 3. Caveats

- **Operating System Specifics**: The file locking issues (`WinError 32` / `PermissionError 13`) are specific to Windows NTFS file sharing semantics and do not manifest on POSIX systems where file descriptors support unlinked deletion.
- **Scope Limit**: As Reviewer 2, in accordance with the 🔒 Key Constraints, no code modifications were applied by this agent. All findings and exact remediation guidance are provided for Worker M1.

---

## 4. Conclusion

**Verdict**: **`REQUEST_CHANGES`**

### Summary of Findings:
1. **Critical — Downloader Incomplete Stream / Premature EOF Handling**:
   - **Location**: `development/shared_core/downloader.py` (lines 176–235)
   - **Issue**: Missing verification of `written_bytes == content_len` upon `b""` EOF in `download_file_resilient`. Truncated streams either corrupt destinations (if unhashed) or prematurely abort/delete `.part` files (if hashed) instead of triggering HTTP Range retry.
   - **Remediation**: In `download_file_resilient`, track bytes read during the response. If `content_len > 0` and bytes read `< content_len` upon `read()` returning `b""`, raise a retryable `ConnectionResetError("Premature stream termination: received fewer bytes than Content-Length")`.

2. **Major — Windows File Contention & Retry Resilience in `_atomic_replace_with_retry`**:
   - **Location**: `development/shared_core/persistence.py` (lines 18–36)
   - **Issue**: Transient `WinError 32` / `PermissionError` during high-frequency concurrent writes on Windows causes write failures when `max_retries` or backoff is exceeded.
   - **Remediation**: Catch `(OSError, PermissionError)`, increase retry attempts or random backoff jitter, and avoid calling `os.remove` if `os.replace` fails with sharing violations.

3. **Approved Components**:
   - `AsyncTaskManager` & `LauncherBridgeAPI` non-blocking async architecture: **PASS**
   - 14/14 Un-atomic write replacements: **PASS**
   - Zero-mock Win32 hardware governor & memory trimming: **PASS**
   - Zero-mock satellite service live pings & telemetry: **PASS**
   - Deep crash stack-trace analyzer (7 matchers): **PASS**
   - Frontend `app.js` zero-mock verification: **PASS**

---

## 5. Verification Method

1. **Verify Downloader Resumption Under Stream Drop**:
   ```pwsh
   python -m unittest tests/test_challenger_stress_m1.py -k test_interrupted_byte_stream_recovery_with_http_range_resumption -v
   ```
2. **Verify Concurrent Atomic Persistence on Windows**:
   ```pwsh
   python -m unittest tests/test_adversarial_m1.py -k test_concurrent_multithreaded_atomic_write_race -v
   python -m unittest tests/test_challenger_stress_m1.py -k test_concurrent_multi_threaded_atomic_json_writers_and_readers -v
   ```
3. **Execute Full Suite**:
   ```pwsh
   python -m unittest discover -s tests -p "test_*.py"
   ```
   **Acceptance Target**: 81/81 tests passing with 0 failures and 0 errors.
