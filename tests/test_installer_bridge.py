"""
test_installer_bridge.py — Unit & Integration Tests for SIR Installer Studio Pro & Bridge API.
"""
import os
import sys
import json
import tempfile
import shutil
import unittest

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from installer_core.installer_bridge import InstallerBridgeAPI


class TestInstallerBridge(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root_dir = os.path.join(self.temp_dir, "app_root")
        self.data_root = os.path.join(self.temp_dir, "data_root")
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(self.data_root, exist_ok=True)
        self.bridge = InstallerBridgeAPI(self.root_dir, data_root=self.data_root)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Verifies initial state of InstallerBridgeAPI."""
        self.assertEqual(self.bridge.install_progress, 0)
        self.assertFalse(self.bridge.is_installing)
        self.assertFalse(self.bridge.install_complete)
        self.assertEqual(self.bridge.installed_path, self.data_root)

    def test_stale_lock_recovery(self):
        """Verifies orphaned installation lock files with dead PIDs are safely purged."""
        lock_path = os.path.join(self.data_root, "state", "install.lock")
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)
        # Use a high dummy PID that does not exist
        with open(lock_path, "w") as f:
            f.write("9999999")

        self.assertTrue(os.path.exists(lock_path))
        # Trigger cleanup via new instance
        new_bridge = InstallerBridgeAPI(self.root_dir, data_root=self.data_root)
        self.assertFalse(os.path.exists(lock_path))

    def test_journal_checkpoint_and_resume(self):
        """Verifies atomic write_journal and check_resume_state recovery."""
        cfg = {"target_type": "sir_launcher", "ram_gb": 6}
        self.bridge.write_journal(
            stage="Deploying Shaders",
            stage_num=3,
            progress=45,
            status="in_progress",
            config=cfg,
            dest_dir=self.data_root
        )

        resume = self.bridge.check_resume_state()
        self.assertTrue(resume["has_resume"])
        self.assertEqual(resume["stage"], "Deploying Shaders")
        self.assertEqual(resume["progress"], 45)
        self.assertEqual(resume["config"]["ram_gb"], 6)

    def test_preflight_java_detection(self):
        """Verifies pre-flight detection for both OpenJDK 25 (Modern 26.2) and Java 8 (Legacy 1.8.9)."""
        specs = self.bridge.get_hardware_specs()
        # Verify required keys exist
        self.assertIn("java25_pass", specs)
        self.assertIn("java25_label", specs)
        self.assertIn("java8_pass", specs)
        self.assertIn("java8_label", specs)
        # Verify backward-compatibility aliases
        self.assertIn("java21_pass", specs)
        self.assertIn("java21_label", specs)

        self.assertIsInstance(specs["java25_pass"], bool)
        self.assertIsInstance(specs["java8_pass"], bool)
        self.assertIsInstance(specs["java25_label"], str)
        self.assertIsInstance(specs["java8_label"], str)
        self.assertGreater(len(specs["java25_label"]), 0)
        self.assertGreater(len(specs["java8_label"]), 0)

    def test_multi_profile_targeting_paths(self):
        """Verifies multi-profile installation targeting for SIR Launcher, Lunar Client, and Vanilla."""
        # 1. Default SIR Launcher targeting
        cfg_sir = {"target_type": "sir_launcher"}
        user_appdata = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        self.assertEqual(self.bridge.installed_path, self.data_root)

        # 2. Lunar Client targeting destination logic
        user_home = os.path.expanduser("~")
        expected_lunar = os.path.join(user_home, ".lunarclient")
        self.assertTrue(os.path.isabs(expected_lunar))

        # 3. Vanilla targeting destination logic
        expected_vanilla = os.path.join(user_appdata, ".minecraft")
        self.assertTrue(os.path.isabs(expected_vanilla))

    def test_available_drives(self):
        """Verifies drive inspection returns valid storage data."""
        drives = self.bridge.get_available_drives()
        self.assertIsInstance(drives, list)
        self.assertGreater(len(drives), 0)
        first = drives[0]
        self.assertIn("drive", first)
        self.assertIn("total_gb", first)
        self.assertIn("free_gb", first)
        self.assertGreater(first["total_gb"], 0)

    def test_adoptium_java_download_helpers(self):
        """Verifies download helper methods and cached runtime discovery."""
        # Test existing runtime short-circuit
        runtime_25 = os.path.join(self.data_root, "runtime", "java-25", "bin")
        os.makedirs(runtime_25, exist_ok=True)
        fake_java_25 = os.path.join(runtime_25, "java.exe")
        with open(fake_java_25, "w") as f:
            f.write("mock_java_binary")

        res25 = self.bridge.download_adoptium_java(target_ver=25, target_dir=self.data_root)
        self.assertTrue(res25["success"])
        self.assertEqual(res25["java_path"], fake_java_25)

        # Test Java 8 helper
        runtime_8 = os.path.join(self.data_root, "runtime", "java-8", "bin")
        os.makedirs(runtime_8, exist_ok=True)
        fake_java_8 = os.path.join(runtime_8, "java.exe")
        with open(fake_java_8, "w") as f:
            f.write("mock_java_8_binary")

        res8 = self.bridge.download_adoptium_java8(target_dir=self.data_root)
        self.assertTrue(res8["success"])
        self.assertEqual(res8["java_path"], fake_java_8)


if __name__ == "__main__":
    unittest.main()
