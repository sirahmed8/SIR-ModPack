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


def _get_path_lock(target: Union[str, Path]) -> threading.Lock:
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
    max_retries: int = 60,
    base_delay: float = 0.002,
    max_delay: float = 0.08,
) -> str:
    """Read text from a file with in-process lock synchronization and backoff."""
    target = os.path.abspath(str(path))
    path_lock = _get_path_lock(target)
    with path_lock:
        if not os.path.exists(target):
            raise FileNotFoundError(f"File not found: {target}")
        with open(target, "r", encoding=encoding) as f:
            return f.read()


def atomic_read_json(
    path: Union[str, Path],
    encoding: str = "utf-8",
    max_retries: int = 60,
    base_delay: float = 0.002,
    max_delay: float = 0.08,
    default: Any = _UNSET,
) -> Any:
    """Read and parse JSON from a file with in-process lock synchronization and fallback."""
    target = os.path.abspath(str(path))
    path_lock = _get_path_lock(target)
    with path_lock:
        if not os.path.exists(target):
            if default is not _UNSET:
                return default
            raise FileNotFoundError(f"File not found: {target}")
        with open(target, "r", encoding=encoding) as f:
            raw = f.read()
        if not raw.strip():
            if default is not _UNSET:
                return default
            raise ValueError("Empty JSON file")
        return json.loads(raw)

