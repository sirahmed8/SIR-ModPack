"""
test_atomic_persistence.py — Comprehensive Tests for Atomic Persistence & Resilient Downloader.
"""
import http.server
import json
import os
import socketserver
import sys
import tempfile
import threading
import time
import unittest
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
)
from launcher_core.controls_service import ControlsService
from launcher_core.packs_service import PacksService
from launcher_core.shaders_service import ShadersService
from launcher_core.skin_studio_service import SkinStudioService
from launcher_core.export_service import ExportService
from launcher_core.worlds_service import WorldsService


class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Local test HTTP server supporting HTTP Range 206 Partial Content headers."""

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()

        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()

        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        fs = os.fstat(f.fileno())
        total_len = fs.st_size

        try:
            range_type, range_val = range_header.strip().split("=")
            if range_type.lower() != "bytes":
                return super().send_head()

            start_str, end_str = range_val.split("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else total_len - 1
            if start >= total_len:
                self.send_error(416, "Requested Range Not Satisfiable")
                f.close()
                return None

            length = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Range", f"bytes {start}-{end}/{total_len}")
            self.send_header("Content-Length", str(length))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            f.seek(start)
            return f
        except Exception:
            f.close()
            return super().send_head()


class TestAtomicPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.serve_dir = tempfile.mkdtemp()
        # Create test payload for local HTTP server
        cls.test_payload_data = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" * 1024  # ~36 KB
        cls.test_payload_file = os.path.join(cls.serve_dir, "payload.bin")
        with open(cls.test_payload_file, "wb") as f:
            f.write(cls.test_payload_data)

        # Compute expected hashes
        import hashlib
        cls.expected_sha256 = hashlib.sha256(cls.test_payload_data).hexdigest()
        cls.expected_sha1 = hashlib.sha1(cls.test_payload_data).hexdigest()

        # Start local range HTTP server on ephemeral port
        handler = lambda *args, **kwargs: RangeHTTPRequestHandler(*args, directory=cls.serve_dir, **kwargs)
        cls.httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
        cls.port = cls.httpd.server_address[1]
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        import shutil
        shutil.rmtree(cls.serve_dir, ignore_errors=True)

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_atomic_write_json(self):
        target = os.path.join(self.temp_dir, "test.json")
        payload = {"version": "26.2", "ram": 8, "profiles": ["ultra", "pvp"]}
        atomic_write_json(target, payload)
        self.assertTrue(os.path.isfile(target))
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data, payload)

    def test_atomic_write_text(self):
        target = os.path.join(self.temp_dir, "options.txt")
        content = "biomeBlendRadius:7\ngraphicsMode:2\nmaxFps:0\n"
        atomic_write_text(target, content)
        self.assertTrue(os.path.isfile(target))
        with open(target, "r", encoding="utf-8") as f:
            read_back = f.read()
        self.assertEqual(read_back, content)

    def test_atomic_copy(self):
        src = os.path.join(self.temp_dir, "source.txt")
        dst = os.path.join(self.temp_dir, "sub", "dest.txt")
        atomic_write_text(src, "Testing atomic file copy mechanism.")
        atomic_copy(src, dst)
        self.assertTrue(os.path.isfile(dst))
        with open(dst, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "Testing atomic file copy mechanism.")

    def test_atomic_write_zip(self):
        target_zip = os.path.join(self.temp_dir, "archive.zip")
        with atomic_write_zip(target_zip) as zf:
            zf.writestr("test.txt", "Sample zip entry content")
            zf.writestr("data/config.json", json.dumps({"active": True}))

        self.assertTrue(os.path.isfile(target_zip))
        with zipfile.ZipFile(target_zip, "r") as check_zf:
            self.assertIsNone(check_zf.testzip())
            self.assertIn("test.txt", check_zf.namelist())
            self.assertIn("data/config.json", check_zf.namelist())

    def test_atomic_overwrite_no_data_loss(self):
        target = os.path.join(self.temp_dir, "state.json")
        atomic_write_json(target, {"step": 1})
        atomic_write_json(target, {"step": 2})
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data, {"step": 2})

    def test_atomic_read_json_valid(self):
        target = os.path.join(self.temp_dir, "read_test.json")
        payload = {"launcher": "SIR", "version": "1.21.4", "threads": 8}
        atomic_write_json(target, payload)
        read_data = atomic_read_json(target)
        self.assertEqual(read_data, payload)

    def test_atomic_read_json_nonexistent_with_default(self):
        target = os.path.join(self.temp_dir, "missing.json")
        default_val = {"status": "default"}
        data = atomic_read_json(target, max_retries=2, default=default_val)
        self.assertEqual(data, default_val)

    def test_atomic_read_json_nonexistent_raises(self):
        target = os.path.join(self.temp_dir, "nonexistent.json")
        with self.assertRaises((FileNotFoundError, OSError)):
            atomic_read_json(target, max_retries=2)

    def test_atomic_read_text_valid(self):
        target = os.path.join(self.temp_dir, "read_test.txt")
        content = "graphicsMode:fast\nfullscreen:true\n"
        atomic_write_text(target, content)
        read_text = atomic_read_text(target)
        self.assertEqual(read_text, content)


    def test_download_file_resilient_full(self):
        url = f"http://127.0.0.1:{self.port}/payload.bin"
        dest = os.path.join(self.temp_dir, "downloaded.bin")
        progress_events = []

        def on_prog(pct, downloaded, total, speed=0.0):
            progress_events.append((pct, downloaded, total))

        success = download_file_resilient(
            url=url,
            dest_path=dest,
            progress_callback=on_prog,
            expected_sha256=self.expected_sha256,
            expected_sha1=self.expected_sha1,
        )
        self.assertTrue(success)
        self.assertTrue(os.path.isfile(dest))
        self.assertEqual(os.path.getsize(dest), len(self.test_payload_data))
        self.assertGreater(len(progress_events), 0)
        self.assertEqual(progress_events[-1][0], 100)

    def test_download_file_resilient_range_resume(self):
        url = f"http://127.0.0.1:{self.port}/payload.bin"
        dest = os.path.join(self.temp_dir, "resumed.bin")
        part_path = dest + f".part-{os.getpid()}"

        # Pre-create 50% of the partial download file
        half_bytes = len(self.test_payload_data) // 2
        with open(part_path, "wb") as f:
            f.write(self.test_payload_data[:half_bytes])

        self.assertTrue(os.path.exists(part_path))
        self.assertEqual(os.path.getsize(part_path), half_bytes)

        # Download should resume and complete remaining 50%
        success = download_file_resilient(
            url=url,
            dest_path=dest,
            expected_sha256=self.expected_sha256,
            enable_resume=True,
        )
        self.assertTrue(success)
        self.assertTrue(os.path.isfile(dest))
        self.assertEqual(os.path.getsize(dest), len(self.test_payload_data))
        self.assertFalse(os.path.exists(part_path))

    def test_download_file_resilient_checksum_mismatch(self):
        url = f"http://127.0.0.1:{self.port}/payload.bin"
        dest = os.path.join(self.temp_dir, "invalid.bin")
        part_path = dest + f".part-{os.getpid()}"

        with self.assertRaises(ValueError):
            download_file_resilient(
                url=url,
                dest_path=dest,
                expected_sha256="0000000000000000000000000000000000000000000000000000000000000000",
                max_retries=1,
            )

        # Target should not exist and part file should be cleaned up
        self.assertFalse(os.path.exists(dest))
        self.assertFalse(os.path.exists(part_path))

    def test_download_files_batch_concurrent(self):
        items = []
        for i in range(6):
            items.append({
                "url": f"http://127.0.0.1:{self.port}/payload.bin",
                "dest": os.path.join(self.temp_dir, f"batch_{i}.bin"),
                "sha256": self.expected_sha256,
            })

        progress_calls = []

        def on_batch(done, tot, pct, name):
            progress_calls.append((done, tot, pct, name))

        result = download_files_batch(items, max_workers=4, progress_callback=on_batch)
        self.assertTrue(result["success"])
        self.assertEqual(result["downloaded"], 6)
        self.assertEqual(result["failed"], 0)
        for i in range(6):
            self.assertTrue(os.path.isfile(os.path.join(self.temp_dir, f"batch_{i}.bin")))

    def test_launcher_services_atomic_write_compliance(self):
        # 1. ControlsService
        inst_dir = os.path.join(self.temp_dir, "instances", "26.2", "minecraft")
        os.makedirs(inst_dir, exist_ok=True)
        opt_path = os.path.join(inst_dir, "options.txt")
        atomic_write_text(opt_path, "key_key.jump:key.keyboard.space\n")

        ctrl = ControlsService(self.temp_dir)
        res = ctrl.apply_control_profile("standard_vanilla", "26.2")
        self.assertTrue(res.get("success"))
        with open(opt_path, "r", encoding="utf-8") as f:
            self.assertIn("key_key.jump:key.keyboard.space", f.read())

        # 2. PacksService
        packs = PacksService(self.temp_dir)
        res = packs.toggle_pack("Faithful_64x.zip", enabled_state=True, instance_id="26.2")
        self.assertTrue(res.get("success"))
        with open(opt_path, "r", encoding="utf-8") as f:
            self.assertIn("resourcePacks:", f.read())

        # 3. ShadersService
        shaders = ShadersService(self.temp_dir)
        res = shaders.apply_shader_preset("balanced", instance_dir="26.2")
        self.assertTrue(res.get("success"))
        shader_opt = os.path.join(inst_dir, "optionsshaders.txt")
        self.assertTrue(os.path.isfile(shader_opt))

        # 4. ExportService
        exporter = ExportService(self.temp_dir)
        imp_res = exporter.import_custom_profile_json(json.dumps({"name": "Custom PVP", "version": "1.21.4"}))
        self.assertTrue(imp_res.get("success"))


if __name__ == "__main__":
    unittest.main()
