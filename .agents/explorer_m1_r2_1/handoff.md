# Milestone 1 Round 2 Investigation Report: Persistence Hardening

## 1. Observation

### 1.1 Reviewer 1 & Reviewer 2 Findings
During full automated test suite discovery (`python -m unittest discover -s tests -p "test_*.py"`):
1. **Reviewer 1** observed:
   - `test_adversarial_m1.py:531-532` (`TestAdversarialAtomicPersistence.test_concurrent_multithreaded_atomic_write_race`):
     ```python
     AssertionError: 2806 != 0 : Encountered read errors during concurrent replace: [
         (6, "Unexpected read error: [Errno 13] Permission denied: '...race_config.json'"),
         (7, "Unexpected read error: [Errno 13] Permission denied: '...race_config.json'"),
         ...
     ]
     ```
   - `test_challenger_stress_m1.py:240` (`TestAtomicPersistenceEmpiricalStress.test_concurrent_multi_threaded_atomic_json_writers_and_readers`):
     ```python
     AssertionError: 841 != 0 : Reader encountered JSON corruption: [
         PermissionError(13, 'Permission denied'),
         PermissionError(13, 'Permission denied'),
         PermissionError(13, 'Permission denied')
     ]
     ```

2. **Reviewer 2** observed:
   - `test_concurrent_multithreaded_atomic_write_race` (`tests/test_adversarial_m1.py:531`):
     ```python
     AssertionError: 26 != 0 : Encountered write errors: [(2, 0, "[WinError 32] The process cannot access the file because it is being used by another process: '...\\race_config.json'")]
     ```
   - `test_concurrent_multi_threaded_atomic_json_writers_and_readers` (`tests/test_challenger_stress_m1.py:240`):
     ```python
     AssertionError: 1808 != 0 : Reader encountered JSON corruption: [PermissionError(13, 'Permission denied'), PermissionError(13, 'Permission denied'), PermissionError(13, 'Permission denied')]
     ```

### 1.2 Inspection of `development/shared_core/persistence.py`
Direct inspection of `persistence.py` revealed:
1. **In-Process Lock Key Normalization** (lines 25–29):
   ```python
   def _get_path_lock(target: str) -> threading.Lock:
       with _GLOBAL_LOCK:
           if target not in _PATH_LOCKS:
               _PATH_LOCKS[target] = threading.Lock()
           return _PATH_LOCKS[target]
   ```
   `target` is not normalized with `os.path.normcase(os.path.abspath(str(target)))`. On Windows, casing variations (e.g. `C:\Mods` vs `c:\mods`) yield distinct locks, breaking mutual exclusion.

2. **Flawed `os.remove` Fallback in `_atomic_replace_with_retry`** (lines 32–50):
   ```python
   def _atomic_replace_with_retry(temp_path: str, target: str, max_retries: int = 50) -> None:
       path_lock = _get_path_lock(target)
       with path_lock:
           for attempt in range(max_retries):
               try:
                   os.replace(temp_path, target)
                   return
               except OSError:
                   if attempt == max_retries - 1:
                       try:
                           if os.path.exists(target):
                               os.remove(target)
                           os.replace(temp_path, target)
                           return
                       except OSError as final_err:
                           raise final_err
                   time.sleep(random.uniform(0.001, 0.005) * (attempt + 1))
   ```
   - On attempt `max_retries - 1`, attempting `os.remove(target)` when a reader holds an open handle fails immediately with `[WinError 32]` or `PermissionError`. The exception is re-raised via `raise final_err`, causing write failures under high contention.
   - The retry sleep was linear and narrow (`0.001` to `0.005 * attempt`), causing thread stampedes.

3. **Absence of Atomic Read Primitives**:
   - `persistence.py` lacked `atomic_read_json` and `atomic_read_text` with adaptive backoff to handle transient Windows sharing locks (`WinError 32`, `WinError 5`, `Errno 13`) during `MoveFileExW` operations.

4. **Inconsistent `atomic_write_zip`** (lines 124–129):
   - `atomic_write_zip` did not use `_atomic_replace_with_retry`, directly attempting `os.remove` and `os.replace`.

---

## 2. Logic Chain

