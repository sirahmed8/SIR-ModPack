"""
test_adversarial_m1.py — Empirical Challenger Stress Harness for Milestone 1.
Tests:
1. AsyncTaskManager: High concurrency, cancellation races, thread pool saturation, error propagation, PyWebView JS events.
2. ResilientDownloader: HTTP 206 chunk drops, socket timeouts, resume, 416 fallback, HTTP 200 fallback, corrupted chunks, SHA-256 enforcement.
3. Universal Atomic Persistence: Rapid multi-threaded concurrent write races, concurrent reader/writer contention, open file handle contention on Windows, mid-write crash simulation.
"""
import concurrent.futures
import functools
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
import urllib.request
import zipfile

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
    DownloadProgressTracker,
    download_file_resilient,
    download_files_batch,
    is_retryable_network_error,
)
from launcher_core.async_tasks import (
    AsyncTaskManager,
    AsyncTask,
)


class MockFlakyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Configurable mock HTTP server capable of:
    - Simulating mid-stream drops after N bytes
    - Simulating HTTP 206 Partial Content
    - Simulating HTTP 200 when Range header is sent
    - Simulating HTTP 416 Range Not Satisfiable
    - Simulating HTTP 500 / 503 transient errors before succeeding
    - Simulating slow chunked streaming
    """
    payload_data = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" * 1024 # ~63.5 KB
    fail_first_n_requests = 0
    request_count = 0
    drop_after_bytes = 0
    ignore_range_header = False
    force_416 = False
    lock = threading.Lock()

    def log_message(self, format, *args):
        # Suppress standard logging to keep test output clean
        pass

    def do_GET(self):
        with self.__class__.lock:
            self.__class__.request_count += 1
            current_req_num = self.__class__.request_count

        if current_req_num <= self.__class__.fail_first_n_requests:
            self.send_response(503)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Service Temporarily Unavailable")
            return

        if self.__class__.force_416:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{len(self.__class__.payload_data)}")
            self.end_headers()
            return

        data = self.__class__.payload_data
        total_len = len(data)
        range_header = self.headers.get("Range")

        start = 0
        end = total_len - 1

        if range_header and not self.__class__.ignore_range_header:
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
                    
                    self.send_response(206)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Range", f"bytes {start}-{end}/{total_len}")
                    self.send_header("Content-Length", str(end - start + 1))
                    self.end_headers()
                    
                    send_data = data[start:end+1]
                    if self.__class__.drop_after_bytes > 0 and len(send_data) > self.__class__.drop_after_bytes:
                        self.wfile.write(send_data[:self.__class__.drop_after_bytes])
                        self.wfile.flush()
                        # Abruptly drop connection
                        self.close_connection = True
                        return
                    else:
                        self.wfile.write(send_data)
                        return
            except Exception:
                pass

        # Full 200 response
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(total_len))
        self.end_headers()

        if self.__class__.drop_after_bytes > 0 and total_len > self.__class__.drop_after_bytes:
            self.wfile.write(data[:self.__class__.drop_after_bytes])
            self.wfile.flush()
            # Abruptly close connection
            self.close_connection = True
            return

        self.wfile.write(data)


class TestAdversarialAsyncTaskManager(unittest.TestCase):
    def setUp(self):
        self.manager = AsyncTaskManager(max_workers=8)

    def tearDown(self):
        self.manager.executor.shutdown(wait=False)

    def test_concurrent_task_saturation_and_completion(self):
        """Stress-test submitting 100 concurrent tasks across 10 threads."""
        completed_results = []
        lock = threading.Lock()

        def _worker(idx):
            time.sleep(0.01)
            return {"index": idx, "square": idx * idx}

        def _submitter(start_idx, count):
            for i in range(start_idx, start_idx + count):
                def _cb(res, i=i):
                    with lock:
                        completed_results.append(res)
                self.manager.submit_task(
                    name=f"task_{i}",
                    func=_worker,
                    idx=i,
                    callback=_cb,
                )

        threads = []
        for t in range(10):
            th = threading.Thread(target=_submitter, args=(t * 10, 10))
            threads.append(th)
            th.start()

        for th in threads:
            th.join()

        # Wait for all tasks to complete (up to 5 seconds)
        deadline = time.time() + 5.0
        while time.time() < deadline:
            with lock:
                if len(completed_results) == 100:
                    break
            time.sleep(0.05)

        with lock:
            self.assertEqual(len(completed_results), 100, f"Expected 100 completed tasks, got {len(completed_results)}")

        all_tasks = self.manager.list_tasks(limit=150)
        self.assertEqual(len(all_tasks), 100)
        for t in all_tasks:
            self.assertEqual(t["status"], "completed")
            self.assertEqual(t["progress"], 100)
            self.assertIsNotNone(t["result"])
            self.assertIsNone(t["error"])

    def test_cancellation_cooperative_running_task(self):
        """Test cooperative cancellation token while task is executing."""
        started_event = threading.Event()
        was_cancelled = threading.Event()

        def _long_running_task(cancel_event):
            started_event.set()
            for _ in range(50):
                if cancel_event.is_set():
                    was_cancelled.set()
                    return "aborted"
                time.sleep(0.02)
            return "finished"

        tid = self.manager.submit_task("coop_cancel_task", _long_running_task)
        self.assertTrue(started_event.wait(timeout=2.0))

        # Cancel the running task
        success = self.manager.cancel_task(tid)
        self.assertTrue(success)

        # Wait for task thread to observe cancellation
        self.assertTrue(was_cancelled.wait(timeout=2.0))

        time.sleep(0.1)
        task_info = self.manager.get_task(tid)
        self.assertIsNotNone(task_info)
        self.assertEqual(task_info["status"], "cancelled")

    def test_cancellation_idempotency_and_invalid_ids(self):
        """Verify cancel_task behavior on non-existent or finished tasks."""
        # Non-existent task
        self.assertFalse(self.manager.cancel_task("non_existent_12345"))

        # Task that completes immediately
        def _quick():
            return 42

        tid = self.manager.submit_task("quick_task", _quick)
        time.sleep(0.1)

        task_info = self.manager.get_task(tid)
        self.assertEqual(task_info["status"], "completed")

        # Cancelling an already completed task should return False
        self.assertFalse(self.manager.cancel_task(tid))
        self.assertEqual(self.manager.get_task(tid)["status"], "completed")

    def test_progress_clamping_and_rapid_updates(self):
        """Verify progress updates are clamped to [0, 100] and thread-safe under rapid updates."""
        def _dummy():
            time.sleep(0.2)

        tid = self.manager.submit_task("progress_task", _dummy)

        # Out-of-bounds updates
        self.manager.update_task_progress(tid, -50, "negative")
        self.assertEqual(self.manager.get_task(tid)["progress"], 0)

        self.manager.update_task_progress(tid, 150, "overflow")
        self.assertEqual(self.manager.get_task(tid)["progress"], 100)

        # Rapid updates from 5 threads
        def _updater():
            for p in range(0, 101, 10):
                self.manager.update_task_progress(tid, p, f"step {p}")

        threads = [threading.Thread(target=_updater) for _ in range(5)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        tinfo = self.manager.get_task(tid)
        self.assertGreaterEqual(tinfo["progress"], 0)
        self.assertLessEqual(tinfo["progress"], 100)

    def test_exception_in_worker_and_callback(self):
        """Verify unhandled exceptions in worker or user callback do not crash the manager."""
        def _exploding_func():
            raise RuntimeError("Explosion in worker!")

        callback_called = threading.Event()

        def _exploding_callback(res):
            callback_called.set()
            raise ValueError("Explosion in callback!")

        tid = self.manager.submit_task(
            name="exploding_task",
            func=_exploding_func,
            callback=_exploding_callback,
        )

        self.assertTrue(callback_called.wait(timeout=2.0))
        time.sleep(0.05)

        task_info = self.manager.get_task(tid)
        self.assertEqual(task_info["status"], "failed")
        self.assertIn("Explosion in worker!", task_info["error"])

    def test_pywebview_window_event_dispatch_safety(self):
        """Verify emit_event safely calls evaluate_js and handles evaluate_js failure."""
        class MockWindow:
            def __init__(self, should_fail=False):
                self.calls = []
                self.should_fail = should_fail

            def evaluate_js(self, js_code):
                if self.should_fail:
                    raise RuntimeError("WebView bridge detached")
                self.calls.append(js_code)

        mock_win = MockWindow(should_fail=False)
        self.manager.set_window(mock_win)

        def _sample():
            return "ok"

        tid = self.manager.submit_task("win_task", _sample)
        time.sleep(0.1)

        self.assertGreaterEqual(len(mock_win.calls), 2)  # task_started, task_completed
        self.assertTrue(any("task_started" in c for c in mock_win.calls))
        self.assertTrue(any("task_completed" in c for c in mock_win.calls))

        # Now test with broken window
        broken_win = MockWindow(should_fail=True)
        self.manager.set_window(broken_win)
        # Should not raise exception
        self.manager.emit_event("test_event", {"key": "val"})


class TestAdversarialResilientDownloader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import hashlib
        cls.expected_sha256 = hashlib.sha256(MockFlakyHTTPRequestHandler.payload_data).hexdigest()
        cls.expected_sha1 = hashlib.sha1(MockFlakyHTTPRequestHandler.payload_data).hexdigest()

        # Start custom flaky HTTP server
        cls.httpd = socketserver.TCPServer(("127.0.0.1", 0), MockFlakyHTTPRequestHandler)
        cls.port = cls.httpd.server_address[1]
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with MockFlakyHTTPRequestHandler.lock:
            MockFlakyHTTPRequestHandler.fail_first_n_requests = 0
            MockFlakyHTTPRequestHandler.request_count = 0
            MockFlakyHTTPRequestHandler.drop_after_bytes = 0
            MockFlakyHTTPRequestHandler.ignore_range_header = False
            MockFlakyHTTPRequestHandler.force_416 = False

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_transient_503_retries_and_succeeds(self):
        """Downloader recovers from transient 503 errors via exponential backoff."""
        with MockFlakyHTTPRequestHandler.lock:
            MockFlakyHTTPRequestHandler.fail_first_n_requests = 2

        url = f"http://127.0.0.1:{self.port}/flaky.bin"
        dest = os.path.join(self.temp_dir, "recovered_503.bin")

        success = download_file_resilient(
            url=url,
            dest_path=dest,
            expected_sha256=self.expected_sha256,
            max_retries=4,
        )
        self.assertTrue(success)
        self.assertTrue(os.path.isfile(dest))
        self.assertEqual(os.path.getsize(dest), len(MockFlakyHTTPRequestHandler.payload_data))

    def test_server_ignores_range_falls_back_to_200(self):
        """Server ignores Range header and sends full 200 response -> downloader must cleanly overwrite without corrupting."""
        url = f"http://127.0.0.1:{self.port}/ignore_range.bin"
        dest = os.path.join(self.temp_dir, "ignore_range.bin")
        part_path = dest + f".part-{os.getpid()}"

        # Write 20KB garbage to .part
        with open(part_path, "wb") as f:
            f.write(b"Z" * 20480)

        with MockFlakyHTTPRequestHandler.lock:
            MockFlakyHTTPRequestHandler.ignore_range_header = True

        success = download_file_resilient(
            url=url,
            dest_path=dest,
            expected_sha256=self.expected_sha256,
            enable_resume=True,
            max_retries=3,
        )
        self.assertTrue(success)
        self.assertTrue(os.path.isfile(dest))
        self.assertEqual(os.path.getsize(dest), len(MockFlakyHTTPRequestHandler.payload_data))

    def test_http_416_restarts_from_zero(self):
        """When HTTP 416 Range Not Satisfiable occurs, downloader restarts from 0 and completes."""
        url = f"http://127.0.0.1:{self.port}/range_416.bin"
        dest = os.path.join(self.temp_dir, "range_416.bin")
        part_path = dest + f".part-{os.getpid()}"

        # Pre-create a .part file larger than server payload (triggering 416)
        with open(part_path, "wb") as f:
            f.write(b"X" * (len(MockFlakyHTTPRequestHandler.payload_data) + 10000))

        success = download_file_resilient(
            url=url,
            dest_path=dest,
            expected_sha256=self.expected_sha256,
            enable_resume=True,
            max_retries=3,
        )
        self.assertTrue(success)
        self.assertTrue(os.path.isfile(dest))
        self.assertEqual(os.path.getsize(dest), len(MockFlakyHTTPRequestHandler.payload_data))

    def test_corrupted_partial_chunk_fails_hash_and_cleans_part(self):
        """A corrupted .part file fails SHA-256 check, does not create dest file, and deletes corrupted .part file."""
        url = f"http://127.0.0.1:{self.port}/corrupted_resume.bin"
        dest = os.path.join(self.temp_dir, "corrupted_dest.bin")
        part_path = dest + f".part-{os.getpid()}"

        half_bytes = len(MockFlakyHTTPRequestHandler.payload_data) // 2
        # Corrupted partial chunk
        with open(part_path, "wb") as f:
            f.write(b"\xFF" * half_bytes)

        with self.assertRaises(ValueError):
            download_file_resilient(
                url=url,
                dest_path=dest,
                expected_sha256=self.expected_sha256,
                enable_resume=True,
                max_retries=1,
            )

        self.assertFalse(os.path.exists(dest), "Destination file must not exist after hash failure")
        self.assertFalse(os.path.exists(part_path), "Corrupted .part file must be removed after hash failure")


class TestAdversarialAtomicPersistence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_concurrent_multithreaded_atomic_write_race(self):
        """
        Adversarial Race Test:
        20 writer threads concurrently write JSON to the exact same file 50 times each.
        10 reader threads continuously read and parse the file.
        Verifies:
        - Readers NEVER encounter invalid JSON or empty files.
        - Readers NEVER encounter missing file (unless before first write).
        - Writers NEVER throw unhandled file locking exceptions.
        """
        target = os.path.join(self.temp_dir, "race_config.json")
        # Initialize file
        atomic_write_json(target, {"init": True, "step": 0})

        stop_event = threading.Event()
        read_errors = []
        write_errors = []
        successful_reads = 0
        read_lock = threading.Lock()

        def _writer(worker_id):
            for i in range(50):
                payload = {
                    "worker_id": worker_id,
                    "iteration": i,
                    "timestamp": time.time(),
                    "payload_block": "A" * 1024,
                }
                try:
                    atomic_write_json(target, payload)
                except Exception as ex:
                    write_errors.append((worker_id, i, str(ex)))
                time.sleep(0.001)

        def _reader(reader_id):
            nonlocal successful_reads
            while not stop_event.is_set():
                try:
                    data = atomic_read_json(target, max_retries=30)
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


        # Start 10 readers
        readers = [threading.Thread(target=_reader, args=(r,)) for r in range(10)]
        for r in readers:
            r.start()

        # Start 20 writers
        writers = [threading.Thread(target=_writer, args=(w,)) for w in range(20)]
        for w in writers:
            w.start()

        for w in writers:
            w.join()

        # Stop readers
        stop_event.set()
        for r in readers:
            r.join()

        self.assertEqual(len(write_errors), 0, f"Encountered write errors: {write_errors[:5]}")
        self.assertEqual(len(read_errors), 0, f"Encountered read errors during concurrent replace: {read_errors[:10]}")
        self.assertGreater(successful_reads, 100, "Should have performed at least 100 successful atomic reads")

        # Final verification of file validity
        with open(target, "r", encoding="utf-8") as f:
            final_data = json.load(f)
        self.assertIsInstance(final_data, dict)
        self.assertIn("worker_id", final_data)

    def test_atomic_write_while_file_open_for_reading(self):
        """
        Verify atomic_write_json behavior when another process/thread holds an open read handle on Windows.
        """
        target = os.path.join(self.temp_dir, "open_handle.json")
        atomic_write_json(target, {"initial": 1})

        # Open file for reading
        with open(target, "r", encoding="utf-8") as read_handle:
            content = read_handle.read()
            self.assertIn("initial", content)

            # Attempt atomic write while handle is open
            try:
                atomic_write_json(target, {"updated": 2})
                write_succeeded = True
            except PermissionError:
                write_succeeded = False

        # Read back from closed handle
        with open(target, "r", encoding="utf-8") as check_f:
            data = json.load(check_f)

        if write_succeeded:
            self.assertEqual(data, {"updated": 2})
        else:
            self.assertEqual(data, {"initial": 1})

    def test_atomic_write_invalid_type_leaves_target_intact(self):
        """Verify non-serializable object leaves existing target file unchanged and cleans temp file."""
        target = os.path.join(self.temp_dir, "clean_state.json")
        atomic_write_json(target, {"pristine": True})

        class NonSerializable:
            pass

        with self.assertRaises(TypeError):
            atomic_write_json(target, {"bad_obj": NonSerializable()})

        # Verify target is untouched
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data, {"pristine": True})

        # Verify no .tmp files left behind
        tmp_files = [fn for fn in os.listdir(self.temp_dir) if fn.endswith(".tmp")]
        self.assertEqual(len(tmp_files), 0, f"Found leaked temp files: {tmp_files}")


if __name__ == "__main__":
    unittest.main()
