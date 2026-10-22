"""
test_lunar_bridge.py — Comprehensive Unit & Integration Tests for Lunar Client Bridge Service.
Verifies Milestone 2 Objectives:
1. BetterCombat crash remediation & mod exclusion.
2. Lunar Mixin injection crash remediation (krypton exclusion).
3. Lunar profile path alignment (Drive D) & bidirectional keycode translation (LWJGL 2 <-> GLFW).
4. Singleplayer world creation, saving, and reopening lifecycle across Modern 26.2 and Legacy 1.8.9.
"""

import gzip
import json
import os
import shutil
import sys
import tempfile
import time
import unittest

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.lunar_bridge_service import (
    GLFW_TO_LWJGL2,
    LWJGL2_TO_GLFW,
    LunarBridgeService,
)


class TestLunarBridgeService(unittest.TestCase):
    """Rigorous verification suite for Lunar Client Profile Bridge and World Lifecycle."""

    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.bridge = LunarBridgeService(self.root_dir)
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_lunar_")

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    # =========================================================================
    # 1. Mod Exclusion & Crash Remediation (BetterCombat, Krypton, Quantified)
    # =========================================================================

    def test_mod_exclusion_pattern_matching(self):
        """Verifies that BetterCombat, Krypton, and Quantified API are identified for exclusion."""
        incompatible_samples = [
            "bettercombat-fabric-3.2.2+26.2.jar",
            "BetterCombat-1.21.4.jar",
            "krypton-0.3.1.jar",
            "krypton-fabric-0.2.0.jar",
            "quantified api-omni-2.2.0.jar",
            "quantified_api_omni-2.2.2.jar",
        ]
        compatible_samples = [
            "sodium-fabric-0.9.2-beta.1+mc26.2.jar",
            "lithium-fabric-0.16.0+mc26.2.jar",
            "fabric-api-0.160.0+26.2.jar",
            "iris-fabric-1.8.1+mc26.2.jar",
            "jei-1.21.4-fabric-19.21.0.246.jar",
        ]

        for mod in incompatible_samples:
            with self.subTest(mod=mod):
                self.assertTrue(
                    LunarBridgeService.is_mod_excluded_for_lunar(mod),
                    f"Expected {mod} to be excluded for Lunar Client"
                )

        for mod in compatible_samples:
            with self.subTest(mod=mod):
                self.assertFalse(
                    LunarBridgeService.is_mod_excluded_for_lunar(mod),
                    f"Expected {mod} to be permitted for Lunar Client"
                )

    def test_sanitize_lunar_profile_mods_removes_incompatible_jars(self):
        """Verifies that sanitize_lunar_profile_mods actively purges excluded JARs from disk."""
        mock_profile = os.path.join(self.temp_dir, "mock_lunar_profile")
        mock_mods = os.path.join(mock_profile, "mods")
        mock_mc_mods = os.path.join(mock_profile, "minecraft", "mods")
        os.makedirs(mock_mods, exist_ok=True)
        os.makedirs(mock_mc_mods, exist_ok=True)

        # Create dummy JARs
        bc_jar = os.path.join(mock_mods, "bettercombat-fabric-3.2.2+26.2.jar")
        kp_jar = os.path.join(mock_mc_mods, "krypton-0.3.1.jar")
        sodium_jar = os.path.join(mock_mods, "sodium-fabric-0.9.2.jar")
        with open(bc_jar, "w") as f:
            f.write("mock")
        with open(kp_jar, "w") as f:
            f.write("mock")
        with open(sodium_jar, "w") as f:
            f.write("mock")

        # Run sanitization
        removed = self.bridge.sanitize_lunar_profile_mods(mock_profile)
        self.assertEqual(len(removed), 2)
        self.assertIn(bc_jar, removed)
        self.assertIn(kp_jar, removed)
        self.assertFalse(os.path.exists(bc_jar))
        self.assertFalse(os.path.exists(kp_jar))
        self.assertTrue(os.path.exists(sodium_jar), "Compatible Sodium JAR was erroneously deleted!")

    # =========================================================================
    # 2. Bidirectional Keycode Translation (LWJGL 2 <-> GLFW)
    # =========================================================================

    def test_to_modern_key_translation(self):
        """Verifies conversion of legacy LWJGL 2 integer scancodes to modern GLFW tokens."""
        scancode_matrix = [
            ("57", "key.keyboard.space"),
            (57, "key.keyboard.space"),
            ("42", "key.keyboard.left.shift"),
            ("29", "key.keyboard.left.control"),
            ("18", "key.keyboard.e"),
            ("47", "key.keyboard.v"),
            ("54", "key.keyboard.right.shift"),
            ("-100", "key.mouse.left"),
            ("-99", "key.mouse.right"),
            ("-98", "key.mouse.middle"),
            ("-97", "key.mouse.4"),
            ("-96", "key.mouse.5"),
            ("key.keyboard.space", "key.keyboard.space"),  # Idempotent
            ("key.mouse.left", "key.mouse.left"),
        ]

        for input_val, expected_glfw in scancode_matrix:
            with self.subTest(input_val=input_val):
                res = LunarBridgeService.to_modern_key(input_val)
                self.assertEqual(res, expected_glfw, f"Failed translation for {input_val}")

    def test_to_legacy_key_translation(self):
        """Verifies conversion of modern GLFW tokens to legacy LWJGL 2 integer scancodes."""
        glfw_matrix = [
            ("key.keyboard.space", "57"),
            ("key.keyboard.left.shift", "42"),
            ("key.keyboard.left.control", "29"),
            ("key.keyboard.e", "18"),
            ("key.keyboard.v", "47"),
            ("key.keyboard.right.shift", "54"),
            ("key.mouse.left", "-100"),
            ("key.mouse.right", "-99"),
            ("key.mouse.middle", "-98"),
            ("key.mouse.4", "-97"),
            ("key.mouse.5", "-96"),
            ("57", "57"),  # Idempotent integer
            ("-100", "-100"),
        ]

        for input_val, expected_scancode in glfw_matrix:
            with self.subTest(input_val=input_val):
                res = LunarBridgeService.to_legacy_key(input_val)
                self.assertEqual(res, expected_scancode, f"Failed translation for {input_val}")

    def test_sanitize_options_keybinds_modern(self):
        """Verifies that modern options dictionary has 0 numeric scancodes and required HUD key."""
        raw_options = {
            "gamma": "1.0",
            "key_key.jump": "57",
            "key_key.sneak": "42",
            "key_key.sprint": "29",
            "key_key.inventory": "18",
            "key_key.attack": "-100",
            "key_key.use": "-99",
            "key_key.modmenu.open_menu": "54",
            "key_key.inventoryhud.openconfig": "54",
        }

        sanitized = LunarBridgeService.sanitize_options_keybinds(raw_options, is_legacy=False)

        # Confirm 0 numeric values for key_* options
        for k, v in sanitized.items():
            if k.startswith("key_"):
                self.assertFalse(
                    v.lstrip("-").isdigit(),
                    f"Option {k} retained numeric scancode {v} in modern configuration!"
                )

        self.assertEqual(sanitized["key_key.jump"], "key.keyboard.space")
        self.assertEqual(sanitized["key_key.attack"], "key.mouse.left")
        self.assertEqual(sanitized["key_key.inventoryhud.openconfig"], "key.keyboard.right.shift")
        self.assertEqual(sanitized["key_key.modmenu.open_menu"], "key.keyboard.right.shift")

    def test_sanitize_options_keybinds_legacy(self):
        """Verifies that legacy options dictionary has 0 GLFW tokens and scancode HUD key."""
        raw_options = {
            "gamma": "1.0",
            "key_key.jump": "key.keyboard.space",
            "key_key.sneak": "key.keyboard.left.shift",
            "key_key.sprint": "key.keyboard.left.control",
            "key_key.inventory": "key.keyboard.e",
            "key_key.attack": "key.mouse.left",
            "key_key.use": "key.mouse.right",
            "key_key.inventoryhud.openconfig": "key.keyboard.right.shift",
            "key_key.modmenu.open_menu": "key.keyboard.right.shift",
        }

        sanitized = LunarBridgeService.sanitize_options_keybinds(raw_options, is_legacy=True)

        for k, v in sanitized.items():
            if k.startswith("key_"):
                self.assertTrue(
                    v.lstrip("-").isdigit(),
                    f"Option {k} retained GLFW token {v} in legacy 1.8.9 configuration!"
                )

        self.assertEqual(sanitized["key_key.jump"], "57")
        self.assertEqual(sanitized["key_key.attack"], "-100")
        self.assertEqual(sanitized["key_key.inventoryhud.openconfig"], "54")
        self.assertEqual(sanitized["key_key.modmenu.open_menu"], "54")

    # =========================================================================
    # 3. Lunar Profile Path Alignment
    # =========================================================================

    def test_lunar_profiles_json_paths_aligned_to_drive_d(self):
        """Verifies that C:/Users/a7med/.lunarclient/profiles.json points to real Drive D instances."""
        profiles_json_path = os.path.join(self.bridge.lunar_root, "profiles.json")
        if not os.path.isfile(profiles_json_path):
            self.skipTest("Lunar Client profiles.json not present on test machine")

        with open(profiles_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        profiles = data.get("profiles", {})
        self.assertGreater(len(profiles), 0)

        for name, p_data in profiles.items():
            game_dir = p_data.get("gameDir", "")
            self.assertTrue(
                game_dir.startswith("D:\\Projects\\SIR ModPack\\instances") or
                game_dir.startswith("d:\\Projects\\SIR ModPack\\instances") or
                game_dir.startswith("D:/Projects/SIR ModPack/instances"),
                f"Profile '{name}' has invalid gameDir: {game_dir}"
            )
            self.assertNotIn(
                "AppData\\Roaming\\SIR ModPack\\instances",
                game_dir,
                f"Profile '{name}' still references nonexistent AppData roaming directory!"
            )

    # =========================================================================
    # 4. Synchronization Operations & Options Integrity
    # =========================================================================

    def test_sync_lunar_to_sir_preserves_modern_integrity(self):
        """Verifies that synchronizing from Lunar to SIR instance preserves GLFW key strings."""
        res = self.bridge.sync_lunar_to_sir("26.2-ultra")
        self.assertTrue(res.get("success"), f"Sync failed: {res.get('error')}")

        target_file = os.path.join(self.root_dir, "instances", "26.2-ultra", "minecraft", "options.txt")
        if not os.path.isfile(target_file):
            target_file = os.path.join(self.root_dir, "instances", "26.2-ultra", "options.txt")

        self.assertTrue(os.path.isfile(target_file))
        opts = self.bridge._parse_options_file(target_file)
        self.assertGreater(len(opts), 0)

        # Must have 0 integer scancodes for key_*
        for k, v in opts.items():
            if k.startswith("key_"):
                self.assertFalse(
                    v.lstrip("-").isdigit(),
                    f"Options file {target_file} was corrupted with integer scancode '{v}' for key '{k}'!"
                )

    def test_sync_lunar_to_sir_preserves_legacy_integrity(self):
        """Verifies that synchronizing from Lunar to SIR legacy instance preserves integer scancodes."""
        res = self.bridge.sync_lunar_to_sir("1.8.9-ultra")
        self.assertTrue(res.get("success"), f"Sync failed: {res.get('error')}")

        target_file = os.path.join(self.root_dir, "instances", "1.8.9-ultra", "minecraft", "options.txt")
        if not os.path.isfile(target_file):
            target_file = os.path.join(self.root_dir, "instances", "1.8.9-ultra", "options.txt")

        self.assertTrue(os.path.isfile(target_file))
        opts = self.bridge._parse_options_file(target_file)
        self.assertGreater(len(opts), 0)

        for k, v in opts.items():
            if k.startswith("key_"):
                self.assertTrue(
                    v.lstrip("-").isdigit(),
                    f"Options file {target_file} was corrupted with GLFW token '{v}' for key '{k}'!"
                )

    # =========================================================================
    # 5. Singleplayer World Creation, Saving & Load Verification
    # =========================================================================

    def test_verify_singleplayer_world_lifecycle_modern_profiles(self):
        """Verifies singleplayer world creation, NBT structure, and saving on all Modern 26.2 profiles."""
        modern_profiles = ["26.2-ultra", "26.2-balanced", "26.2-performance"]
        for prof in modern_profiles:
            with self.subTest(profile=prof):
                res = self.bridge.verify_singleplayer_world_lifecycle(prof, world_name="UnitTestWorld_Modern")
                self.assertTrue(res.get("success"), f"Modern world verification failed for {prof}: {res.get('error')}")
                self.assertFalse(res.get("is_legacy"))
                self.assertGreater(res.get("level_dat_size", 0), 0)

                # Clean up test world
                world_path = res.get("world_path")
                if world_path and os.path.isdir(world_path):
                    shutil.rmtree(world_path, ignore_errors=True)

    def test_verify_singleplayer_world_lifecycle_legacy_profiles(self):
        """Verifies singleplayer world creation, NBT structure, and saving on all Legacy 1.8.9 profiles."""
        legacy_profiles = ["1.8.9-ultra", "1.8.9-balanced", "1.8.9-performance"]
        for prof in legacy_profiles:
            with self.subTest(profile=prof):
                res = self.bridge.verify_singleplayer_world_lifecycle(prof, world_name="UnitTestWorld_Legacy")
                self.assertTrue(res.get("success"), f"Legacy world verification failed for {prof}: {res.get('error')}")
                self.assertTrue(res.get("is_legacy"))
                self.assertGreater(res.get("level_dat_size", 0), 0)

                # Clean up test world
                world_path = res.get("world_path")
                if world_path and os.path.isdir(world_path):
                    shutil.rmtree(world_path, ignore_errors=True)

    def test_verify_singleplayer_world_lifecycle_lunar_profile(self):
        """Verifies singleplayer world verification on Lunar Client profile with crash trigger audits."""
        lunar_prof = "sir-26-ultra"
        if not os.path.isdir(os.path.join(self.bridge.lunar_profiles_dir, lunar_prof)):
            self.skipTest(f"Lunar profile {lunar_prof} not present on test machine")

        res = self.bridge.verify_singleplayer_world_lifecycle(lunar_prof, world_name="UnitTestWorld_Lunar")
        self.assertTrue(res.get("success"), f"Lunar world verification failed: {res.get('error')}")
        self.assertTrue(res.get("is_lunar"))

        # Clean up test world
        world_path = res.get("world_path")
        if world_path and os.path.isdir(world_path):
            shutil.rmtree(world_path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
