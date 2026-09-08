"""
downloader.py — High-Throughput Resilient Chunked Stream Downloader.
Features HTTP Range resume (206 Partial Content), exponential backoff with jitter,
streaming SHA-256 / SHA-1 checksum verification, and batch parallel downloads.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import os
import random
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


class DownloadProgressTracker:
    """Thread-safe progress and smoothed speed calculator."""

    def __init__(
        self,
        total_bytes: int = 0,
        callback: Optional[Callable[[int, int, int, float], None]] = None,
        min_interval_sec: float = 0.05,
    ):
        self.total_bytes = max(0, total_bytes)
        self.downloaded_bytes = 0
        self.callback = callback
        self.min_interval_sec = min_interval_sec
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_downloaded = 0
        self.current_speed = 0.0
        self._lock = threading.Lock()

    def update(self, chunk_len: int) -> None:
        with self._lock:
            self.downloaded_bytes += chunk_len
            now = time.time()
            elapsed_since_update = now - self.last_update_time
            if (
                elapsed_since_update >= self.min_interval_sec
                or (self.total_bytes > 0 and self.downloaded_bytes >= self.total_bytes)
            ):
                delta_bytes = self.downloaded_bytes - self.last_downloaded
                instant_speed = delta_bytes / max(0.001, elapsed_since_update)
                self.current_speed = (
                    (0.7 * instant_speed) + (0.3 * self.current_speed)
                    if self.current_speed > 0
                    else instant_speed
                )
                self.last_update_time = now
                self.last_downloaded = self.downloaded_bytes

                if self.callback:
                    pct = (
                        min(100, max(0, int((self.downloaded_bytes / self.total_bytes) * 100)))
                        if self.total_bytes > 0
                        else 0
                    )
                    try:
                        # Support callbacks with 3 or 4 arguments (pct, downloaded, total, [speed])
                        try:
                            self.callback(pct, self.downloaded_bytes, self.total_bytes, self.current_speed)  # type: ignore
                        except TypeError:
                            self.callback(pct, self.downloaded_bytes, self.total_bytes)  # type: ignore
                    except Exception:
                        pass

    def finish(self) -> None:
        with self._lock:
            if self.callback:
                tot = self.total_bytes if self.total_bytes > 0 else self.downloaded_bytes
                try:
                    try:
                        self.callback(100, tot, tot, self.current_speed)  # type: ignore
                    except TypeError:
                        self.callback(100, tot, tot)  # type: ignore
                except Exception:
                    pass


import http.client

def is_retryable_network_error(exc: Exception) -> bool:
    """Classifies whether an exception is transient and eligible for backoff retry."""
    if isinstance(exc, (socket.timeout, TimeoutError, ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError, OSError, EOFError, http.client.HTTPException)):
        return True
    if isinstance(exc, urllib.error.HTTPError):
        # 408 Request Timeout, 429 Too Many Requests, 500/502/503/504 Server Errors
        return exc.code in (408, 429, 500, 502, 503, 504)
    if isinstance(exc, urllib.error.URLError):
        return True
    return False


def download_file_resilient(
    url: str,
    dest_path: Union[str, Path],
    progress_callback: Optional[Callable[..., None]] = None,
    expected_sha256: Optional[str] = None,
    expected_sha1: Optional[str] = None,
    max_retries: int = 4,
    chunk_size: int = 128 * 1024,
    user_agent: str = "SIR-ModPack/1.0.0 (contact@sirmodpack.org)",
    timeout: float = 20.0,
    enable_resume: bool = True,
) -> bool:
    """
    Resilient chunked stream downloader with HTTP Range resumption, exponential backoff,
    streaming hash verification, and atomic file replacement.
    """
    dest_target = os.path.abspath(str(dest_path))
    dest_dir = os.path.dirname(dest_target)
    os.makedirs(dest_dir, exist_ok=True)

    temp_path = dest_target + f".part-{os.getpid()}"
    last_error: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            existing_bytes = 0
            if enable_resume and os.path.exists(temp_path):
                try:
                    existing_bytes = os.path.getsize(temp_path)
                except OSError:
                    existing_bytes = 0

            req_headers = {"User-Agent": user_agent}
            if existing_bytes > 0:
                req_headers["Range"] = f"bytes={existing_bytes}-"

            req = urllib.request.Request(url, headers=req_headers)

            try:
                resp = urllib.request.urlopen(req, timeout=timeout)
            except urllib.error.HTTPError as http_err:
                if http_err.code == 416:  # Range Not Satisfiable -> Restart from 0
                    existing_bytes = 0
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except OSError:
                            pass
                    req_headers.pop("Range", None)
                    req = urllib.request.Request(url, headers=req_headers)
                    resp = urllib.request.urlopen(req, timeout=timeout)
                else:
                    raise http_err

            with resp:
                status_code = getattr(resp, "status", getattr(resp, "code", 200))
                content_len_hdr = resp.headers.get("Content-Length")
                content_len = int(content_len_hdr) if content_len_hdr and content_len_hdr.isdigit() else 0
                content_range_hdr = resp.headers.get("Content-Range", "")

                # Check if server honored Range header
                is_partial = (status_code == 206) or (existing_bytes > 0 and bool(content_range_hdr))
                if is_partial and existing_bytes > 0:
                    total_bytes = existing_bytes + content_len if content_len > 0 else 0
                    file_mode = "ab"
                else:
                    total_bytes = content_len
                    existing_bytes = 0
                    file_mode = "wb"

                tracker = DownloadProgressTracker(
                    total_bytes=total_bytes, callback=progress_callback
                )
                if existing_bytes > 0:
                    tracker.update(existing_bytes)

                stream_bytes_read = 0
                with open(temp_path, file_mode) as f_out:
                    try:
                        while True:
                            chunk = resp.read(chunk_size)
                            if not chunk:
                                if content_len > 0 and stream_bytes_read < content_len:
                                    raise ConnectionResetError(
                                        f"Premature stream termination: received {stream_bytes_read} of {content_len} bytes from current HTTP stream"
                                    )
                                break
                            stream_bytes_read += len(chunk)
                            f_out.write(chunk)
                            tracker.update(len(chunk))
                    except http.client.IncompleteRead as inc_err:
                        if getattr(inc_err, "partial", None):
                            f_out.write(inc_err.partial)
                            tracker.update(len(inc_err.partial))
                        f_out.flush()
                        raise inc_err
                    finally:
                        f_out.flush()
                        try:
                            os.fsync(f_out.fileno())
                        except OSError:
                            pass

                # Check for truncated stream
                current_written = os.path.getsize(temp_path) if os.path.exists(temp_path) else 0
                if total_bytes > 0 and current_written < total_bytes:
                    raise ConnectionResetError(
                        f"Connection truncated prematurely: written {current_written} of expected {total_bytes} bytes"
                    )


            # Full file cryptographic validation before atomic rename
            if expected_sha256 or expected_sha1:
                hasher_256 = hashlib.sha256() if expected_sha256 else None
                hasher_1 = hashlib.sha1() if expected_sha1 else None

                with open(temp_path, "rb") as check_f:
                    while True:
                        buf = check_f.read(256 * 1024)
                        if not buf:
                            break
                        if hasher_256:
                            hasher_256.update(buf)
                        if hasher_1:
                            hasher_1.update(buf)

                if expected_sha256 and hasher_256:
                    calc_256 = hasher_256.hexdigest().lower()
                    if calc_256 != expected_sha256.lower():
                        raise ValueError(
                            f"SHA-256 mismatch for {dest_target}: expected {expected_sha256}, got {calc_256}"
                        )

                if expected_sha1 and hasher_1:
                    calc_1 = hasher_1.hexdigest().lower()
                    if calc_1 != expected_sha1.lower():
                        raise ValueError(
                            f"SHA-1 mismatch for {dest_target}: expected {expected_sha1}, got {calc_1}"
                        )

            # Atomic replace into final destination
            if os.path.exists(temp_path):
                from shared_core.persistence import _atomic_replace_with_retry
                _atomic_replace_with_retry(temp_path, dest_target)
                tracker.finish()
                return True

        except Exception as ex:
            last_error = ex
            # If checksum error or non-retryable error, clean corrupted .part file
            if isinstance(ex, ValueError) or not is_retryable_network_error(ex):
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

            if attempt < max_retries and is_retryable_network_error(ex):
                backoff = min(8.0, 0.5 * (2 ** (attempt - 1)) + random.uniform(0.05, 0.25))
                time.sleep(backoff)
            else:
                if os.path.exists(temp_path) and not is_retryable_network_error(ex):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass
                break

    if last_error:
        raise last_error
    return False


def download_files_batch(
    items: List[Dict[str, Any]],
    max_workers: int = 8,
    progress_callback: Optional[Callable[[int, int, int, str], None]] = None,
) -> Dict[str, Any]:
    """
    Concurrent worker pool for batch downloading libraries, mods, or assets.
    Each item dict should have: 'url', 'dest', optional 'sha1', optional 'sha256'.
    """
    total_count = len(items)
    if total_count == 0:
        return {"success": True, "downloaded": 0, "failed": 0, "errors": []}

    completed_count = 0
    failed_items: List[Dict[str, Any]] = []
    lock = threading.Lock()

    def _worker(item: Dict[str, Any]) -> bool:
        nonlocal completed_count
        url = item.get("url")
        dest = item.get("dest")
        sha1 = item.get("sha1")
        sha256 = item.get("sha256")
        name = os.path.basename(str(dest))

        if not url or not dest:
            with lock:
                failed_items.append({"item": item, "error": "Missing url or dest"})
            return False

        try:
            download_file_resilient(url, dest, expected_sha1=sha1, expected_sha256=sha256)
            with lock:
                completed_count += 1
                if progress_callback:
                    pct = int((completed_count / total_count) * 100)
                    try:
                        progress_callback(completed_count, total_count, pct, name)
                    except Exception:
                        pass
            return True
        except Exception as err:
            with lock:
                failed_items.append({"item": item, "error": str(err)})
            return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_worker, item) for item in items]
        concurrent.futures.wait(futures)

    return {
        "success": len(failed_items) == 0,
        "downloaded": completed_count,
        "failed": len(failed_items),
        "errors": failed_items,
    }