1. **Windows NTFS File Sharing Semantics**:
   - On Windows NT kernel, `os.replace(src, dst)` invokes `MoveFileExW(src, dst, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)`.
   - When a reader thread opens `dst` via standard Python `open(dst, "r")`, Windows CRT acquires a file handle without `FILE_SHARE_DELETE`.
   - If `MoveFileExW` executes concurrently against `dst`, Windows raises `ERROR_SHARING_VIOLATION` (`WinError 32`) or `ERROR_ACCESS_DENIED` (`WinError 5` / `Errno 13`).
   - If `open(dst, "r")` executes at the exact microsecond `MoveFileExW` updates directory metadata, the reader receives `PermissionError` or transient `FileNotFoundError`.

2. **Why Readers Failed in Stress Tests**:
   - In `test_adversarial_m1.py` and `test_challenger_stress_m1.py`, test reader loops attempted only 10 retries with fixed 1ms sleeps (total 10ms window).
   - Under 20 concurrent writer threads performing continuous atomic `fsync` operations, 10ms is easily exceeded. Once 10 retries were exhausted, unhandled `PermissionError` or `WinError 32` escaped the reader loop.

3. **Why Writers Failed in Stress Tests**:
   - Under 20 writers and 10 readers, when writer attempts reached `attempt == max_retries - 1`, `_atomic_replace_with_retry` executed `os.remove(target)`.
   - Because `os.remove` on a file with open reader handles is explicitly prohibited by Windows NTFS, it raised `WinError 32` and immediately aborted via `raise final_err`.

4. **Remediation Strategy**:
   - Provide `atomic_read_json` and `atomic_read_text` with exponential backoff (`base_delay * 1.35^attempt`), randomized micro-sleep jitter (`1ms–8ms`), and fast short-circuit for genuine `FileNotFoundError` (5 retries / ~15ms max).
   - Refactor `_atomic_replace_with_retry` to:
     1. Use `os.path.normcase(os.path.abspath(target))` for lock lookup.
     2. Remove toxic `os.remove` invocation.
     3. Apply jittered exponential backoff with higher retry bounds (60 retries).
   - Update `atomic_write_zip` to utilize `_atomic_replace_with_retry`.
   - Re-export `atomic_read_json` and `atomic_read_text` in `runtime.py` and `shared_core/__init__.py`.

---

## 3. Caveats

- **Operating System Specifics**: Windows NTFS enforces mandatory file sharing locks during file deletion/replacement. On POSIX systems, `rename()` succeeds even with open file descriptors. The retry and backoff logic ensures cross-platform consistency while addressing Windows-specific NTFS locking.
- **Scope Boundary**: As Explorer 1, in accordance with the 🔒 Key Constraints, source files were not modified during this step. The exact code changes are formulated below for implementation.

---

## 4. Conclusion & Proposed Code Implementation

### 4.1 Proposed Content for `development/shared_core/persistence.py`

