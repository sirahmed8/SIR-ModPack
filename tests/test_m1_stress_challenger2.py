"""
test_m1_stress_challenger2.py — Empirical Challenger 2 Adversarial Stress Suite for Milestone 1.

Rigorously tests:
1. CrashAnalyzer against hostile, malformed, multi-exception, and native crash dumps.
2. TelemetryGovernorService & HardwareMonitorService under rapid polling, multi-threading, invalid PIDs, and EmptyWorkingSet memory trimming.
3. Zero Mock compliance across CleanerService, RepairService, SatelliteService, and JavaService with real disk, crypto, socket, and registry operations.
"""
import ctypes
import hashlib
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEV_DIR = os.path.join(ROOT_DIR, "development")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.crash_analyzer import CrashAnalyzer
from launcher_core.telemetry_governor_service import TelemetryGovernorService
from launcher_core.hardware_monitor_service import HardwareMonitorService
from launcher_core.cleaner_service import CleanerService
from launcher_core.repair_service import RepairService
from launcher_core.satellite_service import SatelliteService
from launcher_core.java_service import JavaService


class TestM1EmpiricalStress(unittest.TestCase):
    """Adversarial stress and verification tests for Milestone 1 components."""

    # =========================================================================
    # 1. CRASH REPORT ANALYZER ADVERSARIAL TESTS
    # =========================================================================

    def test_crash_analyzer_empty_and_hostile_inputs(self):
        """Stress CrashAnalyzer with empty, whitespace, binary garbage, and arbitrary text."""
        # Empty string
        res = CrashAnalyzer.diagnose_crash("")
        self.assertEqual(res["type"], "UNKNOWN")

        # Whitespace
        res_ws = CrashAnalyzer.diagnose_crash("   \n\r\t   ")
        self.assertEqual(res_ws["type"], "GENERIC_CRASH")

        # Arbitrary normal log output
        res_log = CrashAnalyzer.diagnose_crash(
            "[23:00:00] [main/INFO]: Loading Minecraft 1.20.1 with Fabric Loader 0.15.11\n"
            "[23:00:01] [main/INFO]: SpongePowered MIXIN Subsystem Version 0.8.5\n"
            "[23:00:05] [main/INFO]: Game initialized successfully."
        )
        self.assertEqual(res_log["type"], "GENERIC_CRASH")

    def test_crash_analyzer_native_dumps_permutations(self):
        """Test JVM native crash dumps across various GPU vendors, jvm.dll, and non-standard logs."""
        # NVIDIA driver crash in hs_err_pid
        nvidia_dump = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# EXCEPTION_ACCESS_VIOLATION (0xc0000005) at pc=0x00007ffb8a1e321a\n"
            "# Problematic frame:\n"
            "# C  [nvoglv64.dll+0x9b321a]\n"
            "# Failed to write core dump. Minidumps are not enabled by default on Windows"
        )
        res = CrashAnalyzer.diagnose_crash(nvidia_dump, "hs_err_pid8912.log")
        self.assertEqual(res["type"], "JVM_NATIVE_CRASH")
        self.assertIn("nvoglv64.dll", res["offending_module"])
        self.assertIn("NVIDIA", res["fix"])

        # AMD Radeon driver crash
        amd_dump = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# Problematic frame:\n"
            "# C  [atio6axx.dll+0x112233]\n"
        )
        res = CrashAnalyzer.diagnose_crash(amd_dump, "hs_err_pid456.log")
        self.assertEqual(res["type"], "JVM_NATIVE_CRASH")
        self.assertIn("atio6axx.dll", res["offending_module"])
        self.assertIn("AMD", res["fix"])

        # Intel GPU crash
        intel_dump = (
            "# Problematic frame:\n"
            "# C  [ig9icd64.dll+0x445566]\n"
        )
        res = CrashAnalyzer.diagnose_crash(intel_dump, "hs_err_pid789.log")
        self.assertEqual(res["type"], "JVM_NATIVE_CRASH")
        self.assertIn("ig9icd64.dll", res["offending_module"])
        self.assertIn("Intel", res["fix"])

        # JVM Internal Crash
        jvm_dump = (
            "# Problematic frame:\n"
            "# V  [jvm.dll+0x889900]\n"
        )
        res = CrashAnalyzer.diagnose_crash(jvm_dump, "hs_err_pid1011.log")
        self.assertEqual(res["type"], "JVM_NATIVE_CRASH")
        self.assertIn("jvm.dll", res["offending_module"])
        self.assertIn("JVM engine crashed", res["fix"])

        # Native crash without 'Problematic frame' line but with hs_err filename
        raw_native = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "Stack: [0x000000a12b, 0x000000a1cb], sp=0x000000a12a, free space=1020k\n"
            "Native frames: (J=compiled Java code, j=interpreted, Vv=VM code, C=native code)\n"
            "C  [OpenAL64.dll+0x1234]\n"
        )
        res = CrashAnalyzer.diagnose_crash(raw_native, "hs_err_pid999.log")
        self.assertEqual(res["type"], "JVM_NATIVE_CRASH")

    def test_crash_analyzer_oom_spectrum(self):
        """Test all 5 Out-Of-Memory distinct failure modes."""
        cases = [
            ("java.lang.OutOfMemoryError: Direct buffer memory", "DIRECT_MEMORY_EXHAUSTION"),
            ("java.lang.OutOfMemoryError: Metaspace", "METASPACE_EXHAUSTION"),
            ("java.lang.OutOfMemoryError: GC overhead limit exceeded", "GC_OVERHEAD_EXHAUSTION"),
            ("java.lang.OutOfMemoryError: unable to create new native thread", "THREAD_CREATION_EXHAUSTION"),
            ("java.lang.OutOfMemoryError: Java heap space", "OUT_OF_MEMORY"),
        ]
        for log_text, expected_type in cases:
            res = CrashAnalyzer.diagnose_crash(f"Exception in thread 'main' {log_text}\n\tat net.minecraft.client.Main.main")
            self.assertEqual(res["type"], expected_type, f"Failed for {log_text}")

    def test_crash_analyzer_class_version_incompatibility(self):
        """Test UnsupportedClassVersionError extraction and version mapping."""
        # Java 21 class (65.0) on Java 8 (52.0)
        trace_j21_on_j8 = (
            "java.lang.UnsupportedClassVersionError: net/sir/mod/Main has been compiled by a more recent "
            "version of the Java Runtime (class file version 65.0), this version of the Java Runtime only recognizes "
            "class file versions up to 52.0"
        )
        res = CrashAnalyzer.diagnose_crash(trace_j21_on_j8)
        self.assertEqual(res["type"], "JAVA_VERSION_MISMATCH")
        self.assertEqual(res["required_java"], "Java 21")
        self.assertEqual(res["running_java"], "Java 8")

        # Java 17 class (61.0) on Java 16 (60.0)
        trace_j17 = (
            "java.lang.UnsupportedClassVersionError: com/example/Mod (class file version 61.0), "
            "this version of the Java Runtime only recognizes class file versions up to 60.0"
        )
        res = CrashAnalyzer.diagnose_crash(trace_j17)
        self.assertEqual(res["type"], "JAVA_VERSION_MISMATCH")
        self.assertEqual(res["required_java"], "Java 17")
        self.assertEqual(res["running_java"], "Java 16")

    def test_crash_analyzer_mixin_and_dependencies(self):
        """Test complex Fabric & Forge mixin conflict diagnostics and dependency mappings."""
        # Complex Mixin
        mixin_trace = (
            "org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered\n"
            "\tat org.spongepowered.asm.mixin.transformer.MixinProcessor.applyMixins(MixinProcessor.java:392)\n"
            "Caused by: org.spongepowered.asm.mixin.injection.throwables.InjectionError: "
            "Mixin [sodium.mixins.core.json:render.WorldRendererMixin from mod sodium] FAILED during APPLY\n"
            "Mixin transformation of net.minecraft.client.render.WorldRenderer failed"
        )
        res = CrashAnalyzer.diagnose_crash(mixin_trace)
        self.assertEqual(res["type"], "MIXIN_CONFLICT")
        self.assertEqual(res["offending_mod"], "sodium")
        self.assertIn("WorldRenderer", res["target_class"])

        # Missing Dependency: trove4j
        dep_trace = "java.lang.NoClassDefFoundError: gnu/trove/map/TIntObjectMap\n\tat net.minecraftforge.fml.common.FMLCommonHandler"
        res_dep = CrashAnalyzer.diagnose_crash(dep_trace)
        self.assertEqual(res_dep["type"], "MISSING_DEPENDENCY")
        self.assertIn("trove4j", res_dep["cause"])

        # Missing Dependency: Cloth Config
        cloth_trace = "java.lang.ClassNotFoundException: me.shedaniel.clothconfig2.api.ConfigBuilder"
        res_cloth = CrashAnalyzer.diagnose_crash(cloth_trace)
        self.assertEqual(res_cloth["type"], "MISSING_DEPENDENCY")
        self.assertIn("Cloth Config", res_cloth["cause"])

    # =========================================================================
    # 2. TELEMETRY GOVERNOR & HARDWARE MONITOR STRESS TESTS
    # =========================================================================

    def test_hardware_monitor_live_win32_metrics(self):
        """Verify HardwareMonitorService queries live Win32 kernel structures."""
        if sys.platform != "win32":
            self.skipTest("Live hardware monitor metrics query Win32 kernel structures")
        hw = HardwareMonitorService()
        telemetry = hw.get_hardware_telemetry()

        self.assertTrue(telemetry["success"])
        self.assertGreater(telemetry["total_ram_gb"], 0.0)
        self.assertGreater(telemetry["avail_ram_gb"], 0.0)
        self.assertGreaterEqual(telemetry["used_ram_gb"], 0.0)
        self.assertGreaterEqual(telemetry["ram_load_pct"], 0)
        self.assertLessEqual(telemetry["ram_load_pct"], 100)
        self.assertGreaterEqual(telemetry["cpu_cores"], 1)
        self.assertGreaterEqual(telemetry["cpu_load_pct"], 0)
        self.assertLessEqual(telemetry["cpu_load_pct"], 100)
        self.assertIn(telemetry["recommended_ram_gb"], [2, 3, 6, 8, 10])
        self.assertIsInstance(telemetry["all_gpus"], list)

    def test_telemetry_governor_process_tracking(self):
        """Verify live Win32 process tracking for the current Python process."""
        if sys.platform != "win32":
            self.skipTest("Telemetry governor process tracking is Win32-specific")
        gov = TelemetryGovernorService.get_instance()
        current_pid = os.getpid()

        res = gov.get_process_telemetry(current_pid)
        self.assertTrue(res["success"])
        self.assertEqual(res["pid"], current_pid)
        self.assertGreater(res["working_set_mb"], 0.0)
        self.assertGreater(res["private_commit_mb"], 0.0)
        self.assertGreaterEqual(res["peak_working_set_mb"], res["working_set_mb"])
        self.assertGreaterEqual(res["cpu_load_pct"], 0.0)

    def test_telemetry_governor_high_frequency_and_thread_safety(self):
        """Stress CPU delta calculations under rapid polling and concurrent threads."""
        if sys.platform != "win32":
            self.skipTest("Telemetry governor process tracking is Win32-specific")
        gov = TelemetryGovernorService.get_instance()
        pid = os.getpid()

        # Rapid serial calls must not divide by zero
        for _ in range(50):
            res = gov.get_process_telemetry(pid)
            self.assertTrue(res["success"])
            self.assertGreaterEqual(res["cpu_load_pct"], 0.0)

        # Multi-threaded concurrent telemetry polling
        def _poll():
            for _ in range(20):
                r = gov.get_process_telemetry(pid)
                self.assertTrue(r["success"])

        threads = [threading.Thread(target=_poll) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def test_telemetry_governor_invalid_and_nonexistent_pids(self):
        """Verify handling of invalid, zero, negative, and dead PIDs."""
        if sys.platform != "win32":
            self.skipTest("Telemetry governor process tracking is Win32-specific")
        gov = TelemetryGovernorService.get_instance()

        # PID 0 or negative
        self.assertFalse(gov.get_process_telemetry(0)["success"])
        self.assertFalse(gov.get_process_telemetry(-10)["success"])

        # Non-existent high PID
        res = gov.get_process_telemetry(9999999)
        self.assertFalse(res["success"])
        self.assertIn("not running or access denied", res["error"])

    def test_telemetry_governor_empty_working_set_memory_trimming(self):
        """Empirically test EmptyWorkingSet Win32 memory page flushing."""
        if sys.platform != "win32":
            self.skipTest("EmptyWorkingSet is Win32 specific")

        gov = TelemetryGovernorService.get_instance()
        current_pid = os.getpid()

        # Trim current process
        trim_res = gov.trim_process_memory(current_pid)
        self.assertTrue(trim_res["success"])
        self.assertGreater(trim_res["before_mb"], 0.0)
        self.assertGreater(trim_res["after_mb"], 0.0)
        self.assertGreaterEqual(trim_res["freed_mb"], 0.0)
        self.assertIn("Memory Governor trimmed", trim_res["message"])

        # Trim invalid PID
        dead_trim = gov.trim_process_memory(9999999)
        self.assertFalse(dead_trim["success"])

    # =========================================================================
    # 3. ZERO MOCK COMPLIANCE & EMPIRICAL SERVICES AUDIT
    # =========================================================================

    def test_cleaner_service_zero_mock_real_disk_operations(self):
        """Empirically verify CleanerService performs genuine file inspection and deletion without hardcoded metrics."""
        temp_dir = tempfile.mkdtemp(prefix="sir_test_cleaner_")
        try:
            # Create synthetic target structure
            logs_dir = os.path.join(temp_dir, "logs")
            temp_sub = os.path.join(temp_dir, ".temp")
            os.makedirs(logs_dir)
            os.makedirs(temp_sub)

            # Write 5 real files totaling exactly 5000 bytes
            f1 = os.path.join(logs_dir, "latest.log")
            f2 = os.path.join(logs_dir, "debug-1.log")
            f3 = os.path.join(temp_sub, "chunk.tmp")
            with open(f1, "wb") as f:
                f.write(b"A" * 2000)
            with open(f2, "wb") as f:
                f.write(b"B" * 2000)
            with open(f3, "wb") as f:
                f.write(b"C" * 1000)

            cleaner = CleanerService(temp_dir)

            # Dry Run Analysis
            analysis = cleaner.analyze_storage()
            self.assertTrue(analysis["success"])
            self.assertTrue(analysis["dry_run"])
            self.assertEqual(analysis["cleaned_files"], 3)
            self.assertEqual(analysis["cleaned_bytes"], 5000)
            self.assertTrue(os.path.isfile(f1))  # Must NOT delete on dry run

            # Real Cleaning Run
            clean_res = cleaner.run_deep_clean(dry_run=False)
            self.assertTrue(clean_res["success"])
            self.assertFalse(clean_res["dry_run"])
            self.assertEqual(clean_res["cleaned_files"], 3)
            self.assertEqual(clean_res["cleaned_bytes"], 5000)
            self.assertFalse(os.path.isfile(f1))  # Must be removed from disk
            self.assertFalse(os.path.isfile(f2))
            self.assertFalse(os.path.isfile(f3))

            # Subsequent Run should find 0 files
            clean_again = cleaner.run_deep_clean(dry_run=False)
            self.assertEqual(clean_again["cleaned_files"], 0)
            self.assertEqual(clean_again["cleaned_bytes"], 0)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_repair_service_zero_mock_sha256_and_zip_quarantine(self):
        """Empirically verify RepairService SHA-256 calculation, CRC verification, and quarantine of corrupted jars."""
        temp_dir = tempfile.mkdtemp(prefix="sir_test_repair_")
        try:
            mods_dir = os.path.join(temp_dir, "mods")
            os.makedirs(mods_dir)

            # 1. Valid Jar archive
            valid_jar = os.path.join(mods_dir, "valid-mod.jar")
            with zipfile.ZipFile(valid_jar, "w") as zf:
                zf.writestr("fabric.mod.json", '{"id": "valid_mod", "version": "1.0.0"}')
                zf.writestr("com/example/Mod.class", b"\xca\xfe\xba\xbe\x00\x00\x00\x34")

            # Compute real SHA-256
            hasher = hashlib.sha256()
            with open(valid_jar, "rb") as f:
                hasher.update(f.read())
            real_sha = hasher.hexdigest()

            repair = RepairService(temp_dir)

            # Verify valid file
            v_res = repair.verify_file_integrity(valid_jar, expected_sha256=real_sha)
            self.assertTrue(v_res["valid"])
            self.assertEqual(v_res["sha256"], real_sha)

            # Verify sha256 mismatch detection
            bad_hash_res = repair.verify_file_integrity(valid_jar, expected_sha256="0" * 64)
            self.assertFalse(bad_hash_res["valid"])
            self.assertIn("SHA-256 mismatch", bad_hash_res["reason"])

            # 2. Corrupted Jar archive (invalid zip header / truncated zip)
            corrupted_jar = os.path.join(mods_dir, "corrupted-mod.jar")
            with open(corrupted_jar, "wb") as f:
                f.write(b"PK\x03\x04corrupted binary garbage data here that cannot be unzipped")

            c_res = repair.verify_file_integrity(corrupted_jar)
            self.assertFalse(c_res["valid"])
            self.assertIn("Invalid archive structure", c_res["reason"])

            # Run full self-repair scan
            repair_run = repair.run_self_repair()
            self.assertTrue(repair_run["success"])
            self.assertEqual(repair_run["verified_count"], 1)
            self.assertEqual(repair_run["corrupted_count"], 1)
            self.assertEqual(repair_run["quarantined_count"], 1)

            # Ensure corrupted jar was renamed to .corrupted
            self.assertFalse(os.path.exists(corrupted_jar))
            self.assertTrue(os.path.exists(corrupted_jar + ".corrupted"))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_satellite_service_zero_mock_live_sockets(self):
        """Empirically test SatelliteService socket connectivity and latency calculation."""
        sat = SatelliteService()
        status = sat.get_satellite_status()

        self.assertIn("satellite_mesh", status)
        self.assertIn("network_status", status)
        self.assertIsInstance(status["nodes"], list)
        self.assertEqual(len(status["nodes"]), 6)

        # Check node schemas
        for n in status["nodes"]:
            self.assertIn("id", n)
            self.assertIn("host", n)
            self.assertIn("port", n)
            self.assertIn("location", n)
            self.assertIn(n["status"], ["Optimal", "Operational", "High Latency", "Timed Out", "Unreachable"])
            if n["latency_ms"] is not None:
                self.assertGreater(n["latency_ms"], 0)

    def test_java_service_zero_mock_discovery(self):
        """Empirically verify JavaService probes registry, PATH, and parses real JVM output."""
        js = JavaService()
        res = js.discover_java_installations()

        self.assertTrue(res["success"])
        self.assertIsInstance(res["installations"], list)
        self.assertGreaterEqual(res["count"], 0)

        # If any java installations were discovered, check their fields
        for item in res["installations"]:
            self.assertIn("name", item)
            self.assertIn("version", item)
            self.assertIn("path", item)
            self.assertTrue(os.path.isfile(item["path"]), f"Java path {item['path']} does not exist on disk")


if __name__ == "__main__":
    unittest.main()
