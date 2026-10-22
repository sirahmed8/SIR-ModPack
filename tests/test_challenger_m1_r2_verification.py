"""
test_challenger_m1_r2_verification.py — Empirical Challenger Verification Suite for Milestone 1 Round 2.

Exhaustively challenges:
1. atomic_read_json and atomic_write_json under heavy multi-threaded concurrency (50+ threads on Windows NTFS).
2. download_file_resilient against sudden socket drops (multi-drop, 0-byte drop, premature EOF), corrupted byte payloads, and Range recovery.
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
    _get_path_lock,
)

from shared_core.downloader import (
    download_file_resilient,
    download_files_batch,
    is_retryable_network_error,
)


# ============================================================================
# Adversarial Mock Server for Socket Cuts & Byte Corruptions
# ============================================================================

class AdversarialChaosServer(http.server.BaseHTTPRequestHandler):
    payloads: Dict[str, bytes] = {}
    drop_counts: Dict[str, int] = {}
    max_drops: Dict[str, int] = {}
    drop_mode: Dict[str, str] = {}  # "mid_stream", "zero_byte", "premature_eof", "corrupt_data"
    ignore_range: set = set()

    def log_message(self, format: str, *args: Any) -> None:
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
        mode = self.drop_mode.get(clean_path, "none")
        curr_drops = self.drop_counts.get(clean_path, 0)
        max_drops = self.max_drops.get(clean_path, 0)

        range_header = self.headers.get("Range")
        is_range_req = bool(range_header and clean_path not in self.ignore_range)

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

        # Apply corruption if mode is corrupt_data
        if mode == "corrupt_data":
            # Tamper the middle bytes
            tampered = bytearray(chunk_data)
            if len(tampered) > 10:
                tampered[5:10] = b"\xFF\xFF\xFF\xFF\xFF"
            chunk_data = bytes(tampered)

        # Check if we should drop this request
        if curr_drops < max_drops:
            self.drop_counts[clean_path] = curr_drops + 1
            if mode == "zero_byte":
                # Close immediately without sending any chunk bytes
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                except Exception:
                    pass
                return

            elif mode == "premature_eof":
                # Send 30% of bytes then close normally without raising socket error
                send_len = max(1, int(chunk_len * 0.3))
                self.wfile.write(chunk_data[:send_len])
                self.wfile.flush()
                try:
                    self.connection.close()
                except Exception:
                    pass
                return

            else:  # default mid_stream cut
                send_len = max(1, int(chunk_len * 0.45))
                self.wfile.write(chunk_data[:send_len])
                self.wfile.flush()
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                except Exception:
                    pass
                return

        # Clean delivery
        self.wfile.write(chunk_data)
        self.wfile.flush()


# ============================================================================
# Test Cases
# ============================================================================

class TestMilestone1Round2Challenger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload_1mb = os.urandom(1024 * 1024)
        cls.payload_3mb = os.urandom(3 * 1024 * 1024)

        AdversarialChaosServer.payloads = {
            "test_1mb.bin": cls.payload_1mb,
            "test_3mb.bin": cls.payload_3mb,
        }

        cls.httpd = socketserver.TCPServer(("127.0.0.1", 0), AdversarialChaosServer)
        cls.port = cls.httpd.server_address[1]
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir-m1r2-challenger-")
        AdversarialChaosServer.drop_counts.clear()
        AdversarialChaosServer.max_drops.clear()
        AdversarialChaosServer.drop_mode.clear()
        AdversarialChaosServer.ignore_range.clear()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ------------------------------------------------------------------------
    # Part 1: Atomic Persistence Stress Under 50+ Multi-Threaded Workers
    # ------------------------------------------------------------------------

    def test_heavy_concurrency_json_persistence_70_threads(self):
        """
        Adversarial Challenge: 35 concurrent writer threads + 35 concurrent reader threads
        (70 active threads total) hammering a single JSON file on Windows NTFS.
        Verifies:
        - ZERO writer exceptions (sharing violations or lock collisions).
        - ZERO reader exceptions (corrupt JSON, partial read, or decode error).
        - Valid data integrity maintained across all 70 threads.
        """
        target_file = os.path.join(self.test_dir, "heavy_concurrency.json")
        atomic_write_json(target_file, {"seed": 0, "status": "initialized"})

        num_writers = 35
        num_readers = 35
        stop_event = threading.Event()
        writer_errors: List[Exception] = []
        reader_errors: List[Exception] = []
        successful_writes = [0]
        successful_reads = [0]
        lock = threading.Lock()

        def writer_task(writer_id: int):
            for it in range(25):
                if stop_event.is_set():
                    break
                payload = {
                    "writer_id": writer_id,
                    "iteration": it,
                    "timestamp": time.time(),
                    "data": {
                        "metrics": [random.randint(1, 1000) for _ in range(30)],
                        "label": f"worker_{writer_id}_iter_{it}",
                        "unicode_text": "اختبار_التزامن_SIR_Launcher_✓",
                    },
                }
                try:
                    atomic_write_json(target_file, payload, max_retries=60)
                    with lock:
                        successful_writes[0] += 1
                except Exception as ex:
                    with lock:
                        writer_errors.append(ex)
                time.sleep(random.uniform(0.001, 0.004))

        def reader_task(reader_id: int):
            while not stop_event.is_set():
                try:
                    data = atomic_read_json(target_file, max_retries=60)
                    self.assertIsInstance(data, dict)
                    self.assertTrue("writer_id" in data or "seed" in data)
                    with lock:
                        successful_reads[0] += 1
                except Exception as ex:
                    with lock:
                        reader_errors.append(ex)
                time.sleep(random.uniform(0.0005, 0.002))

        writers = [threading.Thread(target=writer_task, args=(i,)) for i in range(num_writers)]
        readers = [threading.Thread(target=reader_task, args=(i,)) for i in range(num_readers)]

        for r in readers:
            r.start()
        for w in writers:
            w.start()

        for w in writers:
            w.join(timeout=15.0)

        stop_event.set()
        for r in readers:
            r.join(timeout=5.0)

        self.assertEqual(len(writer_errors), 0, f"Writer errors encountered: {writer_errors[:5]}")
        self.assertEqual(len(reader_errors), 0, f"Reader errors encountered: {reader_errors[:5]}")
        self.assertGreater(successful_writes[0], 500, "Should have performed >500 successful atomic writes")
        self.assertGreater(successful_reads[0], 500, "Should have performed >500 successful atomic reads")

        # Final check
        final_data = atomic_read_json(target_file)
        self.assertIn("writer_id", final_data)

    def test_heavy_concurrency_text_persistence_60_threads_with_checksum(self):
        """
        Adversarial Challenge: 30 writer threads + 30 reader threads (60 threads)
        writing and reading text files with embedded SHA-256 header validation.
        """
        target_file = os.path.join(self.test_dir, "options_stress.txt")
        initial_body = "gamma:1.0\nrenderDistance:12\n"
        initial_header = f"##CHECKSUM:{hashlib.sha256(initial_body.encode()).hexdigest()}\n"
        atomic_write_text(target_file, initial_header + initial_body)

        stop_event = threading.Event()
        writer_errors: List[Exception] = []
        reader_errors: List[Exception] = []
        successful_reads = [0]
        lock = threading.Lock()

        def writer_task(wid: int):
            for i in range(20):
                if stop_event.is_set():
                    break
                body = f"worker={wid}\niteration={i}\nnoise={'a'*200}\n"
                checksum = hashlib.sha256(body.encode()).hexdigest()
                content = f"##CHECKSUM:{checksum}\n{body}"
                try:
                    atomic_write_text(target_file, content, max_retries=60)
                except Exception as ex:
                    with lock:
                        writer_errors.append(ex)
                time.sleep(random.uniform(0.001, 0.003))

        def reader_task():
            while not stop_event.is_set():
                try:
                    raw = atomic_read_text(target_file, max_retries=60)
                    lines = raw.splitlines(keepends=True)
                    if lines and lines[0].startswith("##CHECKSUM:"):
                        expected_hash = lines[0].strip().split(":")[1]
                        body = "".join(lines[1:])
                        calc_hash = hashlib.sha256(body.encode()).hexdigest()
                        self.assertEqual(calc_hash, expected_hash)
                        with lock:
                            successful_reads[0] += 1
                except Exception as ex:
                    with lock:
                        reader_errors.append(ex)
                time.sleep(0.001)

        writers = [threading.Thread(target=writer_task, args=(i,)) for i in range(30)]
        readers = [threading.Thread(target=reader_task) for _ in range(30)]

        for r in readers:
            r.start()
        for w in writers:
            w.start()

        for w in writers:
            w.join(timeout=15.0)

        stop_event.set()
        for r in readers:
            r.join(timeout=5.0)

        self.assertEqual(len(writer_errors), 0, f"Writer errors: {writer_errors}")
        self.assertEqual(len(reader_errors), 0, f"Reader checksum/read errors: {reader_errors}")
        self.assertGreater(successful_reads[0], 200)

    def test_case_insensitive_path_locking_on_windows(self):
        """
        Adversarial Challenge: Simultaneous writes and reads across mixed uppercase and lowercase
        paths on Windows must share the exact same synchronization lock.
        """
        if sys.platform != "win32":
            self.skipTest("Case-insensitive path locking is Windows NTFS-specific")
        lower_path = os.path.join(self.test_dir, "matrix_case.json").lower()
        upper_path = os.path.join(self.test_dir, "MATRIX_CASE.JSON").upper()

        lock_lower = _get_path_lock(lower_path)
        lock_upper = _get_path_lock(upper_path)

        self.assertIs(lock_lower, lock_upper, "Path locks must be identical regardless of Windows casing")

    def test_concurrent_readers_on_nonexistent_file_with_default(self):
        """
        Adversarial Challenge: 50 threads concurrently attempting to read a nonexistent JSON file
        with a fallback default dictionary.
        """
        missing_path = os.path.join(self.test_dir, "does_not_exist.json")
        default_obj = {"status": "fallback_default", "items": []}

        def worker():
            res = atomic_read_json(missing_path, default=default_obj, max_retries=5)
            self.assertEqual(res, default_obj)

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as pool:
            futures = [pool.submit(worker) for _ in range(50)]
            for f in concurrent.futures.as_completed(futures):
                f.result()

    # ------------------------------------------------------------------------
    # Part 2: Resilient Downloader Chaos & Corruption Challenges
    # ------------------------------------------------------------------------

    def test_downloader_recovers_from_multiple_sudden_socket_disconnects(self):
        """
        Adversarial Challenge: 3 consecutive sudden socket cuts during a 3MB download.
        Downloader must execute 3 Range resumption attempts, receive 206 responses,
        and assemble a byte-for-byte exact 3MB payload matching expected SHA-256.
        """
        path_name = "test_3mb.bin"
        url = f"http://127.0.0.1:{self.port}/{path_name}"
        dest_file = os.path.join(self.test_dir, "resumed_3mb.bin")

        expected_data = self.payload_3mb
        expected_sha256 = hashlib.sha256(expected_data).hexdigest()

        AdversarialChaosServer.max_drops[path_name] = 3
        AdversarialChaosServer.drop_mode[path_name] = "mid_stream"

        success = download_file_resilient(
            url=url,
            dest_path=dest_file,
            expected_sha256=expected_sha256,
            max_retries=5,
            chunk_size=32 * 1024,
            timeout=5.0,
        )

        self.assertTrue(success)
        self.assertTrue(os.path.isfile(dest_file))
        self.assertEqual(AdversarialChaosServer.drop_counts[path_name], 3)

        with open(dest_file, "rb") as f:
            downloaded_bytes = f.read()
        self.assertEqual(len(downloaded_bytes), len(expected_data))
        self.assertEqual(hashlib.sha256(downloaded_bytes).hexdigest(), expected_sha256)

    def test_downloader_zero_byte_socket_close(self):
        """
        Adversarial Challenge: Server accepts connection, sends HTTP headers, but closes socket
        before a single body byte is transmitted (0 bytes received).
        Downloader must catch retryable network error, back off, and complete download on retry.
        """
        path_name = "test_1mb.bin"
        url = f"http://127.0.0.1:{self.port}/{path_name}"
        dest_file = os.path.join(self.test_dir, "zero_byte_recovered.bin")

        expected_data = self.payload_1mb
        expected_sha256 = hashlib.sha256(expected_data).hexdigest()

        AdversarialChaosServer.max_drops[path_name] = 1
        AdversarialChaosServer.drop_mode[path_name] = "zero_byte"

        success = download_file_resilient(
            url=url,
            dest_path=dest_file,
            expected_sha256=expected_sha256,
            max_retries=3,
        )

        self.assertTrue(success)
        with open(dest_file, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), expected_sha256)

    def test_downloader_premature_eof_empty_read_recovery(self):
        """
        Adversarial Challenge: Server sends 30% of content and then cleanly closes without error,
        returning b'' from resp.read() before Content-Length is reached.
        Downloader must raise ConnectionResetError, trigger backoff, issue Range resume, and finish.
        """
        path_name = "test_1mb.bin"
        url = f"http://127.0.0.1:{self.port}/{path_name}"
        dest_file = os.path.join(self.test_dir, "premature_eof_recovered.bin")

        expected_data = self.payload_1mb
        expected_sha256 = hashlib.sha256(expected_data).hexdigest()

        AdversarialChaosServer.max_drops[path_name] = 1
        AdversarialChaosServer.drop_mode[path_name] = "premature_eof"

        success = download_file_resilient(
            url=url,
            dest_path=dest_file,
            expected_sha256=expected_sha256,
            max_retries=3,
        )

        self.assertTrue(success)
        with open(dest_file, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), expected_sha256)

    def test_downloader_tampered_bytes_sha256_rejection_and_cleanup(self):
        """
        Adversarial Challenge: Server transmits tampered bytes (corrupted payload).
        Downloader must calculate SHA-256, raise ValueError, remove .part file,
        and leave NO corrupted destination file on disk.
        """
        path_name = "test_1mb.bin"
        url = f"http://127.0.0.1:{self.port}/{path_name}"
        dest_file = os.path.join(self.test_dir, "corrupted_payload.bin")

        expected_sha256 = hashlib.sha256(self.payload_1mb).hexdigest()

        AdversarialChaosServer.max_drops[path_name] = 0
        AdversarialChaosServer.drop_mode[path_name] = "corrupt_data"

        with self.assertRaises(ValueError) as ctx:
            download_file_resilient(
                url=url,
                dest_path=dest_file,
                expected_sha256=expected_sha256,
                max_retries=2,
            )

        self.assertIn("SHA-256 mismatch", str(ctx.exception))
        self.assertFalse(os.path.exists(dest_file), "Corrupted file must never be created at dest")

        part_files = [f for f in os.listdir(self.test_dir) if ".part-" in f]
        self.assertEqual(len(part_files), 0, "Corrupted .part file must be cleaned up")


if __name__ == "__main__":
    unittest.main(verbosity=2)
