import os
import sys
import json
import shutil
import tempfile
import unittest

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'development'))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.instance_service import InstanceService
from launcher_core.bridge import LauncherBridgeAPI


class TestVideoPresets(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_preset_test_")
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

    def test_preset_potato_modern(self):
        res = self.service.apply_video_preset("26.2", "potato")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("preset"), "potato")
        self.assertEqual(res.get("error"), "")
        applied = res.get("applied", [])
        self.assertIn("options.txt", applied)
        self.assertIn("sodium-options.json", applied)
        self.assertIn("iris.properties", applied)

        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
        self.assertTrue(os.path.exists(opts_path))
        with open(opts_path, "r", encoding="utf-8") as f:
            opts_content = f.read()
        self.assertIn("renderDistance:4", opts_content)
        self.assertIn("particles:2", opts_content)
        self.assertIn("smoothLighting:false", opts_content)

        sodium_path = os.path.join(self.instances_dir, "26.2", "minecraft", "config", "sodium-options.json")
        self.assertTrue(os.path.exists(sodium_path))
        with open(sodium_path, "r", encoding="utf-8") as f:
            sodium_data = json.load(f)
        self.assertEqual(sodium_data["quality"]["leaves_quality"], "FAST")

        iris_path = os.path.join(self.instances_dir, "26.2", "minecraft", "config", "iris.properties")
        self.assertTrue(os.path.exists(iris_path))
        with open(iris_path, "r", encoding="utf-8") as f:
            iris_content = f.read()
        self.assertIn("enableShaders=false", iris_content)

    def test_preset_competitive_modern(self):
        res = self.service.apply_video_preset("sir-26-ultra", "competitive")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("preset"), "competitive")

        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
        with open(opts_path, "r", encoding="utf-8") as f:
            opts_content = f.read()
        self.assertIn("renderDistance:8", opts_content)
        self.assertIn("smoothLighting:false", opts_content)

        sodium_path = os.path.join(self.instances_dir, "26.2", "minecraft", "config", "sodium-options.json")
        with open(sodium_path, "r", encoding="utf-8") as f:
            sodium_data = json.load(f)
        self.assertEqual(sodium_data["quality"]["cloud_distance"], 32)

    def test_preset_balanced_modern(self):
        res = self.service.apply_video_preset("26.2", "balanced")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("preset"), "balanced")

        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
        with open(opts_path, "r", encoding="utf-8") as f:
            opts_content = f.read()
        self.assertIn("renderDistance:12", opts_content)
        self.assertIn("smoothLighting:true", opts_content)

        iris_path = os.path.join(self.instances_dir, "26.2", "minecraft", "config", "iris.properties")
        with open(iris_path, "r", encoding="utf-8") as f:
            iris_content = f.read()
        self.assertIn("enableShaders=true", iris_content)
        self.assertIn("SIR Modern Shader.zip", iris_content)

    def test_preset_ultra_modern(self):
        res = self.service.apply_video_preset("26.2", "ultra")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("preset"), "ultra")

        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
        with open(opts_path, "r", encoding="utf-8") as f:
            opts_content = f.read()
        self.assertIn("renderDistance:16", opts_content)
        self.assertIn("simulationDistance:10", opts_content)

        iris_path = os.path.join(self.instances_dir, "26.2", "minecraft", "config", "iris.properties")
        with open(iris_path, "r", encoding="utf-8") as f:
            iris_content = f.read()
        self.assertIn("enableShaders=true", iris_content)
        self.assertIn("SIR Modern Shader.zip", iris_content)

    def test_presets_legacy_189(self):
        for preset, expected_chunks, expected_shaders in [
            ("potato", "4", "shaderPack=OFF"),
            ("competitive", "8", "shaderPack=OFF"),
            ("balanced", "12", "SIR Legacy Shader.zip"),
            ("ultra", "16", "SIR Legacy Shader.zip"),
        ]:
            res = self.service.apply_video_preset("sir-189-pvp", preset)
            self.assertTrue(res.get("success"), f"Failed for preset {preset}")
            applied = res.get("applied", [])
            self.assertIn("options.txt", applied)
            self.assertIn("optionsof.txt", applied)
            self.assertIn("optionsshaders.txt", applied)

            of_path = os.path.join(self.instances_dir, "1.8.9", "minecraft", "optionsof.txt")
            self.assertTrue(os.path.exists(of_path))
            with open(of_path, "r", encoding="utf-8") as f:
                of_content = f.read()
            self.assertIn(f"ofRenderDistanceChunks:{expected_chunks}", of_content)

            shaders_path = os.path.join(self.instances_dir, "1.8.9", "minecraft", "optionsshaders.txt")
            self.assertTrue(os.path.exists(shaders_path))
            with open(shaders_path, "r", encoding="utf-8") as f:
                shaders_content = f.read()
            self.assertIn(expected_shaders, shaders_content)

    def test_non_destructive_options_preservation(self):
        opts_path = os.path.join(self.instances_dir, "26.2", "minecraft", "options.txt")
        initial_content = (
            "key_key.jump:key.keyboard.space\n"
            "key_key.sprint:key.keyboard.left.control\n"
            "key_key.attack:key.mouse.left\n"
            "soundCategory_master:0.85\n"
            "soundCategory_music:0.0\n"
            "lang:en_us\n"
            "lastServer:play.hypixel.net\n"
            "renderDistance:2\n"
        )
        with open(opts_path, "w", encoding="utf-8") as f:
            f.write(initial_content)

        res = self.service.apply_video_preset("26.2", "ultra")
        self.assertTrue(res.get("success"))

        with open(opts_path, "r", encoding="utf-8") as f:
            updated_content = f.read()

        # Non-graphics keys MUST be preserved exactly
        self.assertIn("key_key.jump:key.keyboard.space", updated_content)
        self.assertIn("key_key.sprint:key.keyboard.left.control", updated_content)
        self.assertIn("key_key.attack:key.mouse.left", updated_content)
        self.assertIn("soundCategory_master:0.85", updated_content)
        self.assertIn("soundCategory_music:0.0", updated_content)
        self.assertIn("lang:en_us", updated_content)
        self.assertIn("lastServer:play.hypixel.net", updated_content)

        # Video keys MUST be updated
        self.assertIn("renderDistance:16", updated_content)

    def test_multi_key_instance_resolution(self):
        # 1. By canonical UI ID
        r1 = self.service.apply_video_preset("sir-26-ultra", "balanced")
        self.assertTrue(r1.get("success"))

        # 2. By short folder ID
        r2 = self.service.apply_video_preset("26.2", "balanced")
        self.assertTrue(r2.get("success"))

        # 3. By legacy ID
        r3 = self.service.apply_video_preset("1.8.9", "competitive")
        self.assertTrue(r3.get("success"))

        # 4. By custom instance
        r4 = self.service.apply_video_preset("custom-profile", "ultra")
        self.assertTrue(r4.get("success"))

    def test_bridge_apply_video_preset_delegation(self):
        bridge = LauncherBridgeAPI(self.test_dir)
        bridge.instances = self.service

        res = bridge.apply_video_preset("26.2", "balanced")
        self.assertIsInstance(res, dict)
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("preset"), "balanced")
        self.assertIsInstance(res.get("applied"), list)
        self.assertGreater(len(res.get("applied")), 0)

    def test_direct_video_preset_service(self):
        from launcher_core.video_preset_service import VideoPresetService, apply_video_preset
        vps = VideoPresetService(self.instances_dir)
        presets = vps.get_available_presets()
        self.assertGreaterEqual(len(presets), 5)
        preset_ids = [p["id"] for p in presets]
        self.assertIn("ultra", preset_ids)
        self.assertIn("balanced", preset_ids)
        self.assertIn("performance", preset_ids)
        self.assertIn("competitive", preset_ids)
        self.assertIn("potato", preset_ids)

        # Test direct top-level apply_video_preset function
        res = apply_video_preset(self.instances_dir, "26.2", "ultra")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("canonical_preset"), "ultra")
        self.assertIn("options.txt", res.get("applied", []))

    def test_shaders_service_presets_and_options(self):
        from launcher_core.shaders_service import ShadersService
        svc = ShadersService(self.test_dir)
        presets = svc.get_shader_presets()
        self.assertGreaterEqual(len(presets), 3)

        # Test applying balanced shader preset
        res_apply = svc.apply_shader_preset("balanced", instance_dir="26.2")
        self.assertTrue(res_apply.get("success"))
        self.assertEqual(res_apply.get("active_shader"), "SIR Modern Shader.zip")

        # Test fine options
        fine_opts = {
            "motion_blur": True,
            "sun_glow_scale": 2.0,
            "water_wave_intensity": "High",
            "ssr_reflections": True,
            "subsurface_scattering": True
        }
        res_save = svc.save_fine_shader_options(fine_opts, instance_dir="26.2")
        self.assertTrue(res_save.get("success"))

        loaded_opts = svc.get_fine_shader_options(instance_dir="26.2")
        self.assertTrue(loaded_opts["motion_blur"])
        self.assertEqual(loaded_opts["sun_glow_scale"], 2.0)
        self.assertEqual(loaded_opts["water_wave_intensity"], "High")


if __name__ == '__main__':
    unittest.main()
