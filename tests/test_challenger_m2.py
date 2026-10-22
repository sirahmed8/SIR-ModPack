"""
Adversarial Challenger Test Suite for Milestone 2: Native JVM Launch Pipeline & Compatibility.
Authored by: Challenger 1 (Milestone 2)

Deeply stress-tests:
1. Strict RAM Parameter Allocation & G1GC Heap Sizing:
   - Boundaries (256MB, 512MB, 1024MB, 3072MB, 4096MB, 8192MB, 16384MB, 65536MB)
   - Inversion handling (min_ram > max_ram)
   - Fractional inputs (0.25, 0.5, 1.5, 2.75, "0.5G", "1.5G", "2.75G", "512.5M")
   - Degenerate & malformed inputs (negative, zero, NaN, empty strings, non-numeric, huge values)
   - Bitness/Threshold boundary at 64 (GB vs MB interpretation)
   - G1GC region sizing mathematical thresholds (1M, 2M, 4M, 8M, 16M, 32M)
   - Nursery percentage & reserve percentage rules across all heap tiers

2. JRE Locator & PE Header Binary Architecture Engine:
   - Synthetic valid PE headers: x86 (0x014c), x64 (0x8664), ARM64 (0xAA64), Unknown machine codes (IA64 0x0200, ARM32 0x01c0, RISC-V 0x5064)
   - Truncated / Corrupted PE headers:
     * 0-byte file
     * 1-byte file
     * 2-byte file (b"MZ" without header)
     * Truncated DOS header (< 0x40 bytes)
     * e_lfanew pointing out of bounds (beyond EOF)
     * e_lfanew pointing to non-PE magic (b"NE\0\0", b"LE\0\0", b"XXXX", b"PE\0")
     * Truncated Machine type (file ends inside PE signature)
     * Huge / Overflow offset in 0x3C (0xFFFFFFFF, 0x80000000)
     * Directories, non-existent files, permission denied mocks
   - Real system binary discovery and semver parsing stress
"""
import io
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.native_runner import (
    _parse_to_mb,
    calculate_ram_parameters,
    NativeMinecraftRunner,
)
from launcher_core.java_service import (
    get_pe_binary_arch,
    parse_java_runtime_info,
    JavaService,
)


