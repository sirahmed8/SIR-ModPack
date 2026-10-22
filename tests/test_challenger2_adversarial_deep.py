"""
test_challenger2_adversarial_deep.py — Challenger 2 Comprehensive Adversarial Test Suite for Milestone 1.

Empirical verification and stress testing across:
1. CrashReportAnalyzer: Edge-case crash dumps, complex mixin conflicts, nested causal chains,
   unknown/out-of-range Java version strings, corrupted/hostile logs, native HotSpot hs_err_pid dumps.
2. TelemetryGovernorService: Simulated child process lifecycles, dead PIDs, invalid/extreme PIDs,
   Win32 handle lifecycle, concurrent polling, and EmptyWorkingSet memory trimming.
3. RepairService: Corrupted ZIP/JAR archives, CRC32 corruption, missing assets, backup self-healing,
   quarantine workflows, and checksum edge cases.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import shutil
import subprocess
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
from launcher_core.crash_analyzer_service import CrashReportAnalyzer
from launcher_core.telemetry_governor_service import TelemetryGovernorService
from launcher_core.repair_service import RepairService


class TestCrashAnalyzerAdversarialDeep(unittest.TestCase):
    """Adversarial stress testing for CrashAnalyzer and CrashReportAnalyzer."""

    def test_analyzer_subclass_contract_parity(self):
        """Verify CrashReportAnalyzer inherits and behaves identically to CrashAnalyzer."""
        self.assertTrue(issubclass(CrashReportAnalyzer, CrashAnalyzer))
        raw_res = CrashAnalyzer.diagnose_crash("")
        service_res = CrashReportAnalyzer.diagnose_crash("")
        self.assertEqual(raw_res, service_res)

    def test_corrupted_and_extreme_log_inputs(self):
        """Adversarially challenge analyzer with corrupted, zero-byte, binary, and extreme logs."""
        # 1. 0-byte input
        res_empty = CrashAnalyzer.diagnose_crash("")
        self.assertEqual(res_empty["type"], "UNKNOWN")
        self.assertIn("Empty crash report", res_empty["cause"])

        # 2. Whitespace and newlines only
        res_ws = CrashAnalyzer.diagnose_crash(" \t \r\n \n \t ")
        self.assertEqual(res_ws["type"], "GENERIC_CRASH")

        # 3. Binary garbage and null bytes
        binary_garbage = "DEBUG \x00\x01\x02\xff\xfe\xca\xfe\xba\xbe\x00\x00 NULL_POINTER_EXCEPTION"
        res_bin = CrashAnalyzer.diagnose_crash(binary_garbage)
        self.assertEqual(res_bin["type"], "GENERIC_CRASH")

        # 4. Format strings and prompt injection tokens
        fmt_string = "%s%s%s%n%x%d${jndi:ldap://127.0.0.1/a} {{config.secret}} <script>alert(1)</script>"
        res_fmt = CrashAnalyzer.diagnose_crash(fmt_string)
        self.assertEqual(res_fmt["type"], "GENERIC_CRASH")

        # 5. Massive 2MB log with 40,000 normal lines and 1 crash at the end (test regex performance)
        large_log = ("[2026-08-30 00:00:00] [main/INFO]: Normal line of game output...\n" * 30000)
        large_log += "java.lang.OutOfMemoryError: Java heap space\n\tat net.minecraft.client.Main.main"
        t0 = time.perf_counter()
        res_large = CrashAnalyzer.diagnose_crash(large_log)
        duration = time.perf_counter() - t0
        self.assertEqual(res_large["type"], "OUT_OF_MEMORY")
        self.assertLess(duration, 1.5, f"CrashAnalyzer took too long ({duration:.3f}s) on large log")

    def test_nested_causal_chains_and_complex_mixins(self):
        """Adversarially test deep causal exception chains and varied mixin conflict patterns."""
        # 1. Nested 5-level Caused by with Mixin at deepest level
        deep_causal = (
            "java.lang.RuntimeException: Could not execute entrypoint stage 'main'\n"
            "\tat net.fabricmc.loader.impl.entrypoint.EntrypointUtils.invoke0(EntrypointUtils.java:53)\n"
            "Caused by: net.fabricmc.loader.impl.FormattedException: Some intermediate error\n"
            "\tat net.fabricmc.loader.impl.game.minecraft.MinecraftGameProvider.launch(MinecraftGameProvider.java:470)\n"
            "Caused by: org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered\n"
            "\tat org.spongepowered.asm.mixin.transformer.MixinProcessor.applyMixins(MixinProcessor.java:392)\n"
            "Caused by: org.spongepowered.asm.mixin.injection.throwables.InjectionError: "
            "Mixin [sodium-extra.mixins.json:features.gui.OptionGuiMixin from mod sodium-extra] FAILED during APPLY\n"
            "Mixin transformation of net.minecraft.class_437 failed"
        )
        res1 = CrashAnalyzer.diagnose_crash(deep_causal)
        self.assertEqual(res1["type"], "MIXIN_CONFLICT")
        self.assertEqual(res1["offending_mod"], "sodium-extra")
        self.assertEqual(res1["target_class"], "net.minecraft.class_437")
        self.assertEqual(res1["mixin_config"], "sodium-extra.mixins.json")

        # 2. Mixin without colon in config specification
        mixin_no_colon = (
            "org.spongepowered.asm.mixin.injection.throwables.InjectionError: "
            "Mixin [WorldRendererMixin from mod iris_shaders_v2] FAILED during APPLY\n"
            "Mixin transformation of net.minecraft.client.render.WorldRenderer$ChunkInfo failed"
        )
        res2 = CrashAnalyzer.diagnose_crash(mixin_no_colon)
        self.assertEqual(res2["type"], "MIXIN_CONFLICT")
        self.assertEqual(res2["offending_mod"], "iris_shaders_v2")
        self.assertEqual(res2["target_class"], "net.minecraft.client.render.WorldRenderer$ChunkInfo")

        # 3. InvalidMixinException without FAILED keyword
        invalid_mixin = (
            "org.spongepowered.asm.mixin.transformer.throwables.InvalidMixinException: "
            "Private accessor in cloth-config.mixins.json cannot find field named 'builder' in net/minecraft/Screen "
            "from mod cloth-config"
        )
        res3 = CrashAnalyzer.diagnose_crash(invalid_mixin)
        self.assertEqual(res3["type"], "MIXIN_CONFLICT")
        self.assertEqual(res3["offending_mod"], "cloth-config")

        # 4. Mixin with complex mod ID containing hyphens, underscores, and digits
        complex_mod_id = (
            "org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: "
            "Mixin [optifine-compat-2026.mixins.json:core.OptiMixin from mod optifine-compat-2026_v3] FAILED\n"
            "Mixin transformation of net.minecraft.client.MinecraftClient failed"
        )
        res4 = CrashAnalyzer.diagnose_crash(complex_mod_id)
        self.assertEqual(res4["type"], "MIXIN_CONFLICT")
        self.assertEqual(res4["offending_mod"], "optifine-compat-2026_v3")

    def test_java_version_mismatches_standard_and_out_of_range(self):
        """Test Java class file version errors with known LTS versions and out-of-range versions."""
        # 1. Java 21 class (65.0) on Java 8 (52.0)
        t_j21_on_j8 = (
            "java.lang.UnsupportedClassVersionError: net/sir/mod/Engine has been compiled by a more recent "
            "version of the Java Runtime (class file version 65.0), this version of the Java Runtime only recognizes "
            "class file versions up to 52.0"
        )
        r1 = CrashAnalyzer.diagnose_crash(t_j21_on_j8)
        self.assertEqual(r1["type"], "JAVA_VERSION_MISMATCH")
        self.assertEqual(r1["required_java"], "Java 21")
        self.assertEqual(r1["running_java"], "Java 8")
        self.assertIn("Temurin 21 LTS", r1["fix"])

        # 2. Java 23 class (67.0) on Java 17 (61.0)
        t_j23_on_j17 = (
            "java.lang.UnsupportedClassVersionError: com/foo/Bar (class file version 67.0), "
            "this version of the Java Runtime only recognizes class file versions up to 61.0"
        )
        r2 = CrashAnalyzer.diagnose_crash(t_j23_on_j17)
        self.assertEqual(r2["type"], "JAVA_VERSION_MISMATCH")
        self.assertEqual(r2["required_java"], "Java 23")
        self.assertEqual(r2["running_java"], "Java 17")

        # 3. Unmapped future Java class version 70.0 (Java 26) on Java 21 (65.0)
        t_future = (
            "java.lang.UnsupportedClassVersionError: com/future/Module (class file version 70.0), "
            "this version of the Java Runtime only recognizes class file versions up to 65.0"
        )
        r3 = CrashAnalyzer.diagnose_crash(t_future)
        self.assertEqual(r3["type"], "JAVA_VERSION_MISMATCH")
        self.assertEqual(r3["required_java"], "Class Ver 70.0")
        self.assertEqual(r3["running_java"], "Java 21")

        # 4. Historical unmapped Java class version 45.3 on 52.0
        t_old = (
            "java.lang.UnsupportedClassVersionError: com/ancient/Mod (class file version 45.3), "
            "this version of the Java Runtime only recognizes class file versions up to 52.0"
        )
        r4 = CrashAnalyzer.diagnose_crash(t_old)
        self.assertEqual(r4["type"], "JAVA_VERSION_MISMATCH")
        self.assertEqual(r4["required_java"], "Class Ver 45.3")
        self.assertEqual(r4["running_java"], "Java 8")

    def test_native_hotspot_hs_err_pid_edge_cases(self):
        """Adversarially test HotSpot native dumps with various GPU modules, OS platforms, and format irregularities."""
        # 1. NVIDIA OpenGL DLL crash
        nv_crash = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# EXCEPTION_ACCESS_VIOLATION (0xc0000005) at pc=0x00007ffb8a1e321a\n"
            "# Problematic frame:\n"
            "# C  [nvoglv64.dll+0x9b321a]\n"
            "# Failed to write core dump."
        )
        r_nv = CrashAnalyzer.diagnose_crash(nv_crash, "hs_err_pid1234.log")
        self.assertEqual(r_nv["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r_nv["offending_module"], "nvoglv64.dll")
        self.assertIn("NVIDIA", r_nv["fix"])

        # 2. NVIDIA DirectX DLL crash
        nvd3d_crash = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# Problematic frame:\n"
            "# C  [nvd3dum.dll+0x102030]\n"
        )
        r_d3d = CrashAnalyzer.diagnose_crash(nvd3d_crash, "hs_err_pid5678.log")
        self.assertEqual(r_d3d["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r_d3d["offending_module"], "nvd3dum.dll")
        self.assertIn("NVIDIA", r_d3d["fix"])

        # 3. AMD Radeon secondary driver crash
        amd_sec_crash = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# Problematic frame:\n"
            "# C  [amdrsscs.dll+0x334455]\n"
        )
        r_amd = CrashAnalyzer.diagnose_crash(amd_sec_crash, "hs_err_pid99.log")
        self.assertEqual(r_amd["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r_amd["offending_module"], "amdrsscs.dll")
        self.assertIn("AMD", r_amd["fix"])

        # 4. Intel Integrated GPU crash
        intel_crash = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# Problematic frame:\n"
            "# C  [ig10icd64.dll+0x778899]\n"
        )
        r_intel = CrashAnalyzer.diagnose_crash(intel_crash, "hs_err_pid101.log")
        self.assertEqual(r_intel["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r_intel["offending_module"], "ig10icd64.dll")
        self.assertIn("Intel", r_intel["fix"])

        # 5. Linux / macOS shared object crash in libjvm.so
        so_crash = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# Problematic frame:\n"
            "# V  [libjvm.so+0xabc123]\n"
        )
        r_so = CrashAnalyzer.diagnose_crash(so_crash, "hs_err_pid202.log")
        self.assertEqual(r_so["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r_so["offending_module"], "libjvm.so")

        # 6. Native crash with no Problematic Frame line but hs_err filename
        no_frame = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# SIGSEGV (0xb) at pc=0x00007f311a2b3c4d, pid=4321, tid=4322\n"
            "# Native frames: (J=compiled Java code, j=interpreted, Vv=VM code, C=native code)\n"
            "C  [OpenAL64.dll+0x1234]\n"
        )
        r_no_frame = CrashAnalyzer.diagnose_crash(no_frame, "hs_err_pid4321.log")
        self.assertEqual(r_no_frame["type"], "JVM_NATIVE_CRASH")
        self.assertIn("OpenAL64.dll", r_no_frame["offending_module"])

    def test_all_oom_variants_and_remediations(self):
        """Test each of the 5 Out-Of-Memory variants and verify custom remediation parameters."""
        cases = [
            (
                "java.lang.OutOfMemoryError: Direct buffer memory",
                "DIRECT_MEMORY_EXHAUSTION",
                "-XX:MaxDirectMemorySize=2G",
            ),
            (
                "java.lang.OutOfMemoryError: Metaspace",
                "METASPACE_EXHAUSTION",
                "-XX:MaxMetaspaceSize=512M",
            ),
            (
                "java.lang.OutOfMemoryError: GC overhead limit exceeded",
                "GC_OVERHEAD_EXHAUSTION",
                "G1GC",
            ),
            (
                "java.lang.OutOfMemoryError: unable to create new native thread",
                "THREAD_CREATION_EXHAUSTION",
                "Reduce concurrent background tasks",
            ),
            (
                "java.lang.OutOfMemoryError: Java heap space",
                "OUT_OF_MEMORY",
                "Increase Allocated RAM",
            ),
        ]
        for snippet, expected_type, expected_fix_keyword in cases:
            res = CrashAnalyzer.diagnose_crash(f"Exception in thread 'main' {snippet}\n\tat net.minecraft.client.Main.main")
            self.assertEqual(res["type"], expected_type, f"Failed for {snippet}")
            self.assertIn(expected_fix_keyword, res["fix"])

    def test_mod_dependency_mappings_and_unmapped_classes(self):
        """Test ClassNotFoundException and NoClassDefFoundError across known libraries and unknown classes."""
        known_tests = [
            ("gnu/trove/map/TIntObjectMap", "trove4j (Legacy Forge dependency)"),
            ("net/fabricmc/fabric/api/event/Event", "Fabric API"),
            ("me/shedaniel/clothconfig2/api/ConfigBuilder", "Cloth Config v2"),
            ("dev/architectury/registry/CreativeTabRegistry", "Architectury API"),
            ("fuzs/puzzleslib/api/core/v1/ModConstructor", "Puzzles Lib"),
            ("org/spongepowered/asm/mixin/Mixin", "Mixin Subsystem"),
            ("com/electronwill/nightconfig/core/file/CommentedFileConfig", "Night Config"),
            ("net/minecraftforge/fml/common/Mod", "Forge Mod Loader"),
            ("org/lwjgl/opengl/GL11", "LWJGL Core Libraries"),
        ]
        for class_path, expected_friendly_name in known_tests:
            # Dot notation
            dot_path = class_path.replace("/", ".")
            res_dot = CrashAnalyzer.diagnose_crash(f"java.lang.NoClassDefFoundError: {dot_path}")
            self.assertEqual(res_dot["type"], "MISSING_DEPENDENCY")
            self.assertIn(expected_friendly_name, res_dot["cause"])

            # Slash notation
            res_slash = CrashAnalyzer.diagnose_crash(f"java.lang.ClassNotFoundException: {class_path}")
            self.assertEqual(res_slash["type"], "MISSING_DEPENDENCY")
            self.assertIn(expected_friendly_name, res_slash["cause"])

        # Unknown custom class
        res_unknown = CrashAnalyzer.diagnose_crash("java.lang.ClassNotFoundException: com.custom.mod.SpecialHelper")
        self.assertEqual(res_unknown["type"], "MISSING_DEPENDENCY")
        self.assertIn("SpecialHelper", res_unknown["cause"])

    def test_world_region_corruption_and_opengl_errors(self):
        """Test world anvil region corruption parsing and OpenGL driver crashes."""
        # 1. World region with positive coords
        res_world1 = CrashAnalyzer.diagnose_crash("Corrupted Chunk in region file r.2.3.mca - AnvilException")
        self.assertEqual(res_world1["type"], "CORRUPTED_WORLD_REGION")
        self.assertEqual(res_world1["region_file"], "r.2.3.mca")
        self.assertIn("r.2.3.mca", res_world1["fix"])

        # 2. World region with negative coords
        res_world2 = CrashAnalyzer.diagnose_crash("RegionFormatException: chunk [ -15, -42 ] wrong location in r.-1.-2.mca")
        self.assertEqual(res_world2["type"], "CORRUPTED_WORLD_REGION")
        self.assertEqual(res_world2["region_file"], "r.-1.-2.mca")

        # 3. Corrupted region without explicit .mca filename
        res_world3 = CrashAnalyzer.diagnose_crash("Corrupted Chunk found: NBTTagCompound payload is malformed")
        self.assertEqual(res_world3["type"], "CORRUPTED_WORLD_REGION")
        self.assertEqual(res_world3["region_file"], "world region")

        # 4. GLFW error 6554
        res_glfw = CrashAnalyzer.diagnose_crash("GLFW error 6554: WGL: The driver does not appear to support OpenGL")
        self.assertEqual(res_glfw["type"], "OPENGL_GPU_ERROR")
        self.assertIn("Balanced 144+ FPS", res_glfw["fix"])


class TestTelemetryGovernorAdversarialDeep(unittest.TestCase):
    """Adversarial stress testing for TelemetryGovernorService."""

    def test_singleton_thread_safety(self):
        """Verify TelemetryGovernorService singleton initialization under race conditions."""
        instances = []

        def _get():
            instances.append(TelemetryGovernorService.get_instance())

        threads = [threading.Thread(target=_get) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(instances), 20)
        first = instances[0]
        for inst in instances[1:]:
            self.assertIs(inst, first)

    def test_invalid_negative_and_extreme_pids(self):
        """Adversarially pass boundary PIDs (0, negative, None, max uint32, dead PID)."""
        if sys.platform != "win32":
            self.skipTest("Telemetry governor process tracking is Win32-specific")
        gov = TelemetryGovernorService.get_instance()

        # Zero PID
        res_0 = gov.get_process_telemetry(0)
        self.assertFalse(res_0["success"])
        self.assertEqual(res_0["error"], "Invalid PID")

        # Negative PID
        res_neg = gov.get_process_telemetry(-999)
        self.assertFalse(res_neg["success"])
        self.assertEqual(res_neg["error"], "Invalid PID")

        # None PID
        res_none = gov.get_process_telemetry(None)  # type: ignore
        self.assertFalse(res_none["success"])

        # Dead / Non-existent high PID
        res_dead = gov.get_process_telemetry(98765432)
        self.assertFalse(res_dead["success"])
        self.assertIn("not running or access denied", res_dead["error"])

    def test_simulated_child_process_lifecycle_telemetry(self):
        """Spawn a real child process, query telemetry while alive, terminate it, and verify graceful post-mortem handling."""
        if sys.platform != "win32":
            self.skipTest("Telemetry governor process tracking is Win32-specific")
        gov = TelemetryGovernorService.get_instance()

        # Spawn a genuine Python child process that sleeps
        proc = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        child_pid = proc.pid

        try:
            time.sleep(0.2)  # Allow process to start and populate working set

            # 1. Telemetry query on live child
            t1 = gov.get_process_telemetry(child_pid)
            self.assertTrue(t1["success"])
            self.assertEqual(t1["pid"], child_pid)
            self.assertGreater(t1["working_set_mb"], 0.0)
            self.assertGreater(t1["private_commit_mb"], 0.0)
            self.assertGreaterEqual(t1["peak_working_set_mb"], t1["working_set_mb"])
            self.assertGreaterEqual(t1["cpu_load_pct"], 0.0)

            # 2. Trim memory on live child process
            if sys.platform == "win32":
                trim_res = gov.trim_process_memory(child_pid)
                self.assertTrue(trim_res["success"])
                self.assertGreater(trim_res["before_mb"], 0.0)
                self.assertGreaterEqual(trim_res["after_mb"], 0.0)
                self.assertGreaterEqual(trim_res["freed_mb"], 0.0)
        finally:
            # Forcibly terminate child process and close pipes
            proc.kill()
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()
            proc.wait(timeout=3)

        # 3. Telemetry query on terminated child while Python still holds process handle (zombie state)
        t_zombie = gov.get_process_telemetry(child_pid)
        # In zombie state with handle held, Windows returns 0.0 MB working set
        if t_zombie["success"]:
            self.assertEqual(t_zombie["working_set_mb"], 0.0)

        # 4. Release all Python-level handles and garbage collect
        del proc
        import gc
        gc.collect()
        time.sleep(0.1)

        # 5. Telemetry query on fully terminated child (must fail cleanly, no crash)
        t_dead = gov.get_process_telemetry(child_pid)
        self.assertFalse(t_dead["success"])
        self.assertIn("not running or access denied", t_dead["error"])

        # 6. Trim memory on dead child
        if sys.platform == "win32":
            trim_dead = gov.trim_process_memory(child_pid)
            self.assertFalse(trim_dead["success"])

    def test_rapid_polling_cpu_delta_zero_division_guard(self):
        """Stress CPU delta calculation by polling in a tight loop with 0ms elapsed time."""
        gov = TelemetryGovernorService.get_instance()
        current_pid = os.getpid()

        # 100 rapid serial iterations
        for _ in range(100):
            res = gov.get_process_telemetry(current_pid)
            self.assertTrue(res["success"])
            self.assertGreaterEqual(res["cpu_load_pct"], 0.0)
            self.assertLessEqual(res["cpu_load_pct"], 100.0)

    def test_concurrent_multi_threaded_telemetry_queries(self):
        """Stress governor under 10 concurrent threads polling simultaneously."""
        gov = TelemetryGovernorService.get_instance()
        current_pid = os.getpid()
        errors = []

        def _worker():
            try:
                for _ in range(25):
                    r = gov.get_process_telemetry(current_pid)
                    if not r["success"]:
                        errors.append(f"Failed query: {r}")
            except Exception as ex:
                errors.append(str(ex))

        threads = [threading.Thread(target=_worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Encountered concurrency errors: {errors[:5]}")

    def test_empty_working_set_on_current_process_and_edge_cases(self):
        """Empirically test EmptyWorkingSet Win32 memory page flushing."""
        if sys.platform != "win32":
            self.skipTest("EmptyWorkingSet is Win32 specific")

        gov = TelemetryGovernorService.get_instance()

        # 1. Default pid=None (current process)
        trim_none = gov.trim_process_memory(None)
        self.assertTrue(trim_none["success"])
        self.assertEqual(trim_none["target"], "SIR Launcher Engine")
        self.assertGreater(trim_none["before_mb"], 0.0)
        self.assertGreater(trim_none["after_mb"], 0.0)

        # 2. pid=0 (current process)
        trim_zero = gov.trim_process_memory(0)
        self.assertTrue(trim_zero["success"])
        self.assertEqual(trim_zero["target"], "SIR Launcher Engine")

        # 3. Invalid PID
        trim_invalid = gov.trim_process_memory(99999999)
        self.assertFalse(trim_invalid["success"])


class TestRepairServiceAdversarialDeep(unittest.TestCase):
    """Adversarial stress testing for RepairService."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_repair_deep_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_calculate_sha256_edge_cases(self):
        """Test SHA-256 calculation on empty files, non-existent files, and directories."""
        repair = RepairService(self.temp_dir)

        # 1. Non-existent file -> returns ""
        self.assertEqual(repair.calculate_sha256(os.path.join(self.temp_dir, "nonexistent.bin")), "")

        # 2. Directory path passed as file -> returns ""
        self.assertEqual(repair.calculate_sha256(self.temp_dir), "")

        # 3. 0-byte file -> returns SHA-256 of empty string
        empty_file = os.path.join(self.temp_dir, "empty.bin")
        with open(empty_file, "wb") as f:
            pass
        expected_empty_sha = hashlib.sha256(b"").hexdigest()
        self.assertEqual(repair.calculate_sha256(empty_file), expected_empty_sha)

        # 4. 2MB file chunked reading integrity
        payload = b"X" * 2000000
        large_file = os.path.join(self.temp_dir, "large.bin")
        with open(large_file, "wb") as f:
            f.write(payload)
        expected_large_sha = hashlib.sha256(payload).hexdigest()
        self.assertEqual(repair.calculate_sha256(large_file), expected_large_sha)

    def test_verify_file_integrity_corrupted_zip_variants(self):
        """Adversarially test various archive corruption modes (truncated header, CRC mismatch, valid zip)."""
        repair = RepairService(self.temp_dir)

        # 1. Non-existent file
        res_missing = repair.verify_file_integrity(os.path.join(self.temp_dir, "missing.jar"))
        self.assertFalse(res_missing["valid"])
        self.assertEqual(res_missing["reason"], "Missing file")

        # 2. 0-byte JAR file
        empty_jar = os.path.join(self.temp_dir, "empty.jar")
        with open(empty_jar, "wb") as f:
            pass
        res_empty = repair.verify_file_integrity(empty_jar)
        self.assertFalse(res_empty["valid"])
        self.assertEqual(res_empty["reason"], "0-byte empty file")

        # 3. Truncated / malformed zip header
        fake_jar = os.path.join(self.temp_dir, "fake.jar")
        with open(fake_jar, "wb") as f:
            f.write(b"PK\x03\x04This is not a real zip archive header format")
        res_fake = repair.verify_file_integrity(fake_jar)
        self.assertFalse(res_fake["valid"])
        self.assertIn("Invalid archive structure", res_fake["reason"])

        # 4. Valid ZIP container where member has corrupted CRC32 / data
        tampered_jar = os.path.join(self.temp_dir, "tampered.jar")
        with zipfile.ZipFile(tampered_jar, "w", compression=zipfile.ZIP_STORED) as zf:
            zf.writestr("fabric.mod.json", '{"schemaVersion": 1, "id": "tampered_mod"}')
            zf.writestr("data.bin", b"A" * 1000)

        # Corrupt bytes in the payload of data.bin
        with open(tampered_jar, "r+b") as f:
            content = bytearray(f.read())
            # Find the payload bytes and corrupt them without altering headers
            idx = content.find(b"A" * 20)
            if idx != -1:
                content[idx:idx + 10] = b"Z" * 10
            else:
                content[len(content) // 2] ^= 0xFF
            f.seek(0)
            f.write(content)

        res_tampered = repair.verify_file_integrity(tampered_jar)
        self.assertFalse(res_tampered["valid"])
        self.assertTrue(
            "Corrupted zip member" in res_tampered["reason"]
            or "Invalid archive structure" in res_tampered["reason"]
        )

        # 5. Perfectly valid JAR file
        valid_jar = os.path.join(self.temp_dir, "valid.jar")
        with zipfile.ZipFile(valid_jar, "w") as zf:
            zf.writestr("fabric.mod.json", '{"schemaVersion": 1, "id": "valid_mod"}')
            zf.writestr("com/mod/Main.class", b"\xca\xfe\xba\xbe\x00\x00\x00\x41")
        res_valid = repair.verify_file_integrity(valid_jar)
        self.assertTrue(res_valid["valid"])
        self.assertEqual(res_valid["size"], os.path.getsize(valid_jar))

        # 6. Case-insensitive SHA-256 validation
        real_sha = res_valid["sha256"]
        res_upper = repair.verify_file_integrity(valid_jar, expected_sha256=real_sha.upper())
        self.assertTrue(res_upper["valid"])

        res_mismatch = repair.verify_file_integrity(valid_jar, expected_sha256="deadbeef" * 8)
        self.assertFalse(res_mismatch["valid"])
        self.assertIn("SHA-256 mismatch", res_mismatch["reason"])

    def test_run_self_repair_self_healing_from_backup_and_quarantine(self):
        """Test full repair workflow: healing corrupted instance mod from root backup, and quarantining unrepairable mods."""
        # Directory structure:
        # root_dir/
        #   mods/
        #     modA.jar (VALID BACKUP)
        #     modB.jar (CORRUPTED BACKUP)
        #   instances/
        #     instance1/
        #       minecraft/
        #         mods/
        #           modA.jar (CORRUPTED -> Should heal from backup)
        #           modB.jar (CORRUPTED -> Backup corrupted -> Should quarantine)
        #           modC.jar (CORRUPTED -> No backup -> Should quarantine)
        #           modD.jar (VALID -> Should remain untouched)
        #           modE.jar.disabled (DISABLED -> Should be skipped)
        #           modF.jar.corrupted (ALREADY QUARANTINED -> Should be skipped)
        root_mods = os.path.join(self.temp_dir, "mods")
        os.makedirs(root_mods)

        inst_mods = os.path.join(self.temp_dir, "instances", "instance1", "minecraft", "mods")
        os.makedirs(inst_mods)

        # 1. Valid backup for modA in root_mods
        modA_backup = os.path.join(root_mods, "modA.jar")
        with zipfile.ZipFile(modA_backup, "w") as zf:
            zf.writestr("fabric.mod.json", '{"id": "modA"}')

        # 2. Corrupted backup for modB in root_mods
        modB_backup = os.path.join(root_mods, "modB.jar")
        with open(modB_backup, "wb") as f:
            f.write(b"PK\x03\x04BAD_BACKUP")

        # 3. Target instance mods
        modA_inst = os.path.join(inst_mods, "modA.jar")
        with open(modA_inst, "wb") as f:
            f.write(b"PK\x03\x04CORRUPTED_INST_A")

        modB_inst = os.path.join(inst_mods, "modB.jar")
        with open(modB_inst, "wb") as f:
            f.write(b"PK\x03\x04CORRUPTED_INST_B")

        modC_inst = os.path.join(inst_mods, "modC.jar")
        with open(modC_inst, "wb") as f:
            f.write(b"PK\x03\x04CORRUPTED_INST_C_NO_BACKUP")

        modD_inst = os.path.join(inst_mods, "modD.jar")
        with zipfile.ZipFile(modD_inst, "w") as zf:
            zf.writestr("fabric.mod.json", '{"id": "modD"}')

        modE_disabled = os.path.join(inst_mods, "modE.jar.disabled")
        with open(modE_disabled, "wb") as f:
            f.write(b"DISABLED")

        modF_corrupted = os.path.join(inst_mods, "modF.jar.corrupted")
        with open(modF_corrupted, "wb") as f:
            f.write(b"ALREADY_CORRUPTED")

        repair = RepairService(self.temp_dir)
        repair_res = repair.run_self_repair()

        self.assertTrue(repair_res["success"])
        # Total scanned in search dirs (root_mods has modA, modB; inst_mods has modA, modB, modC, modD = 6 files)
        self.assertEqual(repair_res["total_scanned"], 6)
        self.assertEqual(repair_res["verified_count"], 2)  # root modA + inst modD
        self.assertEqual(repair_res["healed_count"], 1)    # inst modA healed from root modA!
        self.assertEqual(repair_res["quarantined_count"], 3)  # root modB, inst modB, inst modC quarantined

        # Check post-repair state on disk
        # modA in instance must now be valid
        self.assertTrue(os.path.exists(modA_inst))
        self.assertTrue(repair.verify_file_integrity(modA_inst)["valid"])

        # modB in instance must be renamed to .corrupted
        self.assertFalse(os.path.exists(modB_inst))
        self.assertTrue(os.path.exists(modB_inst + ".corrupted"))

        # modC in instance must be renamed to .corrupted
        self.assertFalse(os.path.exists(modC_inst))
        self.assertTrue(os.path.exists(modC_inst + ".corrupted"))

        # modD must remain untouched and valid
        self.assertTrue(os.path.exists(modD_inst))
        self.assertTrue(repair.verify_file_integrity(modD_inst)["valid"])

        # modE and modF must remain untouched
        self.assertTrue(os.path.exists(modE_disabled))
        self.assertTrue(os.path.exists(modF_corrupted))

    def test_run_self_repair_empty_directories(self):
        """Test run_self_repair when no search directories or files exist."""
        empty_root = os.path.join(self.temp_dir, "empty_ecosystem")
        os.makedirs(empty_root)

        repair = RepairService(empty_root)
        res = repair.run_self_repair()

        self.assertTrue(res["success"])
        self.assertEqual(res["total_scanned"], 0)
        self.assertEqual(res["verified_count"], 0)
        self.assertEqual(res["corrupted_count"], 0)
        self.assertEqual(res["status"], "No assets to verify")


if __name__ == "__main__":
    unittest.main()
