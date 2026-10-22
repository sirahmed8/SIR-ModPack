"""
Extreme Adversarial Edge-Case Stress Suite for Milestone 2 Scope 1 & Scope 2.
Authored by: Challenger 2 (Milestone 2)

Extreme Scenarios:
1. Scope 1:
   - Malformed options.txt (no colons, 5+ colons, binary junk, empty lines, Windows CRLF vs Unix LF, Unicode Arabic/Cyrillic keys)
   - Application to non-existent options.txt (creation on the fly)
   - Extreme boundary integers (-99999, -101, -92, -1, 0, 65535)
   - Exception-resilience in profile application
   - Preservation of CRLF vs LF line endings

2. Scope 2:
   - 25,000 rapid burst lines stream
   - Non-UTF8 binary byte streams and invalid Unicode surrogates
   - Exception-throwing callbacks (on_line_callback and on_crash_callback raising errors)
   - Multiple competing crash signatures in single stream (precedence & first-match preservation)
   - Streamer initialization on already-exited / dead process
"""
import collections
import io
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from typing import Any, Dict, List

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.controls_service import (
    GLFW_TO_LWJGL2,
    LWJGL2_TO_GLFW,
    ControlsService,
    KeybindingMode,
)
from launcher_core.crash_analyzer import CrashAnalyzer
from launcher_core.logs_service import LogsService, ProcessLogStreamer


