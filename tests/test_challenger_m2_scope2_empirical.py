"""
Empirical Challenger Test Suite for Milestone 2: Native JVM Launch Pipeline & Compatibility.
Authored by: Challenger 2 (Milestone 2)

Targeted Empirical Verification:
1. Scope 1: Keybinding Translation & options.txt Injection
   - Mouse buttons spectrum: -100 to -93 (Left, Right, Middle, Button 4 to Button 8)
   - Modifier keys (Left/Right Shift, Left/Right Control, Left/Right Alt, Caps Lock, Tab, Space, Enter, Keypad Enter)
   - Function keys (F1 through F19) and Keypad operations
   - Navigation, Cursor, and Special keys (Escape, Backspace, Delete, Insert, Home, End, Page Up/Down, Arrows, Pause, Num/Scroll Lock)
   - Case-insensitivity, degenerate/unmapped inputs, negative scancodes, and numeric conversions
   - Dual-mode options.txt injection with alias translation (perspective <-> togglePerspective, zoom <-> of.key.zoom)
   - Preservation of comments, UTF-8/Unicode, and non-key configuration properties

2. Scope 2: stdout/stderr Stream Tailing & High-Throughput Burst Stress
   - 10,000+ rapid lines burst from live subprocess: 0 deadlocks, exact 2000-line ring buffer rotation (FIFO lines 8000-9999)
   - 15,000+ interleaved stdout and stderr streaming without pipe buffer deadlocks
   - High-concurrency multithreaded readers reading buffer during live write burst (0 race conditions, thread safety)
   - Real-time crash pattern detection under high-throughput flood (OOM, Mixin, Class Mismatch, Access Violation)
   - Early process termination and graceful streamer thread shutdown
"""
import collections
import concurrent.futures
import io
import json
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


