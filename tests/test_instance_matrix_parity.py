"""
Comprehensive Test Suite for Milestone 5: Instance Profile Matrix Parity & Automated E2E Verification (Feature 21 & Feature 22).
Validates full matrix discovery, configuration parsing, preset injection, dual keybinding conversion,
dynamic classpath assembly, and lifecycle integrity across all 8 profile permutations:
- Modern Fabric: 26.2 (Vanilla+), 26.2-ultra, 26.2-balanced, 26.2-performance
- Legacy Forge: 1.8.9 (PvP Battle Suite), 1.8.9-ultra, 1.8.9-balanced, 1.8.9-performance
"""
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
from launcher_core.controls_service import ControlsService, KeybindingMode
from launcher_core.native_runner import NativeMinecraftRunner, calculate_ram_parameters


class TestInstanceMatrixParity(unittest.TestCase):
    """Deep verification of all 8 instance profiles and cross-subsystem contracts."""

    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.instances_dir = os.path.join(cls.root_dir, "instances")
        cls.video_svc = VideoPresetService(cls.instances_dir)
        cls.controls_svc = ControlsService(cls.root_dir)
        cls.runner = NativeMinecraftRunner(cls.root_dir)

        cls.expected_profiles = [
            "26.2-ultra", "26.2-balanced", "26.2-performance",
            "1.8.9-ultra", "1.8.9-balanced", "1.8.9-performance"
        ]
        cls.modern_profiles = ["26.2-ultra", "26.2-balanced", "26.2-performance"]
        cls.legacy_profiles = ["1.8.9-ultra", "1.8.9-balanced", "1.8.9-performance"]

    def setUp(self):
        self.instance_svc = InstanceService(self.root_dir)
        self.temp_dir = tempfile.mkdtemp(prefix="sir_matrix_test_")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Profile Matrix Discovery & Availability
    # -------------------------------------------------------------------------

    def test_all_eight_instance_profiles_exist_on_disk(self):
        """Verify all 8 physical instance directories exist under instances/."""
        for inst in self.expected_profiles:
            inst_path = os.path.join(self.instances_dir, inst)
            self.assertTrue(os.path.isdir(inst_path), f"Instance profile directory missing: {inst}")
            cfg_path = os.path.join(inst_path, "instance.cfg")
            self.assertTrue(os.path.isfile(cfg_path), f"instance.cfg missing in profile: {inst}")
            pack_path = os.path.join(inst_path, "mmc-pack.json")
            self.assertTrue(os.path.isfile(pack_path), f"mmc-pack.json missing in profile: {inst}")

    def test_instance_service_discovers_all_eight_as_available(self):
        """Verify InstanceService.get_instances reports available: True for all official profiles."""
        res = self.instance_svc.get_instances()
        self.assertIn("instances", res)
        discovered = res["instances"]
        
        found_ids = {inst["id"] for inst in discovered}
        expected_ids = {
            "26.2-ultra", "26.2-balanced", "26.2-performance",
            "1.8.9-ultra", "1.8.9-balanced", "1.8.9-performance"
        }
        self.assertTrue(expected_ids.issubset(found_ids), f"Missing instance IDs: {expected_ids - found_ids}")

        for inst in discovered:
            if inst["id"] in expected_ids:
                self.assertTrue(inst.get("available"), f"Instance {inst['id']} marked unavailable: {inst.get('instancePath')}")
                self.assertTrue(os.path.isdir(inst.get("instancePath")), f"Invalid instancePath for {inst['id']}")

    def test_instgroups_json_structure_and_categorization(self):
        """Verify instances/instgroups.json properly partitions Modern and Legacy profiles."""
        instgroups_path = os.path.join(self.instances_dir, "instgroups.json")
        self.assertTrue(os.path.isfile(instgroups_path), "instgroups.json must exist")
        with open(instgroups_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        groups = data.get("groups", {})
        self.assertIn("Modern", groups)
        self.assertIn("Legacy", groups)

        modern_insts = groups["Modern"].get("instances", [])
        legacy_insts = groups["Legacy"].get("instances", [])

        for p in self.modern_profiles:
            self.assertIn(p, modern_insts, f"Modern profile {p} not registered in Modern group")
        for p in self.legacy_profiles:
            self.assertIn(p, legacy_insts, f"Legacy profile {p} not registered in Legacy group")

    # -------------------------------------------------------------------------
    # 2. Configuration & Loader Metadata Parity
    # -------------------------------------------------------------------------

    def test_modern_mmc_pack_components(self):
        """Verify Fabric loader, Intermediary, and LWJGL 3 components in Modern profiles."""
        for inst in self.modern_profiles:
            pack_path = os.path.join(self.instances_dir, inst, "mmc-pack.json")
            with open(pack_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            comps = {c.get("uid"): c for c in data.get("components", [])}

            self.assertIn("net.minecraft", comps, f"Missing net.minecraft in {inst}")
            self.assertIn("net.fabricmc.fabric-loader", comps, f"Missing Fabric in {inst}")
            self.assertIn("net.fabricmc.intermediary", comps, f"Missing intermediary in {inst}")
            self.assertIn("org.lwjgl3", comps, f"Missing LWJGL 3 in {inst}")

    def test_legacy_mmc_pack_components(self):
        """Verify Forge and Minecraft 1.8.9 components in Legacy profiles."""
        for inst in self.legacy_profiles:
            pack_path = os.path.join(self.instances_dir, inst, "mmc-pack.json")
            with open(pack_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            comps = {c.get("uid"): c for c in data.get("components", [])}

            self.assertIn("net.minecraft", comps, f"Missing net.minecraft in {inst}")
            self.assertEqual(comps["net.minecraft"].get("version"), "1.8.9")
            self.assertIn("net.minecraftforge", comps, f"Missing Forge in {inst}")
            self.assertEqual(comps["net.minecraftforge"].get("version"), "11.15.1.2318")

    def test_instance_cfg_memory_and_group_definitions(self):
        """Verify instance.cfg specifies memory bounds, group tags, and G1GC parameters."""
        for inst in self.expected_profiles:
            cfg_path = os.path.join(self.instances_dir, inst, "instance.cfg")
            with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            self.assertIn("[General]", content, f"Missing [General] header in {inst}")
            self.assertIn("ConfigVersion=1.3", content, f"Invalid ConfigVersion in {inst}")
            self.assertIn("InstanceType=OneSix", content, f"Invalid InstanceType in {inst}")
            self.assertIn("MinMemAlloc=", content, f"Missing MinMemAlloc in {inst}")
            self.assertIn("MaxMemAlloc=", content, f"Missing MaxMemAlloc in {inst}")

            if inst == "26.2":
                self.assertTrue("group=Modern" in content or "group=Vanilla" in content, f"Incorrect group in {inst}")
            else:
                is_modern = inst in self.modern_profiles
                expected_group = "group=Modern" if is_modern else "group=Legacy"
                self.assertIn(expected_group, content, f"Incorrect group in {inst}")

    # -------------------------------------------------------------------------
    # 3. Tri-Layer Video Preset Engine Injection Across Matrix
    # -------------------------------------------------------------------------

    def test_video_preset_injection_modern_matrix(self):
        """Verify VideoPresetService applies tri-layer configurations across Modern profiles."""
        test_inst_dir = os.path.join(self.temp_dir, "test-modern")
        os.makedirs(os.path.join(test_inst_dir, "minecraft"), exist_ok=True)
        svc = VideoPresetService(self.temp_dir)

        # 1. Apply Ultra Preset
        res = svc.apply_video_preset(
            inst_id="test-modern",
            preset_name="ultra",
            instance_info={"version": "1.21.4 (Modern 26.2)", "category": "Modern"}
        )
        self.assertTrue(res.get("success"), f"Failed ultra preset injection: {res}")
        self.assertIn("sodium-options.json", res.get("applied", []))
        self.assertIn("iris.properties", res.get("applied", []))

        # Check options.txt
        opt_path = os.path.join(test_inst_dir, "minecraft", "options.txt")
        self.assertTrue(os.path.isfile(opt_path))
        with open(opt_path, "r", encoding="utf-8") as f:
            opts = dict(line.strip().split(":", 1) for line in f if ":" in line)
        self.assertEqual(opts.get("renderDistance"), "16")
        self.assertEqual(opts.get("smoothLighting"), "true")

        # Check sodium-options.json
        sod_path = os.path.join(test_inst_dir, "minecraft", "config", "sodium-options.json")
        self.assertTrue(os.path.isfile(sod_path))
        with open(sod_path, "r", encoding="utf-8") as f:
            sod_cfg = json.load(f)
        self.assertEqual(sod_cfg.get("quality", {}).get("leaves_quality"), "CUTOUT")
        self.assertEqual(sod_cfg.get("performance", {}).get("chunk_builder"), "SEMI_BLOCKING")

        # Check iris.properties
        iris_path = os.path.join(test_inst_dir, "minecraft", "config", "iris.properties")
        self.assertTrue(os.path.isfile(iris_path))
        with open(iris_path, "r", encoding="utf-8") as f:
            iris_content = f.read()
        self.assertIn("enableShaders=true", iris_content)
        self.assertIn("shaderPack=SIR Modern Shader.zip", iris_content)

        # 2. Apply Potato / Low-End Preset
        res_potato = svc.apply_video_preset(
            inst_id="test-modern",
            preset_name="potato",
            instance_info={"version": "1.21.4 (Modern 26.2)", "category": "Modern"}
        )
        self.assertTrue(res_potato.get("success"))
        with open(opt_path, "r", encoding="utf-8") as f:
            opts = dict(line.strip().split(":", 1) for line in f if ":" in line)
        self.assertEqual(opts.get("renderDistance"), "4")
        self.assertEqual(opts.get("smoothLighting"), "false")

        with open(iris_path, "r", encoding="utf-8") as f:
            iris_content = f.read()
        self.assertIn("enableShaders=false", iris_content)
        self.assertIn("shaderPack=OFF", iris_content)

    def test_video_preset_injection_legacy_matrix(self):
        """Verify VideoPresetService applies dual-layer configurations across Legacy profiles."""
        test_inst_dir = os.path.join(self.temp_dir, "test-legacy")
        os.makedirs(os.path.join(test_inst_dir, "minecraft"), exist_ok=True)
        svc = VideoPresetService(self.temp_dir)

        # Apply Balanced Preset
        res = svc.apply_video_preset(
            inst_id="test-legacy",
            preset_name="balanced",
            instance_info={"version": "1.8.9 (Legacy Forge)", "category": "Legacy"}
        )
        self.assertTrue(res.get("success"), f"Failed legacy preset injection: {res}")
        self.assertIn("optionsof.txt", res.get("applied", []))
        self.assertIn("optionsshaders.txt", res.get("applied", []))

        # Check options.txt
        opt_path = os.path.join(test_inst_dir, "minecraft", "options.txt")
        with open(opt_path, "r", encoding="utf-8") as f:
            opts = dict(line.strip().split(":", 1) for line in f if ":" in line)
        self.assertEqual(opts.get("renderDistance"), "12")
        self.assertEqual(opts.get("anisotropicFiltering"), "4")

        # Check optionsof.txt
        of_path = os.path.join(test_inst_dir, "minecraft", "optionsof.txt")
        with open(of_path, "r", encoding="utf-8") as f:
            of_opts = dict(line.strip().split(":", 1) for line in f if ":" in line)
        self.assertEqual(of_opts.get("ofRenderDistanceChunks"), "12")
        self.assertEqual(of_opts.get("ofFastMath"), "true")

        # Check optionsshaders.txt
        shaders_path = os.path.join(test_inst_dir, "minecraft", "optionsshaders.txt")
        with open(shaders_path, "r", encoding="utf-8") as f:
            shader_line = f.read().strip()
        self.assertEqual(shader_line, "shaderPack=SIR Legacy Shader.zip")

    def test_video_preset_aliases(self):
        """Verify preset name aliases ('fps', 'low', 'cinematic', 'boost', 'pvp') normalize properly."""
        svc = self.video_svc
        self.assertEqual(svc.normalize_preset_name("fps"), "performance")
        self.assertEqual(svc.normalize_preset_name("low"), "potato")
        self.assertEqual(svc.normalize_preset_name("cinematic"), "ultra")
        self.assertEqual(svc.normalize_preset_name("raytrace"), "ultra")
        self.assertEqual(svc.normalize_preset_name("boost"), "performance")
        self.assertEqual(svc.normalize_preset_name("pvp"), "competitive")

    # -------------------------------------------------------------------------
    # 4. Controls & Dual-Mode Keybinding Conversion
    # -------------------------------------------------------------------------

    def test_controls_service_mode_detection(self):
        """Verify detect_instance_mode accurately differentiates Modern vs Legacy profiles."""
        svc = self.controls_svc
        self.assertEqual(svc.detect_instance_mode("", "26.2"), KeybindingMode.MODERN_GLFW)
        self.assertEqual(svc.detect_instance_mode("", "26.2-ultra"), KeybindingMode.MODERN_GLFW)
        self.assertEqual(svc.detect_instance_mode("", "1.8.9"), KeybindingMode.LEGACY_LWJGL2)
        self.assertEqual(svc.detect_instance_mode("", "1.8.9-performance"), KeybindingMode.LEGACY_LWJGL2)

    def test_controls_service_key_translation_mappings(self):
        """Verify bidirectional translation between GLFW token strings and LWJGL 2 numeric scancodes."""
        svc = self.controls_svc

        # Modern to Legacy
        self.assertEqual(svc.translate_key_value("key.keyboard.w", KeybindingMode.LEGACY_LWJGL2), "17")
        self.assertEqual(svc.translate_key_value("key.keyboard.f", KeybindingMode.LEGACY_LWJGL2), "33")
        self.assertEqual(svc.translate_key_value("key.keyboard.space", KeybindingMode.LEGACY_LWJGL2), "57")
        self.assertEqual(svc.translate_key_value("key.keyboard.left.shift", KeybindingMode.LEGACY_LWJGL2), "42")
        self.assertEqual(svc.translate_key_value("key.mouse.left", KeybindingMode.LEGACY_LWJGL2), "-100")
        self.assertEqual(svc.translate_key_value("key.mouse.right", KeybindingMode.LEGACY_LWJGL2), "-99")

        # Legacy to Modern
        self.assertEqual(svc.translate_key_value(17, KeybindingMode.MODERN_GLFW), "key.keyboard.w")
        self.assertEqual(svc.translate_key_value("33", KeybindingMode.MODERN_GLFW), "key.keyboard.f")
        self.assertEqual(svc.translate_key_value(57, KeybindingMode.MODERN_GLFW), "key.keyboard.space")
        self.assertEqual(svc.translate_key_value(-100, KeybindingMode.MODERN_GLFW), "key.mouse.left")

    def test_controls_service_profile_application(self):
        """Verify apply_control_profile applies keybinding profiles cleanly to instance directories."""
        res_modern = self.controls_svc.apply_control_profile("hypixel_pro_pvp", instance_id="26.2")
        self.assertTrue(res_modern.get("success"), f"Failed modern profile application: {res_modern}")

        res_legacy = self.controls_svc.apply_control_profile("hypixel_pro_pvp", instance_id="1.8.9")
        self.assertTrue(res_legacy.get("success"), f"Failed legacy profile application: {res_legacy}")

    # -------------------------------------------------------------------------
    # 5. Dynamic Classpath & Native Runner Profile Inspection
    # -------------------------------------------------------------------------

    def test_runner_inspect_instance_config_across_all_eight_profiles(self):
        """Verify NativeMinecraftRunner.inspect_instance_config parses loader and memory from each profile."""
        for inst in self.expected_profiles:
            inst_path = os.path.join(self.instances_dir, inst)
            info = self.runner.inspect_instance_config(inst_path)

            self.assertIsNotNone(info.get("min_ram_mb"), f"min_ram_mb parsed as None for {inst}")
            self.assertIsNotNone(info.get("max_ram_mb"), f"max_ram_mb parsed as None for {inst}")
            self.assertGreater(info["max_ram_mb"], info["min_ram_mb"] if info["min_ram_mb"] else 0)

            if inst in self.modern_profiles:
                self.assertEqual(info.get("loader"), "fabric", f"Expected fabric loader in {inst}")
                self.assertEqual(info.get("mc_version"), "26.2", f"Expected 26.2 in {inst}")
            else:
                self.assertEqual(info.get("loader"), "forge", f"Expected forge loader in {inst}")
                self.assertEqual(info.get("mc_version"), "1.8.9", f"Expected 1.8.9 in {inst}")

    def test_strict_ram_parameter_calculations(self):
        """Verify calculate_ram_parameters strictly enforces -Xms and -Xmx with dynamic G1GC sizing."""
        # 6GB allocation for Modern Ultra
        ram6 = calculate_ram_parameters(max_ram=6, min_ram=3, mc_version="26.2")
        self.assertEqual(ram6["xmx_flag"], "-Xmx6G")
        self.assertEqual(ram6["xms_flag"], "-Xms3G")
        self.assertEqual(ram6["pause_millis"], 50)
        self.assertEqual(ram6["region_size"], "8M")

        # 4GB allocation for Legacy 1.8.9
        ram4_legacy = calculate_ram_parameters(max_ram=4, min_ram=2, mc_version="1.8.9")
        self.assertEqual(ram4_legacy["xmx_flag"], "-Xmx4G")
        self.assertEqual(ram4_legacy["xms_flag"], "-Xms2G")
        self.assertEqual(ram4_legacy["pause_millis"], 200)

        # Boundary test: string inputs with custom Megabytes
        ram_custom = calculate_ram_parameters(max_ram="7680M", min_ram="3840M", mc_version="26.2")
        self.assertEqual(ram_custom["xmx_flag"], "-Xmx7680M")
        self.assertEqual(ram_custom["xms_flag"], "-Xms3840M")

    # -------------------------------------------------------------------------
    # 6. Instance Lifecycle & Safety Rules
    # -------------------------------------------------------------------------

    def test_default_instance_deletion_protection(self):
        """Verify deleting default instance does not purge physical directory from disk."""
        res_del = self.instance_svc.delete_instance("sir-26-ultra")
        self.assertTrue(res_del.get("success"))
        # Verify physical directory was NOT removed from disk
        self.assertTrue(os.path.isdir(os.path.join(self.instances_dir, "26.2-ultra")))

        res_del_189 = self.instance_svc.delete_instance("sir-189-pvp")
        self.assertTrue(res_del_189.get("success"))
        self.assertTrue(os.path.isdir(os.path.join(self.instances_dir, "1.8.9-balanced")))

    def test_custom_instance_creation_and_cloning_lifecycle(self):
        """Verify creating, cloning, and deleting custom instances maintains data integrity."""
        # 1. Create custom instance
        create_res = self.instance_svc.create_custom_instance(
            name="Test Matrix Custom",
            version="1.21.4",
            loader="fabric",
            ram_gb=4
        )
        self.assertTrue(create_res.get("success"), f"Failed custom instance creation: {create_res}")
        inst_id = create_res["instance"]["id"]
        inst_dir = os.path.join(self.instances_dir, create_res["instance"]["dir_name"])
        self.assertTrue(os.path.isdir(inst_dir))

        # Check instance.cfg was created
        self.assertTrue(os.path.isfile(os.path.join(inst_dir, "instance.cfg")))
        self.assertTrue(os.path.isfile(os.path.join(inst_dir, "mmc-pack.json")))

        # 2. Clone custom instance
        clone_res = self.instance_svc.clone_instance(
            inst_id,
            new_name="Test Matrix Cloned"
        )
        self.assertTrue(clone_res.get("success"), f"Failed instance cloning: {clone_res}")
        cloned_id = clone_res["instance"]["id"]
        cloned_dir = os.path.join(self.instances_dir, clone_res["instance"]["dir_name"])
        self.assertTrue(os.path.isdir(cloned_dir))

        # 3. Clean up custom instances
        self.instance_svc.delete_instance(inst_id)
        self.instance_svc.delete_instance(cloned_id)
        self.assertFalse(os.path.exists(inst_dir))
        self.assertFalse(os.path.exists(cloned_dir))


if __name__ == "__main__":
    unittest.main()
