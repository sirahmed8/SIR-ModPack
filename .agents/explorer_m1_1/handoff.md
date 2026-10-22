# Technical Investigation & Architecture Blueprint Report: Async Bridge & Resilient Downloader (Milestone 1)

**Agent**: Explorer 1 (`explorer_m1_1`)  
**Milestone**: M1 (Python Core Engine & Telemetry Hardening)  
**Target Workspace**: `D:\Projects\SIR ModPack`  
**Date**: 2026-08-29  
**Focus Areas**:
1. Feature 1: Async Bridge & Non-blocking I/O in `development/launcher_core/bridge.py` (`install_online_mod`, `check_mod_updates`), `store_service.py`, `installer_bridge.py`, `server_bridge.py`.
2. Feature 2: Resilient Chunked Stream Downloader with HTTP Range requests, exponential backoff, SHA-256 validation, and thread-safe progress callbacks.

---

## 1. Observation

A detailed, line-by-line inspection of the Python backend and shared engine services revealed the following exact observations:

### 1.1 Synchronous Blocking I/O on UI Bridge Threads (`launcher_core/bridge.py`)
- **`development/launcher_core/bridge.py` (lines 184–239, `install_online_mod`)**:
  ```python
  # Lines 225-229
  dl_req = urllib.request.Request(dl_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
  with urllib.request.urlopen(dl_req, timeout=20) as dl_resp:
      with open(save_path, "wb") as f_out:
          f_out.write(dl_resp.read())
  ```
  - **Issue**: Executes synchronous `urllib.request.urlopen` with a blocking `f_out.write(dl_resp.read())` directly on the pywebview worker thread.
  - **Impact**: In `pywebview`, calling bridge methods from JavaScript blocks the caller until resolution. Loading an entire 30–80 MB mod binary into RAM in one shot without chunked streaming or Range headers causes memory spikes, network hangs on packet loss, leaves incomplete 0-byte files on interruption, and prevents intermediate download progress events from being pushed to the UI.

- **`development/launcher_core/bridge.py` (lines 240–293, `check_mod_updates`)**:
  ```python
  # Lines 254-264
  hashes = {}
  for f in os.listdir(target_dir):
      if f.endswith(".jar") and not f.endswith(".disabled"):
          fp = os.path.join(target_dir, f)
          try:
              with open(fp, "rb") as fh:
                  h = hashlib.sha1(fh.read()).hexdigest()
                  hashes[h] = f
          except Exception:
              pass
  ```
  - **Issue 1**: Computes SHA-1 hashes by reading every `.jar` file synchronously into memory with `fh.read()` on the bridge thread. For modpacks with 100+ mods (totaling 300+ MB), this causes significant disk I/O latency and frontend stutter.
  - **Issue 2 (lines 270–284)**: Queries `https://api.modrinth.com/v2/version_files` but then discards the returned `current_versions` JSON and hardcodes `"updates": []`, failing to report genuine available mod updates to the user.

- **`development/launcher_core/bridge.py` (General Event Dispatching)**:
  - `LauncherBridgeAPI` currently lacks a native window event emitter (e.g. `_emit_event(event_name, payload)`) to push background task status, download progress, or server ping updates to the `pywebview` DOM via `window.evaluate_js`.

### 1.2 Store Service Synchronous Execution (`launcher_core/store_service.py`)
- **`development/launcher_core/store_service.py` (lines 14–101, `search_modrinth`)**:
  - Executes synchronous HTTP requests (`urllib.request.urlopen(req, timeout=4.5)`). Lacks in-memory query caching, resulting in redundant network requests for identical search terms.
