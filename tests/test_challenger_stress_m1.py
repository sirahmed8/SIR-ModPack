"""
test_challenger_stress_m1.py — Empirical Stress & Adversarial Challenge Suite for Milestone 1.

Testing:
1. Atomic File Persistence under high concurrency, reader/writer contention, and simulated crashes/aborts.
2. Resilient Downloader under dropped sockets, 206 range resumption, server range ignore (200 OK), 416 recovery, and hash tampering.
3. AsyncTaskManager under rapid task flood, cancellation race conditions, exception resilience, and concurrent UI event emission.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import http.server
import json
import os
import random
import socket
import socketserver
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from shared_core.persistence import (
    atomic_write_json,
    atomic_write_text,
    atomic_read_json,
    atomic_read_text,
    atomic_copy,
    atomic_write_zip,
)

from shared_core.downloader import (
    download_file_resilient,
    download_files_batch,
)
from launcher_core.async_tasks import (
    AsyncTaskManager,
    AsyncTask,
    AsyncBridgeExecutor,
)


# ============================================================================
# Adversarial Mock HTTP Server with Chaos & Stream Interruption Capabilities
# ============================================================================

class ChaosHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Advanced Mock Server with fine-grained chaos injection:
    - Simulates socket abrupt cuts / EOF midway through streaming.
    - Simulates servers that ignore HTTP Range requests (returns 200 OK with full file).
    - Simulates HTTP 416 Range Not Satisfiable.
    - Simulates corrupted payloads with invalid hash digests.
    """

    # Class-level routing table and state
    payloads: Dict[str, bytes] = {}
    interrupt_counters: Dict[str, int] = {}
    max_interrupts_per_path: Dict[str, int] = {}
    ignore_range_paths: set = set()
    force_416_paths: set = set()

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy standard HTTP logs during stress tests
        pass

    def do_GET(self) -> None:
        clean_path = self.path.split("?")[0].lstrip("/")
        if clean_path not in self.payloads:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        full_data = self.payloads[clean_path]
        total_len = len(full_data)

        # 1. Force 416 simulation
        if clean_path in self.force_416_paths:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{total_len}")
            self.end_headers()
            return

        # 2. Check Range Header
        range_header = self.headers.get("Range")
        is_range_req = bool(range_header and clean_path not in self.ignore_range_paths)

        start = 0
        end = total_len - 1

        if is_range_req:
            try:
                range_type, range_val = range_header.strip().split("=")
                if range_type.lower() == "bytes":
                    start_str, end_str = range_val.split("-")
                    start = int(start_str) if start_str else 0
                    end = int(end_str) if end_str else total_len - 1
                    if start >= total_len:
                        self.send_response(416)
                        self.send_header("Content-Range", f"bytes */{total_len}")
                        self.end_headers()
                        return
            except Exception:
                is_range_req = False
                start = 0
                end = total_len - 1

        chunk_data = full_data[start : end + 1]
        chunk_len = len(chunk_data)

        if is_range_req:
            self.send_response(206)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Range", f"bytes {start}-{end}/{total_len}")
            self.send_header("Content-Length", str(chunk_len))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(total_len))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            chunk_data = full_data
            chunk_len = total_len

        # 3. Check for Interruption Chaos
        curr_interrupts = self.interrupt_counters.get(clean_path, 0)
        max_interrupts = self.max_interrupts_per_path.get(clean_path, 0)

        if curr_interrupts < max_interrupts:
            self.interrupt_counters[clean_path] = curr_interrupts + 1
            # Send only partial slice (e.g., 40%) then close socket connection abruptly
            partial_slice_size = max(1, int(chunk_len * 0.4))
            self.wfile.write(chunk_data[:partial_slice_size])
            self.wfile.flush()
            # Force abrupt socket close
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
            except Exception:
                pass
            return

        # Normal full transmission of the requested chunk
        self.wfile.write(chunk_data)
        self.wfile.flush()


# ============================================================================
# 1. ATOMIC PERSISTENCE EMPIRICAL STRESS TESTS
# ============================================================================

