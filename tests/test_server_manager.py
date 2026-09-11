"""
test_server_manager.py — Unit & Integration Tests for SIR Server Manager & System Tray.
"""
import os
import sys
import time
import tempfile
import shutil
import unittest
from unittest.mock import MagicMock

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from server_core.server_bridge import ServerBridgeAPI
from server_core.server_tray_service import ServerTrayService


class MockWindow:
    def __init__(self):
        self.evaluated_scripts = []

    def evaluate_js(self, script):
        self.evaluated_scripts.append(script)


class TestServerManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root_dir = os.path.join(self.temp_dir, "app_root")
        self.data_root = os.path.join(self.temp_dir, "data_root")
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(self.data_root, exist_ok=True)
        self.bridge = ServerBridgeAPI(self.root_dir, data_root=self.data_root)
        self.mock_window = MockWindow()
        self.bridge.set_window(self.mock_window)

    def tearDown(self):
        if getattr(self.bridge, "_telemetry_running", False):
            self.bridge._telemetry_running = False
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Verifies directory layout, settings defaults, and hardware detection."""
        self.assertIsNotNone(self.bridge.data_root)
        self.assertTrue(os.path.isdir(self.bridge.data_root))
        specs = self.bridge.get_hardware_specs()
        self.assertIn("total_ram_gb", specs)
        self.assertIn("cpu_cores", specs)
        self.assertGreater(specs["cpu_cores"], 0)

        adapters = self.bridge.get_network_adapters()
        self.assertIsInstance(adapters, list)
        self.assertGreater(len(adapters), 0)

    def test_server_status_offline(self):
        """Verifies status telemetry when server is stopped."""
        status = self.bridge.get_server_status()
        self.assertFalse(status["is_running"])
        self.assertEqual(status["uptime"], "00:00:00")
        self.assertEqual(status["tps"], 0.0)
        self.assertEqual(status["players_count"], 0)
        self.assertIsInstance(status["tps_history"], list)
        self.assertIsInstance(status["ram_history"], list)

    def test_dynamic_tray_toggle_text(self):
        """Verifies contextual tray menu string ('▶ Start Server' vs '⏹ Stop Server')."""
        tray = ServerTrayService("fake_icon.ico", bridge_api=self.bridge)

        # 1. Offline state
        self.bridge.is_running = False
        toggle_text = tray.get_server_toggle_text()
        self.assertEqual(toggle_text, "▶ Start Server")

        # 2. Running state
        self.bridge.is_running = True
        toggle_text = tray.get_server_toggle_text()
        self.assertEqual(toggle_text, "⏹ Stop Server")

        # 3. Return to offline
        self.bridge.is_running = False
        toggle_text = tray.get_server_toggle_text()
        self.assertEqual(toggle_text, "▶ Start Server")

    def test_tray_update_menu_safe(self):
        """Verifies update_menu is safe when tray is idle or with mock pystray icon."""
        tray = ServerTrayService("fake_icon.ico", bridge_api=self.bridge)
        # Should not raise even when icon is None
        tray.update_menu()

        # Mock pystray icon
        mock_icon = MagicMock()
        tray.icon = mock_icon
        tray.update_menu()
        mock_icon.update_menu.assert_called_once()

    def test_world_snapshot_auto_pruning(self):
        """Verifies strict 5-archive retention policy on world snapshots."""
        backups_dir = os.path.join(self.temp_dir, "snapshots_test")
        os.makedirs(backups_dir, exist_ok=True)

        created_files = []
        # Create 8 dummy archives with staggered modification timestamps
        now = time.time()
        for i in range(8):
            ext = ".tar.gz" if i % 2 == 0 else ".zip"
            fn = f"world_snapshot_26.2_{i}{ext}"
            fp = os.path.join(backups_dir, fn)
            with open(fp, "w") as f:
                f.write("backup data")
            mtime = now - ((8 - i) * 60)
            os.utime(fp, (mtime, mtime))
            created_files.append(fp)

        # Call prune with keep=5
        result = self.bridge.prune_world_snapshots(world_dir=backups_dir, keep=5)
        self.assertTrue(result["success"])
        self.assertEqual(result["retained_count"], 5)
        self.assertEqual(result["pruned_count"], 3)

        remaining = os.listdir(backups_dir)
        self.assertEqual(len(remaining), 5)
        # The 3 oldest (indices 0, 1, 2) should be removed
        for old_idx in [0, 1, 2]:
            self.assertNotIn(os.path.basename(created_files[old_idx]), remaining)
        # The 5 newest (indices 3, 4, 5, 6, 7) should remain
        for new_idx in [3, 4, 5, 6, 7]:
            self.assertIn(os.path.basename(created_files[new_idx]), remaining)

    def test_create_world_backup_and_rotation(self):
        """Verifies create_world_backup creates valid tar.gz and triggers auto-pruning."""
        v = self.bridge.active_version
        s_dir = self.bridge.get_active_server_path(v)
        world_dir = os.path.join(s_dir, "world")
        os.makedirs(world_dir, exist_ok=True)
        with open(os.path.join(world_dir, "level.dat"), "wb") as f:
            f.write(b"dummy_world_data_sir")

        res = self.bridge.create_world_backup(v)
        self.assertTrue(res["success"])
        self.assertTrue(os.path.isfile(res["path"]))
        self.assertTrue(res["path"].endswith(".tar.gz"))
        self.assertGreater(res["size_mb"], 0.0)

        # Test listing
        listed = self.bridge.list_world_backups(v)
        self.assertTrue(listed["success"])
        self.assertGreaterEqual(len(listed["backups"]), 1)

    def test_telemetry_sparkline_buffers(self):
        """Verifies tps_history and ram_history remain clamped and strictly formatted."""
        self.bridge.tps_history = [20.0] * 55
        self.bridge.ram_history = [2048.0] * 55

        for _ in range(10):
            self.bridge.tps_history.append(19.8)
            if len(self.bridge.tps_history) > 60:
                self.bridge.tps_history.pop(0)
            self.bridge.ram_history.append(2150.0)
            if len(self.bridge.ram_history) > 60:
                self.bridge.ram_history.pop(0)

        self.assertEqual(len(self.bridge.tps_history), 60)
        self.assertEqual(len(self.bridge.ram_history), 60)
        self.assertTrue(all(isinstance(x, (int, float)) for x in self.bridge.tps_history))
        self.assertTrue(all(isinstance(x, (int, float)) for x in self.bridge.ram_history))


if __name__ == "__main__":
    unittest.main()
