"""
Empirical Adversarial Test Suite for Milestone 2: Native JVM Launch Pipeline & Compatibility.
Authored by: Challenger 1 (Milestone 2 Empirical Challenger)

Scope & Stress Dimensions:
1. RAM Boundary Parsing & Clamping:
   - Malformed strings: "invalid", "-10GB", "999999999MB", "4.5G", "-0", "0G", "None", "NaN", "   "
   - Boundary value analysis (256MB safe floor, 512MB, 1024MB, 4096MB, 64GB, extreme 1TB)
   - Min/Max RAM inversion clamping (min_ram > max_ram => min_ram clamped to max_ram)
   - JVM parameter formatting (-Xms / -Xmx consistency, no zero/negative flags)
   - G1GC nursery and region sizing across small, standard, large, and massive heap tiers

2. Pre-Launch Natives Extraction:
   - Target DLLs locked by external process (WinError 32 / PermissionError) using msvcrt.locking
   - Automatic fallback to process-isolated temp directory
   - Missing native JARs in search paths
   - Corrupted / zero-byte / truncated native JAR files
   - Modern 26.2 (LWJGL 3) vs Legacy 1.8.9 (LWJGL 2) architecture & library isolation
   - Existing valid DLLs vs forced re-extraction
   - Rapid multi-threaded concurrent extractions

3. Dynamic Classpath Assembly:
   - Corrupted, truncated, and non-JSON mmc-pack.json manifests
   - Malformed, corrupt, or missing instance.cfg files with non-numeric RAM bounds & Unicode
   - Corrupted or missing version.json manifests
   - Mojang OS & architecture rule evaluation edge cases
   - Layered classpath resolution (Loader -> ASM -> Mixin/Launchwrapper -> Libs -> Client JAR)
   - Duplicate jar elimination and path normalization
   - Monolithic ASM vs Modular ASM deduplication and conflict elimination
"""

import concurrent.futures
import io
import json
import os
import shutil
import struct
import sys
import tempfile
import time
import unittest
import zipfile

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.native_runner import (
    NativeMinecraftRunner,
    _maven_to_path,
    _parse_to_mb,
    calculate_ram_parameters,
)
from launcher_core.instance_service import InstanceService
from launcher_core.java_service import JavaService


