import os
import sys
import json
import stat
import shutil
import tempfile
import threading
import unittest

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'development'))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.instance_service import InstanceService
from launcher_core.bridge import LauncherBridgeAPI


class TestVideoPresetsExhaustiveMatrix(unittest.TestCase):
    """Exhaustively tests all preset types and aliases across Modern and Legacy instance profiles."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_m3_matrix_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "26.2", "minecraft", "config"), exist_ok=True)
        os.makedirs(os.path.join(self.instances_dir, "1.8.9", "minecraft"), exist_ok=True)
        os.makedirs(os.path.join(self.instances_dir, "custom-profile", "minecraft", "config"), exist_ok=True)

        self.service = InstanceService(self.test_dir)
        self.service.instances = [
            {"id": "sir-26-ultra", "instance_id": "26.2", "name": "SIR 26 Ultra", "category": "modern", "version": "26.2"},
            {"id": "sir-26-balanced", "instance_id": "26.2", "name": "SIR 26 Balanced", "category": "modern", "version": "26.2"},
            {"id": "sir-189-pvp", "instance_id": "1.8.9", "name": "SIR 1.8.9 PvP", "category": "legacy", "version": "1.8.9"},
            {"id": "custom-1", "instance_id": "custom-profile", "name": "Custom Profile", "category": "modern", "version": "1.21.4"}
        ]

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_modern_all_presets_parameters(self):
        preset_matrix = [
            ("potato", "4", "2", "false", "FAST", "false", "OFF"),
            ("competitive", "8", "2", "false", "FAST", "false", "OFF"),
            ("balanced", "12", "0", "true", "CUTOUT", "true", "SIR Modern Shader.zip"),
            ("ultra", "16", "0", "true", "CUTOUT", "true", "SIR Modern Shader.zip"),
        ]

        for preset, expected_rd, expected_part, expected_smooth, expected_leaves, expected_shaders, expected_shaderpack in preset_matrix:
            res = self.service.apply_video_preset("sir-26-ultra", preset)
            self.assertTrue(res.get("success"), f"Failed for preset {preset}")
            self.assertEqual(res.get("preset"), preset)

            opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
            with open(opts_path, "r", encoding="utf-8") as f:
                opts = f.read()
            self.assertIn(f"renderDistance:{expected_rd}", opts)
            self.assertIn(f"particles:{expected_part}", opts)
            self.assertIn(f"smoothLighting:{expected_smooth}", opts)

            sodium_path = os.path.join(self.instances_dir, "26.2", "minecraft", "config", "sodium-options.json")
            with open(sodium_path, "r", encoding="utf-8") as f:
                sodium = json.load(f)
            self.assertEqual(sodium["quality"]["leaves_quality"], expected_leaves)

            iris_path = os.path.join(self.instances_dir, "26.2", "minecraft", "config", "iris.properties")
            with open(iris_path, "r", encoding="utf-8") as f:
                iris = f.read()
            self.assertIn(f"enableShaders={expected_shaders}", iris)
            self.assertIn(f"shaderPack={expected_shaderpack}", iris)

    def test_preset_aliases_resolution(self):
        aliases = [
            ("low", "4", "FAST"),
            ("pvp", "8", "FAST"),
            ("performance", "8", "FAST"),
            ("comp", "8", "FAST"),
            ("extreme", "16", "CUTOUT"),
            ("high", "16", "CUTOUT")
        ]
        for alias, expected_rd, expected_leaves in aliases:
            res = self.service.apply_video_preset("sir-26-ultra", alias)
            self.assertTrue(res.get("success"), f"Failed alias {alias}")
            opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
            with open(opts_path, "r", encoding="utf-8") as f:
                opts = f.read()
            self.assertIn(f"renderDistance:{expected_rd}", opts, f"Alias {alias} renderDistance mismatch")

            sodium_path = os.path.join(self.instances_dir, "26.2", "minecraft", "config", "sodium-options.json")
            with open(sodium_path, "r", encoding="utf-8") as f:
                sodium = json.load(f)
            self.assertEqual(sodium["quality"]["leaves_quality"], expected_leaves)


class TestVideoPresetsOptionsPreservationAdversarial(unittest.TestCase):
    """Adversarial stress testing for 100% preservation of custom user options."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_m3_preserv_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "26.2", "minecraft", "config"), exist_ok=True)
        os.makedirs(os.path.join(self.instances_dir, "1.8.9", "minecraft"), exist_ok=True)

        self.service = InstanceService(self.test_dir)
        self.service.instances = [
            {"id": "sir-26-ultra", "instance_id": "26.2", "name": "SIR 26 Ultra", "category": "modern", "version": "26.2"},
            {"id": "sir-189-pvp", "instance_id": "1.8.9", "name": "SIR 1.8.9 PvP", "category": "legacy", "version": "1.8.9"},
        ]

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_exhaustive_custom_options_preservation_modern(self):
        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")

        custom_options = {
            # GLFW Keybindings
            "key_key.jump": "key.keyboard.space",
            "key_key.forward": "key.keyboard.w",
            "key_key.left": "key.keyboard.a",
            "key_key.back": "key.keyboard.s",
            "key_key.right": "key.keyboard.d",
            "key_key.sneak": "key.keyboard.left.shift",
            "key_key.sprint": "key.keyboard.left.control",
            "key_key.attack": "key.mouse.left",
            "key_key.use": "key.mouse.right",
            "key_key.inventory": "key.keyboard.e",
            "key_key.drop": "key.keyboard.q",
            "key_key.hotbar.1": "key.keyboard.1",
            "key_key.hotbar.5": "key.keyboard.5",
            "key_key.hotbar.9": "key.keyboard.9",
            # Modded Keybindings
            "key_replaymod.gui": "key.keyboard.m",
            "key_zoom.zoom": "key.keyboard.c",
            "key_litematica.main_menu": "key.keyboard.m",
            # Audio levels
            "soundCategory_master": "0.42",
            "soundCategory_music": "0.0",
            "soundCategory_records": "0.65",
            "soundCategory_weather": "0.30",
            "soundCategory_blocks": "0.80",
            "soundCategory_hostile": "1.0",
            "soundCategory_neutral": "0.55",
            "soundCategory_players": "0.95",
            "soundCategory_ambient": "0.15",
            "soundCategory_voice": "0.75",
            # Localization
            "lang": "ar_sa",
            # Controls & Accessibility
            "mouseSensitivity": "0.45",
            "invertYMouse": "true",
            "fov": "95.0",
            "bobView": "false",
            "touchscreen": "false",
            "chatVisibility": "0",
            "chatColors": "true",
            "chatLinks": "true",
            "chatOpacity": "0.85",
            "textBackgroundOpacity": "0.6",
            "lastServer": "play.hypixel.net:25565",
            # Old video setting to be updated
            "renderDistance": "2",
            "particles": "1",
            "smoothLighting": "false",
        }

        with open(opts_path, "w", encoding="utf-8") as f:
            for k, v in custom_options.items():
                f.write(f"{k}:{v}\n")

        # Apply ultra preset
        res = self.service.apply_video_preset("sir-26-ultra", "ultra")
        self.assertTrue(res.get("success"))

        with open(opts_path, "r", encoding="utf-8") as f:
            updated_content = f.read()

        # Parse updated file
        updated_dict = {}
        for line in updated_content.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                updated_dict[k] = v

        # Check all non-graphics custom options are 100% intact
        for k, v in custom_options.items():
            if k not in ["renderDistance", "particles", "smoothLighting", "maxFps", "enableVsync", "biomeBlendRadius", "entityDistanceScaling", "entityShadows", "mipmapLevels", "clouds", "graphicsMode", "simulationDistance", "gamma"]:
                self.assertIn(k, updated_dict, f"Custom option key {k} was lost!")
                self.assertEqual(updated_dict[k], v, f"Custom option value for {k} was altered: expected {v}, got {updated_dict[k]}")

        # Check video settings were properly updated to Ultra
        self.assertEqual(updated_dict["renderDistance"], "16")
        self.assertEqual(updated_dict["smoothLighting"], "true")
        self.assertEqual(updated_dict["particles"], "0")

    def test_exhaustive_custom_options_preservation_legacy_189(self):
        opts_path = os.path.join(self.instances_dir, "1.8.9", "minecraft", "options.txt")

        legacy_options = {
            "key_key.jump": "57",
            "key_key.forward": "17",
            "key_key.left": "30",
            "key_key.back": "31",
            "key_key.right": "32",
            "key_key.sneak": "42",
            "key_key.sprint": "29",
            "key_key.inventory": "18",
            "soundCategory_master": "0.5",
            "soundCategory_music": "0.1",
            "lang": "es_es",
            "mouseSensitivity": "0.6",
            "invertYMouse": "false",
            "fov": "85.0",
            "lastServer": "pvp.land:25565",
            "renderDistance": "2"
        }

        with open(opts_path, "w", encoding="utf-8") as f:
            for k, v in legacy_options.items():
                f.write(f"{k}:{v}\n")

        res = self.service.apply_video_preset("sir-189-pvp", "competitive")
        self.assertTrue(res.get("success"))

        with open(opts_path, "r", encoding="utf-8") as f:
            updated_content = f.read()

        updated_dict = {}
        for line in updated_content.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                updated_dict[k] = v

        for k, v in legacy_options.items():
            if k not in ["renderDistance", "particles", "smoothLighting", "maxFps", "enableVsync", "clouds", "anisotropicFiltering", "fancyGraphics", "ao", "guiScale", "gamma", "fullscreen", "resourcePacks"]:
                self.assertIn(k, updated_dict, f"Legacy key {k} lost!")
                self.assertEqual(updated_dict[k], v, f"Legacy value for {k} changed!")

        self.assertEqual(updated_dict["renderDistance"], "8")

    def test_malformed_options_file_graceful_recovery(self):
        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")

        # Malformed lines, blank lines, duplicate colons, comments
        malformed_content = (
            "\n"
            "# Minecraft User Options\n"
            "// Another comment\n"
            "key_key.jump:key.keyboard.space\n"
            "INVALID_LINE_NO_COLON\n"
            "lastServer:play.hypixel.net:25565\n"
            "soundCategory_master:0.77\n"
            "   \n"
        )
        with open(opts_path, "w", encoding="utf-8") as f:
            f.write(malformed_content)

        res = self.service.apply_video_preset("sir-26-ultra", "balanced")
        self.assertTrue(res.get("success"))

        with open(opts_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("key_key.jump:key.keyboard.space", content)
        self.assertIn("lastServer:play.hypixel.net:25565", content)
        self.assertIn("soundCategory_master:0.77", content)
        self.assertIn("renderDistance:12", content)


class TestVideoPresetsModernTriLayer(unittest.TestCase):
    """Verifies complete modern tri-layer configuration generation."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_m3_trilayer_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "26.2", "minecraft"), exist_ok=True)
        self.service = InstanceService(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_tri_layer_files_created_from_scratch(self):
        # config directory does not exist initially
        config_dir = os.path.join(self.instances_dir, "26.2", "minecraft", "config")
        if os.path.exists(config_dir):
            shutil.rmtree(config_dir)

        res = self.service.apply_video_preset("26.2", "ultra")
        self.assertTrue(res.get("success"))
        self.assertEqual(set(res.get("applied", [])), {"options.txt", "sodium-options.json", "iris.properties"})

        # Verify Layer 1
        opts_file = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
        self.assertTrue(os.path.isfile(opts_file))

        # Verify Layer 2
        sodium_file = os.path.join(config_dir, "sodium-options.json")
        self.assertTrue(os.path.isfile(sodium_file))
        with open(sodium_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertIn("quality", data)
            self.assertIn("performance", data)
            self.assertIn("notifications", data)

        # Verify Layer 3
        iris_file = os.path.join(config_dir, "iris.properties")
        self.assertTrue(os.path.isfile(iris_file))
        with open(iris_file, "r", encoding="utf-8") as f:
            data = f.read()
            self.assertIn("enableShaders=true", data)
            self.assertIn("SIR Modern Shader.zip", data)


class TestVideoPresetsLegacyDualLayer(unittest.TestCase):
    """Verifies complete legacy 1.8.9 configuration generation."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_m3_legacy_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "1.8.9", "minecraft"), exist_ok=True)
        self.service = InstanceService(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_legacy_generation_no_modern_sodium_or_iris(self):
        res = self.service.apply_video_preset("1.8.9", "potato")
        self.assertTrue(res.get("success"))
        applied = res.get("applied", [])
        self.assertIn("options.txt", applied)
        self.assertIn("optionsof.txt", applied)
        self.assertIn("optionsshaders.txt", applied)
        self.assertNotIn("sodium-options.json", applied)
        self.assertNotIn("iris.properties", applied)

        mc_dir = os.path.join(self.instances_dir, "1.8.9", "minecraft")
        self.assertTrue(os.path.isfile(os.path.join(mc_dir, "options.txt")))
        self.assertTrue(os.path.isfile(os.path.join(mc_dir, "optionsof.txt")))
        self.assertTrue(os.path.isfile(os.path.join(mc_dir, "optionsshaders.txt")))
        self.assertFalse(os.path.isfile(os.path.join(mc_dir, "config", "sodium-options.json")))
        self.assertFalse(os.path.isfile(os.path.join(mc_dir, "config", "iris.properties")))


class TestVideoPresetsStressAndConcurrency(unittest.TestCase):
    """Stress testing rapid switching and concurrent preset injections."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_m3_stress_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "26.2", "minecraft", "config"), exist_ok=True)
        self.service = InstanceService(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_rapid_sequential_preset_switching(self):
        presets = ["potato", "ultra", "balanced", "competitive", "potato", "ultra"]
        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")

        # Initial custom keybinding
        with open(opts_path, "w", encoding="utf-8") as f:
            f.write("key_key.jump:key.keyboard.space\nsoundCategory_master:0.5\n")

        for p in presets:
            res = self.service.apply_video_preset("26.2", p)
            self.assertTrue(res.get("success"), f"Preset {p} switch failed")

            with open(opts_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("key_key.jump:key.keyboard.space", content, f"Key lost after switching to {p}")
            self.assertIn("soundCategory_master:0.5", content, f"Audio lost after switching to {p}")

    def test_multithreaded_preset_application(self):
        threads = []
        errors = []

        def worker(preset):
            try:
                r = self.service.apply_video_preset("26.2", preset)
                if not r.get("success"):
                    errors.append(f"Failed for {preset}: {r}")
            except Exception as e:
                errors.append(f"Exception for {preset}: {e}")

        for p in ["potato", "balanced", "ultra", "competitive"] * 5:
            t = threading.Thread(target=worker, args=(p,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Threaded preset injection errors: {errors}")


class TestVideoPresetsBridgeAndEdgeCases(unittest.TestCase):
    """Tests bridge delegation and edge cases."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_m3_bridge_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "26.2", "minecraft"), exist_ok=True)
        self.bridge = LauncherBridgeAPI(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_bridge_api_signature_and_response_contract(self):
        res = self.bridge.apply_video_preset("26.2", "ultra")
        self.assertIsInstance(res, dict)
        self.assertIn("success", res)
        self.assertIn("preset", res)
        self.assertIn("applied", res)
        self.assertIn("error", res)
        self.assertIn("message", res)
        self.assertTrue(res["success"])
        self.assertEqual(res["preset"], "ultra")
        self.assertEqual(res["error"], "")

    def test_nonexistent_instance_id_resolution_behavior(self):
        """Empirically test what happens when non-existent instance IDs are passed."""
        res = self.bridge.apply_video_preset("completely-nonexistent-id-9999", "ultra")
        self.assertIsInstance(res, dict)
        # Note: Under current implementation, unknown instance ID falls back to 26.2
        self.assertIn("success", res)
        self.assertIn("preset", res)

    def test_empty_and_unknown_preset_names_fallback(self):
        """Empirically test that unknown or empty preset names fall back gracefully without crash."""
        res_empty = self.bridge.apply_video_preset("26.2", "")
        self.assertTrue(res_empty.get("success"))

        res_unknown = self.bridge.apply_video_preset("26.2", "quantum_hyper_fps")
        self.assertTrue(res_unknown.get("success"))

        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
        with open(opts_path, "r", encoding="utf-8") as f:
            opts = f.read()
        # Fallback preset is balanced (renderDistance:12)
        self.assertIn("renderDistance:12", opts)


if __name__ == "__main__":
    unittest.main()