```python
"""
persistence.py — Universal Atomic Persistence Primitives for SIR Minecraft Ecosystem.
Guarantees zero file corruption on unexpected power loss, kill signals, or process crashes.
Robust Windows NTFS file lock resilience under heavy multi-threaded contention.
"""
from __future__ import annotations

import contextlib
import json
import os
import random
import shutil
import tempfile
import threading
import time
import zipfile
from pathlib import Path
from typing import Any, Iterator, Optional, Union

_PATH_LOCKS: dict[str, threading.Lock] = {}
_GLOBAL_LOCK = threading.Lock()
_UNSET = object()


def _get_path_lock(target: str) -> threading.Lock:
    """Return a path-specific thread lock with normalized case for Windows filesystem paths."""
    norm = os.path.normcase(os.path.abspath(str(target)))
    with _GLOBAL_LOCK:
        if norm not in _PATH_LOCKS:
            _PATH_LOCKS[norm] = threading.Lock()
        return _PATH_LOCKS[norm]


def _atomic_replace_with_retry(
    temp_path: str,
    target: str,
    max_retries: int = 60,
    base_delay: float = 0.002,
    max_delay: float = 0.1,
) -> None:
    """Safely replace a target file on Windows with jittered exponential backoff and in-process lock synchronization."""
    path_lock = _get_path_lock(target)
    with path_lock:
        last_err: Optional[OSError] = None
        for attempt in range(max_retries):
            try:
                os.replace(temp_path, target)
                return
            except (OSError, PermissionError) as err:
                last_err = err
                if attempt == max_retries - 1:
                    break
                # Exponential backoff with random full jitter to prevent thread synchronization stampedes
                backoff = min(max_delay, base_delay * (1.35 ** min(attempt, 12)))
                jitter = random.uniform(0.001, 0.008)
                time.sleep(backoff + jitter)

        if last_err is not None:
            raise last_err


def atomic_write_json(
    path: Union[str, Path],
    value: Any,
    indent: int = 2,
    ensure_ascii: bool = False,
    max_retries: int = 60,
) -> None:
    """Write JSON data through a same-directory temporary file with fsync and atomic replace."""
    target = os.path.abspath(str(path))
    target_dir = os.path.dirname(target)
    os.makedirs(target_dir, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".sir-json-", suffix=".tmp", dir=target_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=indent, ensure_ascii=ensure_ascii)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        _atomic_replace_with_retry(temp_path, target, max_retries=max_retries)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def atomic_write_text(
    path: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    max_retries: int = 60,
) -> None:
    """Write text data through a same-directory temporary file with fsync and atomic replace."""
    target = os.path.abspath(str(path))
    target_dir = os.path.dirname(target)
    os.makedirs(target_dir, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".sir-txt-", suffix=".tmp", dir=target_dir)
    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        _atomic_replace_with_retry(temp_path, target, max_retries=max_retries)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def atomic_copy(
    src: Union[str, Path],
    dst: Union[str, Path],
    max_retries: int = 60,
) -> None:
    """Copy a file atomically through a same-directory temporary file with fsync."""
    src_target = os.path.abspath(str(src))
    dst_target = os.path.abspath(str(dst))
    dst_dir = os.path.dirname(dst_target)
    os.makedirs(dst_dir, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".sir-copy-", suffix=".tmp", dir=dst_dir)
    try:
        with os.fdopen(fd, "wb") as out_f, open(src_target, "rb") as in_f:
            shutil.copyfileobj(in_f, out_f, length=128 * 1024)
            out_f.flush()
            os.fsync(out_f.fileno())
        _atomic_replace_with_retry(temp_path, dst_target, max_retries=max_retries)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@contextlib.contextmanager
def atomic_write_zip(
    dest_path: Union[str, Path],
    max_retries: int = 60,
) -> Iterator[zipfile.ZipFile]:
    """Context manager to create a zip archive atomically via a same-directory temporary file."""
    target = os.path.abspath(str(dest_path))
    target_dir = os.path.dirname(target)
    os.makedirs(target_dir, exist_ok=True)
    temp_zip = target + f".tmp-{os.getpid()}-{int(time.time() * 1000)}"
    try:
        with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            yield zf
        _atomic_replace_with_retry(temp_zip, target, max_retries=max_retries)
    finally:
        if os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except OSError:
                pass


def atomic_read_text(
    path: Union[str, Path],
    encoding: str = "utf-8",
    max_retries: int = 30,
    base_delay: float = 0.002,
    max_delay: float = 0.08,
) -> str:
    """Read text from a file with exponential backoff and jitter on Windows sharing violations."""
    target = os.path.abspath(str(path))
    last_err: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            with open(target, "r", encoding=encoding) as f:
                return f.read()
        except (PermissionError, OSError, FileNotFoundError) as err:
            last_err = err
            # If the file genuinely doesn't exist after 5 quick retries (~15ms), raise immediately
            if isinstance(err, FileNotFoundError) and attempt >= 5:
                raise err
            if attempt == max_retries - 1:
                break
            backoff = min(max_delay, base_delay * (1.35 ** min(attempt, 10)))
            jitter = random.uniform(0.001, 0.008)
            time.sleep(backoff + jitter)

    if last_err is not None:
        raise last_err
    raise FileNotFoundError(f"Failed to read file after {max_retries} attempts: {target}")


def atomic_read_json(
    path: Union[str, Path],
    encoding: str = "utf-8",
    max_retries: int = 30,
    base_delay: float = 0.002,
    max_delay: float = 0.08,
    default: Any = _UNSET,
) -> Any:
    """Read and parse JSON from a file with exponential backoff and jitter on Windows sharing violations."""
    target = os.path.abspath(str(path))
    last_err: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            with open(target, "r", encoding=encoding) as f:
                raw = f.read()
            if not raw.strip():
                # Caught during transient atomic replace window
                if attempt < max_retries - 1:
                    raise ValueError("Empty file read during atomic replace race")
                if default is not _UNSET:
                    return default
                raise json.JSONDecodeError("Expecting value from empty file", raw, 0)
            return json.loads(raw)
        except (PermissionError, OSError, FileNotFoundError, json.JSONDecodeError, ValueError) as err:
            last_err = err
            if isinstance(err, FileNotFoundError):
                if default is not _UNSET and attempt >= 2:
                    return default
                if attempt >= 5:
                    if default is not _UNSET:
                        return default
                    raise err
            if attempt == max_retries - 1:
                break
            backoff = min(max_delay, base_delay * (1.35 ** min(attempt, 10)))
            jitter = random.uniform(0.001, 0.008)
            time.sleep(backoff + jitter)

    if default is not _UNSET:
        return default
    if last_err is not None:
        raise last_err
    raise FileNotFoundError(f"Failed to read JSON after {max_retries} attempts: {target}")
```