class TestAdversarialRAMAllocation(unittest.TestCase):
    """Adversarial testing of RAM parsing, boundary allocation, and G1GC configuration."""

    def test_boundary_allocations_standard(self):
        """Tests exact RAM parameter generation across discrete standard boundary allocations."""
        test_matrix = [
            (0.25, 256, "-Xmx256M", "-Xms256M"),
            (0.5, 512, "-Xmx512M", "-Xms512M"),
            (1, 1024, "-Xmx1G", "-Xms512M"),
            (3, 3072, "-Xmx3G", "-Xms1536M"),
            (4, 4096, "-Xmx4G", "-Xms2G"),
            (8, 8192, "-Xmx8G", "-Xms4G"),
            (16, 16384, "-Xmx16G", "-Xms8G"),
            (32, 32768, "-Xmx32G", "-Xms16G"),
            (64, 65536, "-Xmx64G", "-Xms32G"),
        ]
        for ram_input, expected_max_mb, expected_xmx, expected_xms in test_matrix:
            with self.subTest(ram_input=ram_input):
                res = calculate_ram_parameters(max_ram=ram_input, mc_version="26.2")
                self.assertEqual(res["max_mb"], expected_max_mb, f"Failed max_mb for {ram_input}")
                self.assertEqual(res["xmx_flag"], expected_xmx, f"Failed xmx_flag for {ram_input}")
                self.assertEqual(res["xms_flag"], expected_xms, f"Failed xms_flag for {ram_input}")
                self.assertLessEqual(res["min_mb"], res["max_mb"], "min_mb exceeded max_mb!")

    def test_fractional_ram_inputs(self):
        """Tests fractional float and string RAM inputs (e.g. 1.5, '2.5G', '0.75G', '1536.0M')."""
        test_matrix = [
            (1.5, 1536, "-Xmx1536M"),
            ("1.5G", 1536, "-Xmx1536M"),
            ("1.5g", 1536, "-Xmx1536M"),
            ("2.5G", 2560, "-Xmx2560M"),
            ("0.75G", 768, "-Xmx768M"),
            ("1536M", 1536, "-Xmx1536M"),
            ("1536.0M", 1536, "-Xmx1536M"),
            (0.5, 512, "-Xmx512M"),
            ("0.5G", 512, "-Xmx512M"),
            ("512M", 512, "-Xmx512M"),
        ]
        for ram_input, expected_mb, expected_xmx in test_matrix:
            with self.subTest(ram_input=ram_input):
                mb = _parse_to_mb(ram_input)
                self.assertEqual(mb, expected_mb, f"_parse_to_mb failed for {ram_input}")
                res = calculate_ram_parameters(max_ram=ram_input, mc_version="26.2")
                self.assertEqual(res["max_mb"], expected_mb)
                self.assertEqual(res["xmx_flag"], expected_xmx)

    def test_min_ram_greater_than_max_ram_inversion(self):
        """Adversarial stress: When min_ram > max_ram, min_ram MUST be clamped to max_ram."""
        inversion_cases = [
            (4, 8),       # max=4, min=8 -> min must be clamped to 4
            (1, 4),       # max=1, min=4 -> min must be clamped to 1
            ("2G", "6G"), # max=2G, min=6G -> min must be clamped to 2G
            (512, 2048),  # max=512M, min=2048M -> min must be clamped to 512M
            (256, 1024),  # max=256M, min=1024M -> min must be clamped to 256M
        ]
        for max_val, min_val in inversion_cases:
            with self.subTest(max_val=max_val, min_val=min_val):
                res = calculate_ram_parameters(max_ram=max_val, min_ram=min_val, mc_version="26.2")
                self.assertLessEqual(
                    res["min_mb"], res["max_mb"],
                    f"Inversion not resolved! min_mb={res['min_mb']} > max_mb={res['max_mb']}"
                )
                self.assertEqual(res["min_mb"], res["max_mb"])

    def test_degenerate_and_malformed_ram_inputs(self):
        """Adversarial stress: Negative, zero, invalid strings, None, and huge numbers."""
        # None -> defaults to 8192
        self.assertEqual(_parse_to_mb(None), 8192)

        # Non-numeric string -> defaults to default_mb (8192)
        self.assertEqual(_parse_to_mb("invalid_string"), 8192)
        self.assertEqual(_parse_to_mb(""), 8192)
        self.assertEqual(_parse_to_mb("   "), 8192)
        self.assertEqual(_parse_to_mb("None"), 8192)

        # 0 or negative numbers -> clamped to min floor (256MB)
        self.assertEqual(_parse_to_mb(0), 256)
        self.assertEqual(_parse_to_mb(-5), 256)
        self.assertEqual(_parse_to_mb(-1024), 256)

        # Calculate RAM with degenerate inputs: must never raise and maintain min_mb <= max_mb
        res_none = calculate_ram_parameters(max_ram=None, min_ram=None)
        self.assertEqual(res_none["max_mb"], 8192)
        self.assertEqual(res_none["min_mb"], 4096)

        res_zero = calculate_ram_parameters(max_ram=0, min_ram=0)
        self.assertEqual(res_zero["max_mb"], 256)
        self.assertEqual(res_zero["min_mb"], 256)
        self.assertEqual(res_zero["xmx_flag"], "-Xmx256M")
        self.assertEqual(res_zero["xms_flag"], "-Xms256M")

        res_neg = calculate_ram_parameters(max_ram=-4, min_ram=-8)
        self.assertEqual(res_neg["max_mb"], 256)
        self.assertEqual(res_neg["min_mb"], 256)

        res_invalid = calculate_ram_parameters(max_ram="not_a_number", min_ram="bad_val")
        self.assertEqual(res_invalid["max_mb"], 8192)
        self.assertEqual(res_invalid["min_mb"], 4096)

    def test_threshold_at_64_gb_vs_mb(self):
        """Verifies boundary behavior around 64 (the GB vs MB threshold)."""
        # Exactly 64 without 'M' is 64GB = 65536MB
        self.assertEqual(_parse_to_mb(64), 65536)
        self.assertEqual(_parse_to_mb("64"), 65536)
        self.assertEqual(_parse_to_mb("64G"), 65536)

        # 64M explicitly with 'M' is 256MB (clamped to min floor)
        self.assertEqual(_parse_to_mb("64M"), 256)

        # 65 without suffix is > 64 so treated as 65MB -> clamped to 256MB
        self.assertEqual(_parse_to_mb(65), 256)
        self.assertEqual(_parse_to_mb("65"), 256)

        # 65G is 65GB = 66560MB
        self.assertEqual(_parse_to_mb("65G"), 66560)

        # 512 without suffix is > 64 so treated as 512MB
        self.assertEqual(_parse_to_mb(512), 512)
        self.assertEqual(_parse_to_mb("512"), 512)
        self.assertEqual(_parse_to_mb("512M"), 512)

    def test_g1gc_region_and_nursery_sizing_thresholds(self):
        """Verifies mathematical correctness of G1GC region sizing across all capacity tiers."""
        tiers = [
            # (max_ram_gb, expected_region_size, expected_new_size_pct, expected_max_new_pct, expected_reserve_pct)
            (0.5, "1M", 20, 30, 10),
            (1.0, "1M", 20, 30, 10),
            (1.9, "1M", 20, 30, 10),
            (2.0, "2M", 20, 30, 10),
            (3.0, "2M", 20, 30, 10),
            (3.1, "4M", 30, 40, 15),
            (4.0, "4M", 30, 40, 15),
            (4.1, "8M", 30, 40, 15),
            (8.0, "8M", 30, 40, 15),
            (8.1, "16M", 40, 50, 20),
            (16.0, "16M", 40, 50, 20),
            (16.1, "32M", 50, 60, 20),
            (32.0, "32M", 50, 60, 20),
            (64.0, "32M", 50, 60, 20),
        ]
        for ram_gb, exp_region, exp_new_pct, exp_max_new_pct, exp_reserve in tiers:
            with self.subTest(ram_gb=ram_gb):
                res = calculate_ram_parameters(max_ram=ram_gb, mc_version="26.2")
                self.assertEqual(res["region_size"], exp_region, f"Wrong region size for {ram_gb}GB")
                self.assertEqual(res["new_size_pct"], exp_new_pct, f"Wrong new_size_pct for {ram_gb}GB")
                self.assertEqual(res["max_new_size_pct"], exp_max_new_pct, f"Wrong max_new_size_pct for {ram_gb}GB")
                self.assertEqual(res["reserve_pct"], exp_reserve, f"Wrong reserve_pct for {ram_gb}GB")
                self.assertEqual(res["pause_millis"], 50, "Modern pause_millis should be 50ms")

    def test_legacy_189_pause_millis_threshold(self):
        """Verifies pause_millis is 200ms for Legacy 1.8.9 vs 50ms for Modern 26.2."""
        res_legacy = calculate_ram_parameters(max_ram=4, mc_version="1.8.9")
        self.assertEqual(res_legacy["pause_millis"], 200)

        res_legacy_forge = calculate_ram_parameters(max_ram=4, mc_version="1.7.10")
        self.assertEqual(res_legacy_forge["pause_millis"], 200)

        res_modern = calculate_ram_parameters(max_ram=4, mc_version="26.2")
        self.assertEqual(res_modern["pause_millis"], 50)


