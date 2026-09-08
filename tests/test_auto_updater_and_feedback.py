"""
test_auto_updater_and_feedback.py — Unit tests for Auto-Updater, Developer Feedback Highway, Diagnostics & Window Branding.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEV_DIR = os.path.join(ROOT_DIR, "development")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.bridge import LauncherBridgeAPI
from launcher_core.instance_service import InstanceService
from launcher_core.native_runner import NativeMinecraftRunner


class TestAutoUpdaterAndFeedback(unittest.TestCase):

    def setUp(self):
        self.bridge = LauncherBridgeAPI(ROOT_DIR)

    def test_settings_updater_defaults(self):
        """Ensure auto_check_updates and last_seen_release exist in settings defaults."""
        settings = self.bridge.instances.load_settings()
        self.assertIn("auto_check_updates", settings)
        self.assertIn("auto_download_updates", settings)
        self.assertIn("last_seen_release", settings)
        self.assertTrue(settings["auto_check_updates"])
        self.assertFalse(settings["auto_download_updates"])

    def test_get_system_diagnostic_metadata(self):
        """Verify real system diagnostics returns non-empty OS, GPU, and RAM allocation."""
        meta = self.bridge.get_system_diagnostic_metadata()
        self.assertIsInstance(meta, dict)
        self.assertIn("os", meta)
        self.assertIn("gpu", meta)
        self.assertIn("allocated_ram_gb", meta)
        self.assertIn("active_profile", meta)
        self.assertIn("log_tail", meta)

        self.assertTrue(len(meta["os"]) > 0)
        self.assertTrue(len(meta["gpu"]) > 0)
        self.assertGreater(meta["allocated_ram_gb"], 0)

    def test_check_for_launcher_updates(self):
        """Verify check_for_launcher_updates reports current version 1.0.0."""
        res = self.bridge.check_for_launcher_updates()
        self.assertIsInstance(res, dict)
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("current_version"), "1.0.0")
        self.assertIn("update_available", res)

    def test_whats_new_status_and_marking(self):
        """Verify What's New status lifecycle and marking."""
        # Mark 1.0.0 seen
        mark_res = self.bridge.mark_release_seen("1.0.0")
        self.assertTrue(mark_res.get("success"))
        self.assertEqual(mark_res.get("last_seen"), "1.0.0")

        # Now should_show should be False
        status = self.bridge.get_whats_new_status()
        self.assertFalse(status.get("should_show"))
        self.assertEqual(status.get("current_version"), "1.0.0")

    def test_submit_desktop_feedback_issue(self):
        """Verify issue feedback submission generates valid SIR-ERR ticket."""
        payload = {
            "type": "issue",
            "category": "launcher",
            "severity": "medium",
            "description": "Test automated diagnostic verification ticket.",
            "screenshot_url": "",
            "user_email": "tester@sir-modpack.com",
            "diagnostics": {"os": "Windows 11", "gpu": "RTX 4050"}
        }
        res = self.bridge.submit_desktop_feedback(payload)
        self.assertIsInstance(res, dict)
        self.assertTrue(res.get("success"))
        ticket_id = res.get("ticket_id")
        self.assertIsNotNone(ticket_id)
        self.assertTrue(ticket_id.startswith("SIR-ERR-"))

    def test_submit_desktop_feedback_suggestion(self):
        """Verify suggestion submission generates valid SIR-SUGG ticket."""
        payload = {
            "type": "suggestion",
            "category": "performance",
            "title": "Add Generational ZGC Fast Toggle",
            "description": "Would love an instant toggle on the main launchpad.",
            "screenshot_url": "",
            "user_email": "tester@sir-modpack.com",
            "diagnostics": {}
        }
        res = self.bridge.submit_desktop_feedback(payload)
        self.assertIsInstance(res, dict)
        self.assertTrue(res.get("success"))
        ticket_id = res.get("ticket_id")
        self.assertIsNotNone(ticket_id)
        self.assertTrue(ticket_id.startswith("SIR-SUGG-"))

    def test_jvm_args_window_title_and_branding(self):
        """Verify native_runner passes branding flags and target window title in JVM args."""
        runner = NativeMinecraftRunner(ROOT_DIR)
        jvm_args = runner.build_jvm_args(ram_gb=4, mc_version="26.2")

        # Must declare SIR Launcher branding
        self.assertTrue(any("minecraft.launcher.brand=SIR-Launcher" in arg for arg in jvm_args))
        self.assertTrue(any("minecraft.launcher.version=1.0.0" in arg for arg in jvm_args))
        self.assertTrue(any("Display.title=" in arg for arg in jvm_args))
        self.assertTrue(any("SIR Launcher" in arg for arg in jvm_args))


if __name__ == "__main__":
    unittest.main()
