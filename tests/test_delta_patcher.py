"""
test_delta_patcher.py — Comprehensive Unit & Integration Tests for DeltaPatcher.
Verifies manifest generation, delta planning (add/update/delete/unchanged),
bandwidth calculations, atomic local delta application, and hash verification.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_DIR = os.path.join(ROOT_DIR, "development")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from shared_core.delta_patcher import DeltaPatcher


class TestDeltaPatcher(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sir_test_delta_")
        self.src_dir = os.path.join(self.temp_dir, "source")
        self.dst_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(os.path.join(self.src_dir, "mods"), exist_ok=True)
        os.makedirs(os.path.join(self.src_dir, "config"), exist_ok=True)
        os.makedirs(os.path.join(self.dst_dir, "mods"), exist_ok=True)

        # Populate source files
        with open(os.path.join(self.src_dir, "mods", "modA.jar"), "w") as f:
            f.write("modA-content-v1")
        with open(os.path.join(self.src_dir, "mods", "modB.jar"), "w") as f:
            f.write("modB-content-v1")
        with open(os.path.join(self.src_dir, "config", "settings.json"), "w") as f:
            f.write('{"theme": "dark"}')

        # Populate target (target has identical modA, outdated modB, and an obsolete modC)
        with open(os.path.join(self.dst_dir, "mods", "modA.jar"), "w") as f:
            f.write("modA-content-v1")
        with open(os.path.join(self.dst_dir, "mods", "modB.jar"), "w") as f:
            f.write("modB-content-OUTDATED")
        with open(os.path.join(self.dst_dir, "mods", "obsolete_modC.jar"), "w") as f:
            f.write("obsolete-mod")

        self.patcher = DeltaPatcher(self.src_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_manifest(self):
        manifest = self.patcher.generate_manifest(
            base_dir=self.src_dir,
            include_rel_dirs=["mods", "config"]
        )
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual(manifest["total_files"], 3)
        self.assertIn("mods/modA.jar", manifest["files"])
        self.assertIn("mods/modB.jar", manifest["files"])
        self.assertIn("config/settings.json", manifest["files"])
        self.assertEqual(manifest["files"]["mods/modA.jar"]["category"], "mod")
        self.assertEqual(manifest["files"]["config/settings.json"]["category"], "config")

    def test_plan_delta_detection(self):
        manifest = self.patcher.generate_manifest(
            base_dir=self.src_dir,
            include_rel_dirs=["mods", "config"]
        )
        plan = self.patcher.plan_delta(self.dst_dir, manifest)

        # modA is identical -> unchanged
        self.assertEqual(plan["unchanged_count"], 1)
        # config/settings.json is missing in dst -> to_add
        self.assertEqual(len(plan["to_add"]), 1)
        self.assertEqual(plan["to_add"][0]["path"], "config/settings.json")
        # modB has different content -> to_update
        self.assertEqual(len(plan["to_update"]), 1)
        self.assertEqual(plan["to_update"][0]["path"], "mods/modB.jar")
        # obsolete_modC is not in manifest -> to_delete
        self.assertEqual(len(plan["to_delete"]), 1)
        self.assertTrue(plan["to_delete"][0].endswith("obsolete_modC.jar"))

        # Bandwidth saved should be > 0 (since modA was not transferred)
        self.assertGreater(plan["bandwidth_saved_bytes"], 0)
        self.assertGreater(plan["bandwidth_saved_pct"], 0.0)

    def test_apply_delta_local(self):
        manifest = self.patcher.generate_manifest(
            base_dir=self.src_dir,
            include_rel_dirs=["mods", "config"]
        )
        plan = self.patcher.plan_delta(self.dst_dir, manifest)
        result = self.patcher.apply_delta_local(self.src_dir, self.dst_dir, plan)

        self.assertTrue(result["success"])
        self.assertEqual(result["applied_count"], 2)  # config/settings.json + modB.jar
        self.assertEqual(result["failed_count"], 0)

        # Verify target is now fully synchronized
        with open(os.path.join(self.dst_dir, "mods", "modB.jar"), "r") as f:
            self.assertEqual(f.read(), "modB-content-v1")
        self.assertTrue(os.path.isfile(os.path.join(self.dst_dir, "config", "settings.json")))
        self.assertFalse(os.path.exists(os.path.join(self.dst_dir, "mods", "obsolete_modC.jar")))

        # Re-planning should yield 100% sync
        plan_after = self.patcher.plan_delta(self.dst_dir, manifest)
        self.assertTrue(plan_after["is_fully_synchronized"])
        self.assertEqual(plan_after["files_to_transfer_count"], 0)


if __name__ == "__main__":
    unittest.main()
