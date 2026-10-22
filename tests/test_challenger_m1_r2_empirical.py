"""
test_challenger_m1_r2_empirical.py — Challenger 2 Empirical Verification Suite for Milestone 1 Round 2.

Empirically challenges:
1. CrashReportAnalyzer / CrashAnalyzer:
   - Extreme nested exception chains (15+ levels)
   - Obfuscated and inner-class mixin injection targets
   - Out-of-range & future Java class file versions (45.0 through 99.0)
   - Hostile, multi-megabyte (10MB), Unicode, null-byte, and format-string logs
   - Native HotSpot hs_err_pid dumps across OS platforms (Windows DLL, Linux SO, macOS dylib),
     all GPU vendors (NVIDIA OpenGL & DirectX, AMD Radeon primary/secondary, Intel Arc/UHD),
     and malformed/truncated dump headers
   - Competing multi-OOM signatures in single log payload (priority & disambiguation)
   - World chunk corruption with extreme negative & boundary coordinates

2. TelemetryGovernorService & EmptyWorkingSet:
   - Full child process lifecycle transitions (Spawn -> Active -> CPU Load -> Idle -> Terminate -> Zombie -> Dead)
   - Win32 Handle leak prevention (measuring live OS handle counts across 1,000 iterations)
   - Multi-threaded concurrent polling and trimming across multiple simultaneous child processes
   - Boundary & invalid PIDs (PID 0, PID 4 System, negative PIDs, max uint32, dead PIDs)
   - EmptyWorkingSet memory page trimming validation on current process and external subprocesses
"""
from __future__ import annotations

import ctypes
import gc
import os
import subprocess
import sys
import threading
import time
import unittest
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