class TestChallengerRAMBoundaryAdversarial(unittest.TestCase):
    """Adversarial stress-testing of RAM boundary parsing, clamping, and JVM argument formatting."""

    def test_scope_malformed_string_inputs(self):
        """Scope Item 1: Adversarially test RAM boundary parsing against specified malformed inputs."""
        # 1. "invalid" -> Fallback default_mb (8192 MB)
        self.assertEqual(_parse_to_mb("invalid"), 8192)
        res_invalid = calculate_ram_parameters(max_ram="invalid")
        self.assertEqual(res_invalid["max_mb"], 8192)
        self.assertEqual(res_invalid["xmx_flag"], "-Xmx8G")

        # 2. "-10GB" -> Negative input safely clamped to minimum safe floor (256 MB)
        self.assertEqual(_parse_to_mb("-10GB"), 256)
        res_neg = calculate_ram_parameters(max_ram="-10GB")
        self.assertEqual(res_neg["max_mb"], 256)
        self.assertEqual(res_neg["min_mb"], 256)
        self.assertEqual(res_neg["xmx_flag"], "-Xmx256M")
        self.assertEqual(res_neg["xms_flag"], "-Xms256M")

        # 3. "999999999MB" -> Huge memory value parsed accurately without overflow
        self.assertEqual(_parse_to_mb("999999999MB"), 999999999)
        res_huge = calculate_ram_parameters(max_ram="999999999MB")
        self.assertEqual(res_huge["max_mb"], 999999999)
        self.assertEqual(res_huge["xmx_flag"], "-Xmx999999999M")
        self.assertEqual(res_huge["region_size"], "32M")
        self.assertEqual(res_huge["new_size_pct"], 50)

        # 4. "4.5G" -> Fractional GB parsed to 4608 MB
        self.assertEqual(_parse_to_mb("4.5G"), 4608)
        res_fractional = calculate_ram_parameters(max_ram="4.5G")
        self.assertEqual(res_fractional["max_mb"], 4608)
        self.assertEqual(res_fractional["xmx_flag"], "-Xmx4608M")
        self.assertEqual(res_fractional["min_mb"], 2304)
        self.assertEqual(res_fractional["xms_flag"], "-Xms2304M")

    def test_additional_adversarial_ram_strings(self):
        """Tests extreme edge-case string formats, whitespaces, suffixes, and safe minimum clamping."""
        cases = [
            ("", 8192),
            ("   ", 8192),
            ("None", 8192),
            ("null", 8192),
            ("NaN", 8192),
            ("garbage_value", 8192),
            ("0", 256),       # 0 clamped to safe floor 256MB
            ("0GB", 256),     # 0 clamped to safe floor 256MB
            ("0MB", 256),     # 0 clamped to safe floor 256MB
            ("-0", 256),      # -0 clamped to safe floor 256MB
            ("-0.0G", 256),   # -0.0 clamped to safe floor 256MB
            ("-512M", 256),   # negative clamped to safe floor 256MB
            ("-1024", 256),   # negative clamped to safe floor 256MB
            ("-10.5GB", 256), # negative clamped to safe floor 256MB
            ("65", 256),      # plain number 65 < 256 clamped to safe floor 256MB
            ("128M", 256),    # 128MB < 256 clamped to safe floor 256MB
            ("256M", 256),
            ("512MB", 512),
            ("1024M", 1024),
            ("2048MiB", 2048),
            ("4096mb", 4096),
            ("6 GiB", 6144),
            ("8G", 8192),
            ("16gb", 16384),
            ("32 GIB", 32768),
            ("64G", 65536),
            ("64", 65536),    # <= 64 treated as GB -> 65536 MB
        ]
        for input_val, expected_mb in cases:
            with self.subTest(input_val=input_val):
                self.assertEqual(_parse_to_mb(input_val), expected_mb)

    def test_ram_inversion_and_safe_clamping(self):
        """Verifies that min_ram > max_ram is strictly clamped so -Xms <= -Xmx always holds."""
        inversion_cases = [
            ("16G", "4G", 4096, 4096, "-Xmx4G", "-Xms4G"),
            ("8G", "1G", 1024, 1024, "-Xmx1G", "-Xms1G"),
            ("6144M", "2048M", 2048, 2048, "-Xmx2G", "-Xms2G"),
            ("3072M", "512M", 512, 512, "-Xmx512M", "-Xms512M"),
            ("10GB", "-5GB", 256, 256, "-Xmx256M", "-Xms256M"),
        ]
        for min_input, max_input, expected_max_mb, expected_min_mb, expected_xmx, expected_xms in inversion_cases:
            with self.subTest(min_input=min_input, max_input=max_input):
                res = calculate_ram_parameters(max_ram=max_input, min_ram=min_input)
                self.assertEqual(res["max_mb"], expected_max_mb)
                self.assertEqual(res["min_mb"], expected_min_mb)
                self.assertEqual(res["xmx_flag"], expected_xmx)
                self.assertEqual(res["xms_flag"], expected_xms)
                self.assertLessEqual(res["min_mb"], res["max_mb"])

    def test_g1gc_region_and_nursery_thresholds(self):
        """Verifies mathematical correctness of G1GC dynamic nursery & region sizing across heap tiers."""
        tiers = [
            (1.5, "1M", 20, 30, 10),
            (2.5, "2M", 20, 30, 10),
            (4.0, "4M", 30, 40, 15),
            (6.0, "8M", 30, 40, 15),
            (12.0, "16M", 40, 50, 20),
            (24.0, "32M", 50, 60, 20),
        ]
        for max_gb, exp_region, exp_new, exp_max_new, exp_res in tiers:
            with self.subTest(max_gb=max_gb):
                res = calculate_ram_parameters(max_ram=f"{max_gb}G")
                self.assertEqual(res["region_size"], exp_region)
                self.assertEqual(res["new_size_pct"], exp_new)
                self.assertEqual(res["max_new_size_pct"], exp_max_new)
                self.assertEqual(res["reserve_pct"], exp_res)


