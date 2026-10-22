import os
import sys
import unittest
import tempfile
import shutil

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.instance_service import InstanceService
from launcher_core.bridge import LauncherBridgeAPI
from launcher_core.shaders_service import ShadersService

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
instances_dir = os.path.join(root_dir, "instances")

class VideoPresetEdgeCaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Create a mock modern instance and legacy instance
        self.mock_modern = os.path.join(self.temp_dir, "26.2")
        os.makedirs(os.path.join(self.mock_modern, "minecraft", "config"), exist_ok=True)
        with open(os.path.join(self.mock_modern, "options.txt"), "w") as f:
            f.write("key_key.sprint:key.keyboard.f\nsoundCategory_master:0.75\n")
        
        self.mock_legacy = os.path.join(self.temp_dir, "1.8.9")
        os.makedirs(os.path.join(self.mock_legacy, "minecraft"), exist_ok=True)
        with open(os.path.join(self.mock_legacy, "minecraft", "options.txt"), "w") as f:
            f.write("key_key.sprint:33\nsoundCategory_master:0.5\n")
        
        self.service = InstanceService(root_dir, self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_modern_potato_preset(self):
        res = self.service.apply_video_preset("26.2", "potato")
        self.assertTrue(res["success"])
        self.assertIn("options.txt", res["applied"])
        self.assertIn("sodium-options.json", res["applied"])
        self.assertIn("iris.properties", res["applied"])
        
        # Check options.txt
        with open(os.path.join(self.mock_modern, "options.txt"), "r") as f:
            content = f.read()
        self.assertIn("renderDistance:4", content)
        self.assertIn("simulationDistance:4", content)
        self.assertIn("key_key.sprint:key.keyboard.f", content) # Preserved keybinding!
        self.assertIn("soundCategory_master:0.75", content) # Preserved sound!
        
        # Check sodium
        with open(os.path.join(self.mock_modern, "config", "sodium-options.json"), "r") as f:
            s_data = f.read()
        self.assertIn('"leaves_quality": "FAST"', s_data)
        
        # Check iris
        with open(os.path.join(self.mock_modern, "config", "iris.properties"), "r") as f:
            i_data = f.read()
        self.assertIn("shaderPack=OFF", i_data)

    def test_legacy_competitive_preset(self):
        res = self.service.apply_video_preset("1.8.9", "competitive")
        self.assertTrue(res["success"])
        self.assertIn("options.txt", res["applied"])
        self.assertIn("optionsof.txt", res["applied"])
        self.assertIn("optionsshaders.txt", res["applied"])
        
        # Check 1.8.9 options.txt
        with open(os.path.join(self.mock_legacy, "minecraft", "options.txt"), "r") as f:
            content = f.read()
        self.assertIn("renderDistance:8", content)
        self.assertIn("key_key.sprint:33", content) # Preserved scancode!
        self.assertIn("soundCategory_master:0.5", content) # Preserved sound!
        
        # Check optionsof.txt
        with open(os.path.join(self.mock_legacy, "minecraft", "optionsof.txt"), "r") as f:
            of_data = f.read()
        self.assertIn("ofFastRender:true", of_data)
        
        # Check optionsshaders.txt
        with open(os.path.join(self.mock_legacy, "minecraft", "optionsshaders.txt"), "r") as f:
            s_data = f.read()
        self.assertIn("shaderPack=OFF", s_data)

    def test_cinematic_extreme_preset(self):
        res = self.service.apply_video_preset("26.2", "extreme")
        self.assertTrue(res["success"])
        with open(os.path.join(self.mock_modern, "config", "iris.properties"), "r") as f:
            i_data = f.read()
        self.assertIn("SIR_Extreme_Shader.zip", i_data)

    def test_cinematic_keyword_preset(self):
        res = self.service.apply_video_preset("26.2", "cinematic")
        self.assertTrue(res["success"])
        with open(os.path.join(self.mock_modern, "config", "iris.properties"), "r") as f:
            i_data = f.read()
        print(f"cinematic preset iris output: {i_data.strip()}")

if __name__ == "__main__":
    unittest.main()