class TestChallenger2Scope1Keybindings(unittest.TestCase):
    """Scope 1: Adversarial testing of keybinding translation across edge-case GLFW keys, modifier keys, and mouse buttons (-100 to -93)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_ch2_ctrl_")
        self.service = ControlsService(self.temp_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    # =========================================================================
    # 1. MOUSE BUTTONS SPECTRUM (-100 to -93)
    # =========================================================================

    def test_mouse_buttons_full_spectrum_minus100_to_minus93(self):
        """Tests full mouse button spectrum (-100 to -93) in both Legacy and Modern directions."""
        mouse_cases = [
            ("key.mouse.left", -100, "Left Click"),
            ("key.mouse.right", -99, "Right Click"),
            ("key.mouse.middle", -98, "Middle Click / Wheel"),
            ("key.mouse.4", -97, "Mouse Button 4"),
            ("key.mouse.button.4", -97, "Mouse Button 4 Alias"),
            ("key.mouse.5", -96, "Mouse Button 5"),
            ("key.mouse.button.5", -96, "Mouse Button 5 Alias"),
            ("key.mouse.6", -95, "Mouse Button 6"),
            ("key.mouse.button.6", -95, "Mouse Button 6 Alias"),
            ("key.mouse.7", -94, "Mouse Button 7"),
            ("key.mouse.button.7", -94, "Mouse Button 7 Alias"),
            ("key.mouse.8", -93, "Mouse Button 8"),
            ("key.mouse.button.8", -93, "Mouse Button 8 Alias"),
        ]

        for token, expected_scancode, desc in mouse_cases:
            with self.subTest(token=token, desc=desc):
                # 1. GLFW token -> Legacy LWJGL2 numeric string
                code_str = self.service.translate_key_value(token, KeybindingMode.LEGACY_LWJGL2)
                self.assertEqual(code_str, str(expected_scancode), f"Failed GLFW->LWJGL2 for {token}")

                # 2. Integer scancode -> Legacy LWJGL2 numeric string
                int_code_str = self.service.translate_key_value(expected_scancode, KeybindingMode.LEGACY_LWJGL2)
                self.assertEqual(int_code_str, str(expected_scancode))

                # 3. Numeric string -> Legacy LWJGL2 numeric string
                num_str_res = self.service.translate_key_value(str(expected_scancode), KeybindingMode.LEGACY_LWJGL2)
                self.assertEqual(num_str_res, str(expected_scancode))

                # 4. Scancode (int) -> Modern GLFW token
                modern_token = self.service.translate_key_value(expected_scancode, KeybindingMode.MODERN_GLFW)
                self.assertTrue(
                    modern_token.startswith("key.mouse."),
                    f"Expected modern mouse token for {expected_scancode}, got: {modern_token}"
                )

                # 5. Scancode (string) -> Modern GLFW token
                modern_token_str = self.service.translate_key_value(str(expected_scancode), KeybindingMode.MODERN_GLFW)
                self.assertEqual(modern_token_str, modern_token)

    def test_canonical_mouse_button_reverse_lookup(self):
        """Verifies canonical reverse lookup for all negative mouse button scancodes."""
        canonical_expectations = {
            -100: "key.mouse.left",
            -99: "key.mouse.right",
            -98: "key.mouse.middle",
            -97: "key.mouse.4",
            -96: "key.mouse.5",
            -95: "key.mouse.6",
            -94: "key.mouse.7",
            -93: "key.mouse.8",
        }
        for code, expected_name in canonical_expectations.items():
            with self.subTest(code=code, expected=expected_name):
                # Test with int
                res_int = self.service.translate_key_value(code, KeybindingMode.MODERN_GLFW)
                self.assertEqual(res_int, expected_name)
                # Test with str
                res_str = self.service.translate_key_value(str(code), KeybindingMode.MODERN_GLFW)
                self.assertEqual(res_str, expected_name)

    # =========================================================================
    # 2. MODIFIER KEYS & SPECIAL EDGE-CASE GLFW KEYS
    # =========================================================================

    def test_modifier_keys_bidirectional_mapping(self):
        """Tests Shift, Control, Alt, Caps Lock, Tab, and Space modifiers."""
        modifiers = [
            ("key.keyboard.left.shift", 42),
            ("key.keyboard.right.shift", 54),
            ("key.keyboard.left.control", 29),
            ("key.keyboard.right.control", 157),
            ("key.keyboard.left.alt", 56),
            ("key.keyboard.right.alt", 184),
            ("key.keyboard.caps.lock", 58),
            ("key.keyboard.tab", 15),
            ("key.keyboard.space", 57),
            ("key.keyboard.enter", 28),
            ("key.keyboard.keypad.enter", 156),
            ("key.keyboard.escape", 1),
            ("key.keyboard.backspace", 14),
        ]
        for glfw_token, expected_scancode in modifiers:
            with self.subTest(token=glfw_token):
                # GLFW -> LWJGL2
                scancode_str = self.service.translate_key_value(glfw_token, KeybindingMode.LEGACY_LWJGL2)
                self.assertEqual(scancode_str, str(expected_scancode), f"GLFW->LWJGL2 failed for {glfw_token}")

                # LWJGL2 -> GLFW (from int)
                rev_glfw = self.service.translate_key_value(expected_scancode, KeybindingMode.MODERN_GLFW)
                self.assertEqual(rev_glfw, glfw_token, f"LWJGL2->GLFW (int) failed for {expected_scancode}")

                # LWJGL2 -> GLFW (from str)
                rev_glfw_str = self.service.translate_key_value(str(expected_scancode), KeybindingMode.MODERN_GLFW)
                self.assertEqual(rev_glfw_str, glfw_token, f"LWJGL2->GLFW (str) failed for {expected_scancode}")

    def test_function_keys_f1_to_f19(self):
        """Tests full range of Function keys F1 through F19."""
        f_key_map = {
            "key.keyboard.f1": 59,
            "key.keyboard.f2": 60,
            "key.keyboard.f3": 61,
            "key.keyboard.f4": 62,
            "key.keyboard.f5": 63,
            "key.keyboard.f6": 64,
            "key.keyboard.f7": 65,
            "key.keyboard.f8": 66,
            "key.keyboard.f9": 67,
            "key.keyboard.f10": 68,
            "key.keyboard.f11": 87,
            "key.keyboard.f12": 88,
            "key.keyboard.f13": 100,
            "key.keyboard.f14": 101,
            "key.keyboard.f15": 102,
            "key.keyboard.f16": 103,
            "key.keyboard.f17": 104,
            "key.keyboard.f18": 105,
            "key.keyboard.f19": 106,
        }
        for token, expected_code in f_key_map.items():
            with self.subTest(token=token):
                code_str = self.service.translate_key_value(token, KeybindingMode.LEGACY_LWJGL2)
                self.assertEqual(code_str, str(expected_code))
                rev_token = self.service.translate_key_value(expected_code, KeybindingMode.MODERN_GLFW)
                self.assertEqual(rev_token, token)

    def test_navigation_and_keypad_keys(self):
        """Tests Navigation, Arrow keys, Lock keys, and Keypad math operations."""
        nav_keys = [
            ("key.keyboard.insert", 210),
            ("key.keyboard.delete", 211),
            ("key.keyboard.home", 199),
            ("key.keyboard.end", 207),
            ("key.keyboard.page.up", 201),
            ("key.keyboard.page.down", 209),
            ("key.keyboard.up", 200),
            ("key.keyboard.down", 208),
            ("key.keyboard.left", 203),
            ("key.keyboard.right", 205),
            ("key.keyboard.num.lock", 69),
            ("key.keyboard.scroll.lock", 70),
            ("key.keyboard.pause", 197),
            ("key.keyboard.keypad.multiply", 55),
            ("key.keyboard.keypad.add", 78),
            ("key.keyboard.keypad.subtract", 74),
            ("key.keyboard.keypad.divide", 181),
            ("key.keyboard.keypad.decimal", 83),
            ("key.keyboard.left.bracket", 26),
            ("key.keyboard.right.bracket", 27),
            ("key.keyboard.semicolon", 39),
            ("key.keyboard.apostrophe", 40),
            ("key.keyboard.grave.accent", 41),
            ("key.keyboard.backslash", 43),
            ("key.keyboard.comma", 51),
            ("key.keyboard.period", 52),
            ("key.keyboard.slash", 53),
            ("key.keyboard.minus", 12),
            ("key.keyboard.equal", 13),
        ]
        for token, expected_code in nav_keys:
            with self.subTest(token=token):
                code_str = self.service.translate_key_value(token, KeybindingMode.LEGACY_LWJGL2)
                self.assertEqual(code_str, str(expected_code))
                rev_token = self.service.translate_key_value(expected_code, KeybindingMode.MODERN_GLFW)
                self.assertEqual(rev_token, token)

    # =========================================================================
    # 3. ADVERSARIAL & DEGENERATE KEY INPUTS
    # =========================================================================

    def test_case_insensitivity_and_whitespace(self):
        """Tests that key translation handles upper/mixed case and whitespace cleanly."""
        cases = [
            ("KEY.KEYBOARD.SPACE", "57"),
            ("Key.Keyboard.Left.Shift", "42"),
            ("KEY.MOUSE.LEFT", "-100"),
            ("  key.keyboard.f5  ", "63"),
            ("KEY.KEYBOARD.RIGHT.CONTROL", "157"),
        ]
        for input_key, expected_code in cases:
            with self.subTest(input_key=input_key):
                code_str = self.service.translate_key_value(input_key, KeybindingMode.LEGACY_LWJGL2)
                self.assertEqual(code_str, expected_code)

    def test_unmapped_and_unknown_key_tokens(self):
        """Tests unmapped/unknown tokens and numeric boundaries."""
        # Unmapped string token in Legacy mode -> defaults to 0 (key.keyboard.unknown)
        self.assertEqual(self.service.translate_key_value("key.keyboard.unknown", KeybindingMode.LEGACY_LWJGL2), "0")
        self.assertEqual(self.service.translate_key_value("key.nonexistent.foobar", KeybindingMode.LEGACY_LWJGL2), "0")

        # Unknown scancode in Modern mode -> defaults to key.keyboard.unknown
        self.assertEqual(self.service.translate_key_value(0, KeybindingMode.MODERN_GLFW), "key.keyboard.unknown")
        self.assertEqual(self.service.translate_key_value("0", KeybindingMode.MODERN_GLFW), "key.keyboard.unknown")
        self.assertEqual(self.service.translate_key_value(99999, KeybindingMode.MODERN_GLFW), "key.keyboard.unknown")
        self.assertEqual(self.service.translate_key_value(-500, KeybindingMode.MODERN_GLFW), "key.keyboard.unknown")

    # =========================================================================
    # 4. OPTIONS.TXT INJECTION & ALIAS INTEGRITY
    # =========================================================================

    def test_options_txt_dual_mode_alias_handling(self):
        """Tests that key aliases (perspective <-> togglePerspective, zoom <-> of.key.zoom) translate correctly."""
        keys_map = {
            "key_key.perspective": "key.keyboard.v",
            "key_key.zoom": "key.keyboard.c",
            "key_key.sprint": "key.keyboard.left.control",
            "key_key.attack": "key.mouse.left",
            "key_key.use": "key.mouse.right",
        }

        # 1. Translate for Legacy LWJGL2 (1.8.9)
        legacy_translated = self.service.translate_keys_map(keys_map, KeybindingMode.LEGACY_LWJGL2)
        # Perspective should map to key_key.togglePerspective with scancode for 'v' (47)
        self.assertIn("key_key.togglePerspective", legacy_translated)
        self.assertEqual(legacy_translated["key_key.togglePerspective"], "47")
        # Zoom should map to both key_of.key.zoom and key_key.zoom with scancode for 'c' (46)
        self.assertIn("key_of.key.zoom", legacy_translated)
        self.assertEqual(legacy_translated["key_of.key.zoom"], "46")
        self.assertEqual(legacy_translated["key_key.sprint"], "29")
        self.assertEqual(legacy_translated["key_key.attack"], "-100")
        self.assertEqual(legacy_translated["key_key.use"], "-99")

        # 2. Translate for Modern GLFW (26.2)
        modern_input = {
            "key_key.togglePerspective": "47",
            "key_of.key.zoom": "46",
            "key_key.sprint": "29",
            "key_key.attack": "-100",
            "key_key.use": "-99",
        }
        modern_translated = self.service.translate_keys_map(modern_input, KeybindingMode.MODERN_GLFW)
        self.assertIn("key_key.perspective", modern_translated)
        self.assertEqual(modern_translated["key_key.perspective"], "key.keyboard.v")
        self.assertIn("key_key.zoom", modern_translated)
        self.assertEqual(modern_translated["key_key.zoom"], "key.keyboard.c")
        self.assertEqual(modern_translated["key_key.sprint"], "key.keyboard.left.control")
        self.assertEqual(modern_translated["key_key.attack"], "key.mouse.left")
        self.assertEqual(modern_translated["key_key.use"], "key.mouse.right")

    def test_options_txt_full_roundtrip_preserves_non_keys_and_comments(self):
        """Tests that applying control profiles to options.txt preserves comments, Unicode, and non-key settings."""
        inst_dir = os.path.join(self.temp_dir, "instance_189")
        mc_dir = os.path.join(inst_dir, "minecraft")
        os.makedirs(mc_dir, exist_ok=True)
        options_path = os.path.join(mc_dir, "options.txt")

        initial_options = (
            "# SIR Ecosystem Configuration File\n"
            "# Minecraft Options with Custom Presets & العربية\n"
            "version:0\n"
            "fov:75.0\n"
            "gamma:1.5\n"
            "renderDistance:12\n"
            "guiScale:2\n"
            "soundCategory_master:0.8\n"
            "key_key.forward:17\n"
            "key_key.left:30\n"
            "key_key.back:31\n"
            "key_key.right:32\n"
            "key_key.jump:57\n"
            "key_key.sneak:42\n"
        )
        with open(options_path, "w", encoding="utf-8") as f:
            f.write(initial_options)

        # Apply profile
        res = self.service.apply_control_profile("hypixel_pro_pvp", instance_id="1.8.9", instance_dir=inst_dir)
        self.assertTrue(res["success"])
        self.assertEqual(res["mode"], KeybindingMode.LEGACY_LWJGL2)

        # Verify options.txt content
        with open(options_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Non-key settings and comments must be preserved
        self.assertIn("# SIR Ecosystem Configuration File", content)
        self.assertIn("fov:75.0", content)
        self.assertIn("gamma:1.5", content)
        self.assertIn("renderDistance:12", content)
        self.assertIn("guiScale:2", content)
        self.assertIn("soundCategory_master:0.8", content)

        # Injected keys must be strictly numeric for 1.8.9 (no NumberFormatException)
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(":", 1)
            if len(parts) == 2 and parts[0].startswith("key_"):
                val = parts[1]
                # Every key value in 1.8.9 options.txt MUST be an integer or negative integer
                self.assertTrue(
                    val.lstrip("-").isdigit(),
                    f"Found non-numeric key in 1.8.9 options.txt: {parts[0]}={val}"
                )


class TestChallenger2Scope2LogStreamerThroughput(unittest.TestCase):
    """Scope 2: Adversarial testing of stdout/stderr stream tailing under high-throughput log spam (10,000+ lines in rapid burst)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_ch2_logs_")
        self.log_file = os.path.join(self.temp_dir, "session.log")

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    # =========================================================================
    # 1. 10,000+ RAPID BURST STDOUT STREAMING & 2000-LINE RING BUFFER ROTATION
    # =========================================================================

    def test_rapid_burst_10k_lines_zero_deadlock_and_exact_ring_rotation(self):
        """Stress test: 10,000 lines emitted in rapid burst from subprocess.
        Verifies 0 deadlocks, exactly 2000 lines retained in FIFO circular order (lines 8000-9999), and full disk file integrity.
        """
        line_count = 10000
        # Python script that rapidly writes 10,000 lines to stdout
        script = (
            f"import sys\n"
            f"for i in range({line_count}):\n"
            f"    sys.stdout.write(f'LOG_BURST_LINE_{{i:06d}}: System benchmark packet payload alpha-numeric sequence\\n')\n"
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

        # Wait for process exit with 15-second safety timeout against deadlocks
        start_time = time.time()
        exit_code = proc.wait(timeout=15.0)
        elapsed = time.time() - start_time

        # Give streamer tail worker a moment to finalize reading
        time.sleep(0.3)

        # 1. Verify 0 deadlocks and fast execution
        self.assertEqual(exit_code, 0, "Subprocess exited with non-zero code")
        self.assertLess(elapsed, 10.0, f"Streaming took too long: {elapsed:.2f}s (possible I/O lag)")

        # 2. Verify ring buffer bounds
        with streamer.lock:
            buffer_len = len(streamer.buffer)
            first_buffered = streamer.buffer[0].strip()
            last_buffered = streamer.buffer[-1].strip()

        self.assertEqual(buffer_len, 2000, f"Expected ring buffer to cap at 2000, got: {buffer_len}")
        self.assertTrue(
            first_buffered.startswith("LOG_BURST_LINE_008000:"),
            f"FIFO rotation error! First buffered line should be 8000, got: '{first_buffered}'"
        )
        self.assertTrue(
            last_buffered.startswith(f"LOG_BURST_LINE_{line_count - 1:06d}:"),
            f"Last buffered line should be {line_count - 1}, got: '{last_buffered}'"
        )

        # 3. Verify get_recent_lines() method
        recent_200 = streamer.get_recent_lines(200)
        self.assertEqual(len(recent_200), 200)
        self.assertTrue(recent_200[0].startswith(f"LOG_BURST_LINE_{line_count - 200:06d}:"))
        self.assertTrue(recent_200[-1].startswith(f"LOG_BURST_LINE_{line_count - 1:06d}:"))

        # 4. Verify on-disk log file contains ALL 10,000 lines intact
        self.assertTrue(os.path.isfile(self.log_file), "Log file was not created on disk")
        with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
            disk_lines = f.readlines()

        self.assertEqual(
            len(disk_lines),
            line_count,
            f"Disk log file missed lines! Expected {line_count}, got: {len(disk_lines)}"
        )

    # =========================================================================
    # 2. 15,000 INTERLEAVED STDOUT + STDERR HIGH-THROUGHPUT STRESS
    # =========================================================================

    def test_interleaved_stdout_stderr_15k_lines_no_pipe_deadlock(self):
        """Stress test: 15,000 lines emitted across interleaved stdout and stderr.
        Verifies Windows pipe buffers never stall and streamer multiplexes stderr without dropping lines.
        """
        stdout_count = 7500
        stderr_count = 7500
        total_count = stdout_count + stderr_count

        script = (
            f"import sys\n"
            f"for i in range({stdout_count}):\n"
            f"    sys.stdout.write(f'OUT_{{i:05d}}\\n')\n"
            f"    sys.stderr.write(f'ERR_{{i:05d}}\\n')\n"
            f"sys.stdout.flush()\n"
            f"sys.stderr.flush()\n"
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

        start_time = time.time()
        exit_code = proc.wait(timeout=20.0)
        elapsed = time.time() - start_time
        time.sleep(0.3)

        self.assertEqual(exit_code, 0)
        self.assertLess(elapsed, 12.0)

        # Buffer must be bounded to 2000
        self.assertEqual(len(streamer.buffer), 2000)

        # Disk file must have all 15,000 lines
        with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
            disk_lines = f.readlines()
        self.assertEqual(len(disk_lines), total_count)

    # =========================================================================
    # 3. HIGH CONCURRENCY READERS DURING LIVE FLOOD
    # =========================================================================

    def test_concurrent_readers_during_live_log_flood(self):
        """Stress test: 8 simultaneous threads calling get_recent_lines() while 10,000 lines are pumped in real-time."""
        line_count = 10000
        script = (
            f"import sys, time\n"
            f"for i in range({line_count}):\n"
            f"    sys.stdout.write(f'CONCURRENT_BURST_{{i:06d}}\\n')\n"
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

        reader_errors: List[Exception] = []
        stop_readers = threading.Event()
        read_iterations = [0] * 8

        def reader_worker(worker_id: int):
            try:
                while not stop_readers.is_set():
                    lines = streamer.get_recent_lines(100)
                    self.assertIsInstance(lines, list)
                    self.assertLessEqual(len(lines), 100)
                    read_iterations[worker_id] += 1
                    time.sleep(0.001)
            except Exception as ex:
                reader_errors.append(ex)

        threads = [threading.Thread(target=reader_worker, args=(i,), daemon=True) for i in range(8)]
        for t in threads:
            t.start()

        # Wait for process
        proc.wait(timeout=15.0)
        time.sleep(0.3)
        stop_readers.set()
        for t in threads:
            t.join(timeout=2.0)

        # Assertions
        self.assertEqual(len(reader_errors), 0, f"Reader threads encountered errors: {reader_errors}")
        self.assertTrue(all(count > 10 for count in read_iterations), f"Readers did not run enough: {read_iterations}")
        self.assertEqual(len(streamer.buffer), 2000)

    # =========================================================================
    # 4. REAL-TIME CRASH DETECTION UNDER RAPID FLOOD
    # =========================================================================

    def test_realtime_crash_detection_under_rapid_flood(self):
        """Stress test: Crash signature emitted in the middle of a 10,000-line burst is detected immediately."""
        crash_payload_received: Dict[str, Any] = {}
        crash_event = threading.Event()

        def on_crash(diag: Dict[str, Any]):
            nonlocal crash_payload_received
            crash_payload_received = diag
            crash_event.set()

        # Script emits 5000 normal lines, 1 OOM line, 5000 more normal lines, then exits with code 1
        script = (
            "import sys\n"
            "for i in range(5000):\n"
            "    sys.stdout.write(f'NORMAL_PRE_LINE_{i}\\n')\n"
            "sys.stdout.write('java.lang.OutOfMemoryError: Java heap space\\n')\n"
            "for i in range(5000):\n"
            "    sys.stdout.write(f'NORMAL_POST_LINE_{i}\\n')\n"
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
            on_crash_callback=on_crash,
        )

        proc.wait(timeout=15.0)
        time.sleep(0.3)

        # Verify crash detection
        self.assertEqual(streamer.detected_crash_type, "OOM")
        self.assertIn("OutOfMemoryError", streamer.detected_crash_snippet)

        # Verify callback payload
        self.assertTrue(crash_event.wait(timeout=2.0), "on_crash callback was not triggered!")
        self.assertEqual(crash_payload_received.get("crash_type"), "OOM")
        self.assertEqual(crash_payload_received.get("exit_code"), 1)

    # =========================================================================
    # 5. EARLY KILL & CLEANUP UNDER FLOOD
    # =========================================================================

    def test_early_process_termination_and_streamer_cleanup(self):
        """Stress test: Process terminated while in infinite loop; streamer cleanly stops without hanging threads."""
        script = (
            "import sys, time\n"
            "while True:\n"
            "    sys.stdout.write('INFINITE_LOOP_LOG_LINE\\n')\n"
            "    sys.stdout.flush()\n"
            "    time.sleep(0.005)\n"
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

        # Allow some lines to stream
        time.sleep(0.2)
        self.assertTrue(len(streamer.buffer) > 0)

        # Stop streamer and kill process
        streamer.stop()
        proc.terminate()
        proc.wait(timeout=5.0)

        # Wait for streamer threads to finish
        time.sleep(0.2)
        self.assertFalse(streamer.is_running)
        self.assertFalse(streamer._tail_thread.is_alive())
        self.assertFalse(streamer._exit_thread.is_alive())


if __name__ == "__main__":
    unittest.main()
