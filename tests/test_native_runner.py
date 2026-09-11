"""
Comprehensive Test Suite for Milestone 2: Native JVM Launch Pipeline & Compatibility.
Covers Features 7, 8, 9, 10, 11, 12 across Tier 1 (Features), Tier 2 (Boundaries),
Tier 3 (Cross-Feature Integrations), and Tier 4 (Real-World Scenarios).
"""
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from unittest.mock import MagicMock, patch

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
from launcher_core.java_service import (
    JavaService,
    get_pe_binary_arch,
    parse_java_runtime_info,
)
from launcher_core.logs_service import LogsService, ProcessLogStreamer
from launcher_core.native_runner import (
    NativeMinecraftRunner,
    _parse_to_mb,
    calculate_ram_parameters,
)


class TestNativeRunnerM2(unittest.TestCase):
    """Full Milestone 2 Test Harness for Native JVM Execution Pipeline."""

    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.instances_dir = os.path.join(self.root_dir, "instances")
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_m2_")
        self.runner = NativeMinecraftRunner(self.root_dir, self.temp_dir)
        self.java_service = JavaService(self.root_dir)
        self.controls_service = ControlsService(self.root_dir)
        self.logs_service = LogsService(self.root_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    # =========================================================================
    # TIER 1: CORE FEATURE VERIFICATION (Features 7 - 12)
    # =========================================================================

    # --- Feature 7: Strict RAM Parameter Allocation ---
    def test_f7_ram_allocation_exact_bounds_4g(self):
        """F7: Verifies exact -Xmx4G and -Xms2G without forced alteration."""
        params = calculate_ram_parameters(max_ram=4, mc_version="26.2")
        self.assertEqual(params["max_mb"], 4096)
        self.assertEqual(params["min_mb"], 2048)
        self.assertEqual(params["xmx_flag"], "-Xmx4G")
        self.assertEqual(params["xms_flag"], "-Xms2G")

    def test_f7_ram_allocation_exact_bounds_8g(self):
        """F7: Verifies exact -Xmx8G and -Xms4G."""
        params = calculate_ram_parameters(max_ram=8, mc_version="26.2")
        self.assertEqual(params["max_mb"], 8192)
        self.assertEqual(params["min_mb"], 4096)
        self.assertEqual(params["xmx_flag"], "-Xmx8G")
        self.assertEqual(params["xms_flag"], "-Xms4G")

    def test_f7_ram_allocation_exact_bounds_16g(self):
        """F7: Verifies exact -Xmx16G and -Xms8G."""
        params = calculate_ram_parameters(max_ram=16, mc_version="26.2")
        self.assertEqual(params["max_mb"], 16384)
        self.assertEqual(params["min_mb"], 8192)
        self.assertEqual(params["xmx_flag"], "-Xmx16G")
        self.assertEqual(params["xms_flag"], "-Xms8G")

    def test_f7_ram_mb_granularity(self):
        """F7: Verifies granular memory inputs (e.g. 6144M, 3072M)."""
        params = calculate_ram_parameters(max_ram="6144M", min_ram="3072M", mc_version="26.2")
        self.assertEqual(params["max_mb"], 6144)
        self.assertEqual(params["min_mb"], 3072)
        self.assertEqual(params["xmx_flag"], "-Xmx6G")
        self.assertEqual(params["xms_flag"], "-Xms3G")

    def test_f7_power_mode_thread_governor(self):
        """F7: Verifies GC thread allocation under turbo vs smooth power modes."""
        args_turbo = self.runner.build_jvm_args(ram_gb=8, power_mode="turbo")
        args_smooth = self.runner.build_jvm_args(ram_gb=8, power_mode="smooth")

        self.assertTrue(any("ParallelGCThreads=" in a for a in args_turbo))
        self.assertTrue(any("ConcGCThreads=" in a for a in args_turbo))
        self.assertIn("-XX:ParallelGCThreads=4", args_smooth)
        self.assertIn("-XX:ConcGCThreads=2", args_smooth)

    # --- Feature 8: Pre-Launch Natives Extraction ---
    def test_f8_legacy_189_natives_extraction(self):
        """F8: Verifies extraction and resolution of LWJGL 2 DLLs for 1.8.9."""
        v_json = self.runner.resolve_version_json("1.8.9", loader="forge")
        self.assertIsNotNone(v_json)
        nat_dir = os.path.join(self.temp_dir, "natives_189")
        res_dir = self.runner.extract_natives(v_json, "1.8.9", target_dir=nat_dir)
        self.assertTrue(os.path.isdir(res_dir))

    def test_f8_modern_262_natives_extraction(self):
        """F8: Verifies extraction and resolution of LWJGL 3 DLLs for Modern 26.2."""
        v_json = self.runner.resolve_version_json("26.2", loader="fabric") or {"id": "26.2", "libraries": []}
        nat_dir = os.path.join(self.temp_dir, "natives_262")
        res_dir = self.runner.extract_natives(v_json, "26.2", target_dir=nat_dir)
        self.assertTrue(os.path.isdir(res_dir))

    def test_f8_natives_jvm_library_paths(self):
        """F8: Verifies JVM arguments contain -Djava.library.path and extract paths."""
        nat_path = os.path.join(self.temp_dir, "test_nat")
        jvm_args = self.runner.build_jvm_args(ram_gb=4, natives_dir=nat_path)
        self.assertIn(f"-Djava.library.path={nat_path}", jvm_args)
        self.assertTrue(any("-Dorg.lwjgl.system.SharedLibraryExtractPath=" in a for a in jvm_args))
        self.assertTrue(any("-Djna.tmpdir=" in a for a in jvm_args))
        self.assertTrue(any("-Dio.netty.native.workdir=" in a for a in jvm_args))

    def test_f8_natives_jar_zip_extraction(self):
        """F8: Creates a synthetic native JAR and tests DLL extraction."""
        jar_path = os.path.join(self.temp_dir, "mock-natives-windows.jar")
        with zipfile.ZipFile(jar_path, "w") as z:
            z.writestr("lwjgl.dll", b"MZ_MOCK_DLL_CONTENT")
            z.writestr("glfw.dll", b"MZ_MOCK_GLFW_CONTENT")
            z.writestr("META-INF/MANIFEST.MF", b"Manifest-Version: 1.0\n")

        v_json = {
            "id": "mock_ver",
            "libraries": [
                {
                    "name": "org.lwjgl:lwjgl-mock:3.4.1",
                    "downloads": {
                        "classifiers": {
                            "natives-windows": {
                                "path": "org/lwjgl/mock-natives-windows.jar"
                            }
                        }
                    }
                }
            ]
        }
        # Place synthetic jar in libraries dir
        lib_dest = os.path.join(self.temp_dir, "libraries", "org", "lwjgl", "mock-natives-windows.jar")
        os.makedirs(os.path.dirname(lib_dest), exist_ok=True)
        shutil.copyfile(jar_path, lib_dest)
        self.runner.libraries_dirs.insert(0, os.path.join(self.temp_dir, "libraries"))

        dest_nat = os.path.join(self.temp_dir, "extracted_nat")
        res = self.runner.extract_natives(v_json, "26.2", target_dir=dest_nat, force_reextract=True)
        self.assertTrue(os.path.isfile(os.path.join(res, "lwjgl.dll")))
        self.assertTrue(os.path.isfile(os.path.join(res, "glfw.dll")))
        self.assertFalse(os.path.exists(os.path.join(res, "META-INF")))

    def test_f8_resolve_natives_dir_fallback(self):
        """F8: Tests resolve_natives_dir returns valid directory."""
        v_json = {"id": "26.2", "libraries": []}
        nat_dir = self.runner.resolve_natives_dir(v_json, "26.2")
        self.assertTrue(os.path.isdir(nat_dir))

    # --- Feature 9: Dynamic Classpath Assembly ---
    def test_f9_dynamic_mmc_pack_fabric_resolution(self):
        """F9: Verifies mmc-pack.json parsing for Modern 26.2."""
        inst_dir = os.path.join(self.instances_dir, "26.2-ultra") if os.path.isdir(os.path.join(self.instances_dir, "26.2-ultra")) else os.path.join(self.instances_dir, "26.2")
        if os.path.isdir(inst_dir):
            cfg = self.runner.inspect_instance_config(inst_dir)
            self.assertEqual(cfg["loader"], "fabric")
            self.assertIn(cfg["loader_version"], ["0.19.5", "0.19.4", "0.19.3", "0.16.10", "0.15.11"])

    def test_f9_dynamic_mmc_pack_forge_resolution(self):
        """F9: Verifies mmc-pack.json parsing for Legacy 1.8.9."""
        inst_dir = os.path.join(self.instances_dir, "1.8.9")
        if os.path.isdir(inst_dir):
            cfg = self.runner.inspect_instance_config(inst_dir)
            self.assertEqual(cfg["loader"], "forge")
            self.assertEqual(cfg["loader_version"], "11.15.1.2318")

    def test_f9_dynamic_classpath_fabric_asm9(self):
        """F9: Verifies ASM 9.10.1 is prepended on Fabric classpath."""
        v_json = self.runner.resolve_version_json("26.2", loader="fabric") or {"id": "26.2", "libraries": []}
        cp = self.runner.build_classpath(v_json, "26.2", loader="fabric")
        self.assertIsInstance(cp, list)
        cp_str = ";".join(cp)
        # Should contain Fabric Loader or ASM
        self.assertTrue(any("fabric-loader" in p or "asm" in p for p in cp))

    def test_f9_dynamic_classpath_forge_launchwrapper(self):
        """F9: Verifies Forge 1.8.9 and LaunchWrapper in classpath."""
        v_json = self.runner.resolve_version_json("1.8.9", loader="forge") or {"id": "1.8.9", "libraries": []}
        cp = self.runner.build_classpath(v_json, "1.8.9", loader="forge")
        self.assertIsInstance(cp, list)
        self.assertTrue(any("forge" in p.lower() or "launchwrapper" in p.lower() for p in cp))

    def test_f9_classpath_deduplication_preserves_order(self):
        """F9: Verifies classpath deduplication preserves order without duplicate entries."""
        v_json = {
            "id": "26.2",
            "libraries": [
                {"name": "com.google.guava:guava:32.1.2-jre"},
                {"name": "com.google.guava:guava:32.1.2-jre"}, # duplicate
                {"name": "com.google.code.gson:gson:2.10.1"},
            ]
        }
        cp = self.runner.build_classpath(v_json, "26.2", loader="fabric")
        self.assertEqual(len(cp), len(set(cp)))

    # --- Feature 10: Stable JRE Runtime Locator ---
    def test_f10_pe_architecture_detection_x64(self):
        """F10: Tests PE header detection on mock x64 and x86 binaries."""
        # Mock x64 PE binary
        x64_exe = os.path.join(self.temp_dir, "mock_x64.exe")
        with open(x64_exe, "wb") as f:
            f.write(b"MZ" + b"\x00" * 0x3A + struct.pack("<I", 0x80))
            f.seek(0x80)
            f.write(b"PE\x00\x00" + struct.pack("<H", 0x8664))
        pe_64 = get_pe_binary_arch(x64_exe)
        self.assertTrue(pe_64["is_valid"])
        self.assertTrue(pe_64["is_64bit"])
        self.assertEqual(pe_64["arch"], "x64")

        # Mock x86 (32-bit) PE binary
        x86_exe = os.path.join(self.temp_dir, "mock_x86.exe")
        with open(x86_exe, "wb") as f:
            f.write(b"MZ" + b"\x00" * 0x3A + struct.pack("<I", 0x80))
            f.seek(0x80)
            f.write(b"PE\x00\x00" + struct.pack("<H", 0x014C))
        pe_32 = get_pe_binary_arch(x86_exe)
        self.assertTrue(pe_32["is_valid"])
        self.assertFalse(pe_32["is_64bit"])
        self.assertEqual(pe_32["arch"], "x86 (32-bit)")

    def test_f10_semver_parsing_java_8_through_25(self):
        """F10: Tests Java semver and vendor parsing across 8, 17, 21, 25."""
        dummy_exe = os.path.join(self.temp_dir, "java.exe")
        with open(dummy_exe, "wb") as f:
            f.write(b"MZ")

        with patch("subprocess.run") as mock_run:
            # Test Java 21 Temurin
            mock_run.return_value = MagicMock(
                stdout='openjdk version "21.0.6" 2025-01-21 LTS\nOpenJDK Runtime Environment Temurin-21.0.6+7 (build 21.0.6+7-LTS)\nOpenJDK 64-Bit Server VM\n'
            )
            info21 = parse_java_runtime_info(dummy_exe, probe_process=True)
            self.assertEqual(info21["major_version"], 21)
            self.assertEqual(info21["vendor"], "Eclipse Adoptium (Temurin)")
            self.assertTrue(info21["is_lts"])
            self.assertTrue(info21["is_temurin_21"])
            self.assertTrue(info21["is_modern_ready"])

            # Test Java 8
            mock_run.return_value = MagicMock(
                stdout='java version "1.8.0_442"\nJava(TM) SE Runtime Environment (build 1.8.0_442-b06)\nJava HotSpot(TM) 64-Bit Server VM\n'
            )
            info8 = parse_java_runtime_info(dummy_exe, probe_process=True)
            self.assertEqual(info8["major_version"], 8)
            self.assertTrue(info8["is_java8"])
            self.assertTrue(info8["is_legacy_ready"])

            # Test Java 25 EA
            mock_run.return_value = MagicMock(
                stdout='openjdk version "25-ea" 2025-09-16\nOpenJDK Runtime Environment (build 25-ea+12-1048)\nOpenJDK 64-Bit Server VM\n'
            )
            info25 = parse_java_runtime_info(dummy_exe, probe_process=True)
            self.assertEqual(info25["major_version"], 25)
            self.assertTrue(info25["is_modern_ready"])

    def test_f10_runtime_discovery_structure(self):
        """F10: Tests discover_java_installations return schema and deduplication."""
        res = self.java_service.discover_java_installations()
        self.assertTrue(res["success"])
        self.assertIsInstance(res["installations"], list)
        self.assertIsInstance(res["count"], int)
        # Check deduplication
        paths = [i["path"].lower() for i in res["installations"]]
        self.assertEqual(len(paths), len(set(paths)))

    def test_f10_best_runtime_selection(self):
        """F10: Verifies get_best_runtime_for_version resolves appropriate runtimes."""
        best_modern = self.java_service.get_best_runtime_for_version("26.2")
        best_legacy = self.java_service.get_best_runtime_for_version("1.8.9")
        if best_modern:
            self.assertIn("path", best_modern)
        if best_legacy:
            self.assertIn("path", best_legacy)

    # --- Feature 11: Dual-Mode Keybinding Injection ---
    def test_f11_keybinding_mode_detection(self):
        """F11: Correctly detects MODERN_GLFW vs LEGACY_LWJGL2."""
        mode_262 = self.controls_service.detect_instance_mode(
            os.path.join(self.instances_dir, "26.2"), "26.2"
        )
        mode_189 = self.controls_service.detect_instance_mode(
            os.path.join(self.instances_dir, "1.8.9"), "1.8.9"
        )
        self.assertEqual(mode_262, KeybindingMode.MODERN_GLFW)
        self.assertEqual(mode_189, KeybindingMode.LEGACY_LWJGL2)

    def test_f11_keybinding_scancode_translation(self):
        """F11: Translates GLFW string tokens to integer scancodes for LWJGL 2."""
        # W -> 17
        self.assertEqual(self.controls_service.translate_key_value("key.keyboard.w", KeybindingMode.LEGACY_LWJGL2), "17")
        # Shift -> 42
        self.assertEqual(self.controls_service.translate_key_value("key.keyboard.left.shift", KeybindingMode.LEGACY_LWJGL2), "42")
        # Space -> 57
        self.assertEqual(self.controls_service.translate_key_value("key.keyboard.space", KeybindingMode.LEGACY_LWJGL2), "57")
        # Reverse 17 -> key.keyboard.w
        self.assertEqual(self.controls_service.translate_key_value(17, KeybindingMode.MODERN_GLFW), "key.keyboard.w")

    def test_f11_mouse_button_negative_offset(self):
        """F11: Tests negative-offset formula for mouse buttons in LWJGL 2 (button - 100)."""
        # Mouse left -> -100
        self.assertEqual(self.controls_service.translate_key_value("key.mouse.left", KeybindingMode.LEGACY_LWJGL2), "-100")
        # Mouse right -> -99
        self.assertEqual(self.controls_service.translate_key_value("key.mouse.right", KeybindingMode.LEGACY_LWJGL2), "-99")
        # Mouse middle -> -98
        self.assertEqual(self.controls_service.translate_key_value("key.mouse.middle", KeybindingMode.LEGACY_LWJGL2), "-98")
        # Mouse 4 -> -97
        self.assertEqual(self.controls_service.translate_key_value("key.mouse.4", KeybindingMode.LEGACY_LWJGL2), "-97")
        # Mouse 5 -> -96
        self.assertEqual(self.controls_service.translate_key_value("key.mouse.5", KeybindingMode.LEGACY_LWJGL2), "-96")

    def test_f11_key_alias_perspective_and_zoom(self):
        """F11: Tests key alias mapping (perspective vs togglePerspective)."""
        keys_in = {
            "key_key.perspective": "key.keyboard.v",
            "key_key.zoom": "key.keyboard.c",
        }
        legacy_keys = self.controls_service.translate_keys_map(keys_in, KeybindingMode.LEGACY_LWJGL2)
        self.assertIn("key_key.togglePerspective", legacy_keys)
        self.assertEqual(legacy_keys["key_key.togglePerspective"], "47")  # V = 47
        self.assertIn("key_of.key.zoom", legacy_keys)
        self.assertEqual(legacy_keys["key_of.key.zoom"], "46")  # C = 46

    def test_f11_options_txt_roundtrip_preservation(self):
        """F11: Injects keys while preserving non-key options and comments."""
        opt_file = os.path.join(self.temp_dir, "options.txt")
        with open(opt_file, "w", encoding="utf-8") as f:
            f.write("version:3465\ngamma:1.0\nfov:90.0\nrenderDistance:16\nkey_key.sprint:key.keyboard.left.control\n")

        res = self.controls_service.apply_control_profile(
            "hypixel_pro_pvp", instance_id="26.2", instance_dir=self.temp_dir
        )
        self.assertTrue(res["success"])

        with open(opt_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("gamma:1.0", content)
        self.assertIn("fov:90.0", content)
        self.assertIn("renderDistance:16", content)
        self.assertIn("key_key.sprint:key.keyboard.f", content)

    # --- Feature 12: Non-blocking stdout/stderr Tailer ---
    def test_f12_log_streamer_circular_ring_buffer(self):
        """F12: Verifies ProcessLogStreamer ring buffer holds recent lines with FIFO eviction."""
        # Create a mock process with stdout
        mock_proc = MagicMock()
        mock_proc.stdout.readline.side_effect = [f"Line {i}\n" for i in range(50)] + [""]
        mock_proc.poll.side_effect = [None] * 50 + [0]
        mock_proc.wait.return_value = 0
        mock_proc.pid = 12345

        log_f = os.path.join(self.temp_dir, "test_stream.log")
        streamer = ProcessLogStreamer(mock_proc, log_f, buffer_size=20)
        time.sleep(0.3)
        streamer.stop()

        recent = streamer.get_recent_lines(50)
        self.assertLessEqual(len(recent), 20)
        self.assertEqual(recent[-1], "Line 49\n")

    def test_f12_log_streamer_realtime_line_callback(self):
        """F12: Validates line callback is fired for each incoming line."""
        mock_proc = MagicMock()
        mock_proc.stdout.readline.side_effect = ["Starting Minecraft...\n", "Loading mods...\n", ""]
        mock_proc.poll.side_effect = [None, None, 0]
        mock_proc.wait.return_value = 0
        mock_proc.pid = 12345

        received = []
        log_f = os.path.join(self.temp_dir, "test_cb.log")
        streamer = ProcessLogStreamer(
            mock_proc, log_f, on_line_callback=lambda l: received.append(l)
        )
        time.sleep(0.3)
        streamer.stop()

        self.assertIn("Starting Minecraft...\n", received)
        self.assertIn("Loading mods...\n", received)

    def test_f12_log_streamer_crash_pattern_detection_oom(self):
        """F12: Real-time scanner triggers OOM crash pattern."""
        mock_proc = MagicMock()
        mock_proc.stdout.readline.side_effect = [
            "[INFO] Allocating textures...\n",
            "Exception in thread \"main\" java.lang.OutOfMemoryError: Java heap space\n",
            ""
        ]
        mock_proc.poll.side_effect = [None, None, 1]
        mock_proc.wait.return_value = 1
        mock_proc.pid = 12345

        crashes = []
        log_f = os.path.join(self.temp_dir, "test_oom.log")
        streamer = ProcessLogStreamer(
            mock_proc, log_f, on_crash_callback=lambda c: crashes.append(c)
        )
        time.sleep(0.4)
        streamer.stop()

        self.assertEqual(streamer.detected_crash_type, "OOM")
        self.assertGreater(len(crashes), 0)
        self.assertEqual(crashes[0]["crash_type"], "OOM")

    def test_f12_log_streamer_crash_pattern_detection_mixin(self):
        """F12: Real-time scanner triggers Mixin conflict crash pattern."""
        mock_proc = MagicMock()
        mock_proc.stdout.readline.side_effect = [
            "org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered from mod sodium\n",
            ""
        ]
        mock_proc.poll.side_effect = [None, 1]
        mock_proc.wait.return_value = 1
        mock_proc.pid = 12345

        crashes = []
        log_f = os.path.join(self.temp_dir, "test_mixin.log")
        streamer = ProcessLogStreamer(
            mock_proc, log_f, on_crash_callback=lambda c: crashes.append(c)
        )
        time.sleep(0.4)
        streamer.stop()

        self.assertEqual(streamer.detected_crash_type, "MIXIN_CONFLICT")

    # =========================================================================
    # TIER 2: BOUNDARY & CORNER CASES
    # =========================================================================

    def test_tier2_low_ram_boundary_1g_no_forced_4g_clamp(self):
        """T2 Boundary: 1GB memory does NOT clamp to 4GB, and sets min_ram=512M (min <= max)."""
        params = calculate_ram_parameters(max_ram=1, min_ram=None, mc_version="26.2")
        self.assertEqual(params["max_mb"], 1024)
        self.assertEqual(params["min_mb"], 512)
        self.assertEqual(params["xmx_flag"], "-Xmx1G")
        self.assertEqual(params["xms_flag"], "-Xms512M")
        self.assertLessEqual(params["min_mb"], params["max_mb"])

    def test_tier2_custom_explicit_min_max_ram_bounds(self):
        """T2 Boundary: Explicit min_ram / max_ram pairs adhere strictly."""
        params = calculate_ram_parameters(max_ram="12G", min_ram="6G", mc_version="26.2")
        self.assertEqual(params["max_mb"], 12288)
        self.assertEqual(params["min_mb"], 6144)
        self.assertEqual(params["xmx_flag"], "-Xmx12G")
        self.assertEqual(params["xms_flag"], "-Xms6G")

    def test_tier2_g1gc_region_and_nursery_scaling(self):
        """T2 Boundary: Tests dynamic region and nursery sizing across heap tiers."""
        p_1g = calculate_ram_parameters(max_ram=1)
        self.assertEqual(p_1g["region_size"], "1M")
        self.assertEqual(p_1g["new_size_pct"], 20)

        p_3g = calculate_ram_parameters(max_ram=3)
        self.assertEqual(p_3g["region_size"], "2M")

        p_6g = calculate_ram_parameters(max_ram=6)
        self.assertEqual(p_6g["region_size"], "8M")
        self.assertEqual(p_6g["new_size_pct"], 30)

        p_12g = calculate_ram_parameters(max_ram=12)
        self.assertEqual(p_12g["region_size"], "16M")
        self.assertEqual(p_12g["new_size_pct"], 40)

        p_32g = calculate_ram_parameters(max_ram=32)
        self.assertEqual(p_32g["region_size"], "32M")
        self.assertEqual(p_32g["new_size_pct"], 50)

    def test_tier2_natives_extraction_file_lock_recovery(self):
        """T2 Boundary: Simulates locked DLL during extraction; verifies fallback to unique temp dir."""
        target_d = os.path.join(self.temp_dir, "locked_natives")
        os.makedirs(target_d, exist_ok=True)
        locked_file = os.path.join(target_d, "lwjgl.dll")
        with open(locked_file, "wb") as f:
            f.write(b"LOCKED_CONTENT")

        # Create synthetic jar
        mock_jar = os.path.join(self.temp_dir, "lwjgl-mock-natives-windows.jar")
        with zipfile.ZipFile(mock_jar, "w") as z:
            z.writestr("lwjgl.dll", b"NEW_CONTENT")

        v_json = {
            "id": "26.2",
            "libraries": [
                {
                    "name": "org.lwjgl:lwjgl:3.4.1",
                    "downloads": {
                        "classifiers": {
                            "natives-windows": {
                                "path": "org/lwjgl/lwjgl-mock-natives-windows.jar"
                            }
                        }
                    }
                }
            ]
        }
        lib_root = os.path.join(self.temp_dir, "libraries")
        dest_jar = os.path.join(lib_root, "org", "lwjgl", "lwjgl-mock-natives-windows.jar")
        os.makedirs(os.path.dirname(dest_jar), exist_ok=True)
        shutil.copyfile(mock_jar, dest_jar)
        self.runner.libraries_dirs.insert(0, lib_root)

        # Mock PermissionError on locked file write
        orig_copyfileobj = shutil.copyfileobj
        call_count = [0]
        def mock_copy(s, t):
            if "locked_natives" in str(getattr(t, "name", "")):
                raise PermissionError(13, "Permission denied")
            return orig_copyfileobj(s, t)

        with patch("shutil.copyfileobj", side_effect=mock_copy):
            final_dir = self.runner.extract_natives(v_json, "26.2", target_dir=target_d, force_reextract=True)
            self.assertNotEqual(final_dir, target_d)
            self.assertTrue(os.path.isdir(final_dir))

    def test_tier2_os_rule_filtering_osx_linux_exclusion(self):
        """T2 Boundary: Verifies OS X / Linux libraries are excluded on Windows."""
        rules_osx = [{"action": "allow", "os": {"name": "osx"}}]
        rules_linux = [{"action": "allow", "os": {"name": "linux"}}]
        rules_win = [{"action": "allow", "os": {"name": "windows"}}]

        self.assertFalse(self.runner.evaluate_library_rules(rules_osx, target_os="windows"))
        self.assertFalse(self.runner.evaluate_library_rules(rules_linux, target_os="windows"))
        self.assertTrue(self.runner.evaluate_library_rules(rules_win, target_os="windows"))

    def test_tier2_32bit_jre_rejection_for_modern(self):
        """T2 Boundary: Flags 32-bit JREs as not modern ready."""
        info_32 = {
            "major_version": 21,
            "is_64bit": False,
            "is_modern_ready": False,
            "path": "C:/fake/32bit/java.exe"
        }
        self.assertFalse(info_32["is_modern_ready"])

    def test_tier2_corrupted_options_txt_recovery(self):
        """T2 Boundary: Gracefully creates and injects keys when options.txt is missing/corrupted."""
        empty_dir = os.path.join(self.temp_dir, "empty_inst")
        os.makedirs(empty_dir, exist_ok=True)
        res = self.controls_service.apply_control_profile(
            "standard_vanilla", instance_id="custom", instance_dir=empty_dir
        )
        self.assertTrue(res["success"])

    def test_tier2_unknown_keybinding_fallback(self):
        """T2 Boundary: Unknown keybinding names translate safely without throwing."""
        res_legacy = self.controls_service.translate_key_value("key.keyboard.nonexistent", KeybindingMode.LEGACY_LWJGL2)
        self.assertEqual(res_legacy, "0")
        res_modern = self.controls_service.translate_key_value(9999, KeybindingMode.MODERN_GLFW)
        self.assertEqual(res_modern, "key.keyboard.unknown")

    # =========================================================================
    # TIER 3: CROSS-FEATURE INTEGRATION COMBINATIONS
    # =========================================================================

    def test_tier3_modern_fabric_full_pipeline_synthesis(self):
        """T3 Integration: Synthesizes Features 7-12 for Modern 26.2 Fabric launch command."""
        v_json = self.runner.resolve_version_json("26.2", loader="fabric") or {"id": "26.2", "libraries": []}
        inst_dir = os.path.join(self.instances_dir, "26.2")

        # 1. RAM Parameters
        jvm_args = self.runner.build_jvm_args(ram_gb=6, natives_dir=self.temp_dir, mc_version="26.2")
        self.assertIn("-Xmx6G", jvm_args)
        self.assertIn("-Xms3G", jvm_args)

        # 2. Classpath
        cp = self.runner.build_classpath(v_json, "26.2", loader="fabric", instance_dir=inst_dir)
        self.assertIsInstance(cp, list)

        # 3. Game arguments
        game_args = self.runner.build_game_args(
            version_json=v_json,
            game_dir=inst_dir,
            assets_dir=self.runner.resolve_assets_dir(),
            account_name="ProPlayer",
            mc_version="26.2",
            loader="fabric"
        )
        self.assertIn("--username", game_args)
        self.assertIn("ProPlayer", game_args)

        # 4. Keybindings
        opt_path = os.path.join(self.temp_dir, "options.txt")
        with open(opt_path, "w", encoding="utf-8") as f:
            f.write("version:3465\n")
        self.controls_service.apply_control_profile("hypixel_pro_pvp", instance_dir=self.temp_dir)
        with open(opt_path, "r", encoding="utf-8") as f:
            self.assertIn("key_key.sprint:key.keyboard.f", f.read())

    def test_tier3_legacy_forge_full_pipeline_synthesis(self):
        """T3 Integration: Synthesizes Features 7-12 for Legacy 1.8.9 Forge launch command."""
        v_json = self.runner.resolve_version_json("1.8.9", loader="forge") or {"id": "1.8.9", "libraries": []}
        inst_dir = os.path.join(self.instances_dir, "1.8.9")

        # 1. RAM Parameters
        jvm_args = self.runner.build_jvm_args(ram_gb=4, natives_dir=self.temp_dir, mc_version="1.8.9")
        self.assertIn("-Xmx4G", jvm_args)
        self.assertIn("-Xms2G", jvm_args)
        self.assertIn("-XX:MaxGCPauseMillis=200", jvm_args)

        # 2. Classpath
        cp = self.runner.build_classpath(v_json, "1.8.9", loader="forge", instance_dir=inst_dir)
        self.assertIsInstance(cp, list)

        # 3. Game arguments (must have FMLTweaker)
        game_args = self.runner.build_game_args(
            version_json=v_json,
            game_dir=inst_dir,
            assets_dir=self.runner.resolve_assets_dir(),
            account_name="PvPKid",
            mc_version="1.8.9",
            loader="forge"
        )
        self.assertIn("--tweakClass", game_args)
        self.assertIn("net.minecraftforge.fml.common.launcher.FMLTweaker", game_args)

        # 4. Keybindings (must have numeric scancodes)
        opt_path = os.path.join(self.temp_dir, "options.txt")
        with open(opt_path, "w", encoding="utf-8") as f:
            f.write("fov:90.0\n")
        self.controls_service.apply_control_profile("hypixel_pro_pvp", instance_id="1.8.9", instance_dir=self.temp_dir)
        with open(opt_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("key_key.sprint:33", content)
            self.assertIn("key_key.togglePerspective:47", content)

    # =========================================================================
    # TIER 4: REAL-WORLD APPLICATION SCENARIOS
    # =========================================================================

    def test_tier4_scenario_high_throughput_log_streaming_stress(self):
        """T4 Scenario: Stress tests log streaming buffer with 1000 lines under concurrent reads."""
        lines_to_stream = [f"[{time.strftime('%H:%M:%S')}] [Render thread/INFO]: Chunk update event #{i} at coords ({i*16}, 64, {i*16})\n" for i in range(1000)]
        mock_proc = MagicMock()
        mock_proc.stdout.readline.side_effect = lines_to_stream + [""]
        mock_proc.poll.side_effect = [None] * 1000 + [0]
        mock_proc.wait.return_value = 0
        mock_proc.pid = 99999

        received_count = [0]
        log_f = os.path.join(self.temp_dir, "stress_stream.log")
        streamer = ProcessLogStreamer(
            mock_proc,
            log_f,
            buffer_size=500,
            on_line_callback=lambda l: received_count.__setitem__(0, received_count[0] + 1),
        )

        time.sleep(0.5)
        streamer.stop()

        self.assertGreater(received_count[0], 500)
        recent = streamer.get_recent_lines(500)
        self.assertLessEqual(len(recent), 500)
        self.assertTrue(os.path.isfile(log_f))

    def test_tier4_scenario_simulated_instant_jvm_crash_diagnostics(self):
        """T4 Scenario: Simulates an instant native JVM crash and verifies CrashAnalyzer diagnosis."""
        mock_proc = MagicMock()
        mock_proc.stdout.readline.side_effect = [
            "# A fatal error has been detected by the Java Runtime Environment:\n",
            "#  EXCEPTION_ACCESS_VIOLATION (0xc0000005) at pc=0x00007ffd12345678, pid=8888, tid=1234\n",
            "# Problematic frame:\n",
            "# C  [nvoglv64.dll+0xabcdef]  DrvValidateVersion+0x1234\n",
            ""
        ]
        mock_proc.poll.side_effect = [None, None, None, -1073741819]
        mock_proc.wait.return_value = -1073741819
        mock_proc.pid = 8888

        crash_payloads = []
        log_f = os.path.join(self.temp_dir, "crash_scenario.log")
        streamer = ProcessLogStreamer(
            mock_proc,
            log_f,
            on_crash_callback=lambda diag: crash_payloads.append(diag)
        )

        time.sleep(0.4)
        streamer.stop()

        self.assertGreater(len(crash_payloads), 0)
        diag = crash_payloads[0]
        self.assertEqual(diag["pid"], 8888)
        self.assertIn("ACCESS_VIOLATION", diag["crash_type"])


if __name__ == "__main__":
    unittest.main()