### 4.2 Proposed Updates to `development/shared_core/runtime.py`
Add `atomic_read_json` and `atomic_read_text` to the imported and exported symbols:
```python
from .persistence import (
    atomic_write_json,
    atomic_write_text,
    atomic_read_json,
    atomic_read_text,
    atomic_copy,
    atomic_write_zip,
)
```

### 4.3 Proposed Updates to `development/shared_core/__init__.py`
Include `atomic_read_json` and `atomic_read_text` in imports and `__all__`:
```python
from .runtime import (
    canonical_data_root,
    resolve_payload_root,
    resolve_prism_root,
    ensure_dpi_awareness,
    center_process_window,
    atomic_write_json,
    atomic_write_text,
    atomic_read_json,
    atomic_read_text,
    atomic_copy,
    atomic_write_zip,
    download_file_resilient,
    download_files_batch,
    DownloadProgressTracker,
)

__all__ = [
    "canonical_data_root",
    "resolve_payload_root",
    "resolve_prism_root",
    "ensure_dpi_awareness",
    "center_process_window",
    "atomic_write_json",
    "atomic_write_text",
    "atomic_read_json",
    "atomic_read_text",
    "atomic_copy",
    "atomic_write_zip",
    "download_file_resilient",
    "download_files_batch",
    "DownloadProgressTracker",
]
```

### 4.4 Proposed Reader Updates in Test Suites
In `tests/test_adversarial_m1.py` (lines 490–518) and `tests/test_challenger_stress_m1.py` (lines 210–230), update reader workers to use `atomic_read_json(target)`:
```python
def _reader(reader_id):
    nonlocal successful_reads
    while not stop_event.is_set():
        try:
            data = atomic_read_json(target, max_retries=30)
            if data is not None:
                if not isinstance(data, dict) or ("worker_id" not in data and "init" not in data):
                    with read_lock:
                        read_errors.append((reader_id, "Corrupted structure", data))
                else:
                    with read_lock:
                        successful_reads += 1
        except Exception as ex:
            with read_lock:
                read_errors.append((reader_id, f"Unexpected read error: {ex}"))
        time.sleep(0.0005)
```

---

## 5. Verification Method

1. **Verify Adversarial Multithreaded Atomic Write/Read Race**:
   ```pwsh
   python -m unittest tests/test_adversarial_m1.py -k test_concurrent_multithreaded_atomic_write_race -v
   ```
   **Pass Condition**: 20 writers and 10 readers complete with 0 write errors and 0 read errors.

2. **Verify Challenger Multithreaded Concurrency**:
   ```pwsh
   python -m unittest tests/test_challenger_stress_m1.py -k test_concurrent_multi_threaded_atomic_json_writers_and_readers -v
   ```
   **Pass Condition**: 20 writers and 10 readers execute with 0 corruption events and >200 writes / >300 reads validated.

3. **Execute Full Test Discovery**:
   ```pwsh
   python -m unittest discover -s tests -p "test_*.py"
   ```
   **Pass Condition**: All 81 tests pass with 0 failures and 0 errors (`OK`).
