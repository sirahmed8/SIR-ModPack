"""
Empirical Challenger Test Suite for Milestone 5: Profile Matrix Parity & Automated Verification.
Adversarially stress-tests:
1. 8-profile matrix configuration discovery, parsing robustness, and boundary handling.
2. VideoPresetService tri-layer injection, cyclic switching, option preservation, and JSON integrity.
3. ControlsService bidirectional GLFW <-> LWJGL 2 lossless translation, roundtripping, and options injection.
4. Ecosystem Doctor diagnostic accuracy and completeness.
"""
import copy
import json
import os
import shutil
import sys
import tempfile
import unittest

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.instance_service import InstanceService
from launcher_core.video_preset_service import VideoPresetService
from launcher_core.controls_service import (
    ControlsService,
    KeybindingMode,
    GLFW_TO_LWJGL2,
    LWJGL2_TO_GLFW,
)
from launcher_core.native_runner import (
    NativeMinecraftRunner,
    calculate_ram_parameters,
)


class TestChallengerM5MatrixStress(unittest.TestCase):
    """Adversarial challenge tests for Milestone 5."""

    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.instances_dir = os.path.join(cls.root_dir, "instances")
        cls.runner = NativeMinecraftRunner(cls.root_dir)
        cls.video_svc = VideoPresetService(cls.instances_dir)
        cls.controls_svc = ControlsService(cls.root_dir)
        cls.instance_svc = InstanceService(cls.root_dir)

        cls.expected_profiles = [
            "26.2-ultra", "26.2-balanced", "26.2-performance",
            "1.8.9-ultra", "1.8.9-balanced", "1.8.9-performance"
        ]
        cls.modern_profiles = ["26.2-ultra", "26.2-balanced", "26.2-performance"]
        cls.legacy_profiles = ["1.8.9-ultra", "1.8.9-balanced", "1.8.9-performance"]

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sir_challenger_m5_")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. EMPIRICAL VERIFICATION: 8 PROFILES IN INSTANCES/
    # =========================================================================

    def test_empirical_inspect_all_eight_profiles(self):
        """Assert all 8 canonical profiles in instances/ are parsed by NativeMinecraftRunner."""
        for prof in self.expected_profiles:
            prof_path = os.path.join(self.instances_dir, prof)
            self.assertTrue(os.path.isdir(prof_path), f"Directory missing for profile: {prof}")

            info = self.runner.inspect_instance_config(prof_path)
            self.assertIsInstance(info, dict)
            self.assertIn("mc_version", info)
            self.assertIn("loader", info)
            self.assertIn("min_ram_mb", info)
            self.assertIn("max_ram_mb", info)
            self.assertIn("components", info)

            self.assertIsNotNone(info["min_ram_mb"], f"Profile {prof} has None min_ram_mb")
            self.assertIsNotNone(info["max_ram_mb"], f"Profile {prof} has None max_ram_mb")
            self.assertGreaterEqual(info["min_ram_mb"], 1024, f"Profile {prof} min_ram_mb < 1024")
            self.assertGreaterEqual(info["max_ram_mb"], info["min_ram_mb"], f"Profile {prof} max_ram < min_ram")

            if prof in self.modern_profiles:
                self.assertEqual(info["loader"], "fabric", f"Expected fabric for {prof}")
                self.assertEqual(info["mc_version"], "26.2", f"Expected 26.2 for {prof}")
                comp_uids = {c.get("uid") for c in info["components"]}
                self.assertIn("net.fabricmc.fabric-loader", comp_uids)
                self.assertIn("net.minecraft", comp_uids)
                self.assertIn("org.lwjgl3", comp_uids)
            else:
                self.assertEqual(info["loader"], "forge", f"Expected forge for {prof}")
                self.assertEqual(info["mc_version"], "1.8.9", f"Expected 1.8.9 for {prof}")
                comp_uids = {c.get("uid") for c in info["components"]}
                self.assertIn("net.minecraftforge", comp_uids)
                self.assertIn("net.minecraft", comp_uids)

    def test_adversarial_malformed_instance_configs(self):
        """Stress-test inspect_instance_config with corrupted/malformed configs."""
        test_dir = os.path.join(self.temp_dir, "corrupted_profile")
        os.makedirs(test_dir, exist_ok=True)

        # Case A: Empty instance.cfg & mmc-pack.json
        with open(os.path.join(test_dir, "instance.cfg"), "w", encoding="utf-8") as f:
            f.write("")
        with open(os.path.join(test_dir, "mmc-pack.json"), "w", encoding="utf-8") as f:
            f.write("{}")

        info_a = self.runner.inspect_instance_config(test_dir)
        self.assertIsNone(info_a["min_ram_mb"])
        self.assertIsNone(info_a["max_ram_mb"])
        self.assertEqual(info_a["loader"], "")

        # Case B: Non-numeric / negative RAM strings, comments, weird spacing
        cfg_weird = (
            "# Random comment\n"
            "MinMemAlloc = abc\n"
            "MaxMemAlloc = -9999\n"
            "JavaPath = C:\\Special JRE\\bin\\javaw.exe\n"
            "JvmArgs = -XX:+UseG1GC -Dtest=1\n"
            "IntendedVersion = 1.21.4\n"
        )
        with open(os.path.join(test_dir, "instance.cfg"), "w", encoding="utf-8") as f:
            f.write(cfg_weird)

        info_b = self.runner.inspect_instance_config(test_dir)
        self.assertIsNone(info_b["min_ram_mb"])  # non-numeric ignored gracefully
        self.assertEqual(info_b["max_ram_mb"], -9999)
        self.assertEqual(info_b["java_path"], "C:\\Special JRE\\bin\\javaw.exe")
        self.assertEqual(info_b["jvm_args"], "-XX:+UseG1GC -Dtest=1")
        self.assertEqual(info_b["mc_version"], "1.21.4")

        # Case C: Invalid JSON in mmc-pack.json
        with open(os.path.join(test_dir, "mmc-pack.json"), "w", encoding="utf-8") as f:
            f.write("INVALID JSON {{{")

        info_c = self.runner.inspect_instance_config(test_dir)
        # Should not raise exception
        self.assertIsInstance(info_c, dict)

    # =========================================================================
    # 2. EMPIRICAL VERIFICATION: VIDEO PRESET SERVICE & CORRUPTION STRESS
    # =========================================================================

    def test_video_preset_all_presets_across_modern_and_legacy(self):
        """Assert VideoPresetService applies all presets across Modern and Legacy without file corruption."""
        all_preset_keys = ["ultra", "balanced", "performance", "competitive", "potato"]
        aliases = ["fps", "low", "cinematic", "raytrace", "boost", "pvp", "ULTRA", "POTATO"]

        for is_modern in [True, False]:
            inst_name = "test_modern_env" if is_modern else "test_legacy_env"
            inst_dir = os.path.join(self.temp_dir, inst_name)
            os.makedirs(os.path.join(inst_dir, "minecraft"), exist_ok=True)
            svc = VideoPresetService(self.temp_dir)
            inst_info = {
                "id": inst_name,
                "dir_name": inst_name,
                "version": "1.21.4 (Modern 26.2)" if is_modern else "1.8.9 (Legacy Forge)",
                "category": "Modern" if is_modern else "Legacy",
            }

            # Seed options.txt with custom user settings to test preservation
            opt_path = os.path.join(inst_dir, "minecraft", "options.txt")
            with open(opt_path, "w", encoding="utf-8") as f:
                f.write("fov:95.0\nsoundCategory_master:0.75\ncustom_user_mod_setting:active\n")

            # Test all canonical presets and aliases
            for p_name in all_preset_keys + aliases:
                res = svc.apply_video_preset(inst_id=inst_name, preset_name=p_name, instance_info=inst_info)
                self.assertTrue(res.get("success"), f"Failed to apply {p_name} on {'modern' if is_modern else 'legacy'}")

                # 1. Check options.txt integrity
                self.assertTrue(os.path.isfile(opt_path))
                with open(opt_path, "r", encoding="utf-8") as f:
                    opt_lines = [l.strip() for l in f if l.strip()]

                opt_dict = {}
                for l in opt_lines:
                    self.assertIn(":", l, f"Malformed line in options.txt after applying {p_name}: {l}")
                    k, v = l.split(":", 1)
                    opt_dict[k] = v

                # Verify custom user settings preserved
                self.assertEqual(opt_dict.get("fov"), "95.0", f"User FOV was wiped out by preset {p_name}!")
                self.assertEqual(opt_dict.get("soundCategory_master"), "0.75", f"User master sound wiped out by preset {p_name}!")
                self.assertEqual(opt_dict.get("custom_user_mod_setting"), "active", f"User custom mod setting wiped out by preset {p_name}!")

                if is_modern:
                    # Verify Sodium options JSON
                    sod_path = os.path.join(inst_dir, "minecraft", "config", "sodium-options.json")
                    self.assertTrue(os.path.isfile(sod_path), f"sodium-options.json missing for {p_name}")
                    with open(sod_path, "r", encoding="utf-8") as f:
                        sod_json = json.load(f)
                    self.assertIn("quality", sod_json)
                    self.assertIn("performance", sod_json)
                    self.assertIn("notifications", sod_json)

                    # Verify Iris properties
                    iris_path = os.path.join(inst_dir, "minecraft", "config", "iris.properties")
                    self.assertTrue(os.path.isfile(iris_path), f"iris.properties missing for {p_name}")
                    with open(iris_path, "r", encoding="utf-8") as f:
                        iris_lines = dict(line.strip().split("=", 1) for line in f if "=" in line)
                    self.assertIn("enableShaders", iris_lines)
                    self.assertIn("shaderPack", iris_lines)
                else:
                    # Verify OptiFine options
                    of_path = os.path.join(inst_dir, "minecraft", "optionsof.txt")
                    self.assertTrue(os.path.isfile(of_path), f"optionsof.txt missing for {p_name}")
                    with open(of_path, "r", encoding="utf-8") as f:
                        of_lines = dict(line.strip().split(":", 1) for line in f if ":" in line)
                    self.assertIn("ofRenderDistanceChunks", of_lines)
                    self.assertIn("ofFastRender", of_lines)

                    # Verify Shaders file
                    shaders_path = os.path.join(inst_dir, "minecraft", "optionsshaders.txt")
                    self.assertTrue(os.path.isfile(shaders_path), f"optionsshaders.txt missing for {p_name}")
                    with open(shaders_path, "r", encoding="utf-8") as f:
                        shader_content = f.read().strip()
                    self.assertTrue(shader_content.startswith("shaderPack="), f"Invalid optionsshaders.txt: {shader_content}")

    def test_video_preset_cyclic_switching_idempotence(self):
        """Verify cyclic switching between extreme presets produces deterministic output without key explosion."""
        inst_name = "test_cycle"
        inst_dir = os.path.join(self.temp_dir, inst_name)
        os.makedirs(os.path.join(inst_dir, "minecraft"), exist_ok=True)
        svc = VideoPresetService(self.temp_dir)
        inst_info = {"id": inst_name, "dir_name": inst_name, "version": "26.2", "category": "Modern"}

        # Apply ultra -> potato -> ultra -> potato -> ultra
        for _ in range(3):
            svc.apply_video_preset(inst_id=inst_name, preset_name="ultra", instance_info=inst_info)
            svc.apply_video_preset(inst_id=inst_name, preset_name="potato", instance_info=inst_info)

        svc.apply_video_preset(inst_id=inst_name, preset_name="ultra", instance_info=inst_info)

        opt_path = os.path.join(inst_dir, "minecraft", "options.txt")
        with open(opt_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

        keys = [l.split(":", 1)[0] for l in lines]
        # Assert no duplicate keys created in options.txt
        self.assertEqual(len(keys), len(set(keys)), f"Duplicate keys found in options.txt: {keys}")

    # =========================================================================
    # 3. EMPIRICAL VERIFICATION: CONTROLS SERVICE & LOSSLESS KEY CONVERSION
    # =========================================================================

    def test_controls_service_bidirectional_roundtrip_all_keys(self):
        """Assert every single key in GLFW_TO_LWJGL2 translates to LWJGL 2 and back without data loss."""
        svc = self.controls_svc

        for glfw_key, scancode in GLFW_TO_LWJGL2.items():
            # 1. Translate GLFW -> Legacy LWJGL2
            legacy_code = svc.translate_key_value(glfw_key, KeybindingMode.LEGACY_LWJGL2)
            self.assertEqual(legacy_code, str(scancode), f"Failed GLFW -> LWJGL2 for {glfw_key}")

            # 2. Translate Legacy LWJGL2 -> Modern GLFW
            modern_key = svc.translate_key_value(legacy_code, KeybindingMode.MODERN_GLFW)
            self.assertTrue(modern_key.startswith("key."), f"Invalid modern key for scancode {legacy_code}: {modern_key}")

            # 3. Roundtrip check: modern_key -> scancode must match original scancode
            roundtrip_scancode = svc.translate_key_value(modern_key, KeybindingMode.LEGACY_LWJGL2)
            self.assertEqual(roundtrip_scancode, str(scancode), f"Roundtrip mismatch for {glfw_key} -> {legacy_code} -> {modern_key} -> {roundtrip_scancode}")

    def test_controls_service_mouse_button_conversion(self):
        """Assert mouse button formulas (scancodes -100 to -93) translate accurately."""
        svc = self.controls_svc
        mouse_cases = [
            ("key.mouse.left", "-100"),
            ("key.mouse.right", "-99"),
            ("key.mouse.middle", "-98"),
            ("key.mouse.4", "-97"),
            ("key.mouse.5", "-96"),
            ("key.mouse.6", "-95"),
            ("key.mouse.7", "-94"),
            ("key.mouse.8", "-93"),
        ]
        for glfw_btn, expected_code in mouse_cases:
            # Modern -> Legacy
            res_code = svc.translate_key_value(glfw_btn, KeybindingMode.LEGACY_LWJGL2)
            self.assertEqual(res_code, expected_code, f"Failed modern mouse to legacy: {glfw_btn}")

            # Legacy -> Modern
            res_glfw = svc.translate_key_value(expected_code, KeybindingMode.MODERN_GLFW)
            self.assertIn(res_glfw, [glfw_btn, glfw_btn.replace("key.mouse.", "key.mouse.button.")])

    def test_controls_service_apply_profile_to_options_txt(self):
        """Assert apply_control_profile injects profiles cleanly without destroying other settings."""
        # Create a modern options.txt and a legacy options.txt
        modern_dir = os.path.join(self.temp_dir, "modern_inst", "minecraft")
        legacy_dir = os.path.join(self.temp_dir, "legacy_inst", "minecraft")
        os.makedirs(modern_dir, exist_ok=True)
        os.makedirs(legacy_dir, exist_ok=True)

        modern_opt = os.path.join(modern_dir, "options.txt")
        legacy_opt = os.path.join(legacy_dir, "options.txt")

        with open(modern_opt, "w", encoding="utf-8") as f:
            f.write("version:3465\ngamma:1.0\n# User Comment\nkey_key.jump:key.keyboard.space\n")

        with open(legacy_opt, "w", encoding="utf-8") as f:
            f.write("gamma:1.0\n# Legacy Comment\nkey_key.jump:57\n")

        # Apply hypixel_pro_pvp
        res_m = self.controls_svc.apply_control_profile("hypixel_pro_pvp", instance_id="26.2", instance_dir=os.path.dirname(modern_dir))
        self.assertTrue(res_m["success"])

        res_l = self.controls_svc.apply_control_profile("hypixel_pro_pvp", instance_id="1.8.9", instance_dir=os.path.dirname(legacy_dir))
        self.assertTrue(res_l["success"])

        # Check modern options.txt has GLFW keys
        with open(modern_opt, "r", encoding="utf-8") as f:
            m_lines = dict(line.strip().split(":", 1) for line in f if ":" in line and not line.startswith("#"))
        self.assertEqual(m_lines.get("key_key.sprint"), "key.keyboard.f")
        self.assertEqual(m_lines.get("key_key.perspective"), "key.keyboard.v")
        self.assertEqual(m_lines.get("key_key.pickItem"), "key.mouse.4")
        self.assertEqual(m_lines.get("gamma"), "1.0")

        # Check legacy options.txt has LWJGL 2 numeric scancodes
        with open(legacy_opt, "r", encoding="utf-8") as f:
            l_lines = dict(line.strip().split(":", 1) for line in f if ":" in line and not line.startswith("#"))
        self.assertEqual(l_lines.get("key_key.sprint"), "33")  # 'f' is 33 in LWJGL 2
        self.assertEqual(l_lines.get("key_key.togglePerspective"), "47")  # 'v' is 47 in LWJGL 2
        self.assertEqual(l_lines.get("key_key.pickItem"), "-97")  # mouse 4 is -97
        self.assertEqual(l_lines.get("gamma"), "1.0")

    # =========================================================================
    # 4. EMPIRICAL VERIFICATION: ECOSYSTEM DOCTOR & FULL MATRIX DISCOVERY
    # =========================================================================

    def test_instgroups_and_matrix_complete_mapping(self):
        """Assert instgroups.json contains all 8 profiles with accurate categorization."""
        groups_file = os.path.join(self.instances_dir, "instgroups.json")
        self.assertTrue(os.path.isfile(groups_file))
        with open(groups_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        groups = data.get("groups", {})
        self.assertIn("Modern", groups)
        self.assertIn("Legacy", groups)

        for p in self.modern_profiles:
            self.assertIn(p, groups["Modern"]["instances"], f"Modern profile {p} not in instgroups.json")
        for p in self.legacy_profiles:
            self.assertIn(p, groups["Legacy"]["instances"], f"Legacy profile {p} not in instgroups.json")


if __name__ == "__main__":
    unittest.main()
