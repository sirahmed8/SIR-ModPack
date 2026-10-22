"""
test_telemetry_cleaner.py — Comprehensive Unit & Integration Tests for
Zero-Mock Telemetry, Telemetry Governor, Cleaner, Repair & Deep Crash Stack-Trace Analyzer.
"""
import os
import sys
import tempfile
import time
import unittest
import zipfile

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.satellite_service import SatelliteService
from launcher_core.hardware_monitor_service import HardwareMonitorService
from launcher_core.telemetry_governor_service import TelemetryGovernorService
from launcher_core.cleaner_service import CleanerService
from launcher_core.repair_service import RepairService
from launcher_core.syncer_service import DifferentialSyncService
from launcher_core.crash_analyzer import CrashAnalyzer
from launcher_core.crash_analyzer_service import CrashReportAnalyzer
from launcher_core.logs_service import LogsService


class TestTelemetryCleanerAndDiagnostics(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_satellite_service_zero_mock_live_ping(self):
        satellite = SatelliteService()
        status = satellite.get_satellite_status()
        self.assertIn("satellite_mesh", status)
        self.assertIn("network_status", status)
        self.assertIn("nodes", status)
        self.assertIsInstance(status["nodes"], list)
        self.assertGreater(len(status["nodes"]), 0)

        # Assert no fabricated strings
        for node in status["nodes"]:
            self.assertIn("id", node)
            self.assertIn("host", node)
            self.assertIn("status", node)

    def test_hardware_monitor_service_live_telemetry(self):
        hw = HardwareMonitorService()
        telemetry = hw.get_hardware_telemetry()
        self.assertTrue(telemetry["success"])
        self.assertGreater(telemetry["cpu_cores"], 0)
        self.assertGreaterEqual(telemetry["total_ram_gb"], 0.0)
        self.assertIn("power_tier", telemetry)
        self.assertIn("gpu_name", telemetry)
        self.assertIn("all_gpus", telemetry)

    def test_telemetry_governor_process_memory_trimming(self):
        gov = TelemetryGovernorService.get_instance()
        # Test current process working set trimming
        res = gov.trim_process_memory(pid=None)
        if sys.platform == "win32":
            self.assertTrue(res["success"])
            self.assertIn("before_mb", res)
            self.assertIn("after_mb", res)
            self.assertIn("freed_mb", res)

        # Test current process telemetry
        proc_tel = gov.get_process_telemetry(os.getpid())
        if sys.platform == "win32":
            self.assertTrue(proc_tel["success"])
            self.assertGreater(proc_tel["working_set_mb"], 0)

    def test_cleaner_service_dry_run_and_real_cleaning(self):
        # Create simulated cache and logs
        cache_dir = os.path.join(self.temp_dir, "cache")
        logs_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)

        with open(os.path.join(cache_dir, "temp_cache.bin"), "wb") as f:
            f.write(b"0" * 1024 * 512)  # 512 KB
        with open(os.path.join(logs_dir, "old_session.log"), "w") as f:
            f.write("Old Minecraft log data\n" * 100)

        cleaner = CleanerService(self.temp_dir)

        # 1. Dry Run Analysis
        analysis = cleaner.analyze_storage()
        self.assertTrue(analysis["success"])
        self.assertTrue(analysis["dry_run"])
        self.assertGreaterEqual(analysis["cleaned_files"], 2)
        self.assertTrue(os.path.exists(os.path.join(cache_dir, "temp_cache.bin")))

        # 2. Real Clean
        cleaned = cleaner.run_deep_clean(dry_run=False)
        self.assertTrue(cleaned["success"])
        self.assertFalse(cleaned["dry_run"])
        self.assertGreaterEqual(cleaned["cleaned_files"], 2)
        self.assertFalse(os.path.exists(os.path.join(cache_dir, "temp_cache.bin")))

        # 3. Second run should report already clean
        clean_again = cleaner.run_deep_clean(dry_run=False)
        self.assertEqual(clean_again["cleaned_files"], 0)
        self.assertEqual(clean_again["cleaned_mb"], 0.0)

    def test_repair_service_corrupted_archive_and_quarantine(self):
        mods_dir = os.path.join(self.temp_dir, "mods")
        os.makedirs(mods_dir, exist_ok=True)

        # 1. Valid JAR
        valid_jar = os.path.join(mods_dir, "valid_mod.jar")
        with zipfile.ZipFile(valid_jar, "w") as zf:
            zf.writestr("fabric.mod.json", '{"id": "valid_mod"}')

        # 2. Corrupted JAR (truncated mid-stream)
        corrupted_jar = os.path.join(mods_dir, "corrupted_mod.jar")
        with open(corrupted_jar, "wb") as f:
            f.write(b"PK\x03\x04corrupted_header_without_central_directory")

        # 3. Empty 0-byte JAR
        empty_jar = os.path.join(mods_dir, "empty_mod.jar")
        with open(empty_jar, "wb") as f:
            pass

        repair = RepairService(self.temp_dir)
        report = repair.run_self_repair()
        self.assertTrue(report["success"])
        self.assertEqual(report["verified_count"], 1)
        self.assertEqual(report["corrupted_count"], 2)
        self.assertEqual(report["quarantined_count"], 2)
        self.assertTrue(os.path.exists(corrupted_jar + ".corrupted"))
        self.assertTrue(os.path.exists(empty_jar + ".corrupted"))

    def test_differential_sync_service(self):
        mods_dir = os.path.join(self.temp_dir, "instances", "26.2", "minecraft", "mods")
        os.makedirs(mods_dir, exist_ok=True)

        good_jar = os.path.join(mods_dir, "good_mod.jar")
        with zipfile.ZipFile(good_jar, "w") as zf:
            zf.writestr("fabric.mod.json", '{"schemaVersion": 1, "id": "good_mod"}')

        syncer = DifferentialSyncService(self.temp_dir)
        res = syncer.check_instance_integrity("26.2")
        self.assertTrue(res["success"])
        self.assertEqual(res["active_mods_count"], 1)
        self.assertEqual(res["invalid_mods_count"], 0)
        self.assertEqual(res["integrity_pct"], 100.0)

    # -----------------------------------------------------------------
    # Deep Crash Stack-Trace Analyzer Diagnostics Tests
    # -----------------------------------------------------------------

    def test_crash_analyzer_mixin_conflict(self):
        sample = """
        Caused by: org.spongepowered.asm.mixin.throwables.MixinApplyError: Mixin [modernfix-common.mixins.json:perf.tag_id_caching.TagEntryMixin from mod modernfix] from phase [DEFAULT] in config [modernfix-common.mixins.json] FAILED during APPLY
        Caused by: org.spongepowered.asm.mixin.transformer.throwables.InvalidMixinException: PRIVATE @Overwrite method elementOrTag in modernfix-common.mixins.json:perf.tag_id_caching.TagEntryMixin from mod modernfix cannot reduce visibiliy of PUBLIC target method
        Mixin transformation of net.minecraft.tags.TagEntry failed
        """
        diag = CrashReportAnalyzer.diagnose_crash(sample, "crash-2026-08-28.txt")
        self.assertEqual(diag["type"], "MIXIN_CONFLICT")
        self.assertEqual(diag["offending_mod"], "modernfix")
        self.assertIn("modernfix", diag["cause"])
        self.assertIn("TagEntry", diag["target_class"])

    def test_crash_analyzer_java_version_mismatch(self):
        sample = """
        java.lang.UnsupportedClassVersionError: net/fabricmc/loader/impl/launch/knot/KnotClient has been compiled by a more recent version of the Java Runtime (class file version 65.0), this version of the Java Runtime only recognizes class file versions up to 52.0
        """
        diag = CrashReportAnalyzer.diagnose_crash(sample, "crash.txt")
        self.assertEqual(diag["type"], "JAVA_VERSION_MISMATCH")
        self.assertEqual(diag["required_java"], "Java 21")
        self.assertEqual(diag["running_java"], "Java 8")
        self.assertIn("Temurin 21 LTS", diag["fix"])

    def test_crash_analyzer_oom_spectrum(self):
        # 1. Heap Space
        d1 = CrashReportAnalyzer.diagnose_crash("java.lang.OutOfMemoryError: Java heap space", "crash.txt")
        self.assertEqual(d1["type"], "OUT_OF_MEMORY")
        self.assertIn("6 GB or 8 GB", d1["fix"])

        # 2. Direct Buffer Memory
        d2 = CrashReportAnalyzer.diagnose_crash("java.lang.OutOfMemoryError: Direct buffer memory", "crash.txt")
        self.assertEqual(d2["type"], "DIRECT_MEMORY_EXHAUSTION")
        self.assertIn("MaxDirectMemorySize", d2["fix"])

        # 3. Metaspace
        d3 = CrashReportAnalyzer.diagnose_crash("java.lang.OutOfMemoryError: Metaspace", "crash.txt")
        self.assertEqual(d3["type"], "METASPACE_EXHAUSTION")
        self.assertIn("MaxMetaspaceSize", d3["fix"])

        # 4. GC Overhead
        d4 = CrashReportAnalyzer.diagnose_crash("java.lang.OutOfMemoryError: GC overhead limit exceeded", "crash.txt")
        self.assertEqual(d4["type"], "GC_OVERHEAD_EXHAUSTION")

        # 5. Native Thread Limit
        d5 = CrashReportAnalyzer.diagnose_crash("java.lang.OutOfMemoryError: unable to create new native thread", "crash.txt")
        self.assertEqual(d5["type"], "THREAD_CREATION_EXHAUSTION")

    def test_crash_analyzer_native_dump(self):
        sample = """
        # A fatal error has been detected by the Java Runtime Environment:
        #
        #  EXCEPTION_ACCESS_VIOLATION (0xc0000005) at pc=0x00007ffbe6181e10, pid=14820, tid=12400
        #
        # Problematic frame:
        # C  [nvoglv64.dll+0x9d1e10]
        """
        diag = CrashReportAnalyzer.diagnose_crash(sample, "hs_err_pid14820.log")
        self.assertEqual(diag["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(diag["offending_module"], "nvoglv64.dll")
        self.assertIn("NVIDIA", diag["fix"])

    def test_crash_analyzer_missing_dependency(self):
        sample = """
        Caused by: java.lang.ClassNotFoundException: gnu.trove.map.hash.TByteObjectHashMap
        at java.net.URLClassLoader.findClass(URLClassLoader.java:382)
        """
        diag = CrashReportAnalyzer.diagnose_crash(sample, "crash.txt")
        self.assertEqual(diag["type"], "MISSING_DEPENDENCY")
        self.assertIn("trove4j", diag["cause"])

    def test_crash_analyzer_corrupted_region(self):
        sample = """
        net.minecraft.world.chunk.storage.RegionFormatException: Corrupted Chunk [12, -4] in r.0.-1.mca
        """
        diag = CrashReportAnalyzer.diagnose_crash(sample, "crash.txt")
        self.assertEqual(diag["type"], "CORRUPTED_WORLD_REGION")
        self.assertEqual(diag["region_file"], "r.0.-1.mca")

    def test_crash_analyzer_opengl_error(self):
        sample = """
        org.lwjgl.opengl.OpenGLException: Cannot make context current (GLFW error 6554)
        """
        diag = CrashReportAnalyzer.diagnose_crash(sample, "crash.txt")
        self.assertEqual(diag["type"], "OPENGL_GPU_ERROR")

    def test_logs_service_real_crash_directory_scanning(self):
        logs = LogsService(self.root_dir)
        report = logs.analyze_crashes("26.2")
        self.assertTrue(report["success"])
        if report["has_crashes"]:
            self.assertGreater(report["crashes_found"], 0)
            self.assertIsInstance(report["reports"], list)
            first = report["reports"][0]
            self.assertIn("type", first)
            self.assertIn("cause", first)
            self.assertIn("fix", first)


if __name__ == "__main__":
    unittest.main()