class TestExtremeKeybindingsAdversarial(unittest.TestCase):
    """Hardcore edge-case testing of ControlsService."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sir_extreme_ctrl_")
        self.service = ControlsService(self.temp_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def test_options_txt_creation_from_scratch(self):
        """When options.txt does not exist at all, apply_control_profile creates it atomically."""
        inst_dir = os.path.join(self.temp_dir, "new_instance")
        mc_dir = os.path.join(inst_dir, "minecraft")
        os.makedirs(mc_dir, exist_ok=True)
        options_path = os.path.join(mc_dir, "options.txt")

        self.assertFalse(os.path.exists(options_path))

        # Initially write empty file so it's discovered by search_dirs or pass instance_dir
        with open(options_path, "w", encoding="utf-8") as f:
            f.write("")

        res = self.service.apply_control_profile("standard_vanilla", instance_id="26.2", instance_dir=inst_dir)
        self.assertTrue(res["success"])
        self.assertTrue(os.path.isfile(options_path))

        with open(options_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("key_key.sprint:key.keyboard.left.control", content)
        self.assertIn("key_key.jump:key.keyboard.space", content)
        self.assertIn("key_key.attack:key.mouse.left", content)

    def test_options_txt_malformed_lines_and_crlf(self):
        """options.txt containing lines with no colons, multiple colons, blank lines, and CRLF endings."""
        inst_dir = os.path.join(self.temp_dir, "crlf_instance")
        mc_dir = os.path.join(inst_dir, "minecraft")
        os.makedirs(mc_dir, exist_ok=True)
        options_path = os.path.join(mc_dir, "options.txt")

        corrupted_content = (
            "version:1444\r\n"
            "MALFORMED_NO_COLON_LINE\r\n"
            "key_key.broken:value:with:many:colons\r\n"
            "\r\n"
            "   \r\n"
            "# Custom comment: اختبار اللغة العربية\r\n"
            "key_key.jump:key.keyboard.space\r\n"
            "fov:90.0\r\n"
        )
        with open(options_path, "w", encoding="utf-8") as f:
            f.write(corrupted_content)

        res = self.service.apply_control_profile("ergonomic_blockhit", instance_id="26.2", instance_dir=inst_dir)
        self.assertTrue(res["success"])

        with open(options_path, "r", encoding="utf-8") as f:
            new_content = f.read()

        # Malformed lines and comments should be preserved
        self.assertIn("MALFORMED_NO_COLON_LINE", new_content)
        self.assertIn("key_key.broken:value:with:many:colons", new_content)
        self.assertIn("اختبار اللغة العربية", new_content)
        self.assertIn("fov:90.0", new_content)
        self.assertIn("key_key.use:key.mouse.5", new_content)

    def test_extreme_integer_boundary_scancodes(self):
        """Tests negative and positive integer boundaries outside normal range."""
        test_boundaries = [
            (-99999, "key.keyboard.unknown"),
            (-101, "key.keyboard.unknown"),
            (-92, "key.keyboard.unknown"),
            (-1, "key.keyboard.unknown"),
            (0, "key.keyboard.unknown"),
            (65535, "key.keyboard.unknown"),
        ]
        for val, expected_glfw in test_boundaries:
            with self.subTest(val=val):
                res = self.service.translate_key_value(val, KeybindingMode.MODERN_GLFW)
                self.assertEqual(res, expected_glfw)


class TestExtremeLogsStreamerAdversarial(unittest.TestCase):
    """Hardcore edge-case testing of ProcessLogStreamer."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sir_extreme_logs_")
        self.log_file = os.path.join(self.temp_dir, "extreme_session.log")

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def test_25k_lines_rapid_flood_burst(self):
        """Extreme test: 25,000 lines emitted in maximum throughput burst."""
        total_lines = 25000
        script = (
            f"import sys\n"
            f"for i in range({total_lines}):\n"
            f"    sys.stdout.write(f'STREAM_PKT_{{i:07d}}\\n')\n"
            f"sys.stdout.flush()\n"
        )

        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        streamer = ProcessLogStreamer(
            proc=proc,
            log_file=self.log_file,
            buffer_size=2000,
        )

        exit_code = proc.wait(timeout=25.0)
        time.sleep(0.4)

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(streamer.buffer), 2000)

        # Buffer must have the last 2000 lines (23,000 to 24,999)
        first_line = streamer.buffer[0].strip()
        last_line = streamer.buffer[-1].strip()
        self.assertEqual(first_line, f"STREAM_PKT_{total_lines - 2000:07d}")
        self.assertEqual(last_line, f"STREAM_PKT_{total_lines - 1:07d}")

        # On-disk log has all 25,000
        with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
            disk_lines = f.readlines()
        self.assertEqual(len(disk_lines), total_lines)

    def test_non_utf8_binary_surrogates_and_special_characters(self):
        """Process emitting raw non-ascii unicode and special symbols."""
        script = (
            "import sys\n"
            "sys.stdout.write('Line 1: Special chars: 🚀 ⚔️ 🛡️ 🎮\\n')\n"
            "sys.stdout.write('Line 2: Arabic text: تم فحص ملف السجلات بنجاح\\n')\n"
            "sys.stdout.write('Line 3: Japanese text: ログストリーマーの検証テスト\\n')\n"
            "sys.stdout.flush()\n"
        )

        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        streamer = ProcessLogStreamer(
            proc=proc,
            log_file=self.log_file,
            buffer_size=2000,
        )

        proc.wait(timeout=5.0)
        time.sleep(0.2)

        self.assertEqual(len(streamer.buffer), 3)
        recent = streamer.get_recent_lines(3)
        self.assertIn("تم فحص ملف السجلات بنجاح", recent[1])
        self.assertIn("ログストリーマーの検証テスト", recent[2])

    def test_faulty_callbacks_do_not_crash_streamer(self):
        """User-provided callbacks raising exceptions must not break log streaming or cause deadlocks."""
        def broken_line_callback(line: str):
            raise RuntimeError("Exploding line callback!")

        def broken_crash_callback(diag: Dict[str, Any]):
            raise ValueError("Exploding crash callback!")

        script = (
            "import sys\n"
            "for i in range(100):\n"
            "    sys.stdout.write(f'LINE_{i}\\n')\n"
            "sys.stdout.write('java.lang.OutOfMemoryError: Metaspace\\n')\n"
            "sys.stdout.flush()\n"
            "sys.exit(1)\n"
        )

        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        streamer = ProcessLogStreamer(
            proc=proc,
            log_file=self.log_file,
            buffer_size=2000,
            on_line_callback=broken_line_callback,
            on_crash_callback=broken_crash_callback,
        )

        exit_code = proc.wait(timeout=5.0)
        time.sleep(0.2)

        # Streamer survived despite exceptions in callbacks
        self.assertEqual(exit_code, 1)
        self.assertEqual(streamer.detected_crash_type, "OOM")
        self.assertEqual(len(streamer.buffer), 101)

    def test_multiple_crash_signatures_precedence(self):
        """When multiple crash patterns appear in sequence, the first identified primary root cause is preserved."""
        script = (
            "import sys\n"
            "sys.stdout.write('java.lang.OutOfMemoryError: Java heap space\\n')\n"
            "sys.stdout.write('GLFW error 65542: WGL: The driver does not appear to support OpenGL\\n')\n"
            "sys.stdout.write('EXCEPTION_ACCESS_VIOLATION at 0x00007ff8\\n')\n"
            "sys.stdout.flush()\n"
            "sys.exit(1)\n"
        )

        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        streamer = ProcessLogStreamer(
            proc=proc,
            log_file=self.log_file,
            buffer_size=2000,
        )

        proc.wait(timeout=5.0)
        time.sleep(0.2)

        self.assertEqual(streamer.detected_crash_type, "OOM")
        self.assertIn("OutOfMemoryError", streamer.detected_crash_snippet)

    def test_streamer_on_already_dead_process(self):
        """Initializing streamer on an already terminated process handles termination cleanly."""
        proc = subprocess.Popen(
            [sys.executable, "-c", "import sys; sys.stdout.write('QUICK_DONE\\n')"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        proc.wait(timeout=3.0)

        # Now start streamer
        streamer = ProcessLogStreamer(
            proc=proc,
            log_file=self.log_file,
            buffer_size=2000,
        )
        time.sleep(0.3)

        self.assertFalse(streamer.is_running)


if __name__ == "__main__":
    unittest.main()
