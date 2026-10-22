## 2026-08-29T20:03:56Z
You are the Lead Implementation Worker for Milestone 1 (M1: Python Core Engine & Telemetry Hardening).
Your working directory is: D:\Projects\SIR ModPack\.agents\teamwork_preview_worker_m1
Project root: D:\Projects\SIR ModPack
Master Project Plan: D:\Projects\SIR ModPack\PROJECT.md
Authoritative User Request: D:\Projects\SIR ModPack\.agents\ORIGINAL_REQUEST.md
Test Infrastructure Plan: D:\Projects\SIR ModPack\TEST_INFRA.md
Relevant Domain Skill: C:\Users\a7med\.gemini\config\skills\production-engineering-standards\SKILL.md

Survey & Explorer Technical Blueprints to read and execute:
- D:\Projects\SIR ModPack\.agents\teamwork_preview_explorer_survey_1\handoff.md
- D:\Projects\SIR ModPack\.agents\explorer_m1_1\handoff.md
- D:\Projects\SIR ModPack\.agents\explorer_m1_2\handoff.md
- D:\Projects\SIR ModPack\.agents\explorer_m1_3\handoff.md

Your Assigned Scope & Deliverables for Milestone 1 (Features 1-6):
1. Feature 1 (Async Bridge & Non-blocking I/O):
   - Implement `development/launcher_core/async_tasks.py` with `AsyncTaskManager` (thread pool, task status registry, custom event emitter to PyWebView).
   - Refactor `development/launcher_core/bridge.py` and `store_service.py` to use non-blocking async execution for long operations (`install_online_mod`, `check_mod_updates`, `run_deep_clean`, `run_self_repair`, `export_instance_zip`).
2. Feature 2 (Resilient Chunked Downloader):
   - Enhance `development/shared_core/runtime.py` (`download_file_resilient` and `download_files_batch`) with HTTP Range resume support, exponential backoff (retries), chunk streaming (128KB), SHA-256/SHA-1 validation, and atomic `.part` replacement.
   - Refactor `store_service.py`, `bridge.py`, `installer_bridge.py`, and `server_bridge.py` to use `download_file_resilient` instead of raw `urllib.request.urlopen().read()`.
3. Feature 3 (Universal Atomic File Persistence):
   - Ensure `atomic_write_json`, `atomic_write_text`, and `atomic_copy` in `development/shared_core/runtime.py` and `manifest.py` are robust.
   - Replace all raw `open(..., 'w')` calls with atomic file writes across `instance_service.py`, `bridge.py`, `controls_service.py`, `shaders_service.py`, `skin_studio_service.py`, `export_service.py`, `worlds_service.py`, `repair_service.py`, `native_runner.py`, and `server_bridge.py`.
4. Bug Fix in `InstanceService`:
   - Fix `InstanceService` line 878-886 to call `self._launch_result(...)` instead of nonexistent `self._build_launch_response(...)`.
5. Feature 4 (Zero Mock Telemetry & Cleaner):
   - Remove ALL fake fallback numbers in `cleaner_service.py` (fake 1240.80 MB / 184 files), `repair_service.py` (fake 248 verified files), `syncer_service.py` (fake 100%), `satellite_service.py` (fake 3120 peers / static loads), `hardware_monitor_service.py` (fake 23.8 GB / static praise), and `java_service.py` (fake fallback paths).
   - Implement real dry-run analysis and real deletion in `cleaner_service.py`.
   - Implement genuine SHA-256 and quarantine isolation in `repair_service.py`.
   - Implement real non-blocking TCP socket pings and latency measurements in `satellite_service.py`.
   - Implement real Win32 RAM, CPU, disk usage, multi-GPU enumeration, and dynamic hardware recommendations in `hardware_monitor_service.py`.
6. Feature 5 (Telemetry Governor & Memory Trimming):
   - Implement `development/launcher_core/telemetry_governor_service.py` (and integrate with `hardware_monitor_service.py` / `instance_service.py`) to track child JVM PID CPU % and RAM working set via Win32 `ctypes` (`kernel32.dll`, `psapi.dll`), and provide `EmptyWorkingSet` memory trimming.
7. Feature 6 (Deep Crash Stack-Trace Analyzer):
   - Implement `development/launcher_core/crash_analyzer.py` and integrate with `logs_service.py` with 7 diagnostic pattern matchers (Mixin conflicts with offending mod extraction, Java class major version mismatches like 65.0 vs 52.0, 5 OOM variants, native driver crashes like `nvoglv64.dll`, mod dependencies, corrupted world regions, and shader OpenGL errors).
8. Automated Tests:
   - Create and run `tests/test_launcher_bridge.py`, `tests/test_atomic_persistence.py`, and `tests/test_telemetry_cleaner.py`.
   - Run `python -m unittest discover -s tests -p "test_*.py"` and ensure 100% test pass rate.