class TestChallengerNativesExtractionAdversarial(unittest.TestCase):
    """Adversarial stress-testing of Pre-Launch Natives Extraction under locks, corrupted jars, and missing libs."""

    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.temp_dir = tempfile.mkdtemp(prefix="sir_challenger_nat_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.runner = NativeMinecraftRunner(self.root_dir, self.state_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def _create_synthetic_native_jar(self, jar_path: str, dlls: dict[str, bytes]):
        os.makedirs(os.path.dirname(jar_path), exist_ok=True)
        with zipfile.ZipFile(jar_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name, data in dlls.items():
                z.writestr(name, data)
            z.writestr("META-INF/MANIFEST.MF", b"Manifest-Version: 1.0\n")

    def test_scope_locked_dll_fallback_recovery(self):
        """Scope Item 2: Test pre-launch natives extraction when target DLL is locked by an external process."""
        import msvcrt

        target_dir = os.path.join(self.temp_dir, "locked_target")
        os.makedirs(target_dir, exist_ok=True)
        locked_dll_path = os.path.join(target_dir, "lwjgl64.dll")

        # Create synthetic source native jar
        libs_dir = os.path.join(self.temp_dir, "libraries")
        source_jar = os.path.join(libs_dir, "lwjgl-platform-2.9.4-natives-windows.jar")
        self._create_synthetic_native_jar(source_jar, {
            "lwjgl64.dll": b"NEW_LWJGL_BINARY",
            "OpenAL64.dll": b"NEW_OPENAL_BINARY",
        })
        self.runner.libraries_dirs = [libs_dir]

        version_json = {
            "id": "1.8.9",
            "libraries": [
                {
                    "name": "org.lwjgl.lwjgl:lwjgl-platform:2.9.4",
                    "natives": {"windows": "natives-windows"},
                }
            ]
        }

        # Write initial dummy file and lock it exclusively using msvcrt.locking
        with open(locked_dll_path, "wb") as f:
            f.write(b"ORIGINAL_LOCKED_CONTENT_1234")

        lock_handle = open(locked_dll_path, "r+b")
        lock_handle.seek(0)
        msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 20)

        try:
            # Force extraction into locked_dir
            result_dir = self.runner.extract_natives(
                version_json=version_json,
                mc_version="1.8.9",
                target_dir=target_dir,
                force_reextract=True,
            )

            # Verification: Should have fallen back to a process-isolated temp directory
            self.assertNotEqual(result_dir, target_dir, "Failed to fallback from locked directory!")
            self.assertTrue(os.path.isdir(result_dir), "Fallback directory was not created!")
            self.assertTrue(os.path.isfile(os.path.join(result_dir, "lwjgl64.dll")), "Fallback missing lwjgl64.dll!")
            self.assertTrue(os.path.isfile(os.path.join(result_dir, "OpenAL64.dll")), "Fallback missing OpenAL64.dll!")

            with open(os.path.join(result_dir, "lwjgl64.dll"), "rb") as rf:
                self.assertEqual(rf.read(), b"NEW_LWJGL_BINARY")

        finally:
            msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 20)
            lock_handle.close()

    def test_scope_missing_and_corrupted_native_jars(self):
        """Scope Item 2: Test pre-launch natives extraction when native JARs are completely missing or corrupted."""
        libs_dir = os.path.join(self.temp_dir, "libs_corrupt")
        os.makedirs(libs_dir, exist_ok=True)
        self.runner.libraries_dirs = [libs_dir]

        # 1. Missing native JAR in version.json
        version_json_missing = {
            "id": "26.2",
            "libraries": [
                {
                    "name": "org.lwjgl:lwjgl-missing:3.3.3",
                    "natives": {"windows": "natives-windows"},
                }
            ]
        }
        target_dir1 = os.path.join(self.temp_dir, "target1")
        # Should not crash; returns target_dir gracefully
        res1 = self.runner.extract_natives(version_json_missing, mc_version="26.2", target_dir=target_dir1, force_reextract=True)
        self.assertEqual(res1, target_dir1)

        # 2. Corrupted (zero-byte) native JAR
        corrupt_jar = os.path.join(libs_dir, "corrupt-natives-windows.jar")
        with open(corrupt_jar, "wb") as f:
            f.write(b"")  # 0 bytes

        # 3. Truncated ZIP file
        truncated_jar = os.path.join(libs_dir, "truncated-natives-windows.jar")
        with open(truncated_jar, "wb") as f:
            f.write(b"PK\x03\x04random_corrupted_garbage_bytes")

        version_json_corrupt = {
            "id": "26.2",
            "libraries": [
                {"name": "com.test:corrupt:1.0", "natives": {"windows": "natives-windows"}},
                {"name": "com.test:truncated:1.0", "natives": {"windows": "natives-windows"}},
            ]
        }
        target_dir2 = os.path.join(self.temp_dir, "target2")
        # Must not raise BadZipFile or crash the launcher
        res2 = self.runner.extract_natives(version_json_corrupt, mc_version="26.2", target_dir=target_dir2, force_reextract=True)
        self.assertEqual(res2, target_dir2)

    def test_natives_architecture_isolation_modern_vs_legacy(self):
        """Verifies 32-bit and wrong-version binaries are strictly excluded to avoid linkage crashes."""
        libs_dir = os.path.join(self.temp_dir, "mixed_libs")
        os.makedirs(libs_dir, exist_ok=True)
        self.runner.libraries_dirs = [libs_dir]

        # Put 32-bit x86 jar, ARM64 jar, LWJGL2 jar, and LWJGL3 jar
        self._create_synthetic_native_jar(os.path.join(libs_dir, "lwjgl-3.3.3-natives-windows-x86.jar"), {"lwjgl.dll": b"32BIT_X86"})
        self._create_synthetic_native_jar(os.path.join(libs_dir, "lwjgl-3.3.3-natives-windows-arm64.jar"), {"lwjgl.dll": b"ARM64"})
        self._create_synthetic_native_jar(os.path.join(libs_dir, "lwjgl-platform-2.9.4-natives-windows.jar"), {"lwjgl64.dll": b"LWJGL2_64", "OpenAL64.dll": b"OPENAL2_64"})
        self._create_synthetic_native_jar(os.path.join(libs_dir, "lwjgl-3.3.3-natives-windows.jar"), {"lwjgl.dll": b"LWJGL3_64", "glfw.dll": b"GLFW3_64"})

        # Case A: Modern 26.2 -> Must only extract LWJGL3 64-bit and reject LWJGL2 and 32-bit
        target_modern = os.path.join(self.temp_dir, "nat_modern")
        self.runner.extract_natives({}, mc_version="26.2", target_dir=target_modern, force_reextract=True)
        self.assertTrue(os.path.isfile(os.path.join(target_modern, "lwjgl.dll")))
        with open(os.path.join(target_modern, "lwjgl.dll"), "rb") as f:
            self.assertEqual(f.read(), b"LWJGL3_64")
        self.assertFalse(os.path.isfile(os.path.join(target_modern, "lwjgl64.dll")))

        # Case B: Legacy 1.8.9 -> Must only extract LWJGL2 64-bit
        target_legacy = os.path.join(self.temp_dir, "nat_legacy")
        self.runner.extract_natives({}, mc_version="1.8.9", target_dir=target_legacy, force_reextract=True)
        self.assertTrue(os.path.isfile(os.path.join(target_legacy, "lwjgl64.dll")))
        self.assertTrue(os.path.isfile(os.path.join(target_legacy, "OpenAL64.dll")))
        with open(os.path.join(target_legacy, "lwjgl64.dll"), "rb") as f:
            self.assertEqual(f.read(), b"LWJGL2_64")

    def test_rapid_concurrent_natives_extraction(self):
        """Stress tests 12 concurrent worker threads simultaneously triggering extract_natives."""
        libs_dir = os.path.join(self.temp_dir, "conc_libs")
        os.makedirs(libs_dir, exist_ok=True)
        self._create_synthetic_native_jar(
            os.path.join(libs_dir, "lwjgl-3.3.3-natives-windows.jar"),
            {"lwjgl.dll": b"THREAD_LWJGL", "glfw.dll": b"THREAD_GLFW"},
        )
        self.runner.libraries_dirs = [libs_dir]

        target_dir = os.path.join(self.temp_dir, "conc_target")

        def extract_task(idx):
            runner_inst = NativeMinecraftRunner(self.root_dir, self.state_dir)
            runner_inst.libraries_dirs = [libs_dir]
            return runner_inst.extract_natives({}, mc_version="26.2", target_dir=target_dir, force_reextract=False)

        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            futures = [executor.submit(extract_task, i) for i in range(24)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        self.assertEqual(len(results), 24)
        for r in results:
            self.assertTrue(os.path.isdir(r))


class TestChallengerClasspathAssemblyAdversarial(unittest.TestCase):
    """Adversarial stress-testing of Dynamic Classpath Assembly against corrupt/missing configs and rule edge cases."""

    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.temp_dir = tempfile.mkdtemp(prefix="sir_challenger_cp_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.runner = NativeMinecraftRunner(self.root_dir, self.state_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def test_scope_corrupted_and_missing_json_manifests(self):
        """Scope Item 3: Adversarially test dynamic classpath assembly with simulated corrupted/missing JSON manifests."""
        # 1. Non-existent instance dir
        res_nonexistent = self.runner.inspect_instance_config(os.path.join(self.temp_dir, "does_not_exist"))
        self.assertEqual(res_nonexistent["components"], [])
        self.assertEqual(res_nonexistent["loader"], "")

        # 2. Corrupted mmc-pack.json (syntax error / truncated JSON)
        inst_corrupt = os.path.join(self.temp_dir, "inst_corrupt")
        os.makedirs(inst_corrupt, exist_ok=True)
        with open(os.path.join(inst_corrupt, "mmc-pack.json"), "w", encoding="utf-8") as f:
            f.write("{\"components\": [{\"uid\": \"net.fabricmc.fabric-loader\", \"version\": \"0.15.11\"")  # Unclosed JSON

        res_corrupt = self.runner.inspect_instance_config(inst_corrupt)
        self.assertEqual(res_corrupt["components"], [])

        # 3. Non-dictionary JSON (e.g. integer or list at root)
        with open(os.path.join(inst_corrupt, "mmc-pack.json"), "w", encoding="utf-8") as f:
            f.write("[1, 2, 3, \"malformed\"]")

        res_list = self.runner.inspect_instance_config(inst_corrupt)
        self.assertEqual(res_list["components"], [])

        # 4. Corrupted instance.cfg (binary garbage, null bytes, huge lines)
        with open(os.path.join(inst_corrupt, "instance.cfg"), "wb") as f:
            f.write(b"\x00\xFF\xFE\x00MinMemAlloc=NOT_A_NUMBER\nMaxMemAlloc=4096\n#Comment\n===invalid===")

        res_cfg = self.runner.inspect_instance_config(inst_corrupt)
        self.assertEqual(res_cfg["max_ram_mb"], 4096)
        self.assertIsNone(res_cfg["min_ram_mb"])

    def test_classpath_assembly_with_corrupt_version_json(self):
        """Tests build_classpath resilient recovery when version_json is empty, corrupted, or missing fields."""
        # Setup fake libraries directory with minimal structure
        libs_dir = os.path.join(self.temp_dir, "libraries")
        os.makedirs(os.path.join(libs_dir, "net", "fabricmc", "fabric-loader", "0.19.3"), exist_ok=True)
        loader_jar = os.path.join(libs_dir, "net", "fabricmc", "fabric-loader", "0.19.3", "fabric-loader-0.19.3.jar")
        with open(loader_jar, "wb") as f:
            f.write(b"LOADER_JAR")

        self.runner.libraries_dirs = [libs_dir]

        # Case 1: Completely empty version_json dictionary -> constructs classpath without exceptions
        cp1 = self.runner.build_classpath(
            version_json={},
            mc_version="26.2",
            loader="fabric",
        )
        self.assertIsInstance(cp1, list)
        self.assertTrue(len(cp1) > 0)
        # Should include fabric-loader if available
        self.assertTrue(any("fabric-loader" in j for j in cp1))

        # Case 2: version_json with malformed libraries entries (empty dicts, missing paths, rules)
        malformed_version_json = {
            "id": "26.2",
            "libraries": [
                {},
                {"name": "malformed_coord"},
                {"name": "valid.group:valid-artifact:1.0.0", "rules": [{"action": "disallow", "os": {"name": "windows"}}]},
            ]
        }
        cp2 = self.runner.build_classpath(
            version_json=malformed_version_json,
            mc_version="26.2",
            loader="fabric",
        )
        self.assertIsInstance(cp2, list)

    def test_mojang_library_rules_combinatorial_matrix(self):
        """Verifies Mojang OS rules evaluation under various platform & architecture constraints."""
        # 1. Allow on Windows x64, disallow OSX
        rules1 = [
            {"action": "disallow", "os": {"name": "osx"}},
            {"action": "allow", "os": {"name": "windows"}},
        ]
        self.assertTrue(self.runner.evaluate_library_rules(rules1, target_os="windows", target_arch="x64"))
        self.assertFalse(self.runner.evaluate_library_rules(rules1, target_os="osx", target_arch="x64"))

        # 2. Allow on Windows x86 only
        rules_x86 = [
            {"action": "allow", "os": {"name": "windows", "arch": "x86"}},
        ]
        self.assertFalse(self.runner.evaluate_library_rules(rules_x86, target_os="windows", target_arch="x64"))
        self.assertTrue(self.runner.evaluate_library_rules(rules_x86, target_os="windows", target_arch="x86"))

        # 3. Rule with unsupported feature flag (should be ignored/skipped)
        rules_feat = [
            {"action": "allow", "features": {"is_quick_play_multiplayer": True}},
        ]
        self.assertFalse(self.runner.evaluate_library_rules(rules_feat, target_os="windows", target_arch="x64"))

    def test_monolithic_vs_modular_asm_deduplication(self):
        """Verifies that monolithic ASM (asm-all-5.0.3) is excluded on Fabric to prevent JVM classloader conflicts."""
        libs_dir = os.path.join(self.temp_dir, "asm_libs")
        os.makedirs(libs_dir, exist_ok=True)
        self.runner.libraries_dirs = [libs_dir]

        version_json = {
            "id": "26.2",
            "libraries": [
                {"name": "org.ow2.asm:asm:9.10.1"},
                {"name": "org.ow2.asm:asm-all:5.0.3"},  # Monolithic legacy ASM that would break Java 21+ Fabric
            ]
        }
        cp = self.runner.build_classpath(version_json, mc_version="26.2", loader="fabric")
        self.assertFalse(any("asm-all" in j for j in cp), "Monolithic asm-all was not excluded from Fabric classpath!")


if __name__ == "__main__":
    unittest.main()
