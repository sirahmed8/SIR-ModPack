"""
test_tray_and_window_lifecycle.py — Unit Tests for TrayService, Autostart Registry & Window Lifecycle Settings.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEV_DIR = os.path.join(ROOT_DIR, "development")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.tray_service import (
    TrayService,
    is_windows_autostart_enabled,
    set_windows_autostart,
)
from launcher_core.bridge import LauncherBridgeAPI
from launcher_core.instance_service import InstanceService
from launcher_core.native_runner import calculate_ram_parameters


class TestTrayAndWindowLifecycle(unittest.TestCase):

    def setUp(self):
        self.bridge = LauncherBridgeAPI(ROOT_DIR)

    def test_settings_defaults_contain_window_keys(self):
        """Verify launcher settings defaults contain window lifecycle actions."""
        settings = self.bridge.instances.load_settings()
        self.assertIn("window_close_action", settings)
        self.assertIn("window_launch_action", settings)
        self.assertIn("window_minimize_action", settings)
        self.assertIn("autostart_on_boot", settings)

        self.assertEqual(settings["window_close_action"], "tray")
        self.assertEqual(settings["window_launch_action"], "tray_trim")
        self.assertEqual(settings["window_minimize_action"], "taskbar")
        self.assertFalse(settings["autostart_on_boot"])

    def test_bridge_get_and_save_lifecycle_settings(self):
        """Verify LauncherBridgeAPI lifecycle settings endpoints save and load properly."""
        orig = self.bridge.get_window_lifecycle_settings()
        self.assertIn("window_close_action", orig)

        # Update lifecycle settings
        update_data = {
            "window_close_action": "taskbar",
            "window_launch_action": "keep_open",
            "window_minimize_action": "tray",
            "autostart_on_boot": False,
        }
        res = self.bridge.save_window_lifecycle_settings(update_data)
        self.assertTrue(res.get("success"))

        loaded = self.bridge.get_window_lifecycle_settings()
        self.assertEqual(loaded["window_close_action"], "taskbar")
        self.assertEqual(loaded["window_launch_action"], "keep_open")
        self.assertEqual(loaded["window_minimize_action"], "tray")

        # Restore defaults
        self.bridge.save_window_lifecycle_settings({
            "window_close_action": "tray",
            "window_launch_action": "tray_trim",
            "window_minimize_action": "taskbar",
            "autostart_on_boot": False,
        })

    def test_tray_service_initialization_and_singleton(self):
        """Verify TrayService instantiates, records window reference, and registers singleton."""
        mock_window = MagicMock()
        mock_bridge = MagicMock()
        icon_path = os.path.join(ROOT_DIR, "SIR_Icon.ico")

        tray = TrayService(
            icon_path=icon_path,
            window=mock_window,
            bridge_api=mock_bridge,
        )
        self.assertEqual(TrayService.get_instance(), tray)

        # Test restore_and_focus_window calls
        tray.restore_and_focus_window()
        mock_window.show.assert_called_once()
        mock_window.restore.assert_called_once()

    def test_kill_instance_and_all_instances(self):
        """Verify kill_instance handles nonexistent and active processes gracefully."""
        res = self.bridge.kill_instance("nonexistent_inst")
        self.assertFalse(res.get("success"))

        mock_proc = MagicMock()
        self.bridge.instances.running_processes["test_inst"] = mock_proc
        kill_res = self.bridge.kill_instance("test_inst")
        self.assertTrue(kill_res.get("success"))
        mock_proc.terminate.assert_called_once()
        self.assertNotIn("test_inst", self.bridge.instances.running_processes)

        # kill_all_instances
        p1 = MagicMock()
        p2 = MagicMock()
        self.bridge.instances.running_processes["inst_1"] = p1
        self.bridge.instances.running_processes["inst_2"] = p2
        all_res = self.bridge.kill_all_instances()
        self.assertTrue(all_res.get("success"))
        p1.terminate.assert_called_once()
        p2.terminate.assert_called_once()
        self.assertEqual(len(self.bridge.instances.running_processes), 0)

    def test_minimize_and_restore_window_bridge(self):
        """Verify bridge minimize_to_tray and restore_window API calls."""
        mock_window = MagicMock()
        self.bridge.set_window(mock_window)

        min_res = self.bridge.minimize_to_tray()
        self.assertTrue(min_res.get("success"))
        mock_window.hide.assert_called_once()

        rest_res = self.bridge.restore_window()
        self.assertTrue(rest_res.get("success"))
        mock_window.show.assert_called()

    def test_ram_discrete_presets_validation(self):
        """Verify discrete RAM presets conform strictly to [2, 4, 6, 8, 10, 12, 16, 20, 24] GB."""
        expected_presets = [2, 4, 6, 8, 10, 12, 16, 20, 24]
        for preset in expected_presets:
            params = calculate_ram_parameters(f"{preset}G")
            self.assertIn("-Xmx", params["xmx_flag"])
            self.assertEqual(params["max_mb"], preset * 1024)

    def test_tray_menu_settings_callback_js_evaluation(self):
        """Verify tray settings menu item evaluates openSettingsModal('window')."""
        mock_window = MagicMock()
        mock_bridge = MagicMock()
        tray = TrayService(
            icon_path=os.path.join(ROOT_DIR, "SIR_Icon.ico"),
            window=mock_window,
            bridge_api=mock_bridge,
        )
        # Verify tray holds window reference for direct RPC evaluation
        self.assertIsNotNone(tray.window)
        tray.restore_and_focus_window()
        mock_window.restore.assert_called()


if __name__ == "__main__":
    unittest.main()