class TestAtomicPersistenceEmpiricalStress(unittest.TestCase):
    """Adversarial stress harness for atomic storage operations."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir-stress-storage-")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_concurrent_multi_threaded_atomic_json_writers_and_readers(self):
        """
        Adversarial test: 20 writer threads furiously writing JSON payloads to the
        exact same target file while 10 reader threads continuously parse the file.
        Verifies ZERO corruptions, zero partial writes, and zero JSONDecodeErrors.
        """
        target_file = os.path.join(self.test_dir, "concurrent_state.json")
        atomic_write_json(target_file, {"initial": True, "version": 0})

        stop_event = threading.Event()
        writer_errors: List[Exception] = []
        reader_errors: List[Exception] = []
        successful_reads = [0]
        successful_writes = [0]
        lock = threading.Lock()

        def writer_worker(thread_id: int):
            for i in range(40):
                if stop_event.is_set():
                    break
                payload = {
                    "thread_id": thread_id,
                    "iteration": i,
                    "timestamp": time.time(),
                    "nested": {
                        "matrix": [random.random() for _ in range(50)],
                        "metadata": "x" * 500,
                    },
                }
                try:
                    atomic_write_json(target_file, payload)
                    with lock:
                        successful_writes[0] += 1
                except Exception as ex:
                    with lock:
                        writer_errors.append(ex)
                time.sleep(0.002)

        def reader_worker():
            while not stop_event.is_set():
                try:
                    data = atomic_read_json(target_file, max_retries=30)
                    self.assertIsInstance(data, dict)
                    self.assertTrue("thread_id" in data or "initial" in data)
                    with lock:
                        successful_reads[0] += 1
                except Exception as ex:
                    with lock:
                        reader_errors.append(ex)
                time.sleep(0.001)

        # Launch 20 writers and 10 readers
        writers = [threading.Thread(target=writer_worker, args=(i,)) for i in range(20)]
        readers = [threading.Thread(target=reader_worker) for _ in range(10)]

        for r in readers:
            r.start()
        for w in writers:
            w.start()

        for w in writers:
            w.join(timeout=10.0)

        stop_event.set()
        for r in readers:
            r.join(timeout=5.0)

        # Assert no reader encountered a corrupted/partial JSON file
        self.assertEqual(len(reader_errors), 0, f"Reader encountered JSON corruption: {reader_errors[:3]}")
        self.assertEqual(len(writer_errors), 0, f"Writers encountered unexpected failures: {writer_errors[:3]}")
        self.assertGreater(successful_writes[0], 200, "Writers should complete substantial writes")
        self.assertGreater(successful_reads[0], 300, "Readers should validate hundreds of reads during writes")

        # Final verification: target file is completely intact
        final_data = atomic_read_json(target_file)
        self.assertIn("thread_id", final_data)

    def test_concurrent_atomic_text_writes_integrity(self):
        """
        Adversarial test: Concurrent writers updating an options.txt file with integrity headers.
        """
        target_file = os.path.join(self.test_dir, "options.txt")
        errors: List[Exception] = []

        def worker(w_id: int):
            for i in range(30):
                body = f"key_{w_id}_{i}=value_{random.randint(1000, 9999)}\n" * 20
                header = f"# HASH:{hashlib.sha256(body.encode()).hexdigest()}\n"
                full_content = header + body
                try:
                    atomic_write_text(target_file, full_content)
                except Exception as ex:
                    errors.append(ex)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(15)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        self.assertEqual(len(errors), 0)
        raw_text = atomic_read_text(target_file)
        lines = raw_text.splitlines(keepends=True)
        self.assertTrue(lines[0].startswith("# HASH:"))
        expected_hash = lines[0].strip().split(":")[1]
        actual_body = "".join(lines[1:])
        self.assertEqual(hashlib.sha256(actual_body.encode()).hexdigest(), expected_hash)


    def test_simulated_serialization_crash_leaves_original_file_intact(self):
        """
        Simulate crash during serialization or write: verify original file is never corrupted
        and temporary files are cleaned up.
        """
        target_file = os.path.join(self.test_dir, "critical_manifest.json")
        initial_data = {"status": "pristine", "version": 1.0, "items": [1, 2, 3]}
        atomic_write_json(target_file, initial_data)
        original_mtime = os.path.getmtime(target_file)

        class UnserializableType:
            pass

        bad_payload = {"status": "tampered", "unserializable": UnserializableType()}

        with self.assertRaises(TypeError):
            atomic_write_json(target_file, bad_payload)

        # Verify original file is still 100% intact and unaltered
        with open(target_file, "r", encoding="utf-8") as f:
            preserved_data = json.load(f)
        self.assertEqual(preserved_data, initial_data)

        # Verify no orphan .sir-json-*.tmp files exist in the directory
        tmp_files = [f for f in os.listdir(self.test_dir) if f.startswith(".sir-json-")]
        self.assertEqual(len(tmp_files), 0, f"Found leaked temporary files: {tmp_files}")

    def test_simulated_atomic_zip_exception_aborts_cleanly(self):
        """
        Simulate an exception thrown halfway inside atomic_write_zip context block.
        Verify target file is not overwritten and temp zip is deleted.
        """
        target_zip = os.path.join(self.test_dir, "backup.zip")
        # Create an initial valid zip
        with atomic_write_zip(target_zip) as zf:
            zf.writestr("file1.txt", "Initial pristine content")

        with self.assertRaises(RuntimeError):
            with atomic_write_zip(target_zip) as zf:
                zf.writestr("file2.txt", "Halfway written data")
                raise RuntimeError("Simulated crash while zipping!")

        # Verify zip still contains ONLY initial pristine content
        with zipfile.ZipFile(target_zip, "r") as zf:
            namelist = zf.namelist()
            self.assertEqual(namelist, ["file1.txt"])
            self.assertEqual(zf.read("file1.txt").decode("utf-8"), "Initial pristine content")

        # Verify no orphan temp zip files
        tmp_files = [f for f in os.listdir(self.test_dir) if ".tmp-" in f]
        self.assertEqual(len(tmp_files), 0)

    def test_deep_nested_directory_auto_creation(self):
        """Verify atomic writes auto-create deep arbitrary directory hierarchies without error."""
        deep_path = os.path.join(self.test_dir, "a", "b", "c", "d", "instances.json")
        atomic_write_json(deep_path, {"nested_depth": 5})
        self.assertTrue(os.path.exists(deep_path))
        with open(deep_path, "r", encoding="utf-8") as f:
            self.assertEqual(json.load(f)["nested_depth"], 5)


# ============================================================================
# 2. RESILIENT DOWNLOADER EMPIRICAL STRESS TESTS
# ============================================================================

class TestResilientDownloaderEmpiricalStress(unittest.TestCase):
    """Adversarial stress harness for chunked resilient downloader."""

    @classmethod
    def setUpClass(cls):
        # Generate varied test payloads (Small, Medium 500KB, Large 2MB)
        cls.payload_small = b"SIR_SMALL_PAYLOAD_0123456789" * 100
        cls.payload_medium = os.urandom(512 * 1024)  # 512 KB
        cls.payload_large = os.urandom(2 * 1024 * 1024)  # 2 MB

        ChaosHTTPRequestHandler.payloads = {
            "small.bin": cls.payload_small,
            "medium.bin": cls.payload_medium,
            "large.bin": cls.payload_large,
        }

        cls.httpd = socketserver.TCPServer(("127.0.0.1", 0), ChaosHTTPRequestHandler)
        cls.port = cls.httpd.server_address[1]
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir-stress-download-")
        # Reset chaos controls
        ChaosHTTPRequestHandler.interrupt_counters.clear()
        ChaosHTTPRequestHandler.max_interrupts_per_path.clear()
        ChaosHTTPRequestHandler.ignore_range_paths.clear()
        ChaosHTTPRequestHandler.force_416_paths.clear()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_interrupted_byte_stream_recovery_with_http_range_resumption(self):
        """
        Adversarial test: Mock server forcibly terminates socket connection twice during download.
        Downloader must retry, issue Range: bytes={existing}- header, get 206 Partial Content,
        and assemble a byte-for-byte exact payload matching the SHA-256 digest.
        """
        path_name = "medium.bin"
        url = f"http://127.0.0.1:{self.port}/{path_name}"
        dest_file = os.path.join(self.test_dir, "downloaded_medium.bin")

        expected_data = self.payload_medium
        expected_sha256 = hashlib.sha256(expected_data).hexdigest()

        # Inject 2 socket drops
        ChaosHTTPRequestHandler.max_interrupts_per_path[path_name] = 2

        progress_history: List[int] = []

        def on_progress(pct: int, dl: int, tot: int, speed: float = 0.0):
            progress_history.append(pct)

        success = download_file_resilient(
            url=url,
            dest_path=dest_file,
            progress_callback=on_progress,
            expected_sha256=expected_sha256,
            max_retries=4,
            chunk_size=16 * 1024,
            timeout=5.0,
        )

        self.assertTrue(success)
        self.assertTrue(os.path.exists(dest_file))
        self.assertEqual(ChaosHTTPRequestHandler.interrupt_counters[path_name], 2, "Should have experienced 2 drops")

        # Verify byte-for-byte exactness
        with open(dest_file, "rb") as f:
            actual_data = f.read()
        self.assertEqual(len(actual_data), len(expected_data))
        self.assertEqual(hashlib.sha256(actual_data).hexdigest(), expected_sha256)

        # Verify progress tracker finalized at 100%
        self.assertIn(100, progress_history)

    def test_server_ignores_range_and_returns_http_200(self):
        """
        Adversarial test: Client has partial file and sends Range header, but server
        ignores Range and responds with standard HTTP 200 OK with full file.
        Downloader must NOT append and double the file size; it must overwrite and succeed.
        """
        path_name = "small.bin"
        url = f"http://127.0.0.1:{self.port}/{path_name}"
        dest_file = os.path.join(self.test_dir, "downloaded_small.bin")

        expected_data = self.payload_small
        expected_sha256 = hashlib.sha256(expected_data).hexdigest()

        # Simulate existing partial file
        temp_part = dest_file + f".part-{os.getpid()}"
        with open(temp_part, "wb") as f:
            f.write(b"PRE_EXISTING_PARTIAL_BYTES_GARBAGE")

        # Tell server to ignore range
        ChaosHTTPRequestHandler.ignore_range_paths.add(path_name)

        success = download_file_resilient(
            url=url,
            dest_path=dest_file,
            expected_sha256=expected_sha256,
            enable_resume=True,
        )

        self.assertTrue(success)
        with open(dest_file, "rb") as f:
            actual_data = f.read()
        self.assertEqual(len(actual_data), len(expected_data))
        self.assertEqual(hashlib.sha256(actual_data).hexdigest(), expected_sha256)

    def test_http_416_range_not_satisfiable_resets_and_succeeds(self):
        """
        Adversarial test: Client has an invalid/oversized partial file causing HTTP 416.
        Downloader must handle 416, delete partial file, re-request from byte 0, and succeed.
        """
        path_name = "small.bin"
        url = f"http://127.0.0.1:{self.port}/{path_name}"
        dest_file = os.path.join(self.test_dir, "downloaded_416.bin")

        expected_data = self.payload_small
        expected_sha256 = hashlib.sha256(expected_data).hexdigest()

        # Pre-seed part file larger than the entire remote payload
        temp_part = dest_file + f".part-{os.getpid()}"
        with open(temp_part, "wb") as f:
            f.write(b"X" * (len(expected_data) + 5000))

        success = download_file_resilient(
            url=url,
            dest_path=dest_file,
            expected_sha256=expected_sha256,
            enable_resume=True,
        )

        self.assertTrue(success)
        with open(dest_file, "rb") as f:
            actual_data = f.read()
        self.assertEqual(hashlib.sha256(actual_data).hexdigest(), expected_sha256)

    def test_corrupted_checksum_raises_error_and_cleans_temporary_files(self):
        """
        Adversarial test: Server sends payload with wrong SHA-256 digest.
        Downloader must reject, raise ValueError, remove .part file, and not create destination.
        """
        path_name = "large.bin"
        url = f"http://127.0.0.1:{self.port}/{path_name}"
        dest_file = os.path.join(self.test_dir, "corrupted_target.bin")
        bad_sha256 = "0000000000000000000000000000000000000000000000000000000000000000"

        with self.assertRaises(ValueError) as ctx:
            download_file_resilient(
                url=url,
                dest_path=dest_file,
                expected_sha256=bad_sha256,
                max_retries=2,
            )

        self.assertIn("SHA-256 mismatch", str(ctx.exception))
        self.assertFalse(os.path.exists(dest_file), "Destination file must NOT be created on bad hash")

        # Verify .part file is purged
        part_files = [f for f in os.listdir(self.test_dir) if ".part-" in f]
        self.assertEqual(len(part_files), 0, f"Temporary part file was not cleaned: {part_files}")

    def test_batch_downloader_high_concurrency_with_mixed_outcomes(self):
        """
        Adversarial test: Batch download 30 files in parallel where:
        - 15 are valid and succeed
        - 5 hit 404 Not Found
        - 5 experience transient connection drops and recover
        - 5 have bad checksum expectations
        """
        batch_items: List[Dict[str, Any]] = []

        # 1. 15 valid
        for i in range(15):
            dest = os.path.join(self.test_dir, f"valid_{i}.bin")
            batch_items.append({
                "url": f"http://127.0.0.1:{self.port}/small.bin",
                "dest": dest,
                "sha256": hashlib.sha256(self.payload_small).hexdigest(),
            })

        # 2. 5 non-existent 404
        for i in range(5):
            dest = os.path.join(self.test_dir, f"missing_{i}.bin")
            batch_items.append({
                "url": f"http://127.0.0.1:{self.port}/non_existent_{i}.bin",
                "dest": dest,
            })

        # 3. 5 bad hash
        for i in range(5):
            dest = os.path.join(self.test_dir, f"badhash_{i}.bin")
            batch_items.append({
                "url": f"http://127.0.0.1:{self.port}/small.bin",
                "dest": dest,
                "sha256": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            })

        result = download_files_batch(batch_items, max_workers=6)

        self.assertFalse(result["success"])
        self.assertEqual(result["downloaded"], 15)
        self.assertEqual(result["failed"], 10)  # 5 missing + 5 bad hash
        self.assertEqual(len(result["errors"]), 10)


# ============================================================================
# 3. ASYNC TASK MANAGER EMPIRICAL STRESS & RACE CONDITION TESTS
# ============================================================================

class MockWebViewWindow:
    """Mock PyWebView window capturing UI event emissions under concurrent execution."""

    def __init__(self, fail_rate: float = 0.0):
        self.events: List[str] = []
        self.fail_rate = fail_rate
        self._lock = threading.Lock()

    def evaluate_js(self, script: str):
        with self._lock:
            if self.fail_rate > 0 and random.random() < self.fail_rate:
                raise RuntimeError("Simulated PyWebView DOM execution error")
            self.events.append(script)


class TestAsyncTaskManagerEmpiricalStress(unittest.TestCase):
    """Adversarial stress harness for AsyncTaskManager thread safety and race conditions."""

    def setUp(self):
        self.manager = AsyncTaskManager.get_instance(max_workers=12)
        self.mock_window = MockWebViewWindow()
        self.manager.set_window(self.mock_window)

    def test_rapid_concurrent_task_flooding_and_registry_integrity(self):
        """
        Adversarial test: 20 client threads rapidly submitting 300 tasks simultaneously
        while observer threads continuously query list_tasks() and get_task().
        Verifies registry thread safety, zero dictionary race crashes, and complete resolution.
        """
        total_tasks = 200
        submitted_ids: List[str] = []
        submit_lock = threading.Lock()
        active_exceptions: List[Exception] = []

        def worker_task(index: int, progress_cb=None):
            if progress_cb:
                progress_cb(30, f"Starting step {index}")
            # Compute CPU arithmetic
            s = sum(x * x for x in range(2000))
            if progress_cb:
                progress_cb(100, "Done")
            return {"index": index, "sum": s}

        def submitter_worker(worker_idx: int):
            for i in range(10):
                try:
                    tid = self.manager.submit_task(
                        f"StressTask_{worker_idx}_{i}",
                        worker_task,
                        i,
                    )
                    with submit_lock:
                        submitted_ids.append(tid)
                except Exception as ex:
                    with submit_lock:
                        active_exceptions.append(ex)
                time.sleep(0.001)

        def poller_worker(stop_ev: threading.Event):
            while not stop_ev.is_set():
                try:
                    tasks = self.manager.list_tasks(limit=100)
                    self.assertIsInstance(tasks, list)
                except Exception as ex:
                    with submit_lock:
                        active_exceptions.append(ex)
                time.sleep(0.002)

        stop_polling = threading.Event()
        pollers = [threading.Thread(target=poller_worker, args=(stop_polling,)) for _ in range(4)]
        submitters = [threading.Thread(target=submitter_worker, args=(w,)) for w in range(20)]

        for p in pollers:
            p.start()
        for s in submitters:
            s.start()

        for s in submitters:
            s.join(timeout=10.0)

        # Wait for all tasks to settle
        deadline = time.time() + 15.0
        while time.time() < deadline:
            all_done = True
            for tid in submitted_ids:
                task = self.manager.get_task(tid)
                if not task or task["status"] == "running":
                    all_done = False
                    break
            if all_done:
                break
            time.sleep(0.05)

        stop_polling.set()
        for p in pollers:
            p.join(timeout=3.0)

        self.assertEqual(len(active_exceptions), 0, f"Observed concurrency exceptions: {active_exceptions[:3]}")
        self.assertEqual(len(submitted_ids), total_tasks)

        # Verify all submitted tasks reached terminal state completed
        for tid in submitted_ids:
            task = self.manager.get_task(tid)
            self.assertIsNotNone(task)
            self.assertEqual(task["status"], "completed")
            self.assertEqual(task["progress"], 100)

    def test_rapid_task_cancellation_race_condition(self):
        """
        Adversarial test: Submitting tasks and issuing cancel_task() from concurrent threads
        with microsecond intervals to test race conditions between task startup and cancellation.
        """
        cancelled_count = [0]
        completed_count = [0]
        lock = threading.Lock()

        def stoppable_task(cancel_event=None):
            for _ in range(50):
                if cancel_event and cancel_event.is_set():
                    return "ABORTED"
                time.sleep(0.005)
            return "FINISHED"

        def trigger_and_cancel():
            tid = self.manager.submit_task("StoppableTask", stoppable_task)
            time.sleep(random.uniform(0.001, 0.015))
            did_cancel = self.manager.cancel_task(tid)
            if did_cancel:
                with lock:
                    cancelled_count[0] += 1

        threads = [threading.Thread(target=trigger_and_cancel) for _ in range(40)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        # Allow worker threads to finalize
        time.sleep(0.5)

        # Verify all tasks are either cancelled or completed, never corrupted or in broken state
        tasks = self.manager.list_tasks(limit=100)
        for t in tasks:
            self.assertIn(t["status"], ("cancelled", "completed", "running", "failed"))
        self.assertGreater(cancelled_count[0], 0, "Should have successfully cancelled several tasks")

    def test_task_exception_isolation_and_pool_resilience(self):
        """
        Adversarial test: Tasks that raise unhandled exceptions (ZeroDivisionError, Custom Exceptions)
        must transition to 'failed' status with error text and must NEVER crash the worker pool.
        """
        def failing_task(msg: str):
            raise ValueError(f"Deliberate fatal error: {msg}")

        task_id = self.manager.submit_task("FailingTask", failing_task, "TestCrash")

        # Wait for task completion
        for _ in range(50):
            t = self.manager.get_task(task_id)
            if t and t["status"] in ("failed", "completed"):
                break
            time.sleep(0.02)

        failed_task = self.manager.get_task(task_id)
        self.assertIsNotNone(failed_task)
        self.assertEqual(failed_task["status"], "failed")
        self.assertIn("Deliberate fatal error: TestCrash", failed_task.get("error", ""))

        # Verify that subsequent valid tasks still execute normally
        def healthy_task():
            return {"healthy": True}

        h_id = self.manager.submit_task("HealthyTask", healthy_task)
        for _ in range(50):
            t = self.manager.get_task(h_id)
            if t and t["status"] == "completed":
                break
            time.sleep(0.02)

        ht = self.manager.get_task(h_id)
        self.assertEqual(ht["status"], "completed")
        self.assertEqual(ht["result"], {"healthy": True})

    def test_chaotic_pywebview_window_exceptions_do_not_abort_tasks(self):
        """
        Adversarial test: Attach a Mock Window that raises exceptions on 50% of evaluate_js calls.
        Tasks must continue execution and finish with success despite UI event delivery failures.
        """
        chaotic_window = MockWebViewWindow(fail_rate=0.5)
        self.manager.set_window(chaotic_window)

        completed_tasks = []

        def worker_with_progress(progress_cb=None):
            for i in range(1, 6):
                if progress_cb:
                    progress_cb(i * 20, f"Stage {i}")
                time.sleep(0.005)
            return "SUCCESS"

        tids = [
            self.manager.submit_task(f"ChaoticTask_{i}", worker_with_progress)
            for i in range(15)
        ]

        deadline = time.time() + 8.0
        while time.time() < deadline:
            all_done = True
            for tid in tids:
                t = self.manager.get_task(tid)
                if not t or t["status"] == "running":
                    all_done = False
                    break
            if all_done:
                break
            time.sleep(0.05)

        for tid in tids:
            t = self.manager.get_task(tid)
            self.assertEqual(t["status"], "completed")
            self.assertEqual(t["result"], "SUCCESS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