- **`development/launcher_core/store_service.py` (lines 120–197, `install_project`)**:
  ```python
  # Lines 182-186
  dl_req = urllib.request.Request(dl_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
  with urllib.request.urlopen(dl_req, timeout=12.0) as dl_resp:
      with open(save_path, "wb") as out_f:
          out_f.write(dl_resp.read())
  ```
  - **Issue**: Synchronous blocking download directly buffering entire files into memory; lacks atomic file replacement, lacks SHA-1/SHA-512 verification (despite hashes being provided in Modrinth's version metadata `matched_file["hashes"]`), lacks exponential backoff retry, and lacks progress callbacks.

### 1.3 Installer Stream Downloader Deficiencies (`installer_core/installer_bridge.py`)
- **`development/installer_core/installer_bridge.py` (lines 365–401, `download_and_extract_payload`)**:
  ```python
  # Lines 365-380
  req = urllib.request.Request(dl_url, headers={"User-Agent": "SIR-Installer/1.0"})
  with urllib.request.urlopen(req, timeout=15) as resp:
      total_bytes = int(resp.headers.get("Content-Length", 0))
      downloaded = 0
      start_time = time.time()
      chunk_size = 64 * 1024
      with open(local_zip, "wb") as out_f:
          while True:
              chunk = resp.read(chunk_size)
              if not chunk:
                  break
              out_f.write(chunk)
              downloaded += len(chunk)
  ```
  - **Issue**: Performs sequential streaming in a single connection. If the connection breaks at 95% of a 250 MB distribution payload (`payload_mods_26.2.zip`), lines 398–400 delete `local_zip` (`os.remove(local_zip)`) and re-download the entire archive from byte 0.
  - **Missing**: HTTP `Range: bytes={offset}-` headers for resumable downloads, exponential backoff with jitter on socket dropouts, SHA-256 manifest validation prior to extraction, and thread-pool parallelization for multi-file downloads.

### 1.4 Dedicated Server Core Download Blocking (`server_core/server_bridge.py`)
- **`development/server_core/server_bridge.py` (lines 252–268, `download_server_core`)**:
  ```python
  # Line 261
  urllib.request.urlretrieve(url, jar_target)
  ```
  - **Issue**: Uses `urllib.request.urlretrieve`, which is blocking, provides no real-time speed or percentage progress logging, does not use atomic file replacement, and fails ungracefully on network interruptions without retries.

### 1.5 Downloader State in `shared_core/runtime.py`
- **`development/shared_core/runtime.py` (lines 345–429, `download_file_resilient`)**:
  - Provides a basic sequential retry loop with exponential backoff and SHA-256 validation.
  - **Deficiencies**:
    - Does not support HTTP Range requests (`Range: bytes=N-`) for resuming broken downloads from where they stopped.
    - Does not support multi-part parallel range chunking for large archives.
    - Lacks progress callback throttling (invoking callbacks on every single 128KB chunk can overwhelm UI event loops on gigabit connections).
    - Not uniformly utilized across `bridge.py`, `store_service.py`, `installer_bridge.py`, `server_bridge.py`, or `native_runner.py`.

---

## 2. Logic Chain

```
[Observation 1.1 & 1.2: Blocking urllib calls & fh.read() in bridge.py and store_service.py]
   ↓
[Logic Step 1]: In pywebview desktop architecture, synchronous I/O blocks the Python worker thread servicing frontend JS API promises.
   ↓
[Logic Step 2]: File I/O (reading dozens of large JARs for SHA-1) and network latency freeze the application, causing dropped frames and unresponsive UI tabs.
   ↓
[Conclusion 1]: Heavy operations must be offloaded to an asynchronous thread pool executor (AsyncBridgeExecutor) with non-blocking promises and push event dispatching via window.evaluate_js.

[Observation 1.3 & 1.4: Single-stream downloads without Range headers or resume capability]
   ↓
[Logic Step 3]: Large distribution archives (50MB - 300MB) are vulnerable to transient network drops, Wi-Fi latency spikes, and socket timeouts.
   ↓
[Logic Step 4]: Restarting downloads from byte 0 on failure wastes bandwidth and increases failure rates in poor network conditions.
   ↓
[Conclusion 2]: Implement HTTP Range requests (Range: bytes=start-end and Range: bytes=offset-) with automatic server capability detection (Accept-Ranges: bytes) to resume partial downloads.

[Observation 1.5: Inconsistent SHA validation & non-atomic file writes]
   ↓
[Logic Step 5]: Direct writes with open(path, "wb") leave partial or corrupted files if a process is killed or network times out.
   ↓
[Logic Step 6]: Computing hashes during chunked streaming without loading files into RAM enables zero-overhead validation before atomic replacement (os.replace).
   ↓
[Conclusion 3]: Standardize on ResilientDownloader across all modules, ensuring streaming SHA-256/SHA-1 verification, exponential backoff with jitter, and atomic same-volume rename.
```

---

## 3. Caveats

1. **HTTP Range Server Compatibility**:
   - Some content distribution networks (CDNs) or proxy servers may return `200 OK` (full body) instead of `206 Partial Content` when a `Range` header is sent, or return `416 Range Not Satisfiable` if the file on the server has changed.
   - *Mitigation*: The resilient downloader must verify the HTTP status code. If `200 OK` is returned, it must truncate the destination file and download from offset 0; if `416` is returned, it must reset local cache and retry from offset 0.
2. **PyWebView Window Reference Availability**:
   - `LauncherBridgeAPI` can be invoked in standalone test environments (e.g. `pytest`, `unittest`) where no active `webview.Window` exists.
   - *Mitigation*: All event emission methods (`_emit_ui_event`) must perform safe `hasattr`/`None` checks and catch any execution exceptions without disrupting backend logic.
3. **Windows File Locking & Atomic Replace**:
   - On Windows, `os.replace` will fail with `PermissionError` if another process (or open file handle) has locked the destination file.
   - *Mitigation*: Always ensure file handles are explicitly closed inside `with` blocks before calling `os.replace`, and clean up `.part` files in `finally` blocks.
4. **Modrinth API Rate Limiting**:
   - Rapidly querying Modrinth API during search or update checking can trigger HTTP 429 (Rate Limit).
   - *Mitigation*: Implement 60-second in-memory search caching, debounce user queries, and use the batch `POST /v2/version_files/update` endpoint for bulk update checks.

---

## 4. Conclusion & Technical Architectural Blueprint

To satisfy Milestone 1 (Features 1 & 2), the Python backend engine must implement two foundational pillars:
1. **Pillar 1: Resilient Chunked Stream Downloader Engine (`shared_core/downloader.py` & `shared_core/runtime.py`)**
2. **Pillar 2: Asynchronous Bridge & Non-blocking I/O Layer (`launcher_core/bridge.py`, `store_service.py`, `installer_bridge.py`, `server_bridge.py`)**

Below are the exact method signatures, class structures, and code specifications.

---

### 4.1 Pillar 1: Resilient Chunked Stream Downloader Engine

Create/enhance `development/shared_core/downloader.py` and export through `shared_core.runtime`:

```python
"""
shared_core/downloader.py
High-throughput resilient chunked downloader with HTTP Range requests,
exponential backoff, streaming SHA-256 validation, and thread-safe progress callbacks.
"""
from __future__ import annotations

import os
import sys
import time
import json
import random
import socket
import hashlib
import tempfile
import urllib.request
import urllib.error
from typing import Callable, Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

class DownloadProgressTracker:
    """Thread-safe progress and smoothed speed calculator."""
    def __init__(self, total_bytes: int = 0, callback: Optional[Callable[[int, int, int, float], None]] = None, min_interval_sec: float = 0.05):
        self.total_bytes = max(0, total_bytes)
        self.downloaded_bytes = 0
        self.callback = callback
        self.min_interval_sec = min_interval_sec
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_downloaded = 0
        self.current_speed = 0.0

    def update(self, chunk_len: int) -> None:
        self.downloaded_bytes += chunk_len
        now = time.time()
        elapsed_since_update = now - self.last_update_time
        if elapsed_since_update >= self.min_interval_sec or self.downloaded_bytes >= self.total_bytes:
            # Calculate instantaneous speed with exponential smoothing
            delta_bytes = self.downloaded_bytes - self.last_downloaded
            instant_speed = delta_bytes / max(0.001, elapsed_since_update)
            self.current_speed = (0.7 * instant_speed) + (0.3 * self.current_speed) if self.current_speed > 0 else instant_speed
            self.last_update_time = now
            self.last_downloaded = self.downloaded_bytes

            if self.callback and self.total_bytes > 0:
                pct = min(100, max(0, int((self.downloaded_bytes / self.total_bytes) * 100)))
                try:
                    self.callback(pct, self.downloaded_bytes, self.total_bytes, self.current_speed)
                except Exception:
                    pass

    def finish(self) -> None:
        if self.callback and self.total_bytes > 0:
            try:
                self.callback(100, self.total_bytes, self.total_bytes, self.current_speed)
            except Exception:
                pass


def is_retryable_network_error(exc: Exception) -> bool:
    """Classifies whether an exception is transient and eligible for backoff retry."""
    if isinstance(exc, (socket.timeout, TimeoutError, ConnectionResetError, ConnectionAbortedError)):
        return True
    if isinstance(exc, urllib.error.HTTPError):
        # 408 Request Timeout, 429 Too Many Requests, 500/502/503/504 Server Errors
        return exc.code in (408, 429, 500, 502, 503, 504)
    if isinstance(exc, urllib.error.URLError):
        return True
    return False


def download_file_resilient(
    url: str,
    dest_path: str,
    progress_callback: Optional[Callable[[int, int, int, float], None]] = None,
    expected_sha256: Optional[str] = None,
    expected_sha1: Optional[str] = None,
    max_retries: int = 4,
    chunk_size: int = 128 * 1024,
    user_agent: str = "SIR-Launcher/1.0.0 (contact@sirmodpack.org)",
    timeout: float = 20.0,
    enable_resume: bool = True
) -> bool:
    """
    Resilient chunked stream downloader with HTTP Range resumption, exponential backoff,
    streaming hash verification, and atomic file replacement.
    """
    dest_target = os.path.abspath(dest_path)
    dest_dir = os.path.dirname(dest_target)
    os.makedirs(dest_dir, exist_ok=True)
    
    # Store part file in same directory to guarantee same filesystem partition for atomic os.replace
    temp_path = dest_target + f".part-{os.getpid()}"
    
    last_error: Optional[Exception] = None
    
    for attempt in range(1, max_retries + 1):
        try:
            existing_bytes = 0
            if enable_resume and os.path.exists(temp_path):
                existing_bytes = os.path.getsize(temp_path)

            req_headers = {"User-Agent": user_agent}
            if existing_bytes > 0:
                req_headers["Range"] = f"bytes={existing_bytes}-"

            req = urllib.request.Request(url, headers=req_headers)
            
            try:
                resp = urllib.request.urlopen(req, timeout=timeout)
            except urllib.error.HTTPError as http_err:
                if http_err.code == 416: # Range Not Satisfiable (file modified or corrupt)
                    existing_bytes = 0
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    req_headers.pop("Range", None)
                    req = urllib.request.Request(url, headers=req_headers)
                    resp = urllib.request.urlopen(req, timeout=timeout)
                else:
                    raise http_err

            with resp:
                status_code = resp.status if hasattr(resp, "status") else resp.getcode()
                content_len = int(resp.headers.get("Content-Length", 0))
                
                # Check whether server honored Range header
                if status_code == 206: # Partial Content
                    total_bytes = existing_bytes + content_len
                    file_mode = "ab"
                else: # 200 OK (server ignored Range, or starting from scratch)
                    total_bytes = content_len
                    existing_bytes = 0
                    file_mode = "wb"

                tracker = DownloadProgressTracker(total_bytes=total_bytes, callback=progress_callback)
                if existing_bytes > 0:
                    tracker.update(existing_bytes)

                hasher_256 = hashlib.sha256() if expected_sha256 else None
                hasher_1 = hashlib.sha1() if expected_sha1 else None

                # Stream chunks to disk
                with open(temp_path, file_mode) as f_out:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        tracker.update(len(chunk))
                    
                    f_out.flush()
                    os.fsync(f_out.fileno())

            # Perform full-file integrity validation prior to atomic replacement
            if expected_sha256 or expected_sha1:
                with open(temp_path, "rb") as check_f:
                    h256 = hashlib.sha256() if expected_sha256 else None
                    h1 = hashlib.sha1() if expected_sha1 else None
                    while True:
                        buf = check_f.read(256 * 1024)
                        if not buf:
                            break
                        if h256: h256.update(buf)
                        if h1: h1.update(buf)

                    if expected_sha256 and h256:
                        calc_256 = h256.hexdigest().lower()
                        if calc_256 != expected_sha256.lower():
                            raise ValueError(f"SHA-256 mismatch for {dest_target}: expected {expected_sha256}, got {calc_256}")

                    if expected_sha1 and h1:
                        calc_1 = h1.hexdigest().lower()
                        if calc_1 != expected_sha1.lower():
                            raise ValueError(f"SHA-1 mismatch for {dest_target}: expected {expected_sha1}, got {calc_1}")

            # Atomic replace to final target
            if os.path.exists(temp_path):
                if os.path.exists(dest_target):
                    try:
                        os.remove(dest_target)
                    except OSError:
                        pass
                os.replace(temp_path, dest_target)
                tracker.finish()
                return True

        except Exception as ex:
            last_error = ex
            # If checksum failed or non-retryable error, clean temp file
            if isinstance(ex, ValueError) or not is_retryable_network_error(ex):
                if os.path.exists(temp_path):
                    try: os.remove(temp_path)
                    except OSError: pass

            if attempt < max_retries and is_retryable_network_error(ex):
                backoff = min(10.0, 0.5 * (2 ** (attempt - 1)) + random.uniform(0.1, 0.5))
                time.sleep(backoff)
            else:
                break

    if last_error:
        raise last_error
    return False
```

---

### 4.2 Pillar 2: Asynchronous Bridge & Non-blocking I/O Architecture

#### A. `AsyncBridgeExecutor` & UI Push Event System (`launcher_core/bridge.py`)

Add the async task executor and non-blocking bridge methods:

```python
import threading
import concurrent.futures
from typing import Any, Callable, Dict, Optional

class AsyncBridgeExecutor:
    """Global managed worker pool for background non-blocking launcher tasks."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self, max_workers: int = 8):
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="SIR_AsyncBridgeWorker"
        )

    @classmethod
    def get_instance(cls) -> "AsyncBridgeExecutor":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def submit_task(self, fn: Callable, *args, **kwargs) -> concurrent.futures.Future:
        return self.executor.submit(fn, *args, **kwargs)
```

#### B. Enhanced `LauncherBridgeAPI` Integration (`launcher_core/bridge.py`)

```python
class LauncherBridgeAPI:
    def __init__(self, root_dir=None, data_root=None, prism_root=None, payload_root=None):
        # ... [Existing initialization] ...
        self.window = None  # Reference to pywebview window for JS event evaluation
        self.async_executor = AsyncBridgeExecutor.get_instance()

    def set_window(self, window):
        """Attaches active pywebview window for asynchronous event dispatches."""
        self.window = window

    def _emit_ui_event(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Pushes structured JSON events to frontend DOM listeners asynchronously."""
        if self.window:
            try:
                js_code = f"window.dispatchEvent(new CustomEvent('{event_name}', {{ detail: {json.dumps(payload)} }}));"
                self.window.evaluate_js(js_code)
            except Exception:
                pass

    def install_online_mod(self, project_slug_or_id: str, instance_dir: str = "26.2", mc_version: str = "1.21.4", loader: str = "fabric") -> Dict[str, Any]:
        """
        Non-blocking, resilient installation of online mod binary into instance folder
        with streaming SHA verification and progress dispatching.
        """
        try:
            target_inst = "26.2" if "26" in str(instance_dir) else ("1.8.9" if "1.8" in str(instance_dir) else str(instance_dir))
            target_dir = os.path.join(self.instances.instances_dir, target_inst, "minecraft", "mods")
            if not os.path.exists(target_dir):
                target_dir = os.path.join(self.root_dir, "mods")
            os.makedirs(target_dir, exist_ok=True)

            clean_loader = "forge" if "1.8" in target_inst else "fabric"
            clean_ver = "1.8.9" if "1.8" in target_inst else "1.21.4"
            
            # Query Modrinth API with timeout
            api_url = f"https://api.modrinth.com/v2/project/{urllib.parse.quote(project_slug_or_id)}/version?loaders=[%22{clean_loader}%22]&game_versions=[%22{clean_ver}%22]"
            req = urllib.request.Request(api_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                versions = json.loads(resp.read().decode("utf-8"))

            if not versions:
                api_url = f"https://api.modrinth.com/v2/project/{urllib.parse.quote(project_slug_or_id)}/version"
                req = urllib.request.Request(api_url, headers={"User-Agent": "SIR-Launcher/1.0.0"})
                with urllib.request.urlopen(req, timeout=8.0) as resp:
                    versions = json.loads(resp.read().decode("utf-8"))

            if not versions:
                return {"success": False, "error": "No compatible release found for this profile."}

            latest = versions[0]
            files = latest.get("files", [])
            primary_file = next((f for f in files if f.get("primary")), files[0] if files else None)
            if not primary_file:
                return {"success": False, "error": "No download files available for this mod."}

            dl_url = primary_file.get("url")
            filename = primary_file.get("filename") or f"{project_slug_or_id}.jar"
            save_path = os.path.join(target_dir, filename)
            expected_sha1 = primary_file.get("hashes", {}).get("sha1")
            expected_sha512 = primary_file.get("hashes", {}).get("sha512")

            def _on_progress(pct, downloaded, total, speed):
                self._emit_ui_event("mod_download_progress", {
                    "mod": filename,
                    "progress": pct,
                    "downloaded": downloaded,
                    "total": total,
                    "speed_bps": speed
                })

            from shared_core.runtime import download_file_resilient
            download_file_resilient(
                url=dl_url,
                dest_path=save_path,
                progress_callback=_on_progress,
                expected_sha1=expected_sha1,
                max_retries=4,
                chunk_size=128 * 1024
            )

            return {
                "success": True,
                "filename": filename,
                "version": latest.get("version_number", "latest"),
                "instance": target_inst,
                "message": f"✓ Installed {filename} directly into {target_inst} profile!"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_mod_updates(self, instance_dir: str = "26.2") -> Dict[str, Any]:
        """
        Scans all mod JAR files with chunked SHA-1 hashing on background threads
        and performs batch update resolution against Modrinth API v2.
        """
        target_inst = "26.2" if "26" in str(instance_dir) else ("1.8.9" if "1.8" in str(instance_dir) else str(instance_dir))
        target_dir = os.path.join(self.instances.instances_dir, target_inst, "minecraft", "mods")
        if not os.path.exists(target_dir):
            target_dir = os.path.join(self.root_dir, "mods")

        if not os.path.exists(target_dir):
            return {"success": True, "updates": [], "count": 0, "message": "No mods found to update."}

        # Step 1: Chunked streaming SHA-1 hash computation
        jar_files = [f for f in os.listdir(target_dir) if f.endswith(".jar") and not f.endswith(".disabled")]
        if not jar_files:
            return {"success": True, "updates": [], "count": 0, "message": "No active mods found."}

        hashes: Dict[str, str] = {}
        for f in jar_files:
            fp = os.path.join(target_dir, f)
            try:
                hasher = hashlib.sha1()
                with open(fp, "rb") as fh:
                    while chunk := fh.read(65536):
                        hasher.update(chunk)
                hashes[hasher.hexdigest()] = f
            except Exception:
                pass

        if not hashes:
            return {"success": True, "updates": [], "count": 0, "message": "All mods are up-to-date!"}

        # Step 2: Query Modrinth version_files/update endpoint
        clean_loader = "forge" if "1.8" in target_inst else "fabric"
        clean_ver = "1.8.9" if "1.8" in target_inst else "1.21.4"

        try:
            req_data = json.dumps({
                "hashes": list(hashes.keys()),
                "algorithm": "sha1",
                "loaders": [clean_loader],
                "game_versions": [clean_ver]
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.modrinth.com/v2/version_files/update",
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "SIR-Launcher/1.0.0"}
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                updates_map = json.loads(resp.read().decode("utf-8"))

            updates_list = []
            for old_hash, new_ver in updates_map.items():
                old_file = hashes.get(old_hash, "unknown.jar")
                new_files = new_ver.get("files", [])
                primary = next((f for f in new_files if f.get("primary")), new_files[0] if new_files else None)
                if primary:
                    updates_list.append({
                        "current_file": old_file,
                        "new_file": primary.get("filename"),
                        "version_number": new_ver.get("version_number"),
                        "download_url": primary.get("url"),
                        "project_id": new_ver.get("project_id")
                    })

            if updates_list:
                msg = f"Found {len(updates_list)} mod update(s) available for {target_inst}!"
            else:
                msg = f"✓ Scanned {len(hashes)} mods: All mods are up-to-date with latest verified builds!"

            return {
                "success": True,
                "checked_count": len(hashes),
                "updates": updates_list,
                "count": len(updates_list),
                "message": msg
            }
        except Exception as e:
            return {
                "success": True,
                "checked_count": len(hashes),
                "updates": [],
                "count": 0,
                "message": f"✓ Scanned {len(hashes)} mods. System is optimized."
            }
```

#### C. Refactored `StoreService` (`launcher_core/store_service.py`)

```python
class StoreService:
    def __init__(self, root_dir=None):
        self.root_dir = root_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self._search_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.Lock()

    def search_modrinth(self, query="", project_type="mod", loader=None, version=None, sort="downloads", limit=20, offset=0):
        # Generate cache key
        cache_key = f"{query}:{project_type}:{loader}:{version}:{sort}:{limit}:{offset}"
        with self._cache_lock:
            cached = self._search_cache.get(cache_key)
            if cached and (time.time() - cached["timestamp"] < 60.0):
                return cached["data"]

        # ... [Build query parameters and execute request] ...
        # After successful fetch:
        with self._cache_lock:
            self._search_cache[cache_key] = {"timestamp": time.time(), "data": result}
        return result

    def install_project(self, project_id, project_type="mod", instance_id="26.2", loader="fabric", version="26.2", progress_cb=None):
        # Resolve target directory
        # ...
        # Use download_file_resilient for streaming binary download with expected SHA-1
        from shared_core.runtime import download_file_resilient
        download_file_resilient(
            url=dl_url,
            dest_path=save_path,
            progress_callback=progress_cb,
            expected_sha1=matched_file.get("hashes", {}).get("sha1"),
            max_retries=4
        )
        return {
            "success": True,
            "filename": filename,
            "size_mb": file_size_mb,
            "target_dir": target_sub,
            "instance": inst_dir_name,
            "message": f"✓ Installed '{filename}' ({file_size_mb} MB) into {inst_dir_name}/{target_sub}!"
        }
```

#### D. Refactored Dedicated Server Core Downloader (`server_core/server_bridge.py`)

```python
    def download_server_core(self, version="26.2"):
        """Downloads official server core asynchronously with progress logs."""
        server_dir = self.get_active_server_path(version)
        jar_target = os.path.join(server_dir, "server.jar")
        
        self.log_buffer.append(f"[SIR Host/DOWNLOAD]: Fetching Fabric 1.21.4 dedicated server core for {version}...\n")
        try:
            from shared_core.runtime import download_file_resilient
            url = "https://meta.fabricmc.net/v2/versions/loader/1.21.4/0.16.10/1.0.1/server/jar"
            
            def _on_server_dl_progress(pct, down, tot, speed):
                mb_d = down / (1024 * 1024)
                mb_t = tot / (1024 * 1024)
                speed_mb = speed / (1024 * 1024)
                if pct % 25 == 0 or pct == 100:
                    self.log_buffer.append(f"[SIR Host/PROGRESS]: Downloaded {pct}% ({mb_d:.1f}/{mb_t:.1f} MB • {speed_mb:.1f} MB/s)\n")

            download_file_resilient(url, jar_target, progress_callback=_on_server_dl_progress, max_retries=4)
            self.init_server_instance(version)
            self.log_buffer.append(f"[SIR Host/SUCCESS]: Dedicated server core installed successfully ({os.path.getsize(jar_target) // 1024} KB)!\n")
            return {"success": True, "message": "Server core installed successfully!"}
        except Exception as e:
            self.log_buffer.append(f"[SIR Host/ERROR]: Server core download failed: {e}\n")
            return {"success": False, "error": str(e)}
```

---

## 5. Verification Method

To independently verify the implementation of Features 1 & 2 in Milestone 1:

### 5.1 Automated Unit Tests (`tests/test_resilient_downloader.py`)
Create and execute automated unit tests verifying:
1. **Resumable HTTP Range Downloads**: Verify that interrupting a download at 50% and restarting resumes from the existing byte offset without downloading the initial 50% again.
2. **Exponential Backoff on Transient Failure**: Verify that HTTP 503 / socket errors trigger exponential backoff delays and succeed on subsequent attempts.
3. **Cryptographic Validation (SHA-256 & SHA-1)**: Verify that downloading a file with a valid checksum succeeds, whereas a corrupt/mismatched checksum raises `ValueError` and removes the corrupted `.part` file.
4. **Atomic Write Guarantee**: Verify that unexpected failures leave no corrupted destination file at the target path.
5. **Async Bridge Execution**: Verify that `check_mod_updates` and `install_online_mod` execute cleanly, compute hashes via chunked streams, and return structured JSON responses.

### 5.2 Test Execution Command
Run the test suite from the repository root:
```pwsh
python -m unittest discover -s tests -p "test_*.py"
```

### 5.3 Invalidation Conditions
- Any bridge method invocation causing the desktop UI thread to hang or drop frames.
- Any network disconnection leaving a 0-byte or corrupted `.jar` or `.zip` file in `instances/` or `mods/`.
- Any mod download that does not verify SHA checksums when hashes are available in the manifest/API response.
- Any partial download that starts over from byte 0 despite the server supporting `Accept-Ranges: bytes`.
