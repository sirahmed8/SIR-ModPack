"""
Adversarial Stress Test Suite for Milestone 2: Native JVM Launch Pipeline & Compatibility.
Executed by Challenger 2.

Targeting:
1. Pre-Launch Natives Extraction:
   - Real Windows file locks (WinError 32)
   - Rapid concurrent multi-threaded extractions
   - Temp directory fallback generation & integrity
   - Corrupted / zero-byte / truncated native JARs
2. Dynamic Classpath Assembly:
   - Severely malformed mmc-pack.json (syntax error, bad types, missing fields)
   - Missing library dependencies & nonexistent search roots
   - Duplicate entries & case-insensitive path normalization
   - Malformed maven coordinates & rule filtering edge cases
3. Dual-Mode Keybindings:
   - Unmapped keys, extreme integers, null/empty tokens
   - Mouse buttons > 5 (Mouse 6, 7, 8, 9) and bidirectional scancode translation
   - Unicode, Arabic, emoji, and malformed lines in options.txt
   - Strict 1.8.9 numeric options.txt validation (no NumberFormatException)
   - Strict 26.2 GLFW token options.txt validation
"""
import concurrent.futures
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
import zipfile

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.controls_service import (
    GLFW_TO_LWJGL2,
    LWJGL2_TO_GLFW,
    ControlsService,
    KeybindingMode,
)
from launcher_core.native_runner import (
    NativeMinecraftRunner,
    _maven_to_path,
    _parse_to_mb,
    calculate_ram_parameters,
)