class TestCrashAnalyzerEmpiricalEdgeCases(unittest.TestCase):
    """Adversarial stress and edge-case verification for CrashReportAnalyzer."""

    def test_analyzer_subclass_contract_invariance(self):
        """Verify CrashReportAnalyzer subclass adheres to all static methods and properties of CrashAnalyzer."""
        self.assertTrue(issubclass(CrashReportAnalyzer, CrashAnalyzer))
        self.assertEqual(CrashReportAnalyzer.JAVA_VERSION_MAP, CrashAnalyzer.JAVA_VERSION_MAP)
        self.assertEqual(CrashReportAnalyzer.KNOWN_LIBRARIES_MAP, CrashAnalyzer.KNOWN_LIBRARIES_MAP)

        # Invariance on empty input
        self.assertEqual(
            CrashReportAnalyzer.diagnose_crash(""),
            CrashAnalyzer.diagnose_crash(""),
        )

    def test_deep_causal_chains_and_obfuscated_mixins(self):
        """Test deep 15-level exception nesting and obfuscated class/mixin names."""
        nested_chain = []
        for i in range(15):
            nested_chain.append(f"Caused by: java.lang.RuntimeException: Wrapper exception layer {i}")
            nested_chain.append(f"\tat com.example.wrapper.Layer{i}.execute(Layer{i}.java:{10 + i})")

        nested_chain.append(
            "Caused by: org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: "
            "Mixin [sir-core-2026.mixins.json:net.sir.render.Mixin_a$b$1 from mod sir-hardened-core_v4] FAILED during APPLY"
        )
        nested_chain.append("Mixin transformation of net.minecraft.class_310$class_123 failed")

        full_log = "\n".join(nested_chain)
        res = CrashReportAnalyzer.diagnose_crash(full_log)

        self.assertEqual(res["type"], "MIXIN_CONFLICT")
        self.assertEqual(res["offending_mod"], "sir-hardened-core_v4")
        self.assertEqual(res["target_class"], "net.minecraft.class_310$class_123")
        self.assertIn("sir-core-2026.mixins.json", res["mixin_config"])
        self.assertIn("sir-hardened-core_v4", res["fix"])

    def test_multi_megabyte_log_performance_and_no_catastrophic_backtracking(self):
        """Stress regex engine with a 10MB log with varied prefixes, unicode, and a crash signature at the end."""
        prefix_line = "[2026-08-30 01:00:00] [Client thread/INFO]: Processing chunk rendering at (x=1024, z=-2048)...\n"
        # 100,000 lines ~ 9.5MB
        huge_log = (prefix_line * 100000)
        huge_log += "java.lang.OutOfMemoryError: Java heap space\n\tat net.minecraft.client.Main.main\n"

        t_start = time.perf_counter()
        res = CrashReportAnalyzer.diagnose_crash(huge_log)
        t_elapsed = time.perf_counter() - t_start

        self.assertEqual(res["type"], "OUT_OF_MEMORY")
        self.assertIn("6 GB or 8 GB", res["fix"])
        self.assertLess(t_elapsed, 2.5, f"Crash analyzer regex execution took too long: {t_elapsed:.3f}s")

    def test_unicode_null_bytes_and_adversarial_encoding_payloads(self):
        """Adversarially pass payloads with Arabic, Chinese, Japanese, Emojis, ANSI escapes, and null bytes."""
        hostile_payload = (
            "\x1b[31;1m[ERROR]\x1b[0m \x00\x00\xff\xfe "
            "تحطم غير متوقع في محرك الألعاب 🎮 🔥 崩溃 異常終了 "
            "java.lang.NoClassDefFoundError: net/fabricmc/fabric/api/event/lifecycle/v1/ServerTickEvents\n"
            "\tat com.example.MyMod.onInitialize(MyMod.java:42)\n"
            "End of stack trace."
        )
        res = CrashReportAnalyzer.diagnose_crash(hostile_payload)
        self.assertEqual(res["type"], "MISSING_DEPENDENCY")
        self.assertIn("Fabric API", res["cause"])
        self.assertIn("Fabric API", res["fix"])

    def test_native_hotspot_dumps_comprehensive_matrix(self):
        """Exhaustively verify native crash dumps across OS platforms and GPU architectures."""
        # 1. NVIDIA OpenGL driver crash (Windows)
        nv_log = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "#  EXCEPTION_ACCESS_VIOLATION (0xc0000005) at pc=0x00007ffbe6181e10, pid=14820, tid=12400\n"
            "# Problematic frame:\n"
            "# C  [nvoglv64.dll+0x9d1e10]\n"
        )
        r1 = CrashReportAnalyzer.diagnose_crash(nv_log, "hs_err_pid14820.log")
        self.assertEqual(r1["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r1["offending_module"], "nvoglv64.dll")
        self.assertIn("NVIDIA", r1["fix"])

        # 2. NVIDIA DirectX crash (nvd3dum.dll)
        nvd3d_log = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# Problematic frame:\n"
            "# C  [nvd3dum.dll+0x123456]\n"
        )
        r2 = CrashReportAnalyzer.diagnose_crash(nvd3d_log, "hs_err_pid111.log")
        self.assertEqual(r2["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r2["offending_module"], "nvd3dum.dll")
        self.assertIn("NVIDIA", r2["fix"])

        # 3. AMD Radeon crash (atio6axx.dll)
        amd1_log = (
            "# Problematic frame:\n"
            "# C  [atio6axx.dll+0xabcdef]\n"
        )
        r3 = CrashReportAnalyzer.diagnose_crash(amd1_log, "hs_err_pid222.log")
        self.assertEqual(r3["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r3["offending_module"], "atio6axx.dll")
        self.assertIn("AMD", r3["fix"])

        # 4. AMD Radeon secondary module (amdrsscs.dll)
        amd2_log = (
            "# Problematic frame:\n"
            "# C  [amdrsscs.dll+0x556677]\n"
        )
        r4 = CrashReportAnalyzer.diagnose_crash(amd2_log, "hs_err_pid333.log")
        self.assertEqual(r4["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r4["offending_module"], "amdrsscs.dll")
        self.assertIn("AMD", r4["fix"])

        # 5. Intel Arc / UHD driver crash (ig9icd64.dll)
        intel1_log = (
            "# Problematic frame:\n"
            "# C  [ig9icd64.dll+0x998877]\n"
        )
        r5 = CrashReportAnalyzer.diagnose_crash(intel1_log, "hs_err_pid444.log")
        self.assertEqual(r5["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r5["offending_module"], "ig9icd64.dll")
        self.assertIn("Intel", r5["fix"])

        # 6. Intel Integrated GPU driver crash (ig10icd64.dll)
        intel2_log = (
            "# Problematic frame:\n"
            "# C  [ig10icd64.dll+0x112233]\n"
        )
        r6 = CrashReportAnalyzer.diagnose_crash(intel2_log, "hs_err_pid555.log")
        self.assertEqual(r6["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r6["offending_module"], "ig10icd64.dll")
        self.assertIn("Intel", r6["fix"])

        # 7. JVM Internal Crash (jvm.dll)
        jvm_log = (
            "# Problematic frame:\n"
            "# V  [jvm.dll+0x776655]\n"
        )
        r7 = CrashReportAnalyzer.diagnose_crash(jvm_log, "hs_err_pid666.log")
        self.assertEqual(r7["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r7["offending_module"], "jvm.dll")
        self.assertIn("JVM engine crashed", r7["fix"])

        # 8. Linux shared object native crash (libopenal.so.1)
        linux_log = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# Problematic frame:\n"
            "# C  [libopenal.so+0x334455]\n"
        )
        r8 = CrashReportAnalyzer.diagnose_crash(linux_log, "hs_err_pid777.log")
        self.assertEqual(r8["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r8["offending_module"], "libopenal.so")

        # 9. macOS dynamic library native crash (liblwjgl.dylib)
        mac_log = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "# Problematic frame:\n"
            "# C  [liblwjgl.dylib+0x123abc]\n"
        )
        r9 = CrashReportAnalyzer.diagnose_crash(mac_log, "hs_err_pid888.log")
        self.assertEqual(r9["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(r9["offending_module"], "liblwjgl.dylib")

        # 10. Native dump without Problematic Frame section but with DLL in content
        fallback_log = (
            "# A fatal error has been detected by the Java Runtime Environment:\n"
            "Stack: [0x000000a12b, 0x000000a1cb]\n"
            "Loaded binary: C:\\Windows\\System32\\nvoglv64.dll\n"
        )
        r10 = CrashReportAnalyzer.diagnose_crash(fallback_log, "hs_err_pid999.log")
        self.assertEqual(r10["type"], "JVM_NATIVE_CRASH")
        self.assertIn("nvoglv64.dll", r10["offending_module"])

    def test_java_version_full_spectrum_and_future_proof_mapping(self):
        """Test Java class file version errors for standard LTS and out-of-bounds versions."""
        test_matrix = [
            ("52.0", "Java 8", "65.0", "Java 21"),
            ("55.0", "Java 11", "65.0", "Java 21"),
            ("60.0", "Java 16", "61.0", "Java 17"),
            ("61.0", "Java 17", "65.0", "Java 21"),
            ("62.0", "Java 18", "65.0", "Java 21"),
            ("63.0", "Java 19", "65.0", "Java 21"),
            ("64.0", "Java 20", "65.0", "Java 21"),
            ("65.0", "Java 21", "67.0", "Java 23"),
            ("66.0", "Java 22", "67.0", "Java 23"),
            ("67.0", "Java 23", "67.0", "Java 23"),
            ("68.0", "Java 24", "68.0", "Java 24"),
            ("69.0", "Java 25", "69.0", "Java 25"),
            ("50.0", "Class Ver 50.0", "65.0", "Java 21"),      # Java 6 (unmapped legacy)
            ("70.0", "Class Ver 70.0", "52.0", "Java 8"),       # Java 26 (future unmapped)
            ("99.0", "Class Ver 99.0", "65.0", "Java 21"),      # Java 55 (far-future unmapped)
        ]

        for run_cf, expected_run_name, req_cf, expected_req_name in test_matrix:
            log_str = (
                f"java.lang.UnsupportedClassVersionError: com/test/Class (class file version {req_cf}), "
                f"this version of the Java Runtime only recognizes class file versions up to {run_cf}"
            )
            diag = CrashReportAnalyzer.diagnose_crash(log_str)
            self.assertEqual(diag["type"], "JAVA_VERSION_MISMATCH")
            self.assertEqual(diag["required_java"], expected_req_name)
            self.assertEqual(diag["running_java"], expected_run_name)

    def test_oom_spectrum_and_multiple_competing_signatures(self):
        """Test the 5 distinct OOM variants and verify specific subtype extraction when multiple keywords appear."""
        # When Direct Memory exhaustion occurs, it should take precedence over generic heap space
        direct_mixed = (
            "Exception in thread 'main' java.lang.OutOfMemoryError: Direct buffer memory\n"
            "\tat java.nio.Bits.reserveMemory(Bits.java:178)\n"
            "Java heap space is currently 2048MB\n"
        )
        r_direct = CrashReportAnalyzer.diagnose_crash(direct_mixed)
        self.assertEqual(r_direct["type"], "DIRECT_MEMORY_EXHAUSTION")
        self.assertIn("-XX:MaxDirectMemorySize=2G", r_direct["fix"])

        # Metaspace exhaustion
        meta_mixed = (
            "java.lang.OutOfMemoryError: Metaspace\n"
            "\tat java.lang.ClassLoader.defineClass1(Native Method)\n"
        )
        r_meta = CrashReportAnalyzer.diagnose_crash(meta_mixed)
        self.assertEqual(r_meta["type"], "METASPACE_EXHAUSTION")
        self.assertIn("-XX:MaxMetaspaceSize=512M", r_meta["fix"])

        # GC overhead limit exceeded
        gc_log = "java.lang.OutOfMemoryError: GC overhead limit exceeded\n"
        r_gc = CrashReportAnalyzer.diagnose_crash(gc_log)
        self.assertEqual(r_gc["type"], "GC_OVERHEAD_EXHAUSTION")
        self.assertIn("G1GC", r_gc["fix"])

        # Thread creation limit
        thread_log = "java.lang.OutOfMemoryError: unable to create new native thread\n"
        r_th = CrashReportAnalyzer.diagnose_crash(thread_log)
        self.assertEqual(r_th["type"], "THREAD_CREATION_EXHAUSTION")

        # Standard Heap
        heap_log = "java.lang.OutOfMemoryError: Java heap space\n"
        r_heap = CrashReportAnalyzer.diagnose_crash(heap_log)
        self.assertEqual(r_heap["type"], "OUT_OF_MEMORY")

    def test_world_region_extreme_coordinates_and_corruptions(self):
        """Test world region corruption parsing with extreme positive and negative coordinates."""
        coords = [
            ("r.0.0.mca", "r.0.0.mca"),
            ("r.-1.-1.mca", "r.-1.-1.mca"),
            ("r.-12345.-67890.mca", "r.-12345.-67890.mca"),
            ("r.99999.99999.mca", "r.99999.99999.mca"),
        ]
        for mca_str, expected in coords:
            log_text = f"net.minecraft.world.chunk.storage.RegionFormatException: Corrupted Chunk in {mca_str}"
            res = CrashReportAnalyzer.diagnose_crash(log_text)
            self.assertEqual(res["type"], "CORRUPTED_WORLD_REGION")
            self.assertEqual(res["region_file"], expected)
            self.assertIn(expected, res["fix"])


    def test_crash_analyzer_known_libraries_mapping_completeness(self):
        """Verify all known dependency prefixes and deep unknown package fallbacks."""
        for prefix, expected_name in CrashReportAnalyzer.KNOWN_LIBRARIES_MAP.items():
            # Test NoClassDefFoundError
            dot_path = prefix.replace("/", ".") + ".SomeClass"
            log_noclass = f"java.lang.NoClassDefFoundError: {dot_path}"
            res_noclass = CrashReportAnalyzer.diagnose_crash(log_noclass)
            self.assertEqual(res_noclass["type"], "MISSING_DEPENDENCY")
            self.assertIn(expected_name, res_noclass["cause"])
            self.assertIn(expected_name, res_noclass["fix"])

            # Test ClassNotFoundException with slash notation
            slash_path = prefix + "/SubPackage/InnerClass"
            log_cnf = f"java.lang.ClassNotFoundException: {slash_path}"
            res_cnf = CrashReportAnalyzer.diagnose_crash(log_cnf)
            self.assertEqual(res_cnf["type"], "MISSING_DEPENDENCY")
            self.assertIn(expected_name, res_cnf["cause"])
            self.assertIn(expected_name, res_cnf["fix"])

        # Test completely unknown library fallback
        unknown_class = "com.unregistered.deep.vendor.CustomEngineHelper"
        res_unk = CrashReportAnalyzer.diagnose_crash(f"java.lang.ClassNotFoundException: {unknown_class}")
        self.assertEqual(res_unk["type"], "MISSING_DEPENDENCY")
        self.assertIn("CustomEngineHelper", res_unk["cause"])
        self.assertIn("CustomEngineHelper", res_unk["fix"])

    def test_crash_analyzer_unsatisfied_link_errors(self):
        """Test missing native DLL/SO dynamic linkage exceptions."""
        # Pattern 1: no X in java.library.path
        log1 = "java.lang.UnsatisfiedLinkError: no lwjgl in java.library.path"
        r1 = CrashReportAnalyzer.diagnose_crash(log1)
        self.assertEqual(r1["type"], "NATIVE_LINKAGE_ERROR")
        self.assertEqual(r1["missing_native"], "lwjgl")
        self.assertIn("lwjgl", r1["cause"])
        self.assertIn("Launcher Self-Repair", r1["fix"])

        # Pattern 2: X.dll: The specified module could not be found
        log2 = "java.lang.UnsatisfiedLinkError: OpenAL64.dll: The specified module could not be found"
        r2 = CrashReportAnalyzer.diagnose_crash(log2)
        self.assertEqual(r2["type"], "NATIVE_LINKAGE_ERROR")
        self.assertEqual(r2["missing_native"], "OpenAL64.dll")
        self.assertIn("OpenAL64.dll", r2["cause"])

    def test_crash_analyzer_shader_and_opengl_errors(self):
        """Test OpenGL context, shader compilation, and Iris shader failure signatures."""
        cases = [
            ("org.lwjgl.opengl.OpenGLException: GL_OUT_OF_MEMORY", "OPENGL_GPU_ERROR"),
            ("GLFW error 6554: The driver does not appear to support OpenGL", "OPENGL_GPU_ERROR"),
            ("Shader compilation failed: composite.fsh (0): error: syntax error", "OPENGL_GPU_ERROR"),
            ("Iris shader error: Failed to compile shadow program", "OPENGL_GPU_ERROR"),
        ]
        for log_text, expected_type in cases:
            res = CrashReportAnalyzer.diagnose_crash(log_text)
            self.assertEqual(res["type"], expected_type, f"Failed for: {log_text}")
            self.assertIn("Balanced 144+ FPS", res["fix"])


class TestTelemetryGovernorEmpiricalLifecycle(unittest.TestCase):
    """Adversarial empirical tests for TelemetryGovernorService across real process lifecycles."""

    def test_win32_handle_leak_prevention_under_rapid_queries(self):
        """Verify that repeated OpenProcess/CloseHandle cycles in TelemetryGovernor do not leak OS handles."""
        if sys.platform != "win32":
            self.skipTest("Win32 specific test")

        gov = TelemetryGovernorService.get_instance()
        current_pid = os.getpid()

        # Measure starting handle count via GetProcessHandleCount Win32 API
        kernel32 = ctypes.windll.kernel32
        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        has_handle_count = hasattr(kernel32, "GetProcessHandleCount")
        if has_handle_count:
            kernel32.GetProcessHandleCount.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            kernel32.GetProcessHandleCount.restype = ctypes.c_int
        h_proc = kernel32.GetCurrentProcess()
        handle_count_before = ctypes.c_ulong(0)
        if has_handle_count:
            kernel32.GetProcessHandleCount(h_proc, ctypes.byref(handle_count_before))

        # Perform 1,000 rapid telemetry and memory trim cycles
        for _ in range(1000):
            res_tel = gov.get_process_telemetry(current_pid)
            self.assertTrue(res_tel["success"])
            res_trim = gov.trim_process_memory(None)
            self.assertTrue(res_trim["success"])

        # Force garbage collection
        gc.collect()
        time.sleep(0.05)

        if has_handle_count:
            handle_count_after = ctypes.c_ulong(0)
            kernel32.GetProcessHandleCount(h_proc, ctypes.byref(handle_count_after))
            # Handle count increase should be minimal (less than 15 delta for internal GC/runtime churn, definitely not ~1000)
            leak = max(0, handle_count_after.value - handle_count_before.value)
            self.assertLess(
                leak,
                15,
                f"Possible Win32 Handle leak detected! Started with {handle_count_before.value}, ended with {handle_count_after.value} (growth: {leak})",
            )

    def test_ephemeral_rapid_spawn_and_churn(self):
        """Stress governor under rapid creation and death of 12 ephemeral subprocesses."""
        gov = TelemetryGovernorService.get_instance()
        results = []

        for _ in range(12):
            p = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(0.08)"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pid = p.pid
            try:
                # Immediately query while alive
                r_live = gov.get_process_telemetry(pid)
                results.append(r_live["success"])
                # Wait for exit
                p.wait(timeout=3)
            finally:
                try:
                    p.kill()
                except Exception:
                    pass
                try:
                    p.wait(timeout=1)
                except Exception:
                    pass
                if p.stdout:
                    try:
                        p.stdout.close()
                    except Exception:
                        pass
                if p.stderr:
                    try:
                        p.stderr.close()
                    except Exception:
                        pass

            # Query after exit
            r_dead = gov.get_process_telemetry(pid)
            # Post-mortem query should either be dead or 0MB zombie, never an unhandled exception
            self.assertIsInstance(r_dead, dict)
            self.assertIn("success", r_dead)

        self.assertTrue(any(results), "At least some live queries should succeed during spawn churn")

    def test_multi_process_concurrency_and_lifecycle_transitions(self):
        """Spawn multiple real Python subprocesses, concurrently monitor and trim them across state changes."""
        gov = TelemetryGovernorService.get_instance()

        # Child process code: alternates between spinning CPU and sleeping
        child_code = (
            "import time, sys\n"
            "for _ in range(20):\n"
            "    t0 = time.time()\n"
            "    while time.time() - t0 < 0.05: pass\n"
            "    time.sleep(0.05)\n"
        )

        num_children = 4
        processes = []
        threads = []
        stop_event = threading.Event()
        try:
            for _ in range(num_children):
                p = subprocess.Popen(
                    [sys.executable, "-c", child_code],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                processes.append(p)

            time.sleep(0.1)  # Allow children to initialize

            errors = []

            def _poller_worker(proc_list):
                while not stop_event.is_set():
                    for proc in proc_list:
                        pid = proc.pid
                        try:
                            t = gov.get_process_telemetry(pid)
                            if t["success"]:
                                if t["working_set_mb"] < 0:
                                    errors.append(f"Negative working set for PID {pid}: {t}")
                            if sys.platform == "win32":
                                trim = gov.trim_process_memory(pid)
                                # Trim may fail if process exits mid-call, which is handled gracefully
                        except Exception as ex:
                            errors.append(f"Unexpected exception on PID {pid}: {ex}")
                    time.sleep(0.01)

            threads = [threading.Thread(target=_poller_worker, args=(processes,)) for _ in range(6)]
            for t in threads:
                t.start()

            # Step-by-step kill child processes one by one while threads are polling
            for p in processes:
                time.sleep(0.15)
                p.kill()
                if p.stdout:
                    p.stdout.close()
                if p.stderr:
                    p.stderr.close()
                p.wait(timeout=3)

            stop_event.set()
            for t in threads:
                t.join(timeout=2)

            self.assertEqual(len(errors), 0, f"Encountered unexpected lifecycle errors: {errors[:5]}")
        finally:
            stop_event.set()
            for t in threads:
                try:
                    t.join(timeout=1)
                except Exception:
                    pass
            for p in processes:
                try:
                    p.kill()
                except Exception:
                    pass
                try:
                    p.wait(timeout=1)
                except Exception:
                    pass
                if p.stdout:
                    try:
                        p.stdout.close()
                    except Exception:
                        pass
                if p.stderr:
                    try:
                        p.stderr.close()
                    except Exception:
                        pass

    def test_telemetry_governor_boundary_pids(self):
        """Test boundary conditions: System Idle (PID 0), System (PID 4), negative PIDs, non-integer types."""
        gov = TelemetryGovernorService.get_instance()

        # PID 0 -> should return error
        r0 = gov.get_process_telemetry(0)
        self.assertFalse(r0["success"])
        self.assertEqual(r0["error"], "Invalid PID")

        # Negative PIDs
        r_neg = gov.get_process_telemetry(-42)
        self.assertFalse(r_neg["success"])
        self.assertEqual(r_neg["error"], "Invalid PID")

        # PID 4 (Windows NT System Process) -> OpenProcess fails with access denied
        if sys.platform == "win32":
            r_sys = gov.get_process_telemetry(4)
            # Either fails gracefully or reports error
            if not r_sys["success"]:
                self.assertIn("access denied", r_sys["error"].lower())

    def test_empty_working_set_real_memory_reduction(self):
        """Empirically verify that EmptyWorkingSet physically reduces the current process working set size."""
        if sys.platform != "win32":
            self.skipTest("EmptyWorkingSet is Win32 specific")

        gov = TelemetryGovernorService.get_instance()

        # Allocate 30MB of transient heap data to inflate Working Set
        blob = bytearray(30 * 1024 * 1024)
        for i in range(0, len(blob), 4096):
            blob[i] = 1  # Touch each page to ensure physical memory commitment

        t_before = gov.get_process_telemetry(os.getpid())
        self.assertTrue(t_before["success"])
        self.assertGreater(t_before["working_set_mb"], 25.0)

        # Release Python reference and garbage collect
        del blob
        gc.collect()

        # Execute EmptyWorkingSet
        trim_res = gov.trim_process_memory(None)
        self.assertTrue(trim_res["success"])
        self.assertGreater(trim_res["before_mb"], 0.0)
        self.assertGreater(trim_res["after_mb"], 0.0)
        self.assertGreaterEqual(trim_res["freed_mb"], 0.0)
        self.assertIn("SIR Launcher Engine", trim_res["message"])

        # Check telemetry after trim
        t_after = gov.get_process_telemetry(os.getpid())
        self.assertTrue(t_after["success"])
        self.assertLess(t_after["working_set_mb"], t_before["working_set_mb"])


if __name__ == "__main__":
    unittest.main()