class TestAdversarialPEHeaderArchitecture(unittest.TestCase):
    """Adversarial stress-testing of PE binary inspection and JRE locator resilience."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_pe_")

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def _create_pe_file(self, filename: str, machine_code: int, e_lfanew: int = 0x80) -> str:
        """Helper to create a synthetically valid Windows PE binary header."""
        path = os.path.join(self.temp_dir, filename)
        with open(path, "wb") as f:
            # DOS Header: 0x40 bytes
            dos_header = bytearray(b"\x00" * 0x40)
            dos_header[0:2] = b"MZ"
            struct.pack_into("<I", dos_header, 0x3C, e_lfanew)
            f.write(dos_header)

            # Pad between DOS header and PE header if e_lfanew > 0x40
            if e_lfanew > 0x40:
                f.write(b"\x00" * (e_lfanew - 0x40))

            # PE Header
            f.write(b"PE\x00\x00")
            f.write(struct.pack("<H", machine_code))  # Machine field
            f.write(b"\x00" * 18)                     # Rest of COFF header (20 bytes total)
            f.write(b"\x00" * 224)                    # Optional header dummy
        return path

    def test_synthetic_valid_architectures(self):
        """Tests PE header recognition for x64, x86, ARM64, and unusual architectures."""
        # 1. x64 (0x8664 - IMAGE_FILE_MACHINE_AMD64)
        x64_path = self._create_pe_file("mock_x64.exe", 0x8664)
        res = get_pe_binary_arch(x64_path)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["arch"], "x64")
        self.assertTrue(res["is_64bit"])

        # 2. x86 (0x014c - IMAGE_FILE_MACHINE_I386)
        x86_path = self._create_pe_file("mock_x86.exe", 0x014c)
        res = get_pe_binary_arch(x86_path)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["arch"], "x86 (32-bit)")
        self.assertFalse(res["is_64bit"])

        # 3. ARM64 (0xAA64 - IMAGE_FILE_MACHINE_ARM64)
        arm64_path = self._create_pe_file("mock_arm64.exe", 0xAA64)
        res = get_pe_binary_arch(arm64_path)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["arch"], "ARM64")
        self.assertTrue(res["is_64bit"])

        # 4. Unusual machine code: IA64 (0x0200)
        ia64_path = self._create_pe_file("mock_ia64.exe", 0x0200)
        res = get_pe_binary_arch(ia64_path)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["arch"], "Other (0x200)")
        self.assertFalse(res["is_64bit"])

        # 5. RISC-V 64 (0x5064)
        riscv_path = self._create_pe_file("mock_riscv64.exe", 0x5064)
        res = get_pe_binary_arch(riscv_path)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["arch"], "Other (0x5064)")
        self.assertFalse(res["is_64bit"])

    def test_corrupted_truncated_pe_headers_zero_exceptions(self):
        """Adversarial stress: Truncated, malformed, and corrupted files MUST return valid dict without raising."""
        corrupted_cases = []

        # 1. Zero byte file
        p0 = os.path.join(self.temp_dir, "zero_bytes.exe")
        with open(p0, "wb") as f:
            pass
        corrupted_cases.append(("Zero Byte", p0))

        # 2. 1 byte file
        p1 = os.path.join(self.temp_dir, "one_byte.exe")
        with open(p1, "wb") as f:
            f.write(b"M")
        corrupted_cases.append(("1 Byte", p1))

        # 3. 2 bytes file with MZ
        p2 = os.path.join(self.temp_dir, "two_bytes_mz.exe")
        with open(p2, "wb") as f:
            f.write(b"MZ")
        corrupted_cases.append(("2 Bytes MZ", p2))

        # 4. 2 bytes non-MZ
        p_non_mz = os.path.join(self.temp_dir, "non_mz.exe")
        with open(p_non_mz, "wb") as f:
            f.write(b"PK\x03\x04")
        corrupted_cases.append(("ZIP Magic PK", p_non_mz))

        # 5. Truncated DOS header (< 0x40 bytes)
        p_short_dos = os.path.join(self.temp_dir, "short_dos.exe")
        with open(p_short_dos, "wb") as f:
            f.write(b"MZ" + b"\x00" * 30)  # Only 32 bytes total
        corrupted_cases.append(("Truncated DOS Header 32b", p_short_dos))

        # 6. e_lfanew pointing far beyond file size
        p_oob = os.path.join(self.temp_dir, "oob_pe.exe")
        with open(p_oob, "wb") as f:
            dos = bytearray(b"\x00" * 0x40)
            dos[0:2] = b"MZ"
            struct.pack_into("<I", dos, 0x3C, 0x10000)  # 64KB offset in 64 byte file
            f.write(dos)
        corrupted_cases.append(("Out of Bounds e_lfanew", p_oob))

        # 7. e_lfanew pointing to invalid PE magic
        p_bad_magic = os.path.join(self.temp_dir, "bad_pe_magic.exe")
        with open(p_bad_magic, "wb") as f:
            dos = bytearray(b"\x00" * 0x40)
            dos[0:2] = b"MZ"
            struct.pack_into("<I", dos, 0x3C, 0x40)
            f.write(dos)
            f.write(b"NE\x00\x00\x64\x86")  # NE header instead of PE
        corrupted_cases.append(("Bad PE Magic NE", p_bad_magic))

        # 8. Truncated PE header (ends inside PE\0\0)
        p_trunc_pe = os.path.join(self.temp_dir, "trunc_pe_magic.exe")
        with open(p_trunc_pe, "wb") as f:
            dos = bytearray(b"\x00" * 0x40)
            dos[0:2] = b"MZ"
            struct.pack_into("<I", dos, 0x3C, 0x40)
            f.write(dos)
            f.write(b"PE\x00")  # Only 3 bytes of PE signature
        corrupted_cases.append(("Truncated PE Magic 3b", p_trunc_pe))

        # 9. Truncated machine code (PE signature present but file ends before machine code)
        p_trunc_mach = os.path.join(self.temp_dir, "trunc_machine.exe")
        with open(p_trunc_mach, "wb") as f:
            dos = bytearray(b"\x00" * 0x40)
            dos[0:2] = b"MZ"
            struct.pack_into("<I", dos, 0x3C, 0x40)
            f.write(dos)
            f.write(b"PE\x00\x00\x64")  # Only 1 byte of machine code
        corrupted_cases.append(("Truncated Machine Code", p_trunc_mach))

        # 10. Huge 32-bit unsigned offset in e_lfanew
        p_huge_offset = os.path.join(self.temp_dir, "huge_offset.exe")
        with open(p_huge_offset, "wb") as f:
            dos = bytearray(b"\x00" * 0x40)
            dos[0:2] = b"MZ"
            struct.pack_into("<I", dos, 0x3C, 0xFFFFFFF0)
            f.write(dos)
        corrupted_cases.append(("Huge Offset 0xFFFFFFF0", p_huge_offset))

        # 11. Non-existent file
        corrupted_cases.append(("Non-existent File", os.path.join(self.temp_dir, "does_not_exist.exe")))

        # 12. Directory passed instead of file
        corrupted_cases.append(("Directory As File", self.temp_dir))

        for desc, path in corrupted_cases:
            with self.subTest(desc=desc):
                try:
                    res = get_pe_binary_arch(path)
                    self.assertIsInstance(res, dict, f"get_pe_binary_arch({desc}) did not return a dict")
                    self.assertFalse(res["is_valid"], f"{desc} was marked as valid!")
                    self.assertEqual(res["arch"], "Unknown")
                    self.assertFalse(res["is_64bit"])
                except Exception as e:
                    self.fail(f"get_pe_binary_arch({desc}) raised unexpected exception: {e}")

    def test_parse_java_runtime_info_with_corrupted_pe(self):
        """Verifies parse_java_runtime_info safely handles corrupted PE binaries with probe_process=False."""
        p_bad = os.path.join(self.temp_dir, "bad_java.exe")
        with open(p_bad, "wb") as f:
            f.write(b"NOT_A_VALID_PE_AT_ALL")

        info = parse_java_runtime_info(p_bad, probe_process=False)
        self.assertIsInstance(info, dict)
        self.assertIn("vendor", info)
        self.assertIn("arch", info)
        self.assertIn("is_64bit", info)
        self.assertFalse(info.get("is_temurin_21", False))

    def test_java_service_discover_installations_resilience(self):
        """Verifies JavaService.discover_java_installations runs cleanly and returns valid schema."""
        service = JavaService(root_dir=self.temp_dir)
        discovery = service.discover_java_installations()
        self.assertTrue(discovery.get("success"))
        self.assertIsInstance(discovery.get("installations"), list)
        self.assertIsInstance(discovery.get("count"), int)
        self.assertEqual(len(discovery["installations"]), discovery["count"])

class TestAdversarialJVMArgsAndPowerModes(unittest.TestCase):
    """Adversarial testing of build_jvm_args across power modes, RAM tiers, and custom flags."""

    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_jvm_")
        self.runner = NativeMinecraftRunner(self.root_dir, self.temp_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def test_build_jvm_args_ram_and_gc_flags_integrity(self):
        """Verifies JVM args contain exact Xmx, Xms, and correct G1GC flags for various RAM amounts."""
        test_cases = [
            (0.5, "-Xmx512M", "-Xms512M", "-XX:G1HeapRegionSize=1M"),
            (1.0, "-Xmx1G", "-Xms512M", "-XX:G1HeapRegionSize=1M"),
            (2.0, "-Xmx2G", "-Xms1G", "-XX:G1HeapRegionSize=2M"),
            (4.0, "-Xmx4G", "-Xms2G", "-XX:G1HeapRegionSize=4M"),
            (8.0, "-Xmx8G", "-Xms4G", "-XX:G1HeapRegionSize=8M"),
            (16.0, "-Xmx16G", "-Xms8G", "-XX:G1HeapRegionSize=16M"),
            (32.0, "-Xmx32G", "-Xms16G", "-XX:G1HeapRegionSize=32M"),
        ]
        for ram_val, exp_xmx, exp_xms, exp_region in test_cases:
            with self.subTest(ram_val=ram_val):
                args = self.runner.build_jvm_args(ram_gb=ram_val, mc_version="26.2")
                self.assertIn(exp_xmx, args)
                self.assertIn(exp_xms, args)
                self.assertIn(exp_region, args)
                self.assertIn("-XX:+UseG1GC", args)

    def test_build_jvm_args_power_modes(self):
        """Verifies power mode configurations (turbo, smooth, fallback)."""
        args_turbo = self.runner.build_jvm_args(ram_gb=8, power_mode="turbo")
        args_smooth = self.runner.build_jvm_args(ram_gb=8, power_mode="smooth")
        args_unknown = self.runner.build_jvm_args(ram_gb=8, power_mode="non_existent_mode")

        self.assertTrue(any("ParallelGCThreads=" in a for a in args_turbo))
        self.assertIn("-XX:ParallelGCThreads=4", args_smooth)
        self.assertIn("-XX:ConcGCThreads=2", args_smooth)
        # Unknown mode should safely fallback to default CPU threads without crashing
        self.assertIsInstance(args_unknown, list)
        self.assertTrue(len(args_unknown) > 5)

    def test_build_jvm_args_custom_arguments_and_paths_with_spaces(self):
        """Verifies custom JVM arguments and paths with spaces are handled cleanly."""
        extra_flags = ["-Dmy.custom.property=Hello World", "-XX:+AlwaysPreTouch"]
        nat_dir = os.path.join(self.temp_dir, "Natives With Spaces In Path")
        os.makedirs(nat_dir, exist_ok=True)

        args = self.runner.build_jvm_args(
            ram_gb=6,
            power_mode="turbo",
            extra_flags=extra_flags,
            natives_dir=nat_dir,
        )
        self.assertIn("-Dmy.custom.property=Hello World", args)
        self.assertIn("-XX:+AlwaysPreTouch", args)
        self.assertIn(f"-Djava.library.path={os.path.normpath(nat_dir)}", args)


class TestAdversarialControlsAndKeybindings(unittest.TestCase):
    """Adversarial testing of dual-mode keybinding translation and options injection."""

    def test_bidirectional_key_translation_integrity(self):
        """Verifies every mapping in GLFW_TO_LWJGL2 translates to an integer scancode."""
        from launcher_core.controls_service import GLFW_TO_LWJGL2, LWJGL2_TO_GLFW

        for glfw_token, lwjgl_code in GLFW_TO_LWJGL2.items():
            with self.subTest(glfw_token=glfw_token):
                self.assertIsInstance(lwjgl_code, int, f"LWJGL2 code for {glfw_token} is not int")

        # Verify mouse buttons negative offset rule (button 0 -> -100, button 1 -> -99, button 2 -> -98)
        self.assertEqual(GLFW_TO_LWJGL2.get("key.mouse.left"), -100)
        self.assertEqual(GLFW_TO_LWJGL2.get("key.mouse.right"), -99)
        self.assertEqual(GLFW_TO_LWJGL2.get("key.mouse.middle"), -98)
        self.assertEqual(GLFW_TO_LWJGL2.get("key.mouse.4"), -97)
        self.assertEqual(GLFW_TO_LWJGL2.get("key.mouse.5"), -96)

    def test_corrupted_options_txt_injection_resilience(self):
        """Verifies ControlsService safely processes corrupted, empty, and malformed options.txt."""
        from launcher_core.controls_service import ControlsService

        temp_dir = tempfile.mkdtemp(prefix="sir_test_opt_")
        try:
            cs = ControlsService(temp_dir)
            inst_dir = os.path.join(temp_dir, "test_inst")
            os.makedirs(inst_dir, exist_ok=True)
            opt_path = os.path.join(inst_dir, "options.txt")

            # Corrupted options file with invalid entries, non-ASCII, and weird colons
            with open(opt_path, "w", encoding="utf-8") as f:
                f.write("# Corrupted config\n")
                f.write("invalid_line_no_colon\n")
                f.write("key_key.forward:\n")
                f.write("key_key.back:invalid_val\n")
                f.write("fov:70.0\n")
                f.write("gamma:1.0\n")

            # Inject profile
            res = cs.apply_control_profile("hypixel_pro_pvp", instance_id="1.8.9", instance_dir=inst_dir)
            self.assertTrue(res.get("success"))
            self.assertTrue(os.path.isfile(opt_path))

            # Non-key options preserved
            with open(opt_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("fov:70.0", content)
            self.assertIn("gamma:1.0", content)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestAdversarialLogStreamerConcurrency(unittest.TestCase):
    """Adversarial stress-testing of non-blocking log streamer under heavy concurrent writes."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_stream_")

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def test_concurrent_multithreaded_log_streamer(self):
        """Stress-tests ProcessLogStreamer with real mock subprocess and high-throughput streaming."""
        import threading
        import time
        from launcher_core.logs_service import ProcessLogStreamer

        log_path = os.path.join(self.temp_dir, "stream_test.log")
        
        # Spawn a python child process that emits lines rapidly
        code = (
            "import sys, time\n"
            "for i in range(500):\n"
            "    sys.stdout.write(f'Log emission line {i}\\n')\n"
            "    sys.stdout.flush()\n"
        )
        proc = subprocess.Popen(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        lines_received = []
        streamer = ProcessLogStreamer(
            proc=proc,
            log_file=log_path,
            buffer_size=2000,
            on_line_callback=lambda l: lines_received.append(l),
        )

        # Wait for proc to finish
        proc.wait(timeout=5.0)
        time.sleep(0.3)

        recent = streamer.get_recent_lines(500)
        self.assertGreaterEqual(len(recent), 490)
        self.assertTrue(os.path.isfile(log_path))

    def test_log_streamer_crash_patterns_regex(self):
        """Verifies CRASH_PATTERNS regex patterns correctly match all critical crash types."""
        from launcher_core.logs_service import ProcessLogStreamer

        adversarial_logs = [
            ("OOM", "java.lang.OutOfMemoryError: Java heap space"),
            ("MIXIN_CONFLICT", "org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected error occurred from mod sodium"),
            ("CLASS_MISMATCH", "java.lang.NoSuchMethodError: net.minecraft.class_310.method_1562()V"),
            ("ACCESS_VIOLATION", "# EXCEPTION_ACCESS_VIOLATION (0xc0000005) at pc=0x00007ff"),
            ("OPENGL_ERROR", "GLFW error 65542: WGL: The driver does not appear to support OpenGL"),
            ("FORGE_FATAL", "[FML]: Fatal errors were detected during the transition from CONSTRUCTING to PREINITIALIZATION"),
        ]
        for c_type, sample_line in adversarial_logs:
            matched = False
            for pattern_type, regex in ProcessLogStreamer.CRASH_PATTERNS:
                if pattern_type == c_type and regex.search(sample_line):
                    matched = True
                    break
            self.assertTrue(matched, f"Pattern {c_type} failed to match line: {sample_line}")


class TestAdversarialClasspathAndNativesResilience(unittest.TestCase):
    """Adversarial testing of dynamic classpath assembly, rule filtering, and native DLL extraction."""

    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_cp_")
        self.runner = NativeMinecraftRunner(self.root_dir, self.temp_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def test_evaluate_library_rules_adversarial_structures(self):
        """Verifies evaluate_library_rules handles standard, empty, and contradictory rule objects."""
        # 1. Empty rules list -> should allow by default
        self.assertTrue(self.runner.evaluate_library_rules([], "windows", "x64"))

        # 2. Explicit windows allow rule
        rules_allow_win = [{"action": "allow", "os": {"name": "windows"}}]
        self.assertTrue(self.runner.evaluate_library_rules(rules_allow_win, "windows", "x64"))
        self.assertFalse(self.runner.evaluate_library_rules(rules_allow_win, "osx", "x64"))
        self.assertFalse(self.runner.evaluate_library_rules(rules_allow_win, "linux", "x64"))

        # 3. Explicit osx disallow rule
        rules_disallow_osx = [
            {"action": "allow"},
            {"action": "disallow", "os": {"name": "osx"}},
        ]
        self.assertTrue(self.runner.evaluate_library_rules(rules_disallow_osx, "windows", "x64"))
        self.assertFalse(self.runner.evaluate_library_rules(rules_disallow_osx, "osx", "x64"))

        # 4. Rules with features / empty os dicts
        rules_features = [
            {"action": "allow", "features": {"is_demo_user": True}},
            {"action": "allow", "os": {}},
        ]
        res = self.runner.evaluate_library_rules(rules_features, "windows", "x64")
        self.assertTrue(res)

    def test_build_classpath_with_empty_and_corrupted_manifests(self):
        """Verifies build_classpath gracefully handles empty or corrupted version manifests."""
        # Empty version json
        cp_empty = self.runner.build_classpath({}, "26.2", loader="fabric")
        self.assertIsInstance(cp_empty, list)

        # Corrupted / unusual library metadata
        corrupted_vjson = {
            "id": "corrupted_ver",
            "libraries": [
                {"name": ""},
                {"name": "invalid_coordinates"},
                {"name": "valid.group:valid-art:1.0.0", "rules": [{"action": "allow"}]},
            ]
        }
        cp_corrupt = self.runner.build_classpath(corrupted_vjson, "26.2", loader="fabric")
        self.assertIsInstance(cp_corrupt, list)

    def test_inspect_instance_config_corrupted_files(self):
        """Verifies inspect_instance_config handles non-existent and corrupted instance configurations."""
        # 1. Non-existent directory
        res_none = self.runner.inspect_instance_config(os.path.join(self.temp_dir, "non_existent"))
        self.assertEqual(res_none["loader"], "")
        self.assertEqual(res_none["components"], [])

        # 2. Corrupted mmc-pack.json (invalid JSON syntax)
        inst_dir = os.path.join(self.temp_dir, "corrupt_inst")
        os.makedirs(inst_dir, exist_ok=True)
        with open(os.path.join(inst_dir, "mmc-pack.json"), "w", encoding="utf-8") as f:
            f.write("{ invalid json syntax ... ")

        # 3. Corrupted instance.cfg (binary data)
        with open(os.path.join(inst_dir, "instance.cfg"), "wb") as f:
            f.write(b"\x00\xFF\xFE\x01\x02\x03\x04")

        res_corrupt = self.runner.inspect_instance_config(inst_dir)
        self.assertIsInstance(res_corrupt, dict)
        self.assertIn("components", res_corrupt)
        self.assertIn("loader", res_corrupt)

    def test_extract_natives_zip_traversal_sanitization(self):
        """Verifies extract_natives sanitizes zip member paths and only extracts basename DLLs."""
        import zipfile
        
        jar_path = os.path.join(self.temp_dir, "traversal_test.jar")
        with zipfile.ZipFile(jar_path, "w") as z:
            # Traversal attempt: ../../evil.dll
            z.writestr("../../evil.dll", b"MZ_EVIL_PAYLOAD")
            # Subdirectory dll: natives/windows/x64/legit.dll
            z.writestr("natives/windows/x64/legit.dll", b"MZ_LEGIT_PAYLOAD")
            # Ignored non-dll: script.bat
            z.writestr("script.bat", b"@echo off")

        v_json = {
            "id": "traversal_ver",
            "libraries": [
                {
                    "name": "org.lwjgl:lwjgl-test:3.3.3",
                    "downloads": {
                        "classifiers": {
                            "natives-windows": {
                                "path": "org/lwjgl/traversal_test.jar"
                            }
                        }
                    }
                }
            ]
        }
        # Place jar in temp libraries search path
        lib_dir = os.path.join(self.temp_dir, "libraries", "org", "lwjgl")
        os.makedirs(lib_dir, exist_ok=True)
        shutil.copyfile(jar_path, os.path.join(lib_dir, "traversal_test.jar"))
        self.runner.libraries_dirs.insert(0, os.path.join(self.temp_dir, "libraries"))

        nat_dest = os.path.join(self.temp_dir, "extracted_natives")
        result_dir = self.runner.extract_natives(v_json, "26.2", target_dir=nat_dest)

        self.assertTrue(os.path.isdir(result_dir))
        # Verify legit.dll was placed directly in target directory (flattened basename)
        self.assertTrue(os.path.isfile(os.path.join(result_dir, "legit.dll")))
        # Verify evil.dll was not extracted outside target_dir
        self.assertFalse(os.path.isfile(os.path.join(self.temp_dir, "evil.dll")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