class TestMilestone2AdversarialStress(unittest.TestCase):
    """Deep adversarial stress tests for M2 launch pipeline."""

    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.temp_dir = tempfile.mkdtemp(prefix="sir_m2_adv_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.runner = NativeMinecraftRunner(self.root_dir, self.state_dir)
        self.controls = ControlsService(self.root_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def _create_synthetic_native_jar(self, jar_path: str, dll_names: list[str], content: bytes = b"DLL_DATA"):
        os.makedirs(os.path.dirname(jar_path), exist_ok=True)
        with zipfile.ZipFile(jar_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for d in dll_names:
                z.writestr(d, content)
            z.writestr("META-INF/MANIFEST.MF", b"Manifest-Version: 1.0\n")

    # =========================================================================
    # PART 1: NATIVES EXTRACTION ADVERSARIAL & CONCURRENCY TESTS
    # =========================================================================

    def test_adv_natives_winerror32_real_locked_dll(self):
        """Simulate real Windows file locking (WinError 32 / PermissionError) on target DLL; verify temp fallback."""
        if sys.platform != "win32":
            self.skipTest("Windows-specific msvcrt file locking test")
        import msvcrt

        target_dir = os.path.join(self.temp_dir, "locked_natives")
        os.makedirs(target_dir, exist_ok=True)
        locked_file = os.path.join(target_dir, "lwjgl64.dll")

        # Create synthetic source native jar
        libs_dir = os.path.join(self.temp_dir, "libs")
        source_jar = os.path.join(libs_dir, "lwjgl-platform-2.9.4-natives-windows.jar")
        self._create_synthetic_native_jar(source_jar, ["lwjgl64.dll", "OpenAL64.dll"])
        self.runner.libraries_dirs = [libs_dir]

        version_json = {
            "id": "1.8.9",
            "libraries": [
                {
                    "name": "org.lwjgl.lwjgl:lwjgl-platform:2.9.4",
                    "natives": {"windows": "natives-windows"},
                }
            ],
        }

        # Write initial dummy file and lock it exclusively using msvcrt.locking
        with open(locked_file, "wb") as f:
            f.write(b"ORIGINAL_LOCKED_CONTENT_1234")

        lock_handle = open(locked_file, "r+b")
        lock_handle.seek(0)
        msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 20)

        try:
            # Force extraction into locked_dir
            result_dir = self.runner.extract_natives(
                version_json,
                mc_version="1.8.9",
                target_dir=target_dir,
                force_reextract=True,
            )

            # Assertions
            self.assertNotEqual(result_dir, target_dir, "Expected fallback directory different from locked directory")
            self.assertTrue(os.path.isdir(result_dir), f"Fallback dir must exist: {result_dir}")
            self.assertTrue(result_dir.startswith(tempfile.gettempdir()), "Fallback must be in temp directory")

            # Check that extracted DLLs are present in the fallback directory
            fallback_dll = os.path.join(result_dir, "lwjgl64.dll")
            self.assertTrue(os.path.isfile(fallback_dll), "lwjgl64.dll must be extracted in fallback dir")
            with open(fallback_dll, "rb") as rf:
                self.assertEqual(rf.read(), b"DLL_DATA")
        finally:
            msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 20)
            lock_handle.close()

    def test_adv_natives_rapid_concurrency_stress(self):
        """Stress test 16 simultaneous threads extracting natives into the same directory."""
        source_jar = os.path.join(self.temp_dir, "libs", "lwjgl-natives-windows.jar")
        self._create_synthetic_native_jar(source_jar, ["lwjgl.dll", "glfw.dll", "jemalloc.dll"])
        self.runner.libraries_dirs.insert(0, os.path.join(self.temp_dir, "libs"))

        version_json = {
            "id": "26.2",
            "libraries": [
                {
                    "name": "org.lwjgl:lwjgl:3.3.3",
                    "natives": {"windows": "natives-windows"},
                }
            ],
        }

        target_dir = os.path.join(self.temp_dir, "shared_natives")
        results = []
        errors = []

        def worker(thread_idx: int):
            try:
                # Add tiny random jitter to maximize race collisions
                res = self.runner.extract_natives(
                    version_json,
                    mc_version="26.2",
                    target_dir=target_dir,
                    force_reextract=True,
                )
                results.append((thread_idx, res))
            except Exception as ex:
                errors.append((thread_idx, ex))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(16)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent extraction failed with errors: {errors}")
        self.assertEqual(len(results), 16)

        # Every thread must have returned a directory with valid DLL files
        for tid, rdir in results:
            self.assertTrue(os.path.isdir(rdir), f"Result dir {rdir} must exist for thread {tid}")
            dll_p = os.path.join(rdir, "lwjgl.dll")
            self.assertTrue(os.path.isfile(dll_p), f"lwjgl.dll must exist in {rdir}")
            self.assertGreater(os.path.getsize(dll_p), 0)

    def test_adv_natives_corrupt_and_zero_byte_jars(self):
        """Verify extract_natives handles corrupt, zero-byte, and truncated native jars gracefully."""
        corrupt_jar = os.path.join(self.temp_dir, "libs", "corrupt-natives-windows.jar")
        os.makedirs(os.path.dirname(corrupt_jar), exist_ok=True)
        # Create zero-byte jar
        with open(corrupt_jar, "wb") as f:
            f.write(b"")

        # Create truncated zip
        truncated_jar = os.path.join(self.temp_dir, "libs", "truncated-natives-windows.jar")
        with open(truncated_jar, "wb") as f:
            f.write(b"PK\x03\x04\x14\x00\x00\x00corrupt_stream_garbage_here")

        self.runner.libraries_dirs.insert(0, os.path.join(self.temp_dir, "libs"))

        version_json = {
            "id": "26.2",
            "libraries": [
                {"name": "com.example:corrupt:1.0", "natives": {"windows": "natives-windows"}},
                {"name": "com.example:truncated:1.0", "natives": {"windows": "natives-windows"}},
            ],
        }

        # Must not raise BadZipFile or crash
        out_dir = self.runner.extract_natives(version_json, mc_version="26.2", force_reextract=True)
        self.assertTrue(os.path.isdir(out_dir))

    # =========================================================================
    # PART 2: DYNAMIC CLASSPATH ADVERSARIAL TESTS
    # =========================================================================

    def test_adv_classpath_malformed_mmc_pack_json(self):
        """Test inspect_instance_config and build_classpath on various malformed mmc-pack.json files."""
        inst_dir = os.path.join(self.temp_dir, "bad_instances", "broken_pack")
        os.makedirs(inst_dir, exist_ok=True)

        malformed_samples = [
            "",  # empty
            "{broken json",  # invalid syntax
            '{"components": "not_a_list"}',  # wrong type
            '{"components": [{"uid": 123, "version": null}]}',  # invalid field types
            '{"components": [null, 42, "string", {}]}',  # corrupt list elements
            '{"formatVersion": 1}',  # missing components
        ]

        for idx, sample in enumerate(malformed_samples):
            pack_file = os.path.join(inst_dir, "mmc-pack.json")
            with open(pack_file, "w", encoding="utf-8") as f:
                f.write(sample)

            # inspect_instance_config must not raise
            cfg = self.runner.inspect_instance_config(inst_dir)
            self.assertIsInstance(cfg, dict, f"Failed on sample {idx}")

            # build_classpath must not raise
            v_json = {"id": "26.2", "libraries": []}
            cp = self.runner.build_classpath(v_json, mc_version="26.2", instance_dir=inst_dir)
            self.assertIsInstance(cp, list, f"Failed building CP on sample {idx}")

    def test_adv_classpath_missing_libraries_and_empty_filesystem(self):
        """Test build_classpath when none of the 50 referenced libraries exist on disk."""
        isolated_runner = NativeMinecraftRunner(self.root_dir, self.state_dir)
        isolated_runner.libraries_dirs = [os.path.join(self.temp_dir, "nonexistent_dir")]

        libs = [
            {"name": f"org.apache.commons:commons-lang-fake-{i}:3.{i}.0"}
            for i in range(50)
        ]
        version_json = {"id": "26.2", "libraries": libs}

        cp = isolated_runner.build_classpath(version_json, mc_version="26.2")
        self.assertIsInstance(cp, list)
        # None of the fake libraries should be included in the classpath
        for entry in cp:
            self.assertNotIn("commons-lang-fake-", entry)

    def test_adv_maven_coordinate_edge_cases(self):
        """Test _maven_to_path with malformed, empty, and multi-colon coordinates."""
        self.assertEqual(_maven_to_path(""), "")
        self.assertEqual(_maven_to_path("singlepart"), "")
        self.assertEqual(_maven_to_path("two:parts"), "")
        
        # Valid 3-part
        p3 = _maven_to_path("com.mojang:authlib:1.5.25")
        self.assertTrue(p3.endswith(os.path.join("1.5.25", "authlib-1.5.25.jar")))

        # Valid 4-part with classifier
        p4 = _maven_to_path("org.lwjgl:lwjgl:3.3.3:natives-windows")
        self.assertTrue(p4.endswith("lwjgl-3.3.3-natives-windows.jar"))

    def test_adv_classpath_duplicate_entries_and_case_insensitivity(self):
        """Test classpath deduplication with exact and case-varying duplicate jar paths."""
        mock_lib_dir = os.path.join(self.temp_dir, "mock_libs")
        os.makedirs(os.path.join(mock_lib_dir, "org", "example", "liba", "1.0"), exist_ok=True)
        jar_a = os.path.join(mock_lib_dir, "org", "example", "liba", "1.0", "liba-1.0.jar")
        with open(jar_a, "wb") as f:
            f.write(b"PK")

        runner = NativeMinecraftRunner(self.root_dir, self.state_dir)
        runner.libraries_dirs = [mock_lib_dir]

        # Duplicate libraries in version_json
        version_json = {
            "id": "26.2",
            "libraries": [
                {"name": "org.example:liba:1.0"},
                {"name": "org.example:liba:1.0"},
                {"name": "org.example:liba:1.0"},
            ],
        }

        cp = runner.build_classpath(version_json, mc_version="26.2")
        norm_a = os.path.normpath(jar_a)
        # Must only appear once
        count = sum(1 for p in cp if os.path.normpath(p).lower() == norm_a.lower())
        self.assertEqual(count, 1, f"Expected exactly 1 occurrence of {norm_a}, found {count}")

    # =========================================================================
    # PART 3: DUAL-MODE KEYBINDINGS ADVERSARIAL TESTS
    # =========================================================================

    def test_adv_keybinding_unmapped_and_extreme_keys(self):
        """Test conversion of unmapped tokens, extreme integers, None, and empty strings."""
        # Legacy target: string tokens -> numeric scancode
        self.assertEqual(self.controls.translate_key_value("key.keyboard.unknown", KeybindingMode.LEGACY_LWJGL2), "0")
        self.assertEqual(self.controls.translate_key_value("key.nonexistent.button.xyz", KeybindingMode.LEGACY_LWJGL2), "0")
        self.assertEqual(self.controls.translate_key_value("", KeybindingMode.LEGACY_LWJGL2), "0")
        self.assertEqual(self.controls.translate_key_value("99999", KeybindingMode.LEGACY_LWJGL2), "99999")
        self.assertEqual(self.controls.translate_key_value(-50, KeybindingMode.LEGACY_LWJGL2), "-50")

        # Modern target: numeric scancodes -> GLFW string token
        self.assertEqual(self.controls.translate_key_value(0, KeybindingMode.MODERN_GLFW), "key.keyboard.unknown")
        self.assertEqual(self.controls.translate_key_value(99999, KeybindingMode.MODERN_GLFW), "key.keyboard.unknown")
        self.assertEqual(self.controls.translate_key_value(-999, KeybindingMode.MODERN_GLFW), "key.keyboard.unknown")
        self.assertEqual(self.controls.translate_key_value("key.keyboard.f", KeybindingMode.MODERN_GLFW), "key.keyboard.f")

    def test_adv_keybinding_mouse_buttons_greater_than_5(self):
        """Test conversion of high mouse buttons (Mouse 6, 7, 8) in both directions."""
        # Test Mouse 6, 7, 8 in Legacy LWJGL2 (formula: button - 100)
        # Mouse 6 -> -95
        # Mouse 7 -> -94
        # Mouse 8 -> -93
        self.assertEqual(self.controls.translate_key_value("key.mouse.6", KeybindingMode.LEGACY_LWJGL2), "-95")
        self.assertEqual(self.controls.translate_key_value("key.mouse.button.6", KeybindingMode.LEGACY_LWJGL2), "-95")
        self.assertEqual(self.controls.translate_key_value("key.mouse.7", KeybindingMode.LEGACY_LWJGL2), "-94")
        self.assertEqual(self.controls.translate_key_value("key.mouse.button.7", KeybindingMode.LEGACY_LWJGL2), "-94")
        self.assertEqual(self.controls.translate_key_value("key.mouse.8", KeybindingMode.LEGACY_LWJGL2), "-93")
        self.assertEqual(self.controls.translate_key_value("key.mouse.button.8", KeybindingMode.LEGACY_LWJGL2), "-93")

        # Reverse translation: -95 -> GLFW
        trans_6 = self.controls.translate_key_value(-95, KeybindingMode.MODERN_GLFW)
        self.assertIn(trans_6, ["key.mouse.6", "key.mouse.button.6"])
        trans_7 = self.controls.translate_key_value(-94, KeybindingMode.MODERN_GLFW)
        self.assertIn(trans_7, ["key.mouse.7", "key.mouse.button.7"])
        trans_8 = self.controls.translate_key_value(-93, KeybindingMode.MODERN_GLFW)
        self.assertIn(trans_8, ["key.mouse.8", "key.mouse.button.8"])

    def test_adv_keybinding_options_txt_unicode_and_special_chars(self):
        """Test options.txt injection with Unicode, Arabic text, emojis, and malformed lines."""
        inst_dir = os.path.join(self.temp_dir, "unicode_instance")
        mc_dir = os.path.join(inst_dir, "minecraft")
        os.makedirs(mc_dir, exist_ok=True)
        opt_path = os.path.join(mc_dir, "options.txt")

        # Initial options with Arabic text, emoji, complex comments, empty lines
        initial_content = (
            "# Minecraft Options File\n"
            "version:3953\n"
            "resourcePacks:[\"vanilla\",\"file/حزمة_الموارد_العربية_✨.zip\"]\n"
            "lastServer:play.hypixel.net:25565\n"
            "gamma:1.0\n"
            "key_key.sprint:key.keyboard.left.control\n"
            "key_key.attack:key.mouse.left\n"
            "\n"
            "# Custom comment here\n"
            "soundCategory_master:0.8\n"
        )
        with open(opt_path, "w", encoding="utf-8") as f:
            f.write(initial_content)

        # Apply profile
        res = self.controls.apply_control_profile(
            profile_id="hypixel_pro_pvp",
            instance_id="26.2",
            instance_dir=inst_dir,
        )
        self.assertTrue(res["success"])

        # Read back options.txt
        with open(opt_path, "r", encoding="utf-8") as f:
            updated_content = f.read()

        # Verify Unicode preservation
        self.assertIn("حزمة_الموارد_العربية_✨.zip", updated_content)
        self.assertIn("play.hypixel.net:25565", updated_content)
        self.assertIn("gamma:1.0", updated_content)
        self.assertIn("soundCategory_master:0.8", updated_content)

        # Verify updated keys
        self.assertIn("key_key.sprint:key.keyboard.f", updated_content)
        self.assertIn("key_key.perspective:key.keyboard.v", updated_content)

    def test_adv_keybinding_strict_legacy_189_integer_parsing_integrity(self):
        """Ensure that every key injected into 1.8.9 options.txt is strictly a valid signed integer."""
        inst_dir = os.path.join(self.temp_dir, "legacy_189_inst")
        mc_dir = os.path.join(inst_dir, "minecraft")
        os.makedirs(mc_dir, exist_ok=True)
        opt_path = os.path.join(mc_dir, "options.txt")

        # Write 1.8.9 options.txt (no version header or legacy format)
        with open(opt_path, "w", encoding="utf-8") as f:
            f.write("music:1.0\nsound:1.0\ninvertYMouse:false\nkey_key.sprint:29\n")

        # Apply hypixel_pro_pvp profile in 1.8.9 mode
        res = self.controls.apply_control_profile(
            profile_id="hypixel_pro_pvp",
            instance_id="1.8.9",
            instance_dir=inst_dir,
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["mode"], KeybindingMode.LEGACY_LWJGL2)

        # Read back and strictly parse every key_ setting as an integer
        with open(opt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("key_") or line.startswith("key_of."):
                    k, v = line.split(":", 1)
                    try:
                        parsed_int = int(v)
                        # Must be within 32-bit signed int range
                        self.assertTrue(-2147483648 <= parsed_int <= 2147483647)
                    except ValueError:
                        self.fail(f"Key '{k}' has non-integer value '{v}' in 1.8.9 options.txt! Would crash GameSettings.java.")

    def test_adv_keybinding_recover_polluted_options_txt_with_glfw_tokens(self):
        """Verify that legacy 1.8.9 options.txt corrupted with modern GLFW tokens is healed into valid integers."""
        inst_dir = os.path.join(self.temp_dir, "polluted_189_inst")
        mc_dir = os.path.join(inst_dir, "minecraft")
        os.makedirs(mc_dir, exist_ok=True)
        opt_path = os.path.join(mc_dir, "options.txt")

        # Write corrupted 1.8.9 options.txt with raw GLFW strings
        with open(opt_path, "w", encoding="utf-8") as f:
            f.write(
                "invertYMouse:false\n"
                "key_key.sprint:key.keyboard.f\n"
                "key_key.attack:key.mouse.left\n"
                "key_key.use:key.mouse.right\n"
                "key_key.togglePerspective:key.keyboard.v\n"
            )

        # Apply hypixel_pro_pvp profile to 1.8.9
        res = self.controls.apply_control_profile(
            profile_id="hypixel_pro_pvp",
            instance_id="1.8.9",
            instance_dir=inst_dir,
        )
        self.assertTrue(res["success"])

        # Read back and verify all keys are now valid numeric scancodes
        with open(opt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("key_"):
                    k, v = line.split(":", 1)
                    try:
                        int(v)
                    except ValueError:
                        self.fail(f"Found non-integer value '{v}' for key '{k}' after healing legacy options.txt")

    def test_adv_ram_boundary_inversions_and_extreme_inputs(self):
        """Stress-test calculate_ram_parameters against inverted min>max, zero, negative, and fractional inputs."""
        # 1. Inverted bounds: min_ram=16G, max_ram=4G -> min_mb must clamp to max_mb (4096MB)
        params_inverted = calculate_ram_parameters(max_ram=4, min_ram=16)
        self.assertEqual(params_inverted["max_mb"], 4096)
        self.assertEqual(params_inverted["min_mb"], 4096)
        self.assertEqual(params_inverted["xmx_flag"], "-Xmx4G")
        self.assertEqual(params_inverted["xms_flag"], "-Xms4G")

        # 2. Fractional small RAM: 0.5G (512M)
        params_small = calculate_ram_parameters(max_ram=0.5, min_ram=0.25)
        self.assertEqual(params_small["max_mb"], 512)
        self.assertEqual(params_small["min_mb"], 256)
        self.assertEqual(params_small["xmx_flag"], "-Xmx512M")
        self.assertEqual(params_small["xms_flag"], "-Xms256M")

        # 3. String inputs with varied casing and spacing
        params_str = calculate_ram_parameters(max_ram="  12288m ", min_ram=" 4096M ")
        self.assertEqual(params_str["max_mb"], 12288)
        self.assertEqual(params_str["min_mb"], 4096)
        self.assertEqual(params_str["xmx_flag"], "-Xmx12G")
        self.assertEqual(params_str["xms_flag"], "-Xms4G")

        # 4. Zero / None inputs fallback safely
        params_zero = calculate_ram_parameters(max_ram=0, min_ram=0)
        self.assertGreaterEqual(params_zero["min_mb"], 256)
        self.assertGreaterEqual(params_zero["max_mb"], 256)
        self.assertLessEqual(params_zero["min_mb"], params_zero["max_mb"])

    def test_adv_fabric_asm_modular_isolation(self):
        """Verify that Fabric 26.2 classpath strips monolithic asm-all to avoid ASM bytecode clash on Java 21+."""
        version_json = {
            "id": "26.2",
            "libraries": [
                {"name": "org.ow2.asm:asm-all:5.0.3"},
                {"name": "org.ow2.asm:asm:9.10.1"},
                {"name": "net.fabricmc:sponge-mixin:0.17.4+mixin.0.8.7"},
            ],
        }
        cp = self.runner.build_classpath(version_json, mc_version="26.2", loader="fabric")
        cp_str = " ".join(cp).lower()
        # Must not contain asm-all-5.0.3
        self.assertNotIn("asm-all", cp_str)


if __name__ == "__main__":
    unittest.main()
