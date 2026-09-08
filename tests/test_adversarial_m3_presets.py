import os
import sys
import json
import shutil
import tempfile
import threading
import unittest

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'development'))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.instance_service import InstanceService
from launcher_core.bridge import LauncherBridgeAPI


class TestAdversarialM3Presets(unittest.TestCase):
    """Adversarial stress-testing suite for Milestone 3 (Features 13 & 14)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_m3_adv_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "26.2", "minecraft", "config"), exist_ok=True)
        os.makedirs(os.path.join(self.instances_dir, "1.8.9", "minecraft"), exist_ok=True)
        self.service = InstanceService(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_corrupted_and_malformed_options_file(self):
        """Stress-test options.txt with malformed lines, multiline values, and invalid colons."""
        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
        malformed_content = (
            "# Minecraft Options Configuration File\n"
            "   \n"
            "key_key.jump:key.keyboard.space\n"
            "malformed_line_without_colon\n"
            "weird:key:with:many:colons:and:values\n"
            "soundCategory_ambient:0.5\n"
            "trailing_space_key: value_with_spaces   \n"
            "null_byte_simulated_key:valid_val\n"
        )
        with open(opts_path, "w", encoding="utf-8") as f:
            f.write(malformed_content)

        res = self.service.apply_video_preset("26.2", "ultra")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("preset"), "ultra")

        with open(opts_path, "r", encoding="utf-8") as f:
            updated = f.read()

        self.assertIn("key_key.jump:key.keyboard.space", updated)
        self.assertIn("soundCategory_ambient:0.5", updated)
        self.assertIn("weird:key:with:many:colons:and:values", updated)
        self.assertIn("renderDistance:16", updated)

    def test_uninitialized_instance_folder_creation(self):
        """Applying preset to a non-existent instance ID must automatically provision directories and succeed."""
        ghost_id = "ghost-instance-99"
        res = self.service.apply_video_preset(ghost_id, "potato")
        self.assertTrue(res.get("success"))
        self.assertIn("options.txt", res.get("applied", []))

    def test_preset_case_insensitivity_and_aliases(self):
        """Test aliases: potato, low, comp, competitive, pvp, performance, balanced, ultra, extreme, high."""
        aliases = [
            ("PoTaTo", "potato", "4"),
            ("LOW", "low", "4"),
            ("CoMpEtItIvE", "competitive", "8"),
            ("pvp", "pvp", "8"),
            ("performance", "performance", "8"),
            ("BALANCED", "balanced", "12"),
            ("uLtRa", "ultra", "16"),
            ("extreme", "extreme", "16"),
            ("HIGH", "high", "16"),
            ("unknown_fallback", "unknown_fallback", "12"),  # Falls back to balanced (12)
        ]
        for input_name, expected_clean, expected_rd in aliases:
            with self.subTest(input_name=input_name):
                res = self.service.apply_video_preset("26.2", input_name)
                self.assertTrue(res.get("success"))
                opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
                with open(opts_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn(f"renderDistance:{expected_rd}", content)

    def test_concurrent_preset_application_thread_safety(self):
        """Stress-test 12 concurrent threads writing presets to the same instance without file corruption."""
        errors = []
        presets = ["potato", "competitive", "balanced", "ultra"]

        def worker(thread_idx):
            try:
                preset = presets[thread_idx % len(presets)]
                res = self.service.apply_video_preset("26.2", preset)
                if not res.get("success"):
                    errors.append(f"Thread {thread_idx} failed: {res}")
            except Exception as ex:
                errors.append(f"Thread {thread_idx} raised {ex}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(12)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent preset errors: {errors}")

        # Verify json integrity of sodium-options.json
        sodium_path = os.path.join(self.instances_dir, "26.2", "minecraft", "config", "sodium-options.json")
        self.assertTrue(os.path.exists(sodium_path))
        with open(sodium_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("quality", data)
        self.assertIn("performance", data)

    def test_bridge_contract_invariants(self):
        """Bridge apply_video_preset must strictly conform to contract dictionary schema."""
        bridge = LauncherBridgeAPI(self.test_dir)
        bridge.instances = self.service

        res = bridge.apply_video_preset("1.8.9", "competitive")
        self.assertIsInstance(res, dict)
        self.assertIn("success", res)
        self.assertIn("preset", res)
        self.assertIn("applied", res)
        self.assertIn("error", res)
        self.assertIn("message", res)
        self.assertTrue(res["success"])
        self.assertIn("optionsof.txt", res["applied"])
        self.assertIn("optionsshaders.txt", res["applied"])


if __name__ == '__main__':
    unittest.main()
