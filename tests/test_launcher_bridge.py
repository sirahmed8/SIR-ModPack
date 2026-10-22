"""
test_launcher_bridge.py — Comprehensive Unit & Integration Tests for LauncherBridgeAPI & AsyncTaskManager.
"""
import json
import os
import sys
import tempfile
import time
import unittest

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.bridge import LauncherBridgeAPI
from launcher_core.async_tasks import AsyncTaskManager, AsyncTask
from launcher_core.hardware_monitor_service import HardwareMonitorService
from launcher_core.instance_service import InstanceService
from launcher_core.cleaner_service import CleanerService
from launcher_core.repair_service import RepairService
from launcher_core.store_service import StoreService


class MockWebViewWindow:
    """Mock PyWebView window for verifying custom event dispatches."""

    def __init__(self):
        self.evaluated_js = []

    def evaluate_js(self, script: str):
        self.evaluated_js.append(script)


class TestLauncherBridge(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.temp_dir = tempfile.mkdtemp()
        self.bridge = LauncherBridgeAPI(self.root_dir, data_root=self.temp_dir)
        self.mock_window = MockWebViewWindow()
        self.bridge.set_window(self.mock_window)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        exports_dir = os.path.join(self.root_dir, "exports")
        if os.path.isdir(exports_dir):
            for f in os.listdir(exports_dir):
                if f.startswith("SIR_ModPack_") and f.endswith(".zip"):
                    try:
                        os.remove(os.path.join(exports_dir, f))
                    except Exception:
                        pass

    def test_hardware_telemetry_live(self):
        hw = HardwareMonitorService()
        data = hw.get_hardware_telemetry()
        self.assertTrue(data.get("success"))
        self.assertIn("total_ram_gb", data)
        self.assertIn("cpu_cores", data)
        self.assertGreater(data.get("cpu_cores", 0), 0)
        self.assertIn("disk_total_gb", data)
        self.assertIn("gpu_name", data)

    def test_instance_list(self):
        result = self.bridge.get_instances()
        self.assertIsInstance(result, dict)
        self.assertIn("instances", result)
        instances = result["instances"]
        self.assertIsInstance(instances, list)
        self.assertGreater(len(instances), 0)
        ids = [i.get("id") for i in instances]
        self.assertTrue(any("26" in str(x) or "ultra" in str(x) or "1.8.9" in str(x) for x in ids))

    def test_video_presets_exist(self):
        instances_dir = os.path.join(self.root_dir, "instances")
        inst_service = InstanceService(self.root_dir, instances_dir)
        res = inst_service.apply_video_preset("sir-26-ultra", "balanced")
        self.assertIsInstance(res, dict)
        self.assertIn("success", res)

    def test_cleaner_and_repair(self):
        cleaner = CleanerService(self.root_dir)
        clean_res = cleaner.run_deep_clean(dry_run=True)
        self.assertTrue(clean_res.get("success"))
        self.assertTrue(clean_res.get("dry_run"))

        repair = RepairService(self.root_dir)
        self.assertTrue(hasattr(repair, "verify_file_integrity"))

    def test_async_task_manager_submission_and_completion(self):
        manager = AsyncTaskManager.get_instance()

        def sample_work(progress_cb=None):
            if progress_cb:
                progress_cb(50, "Halfway done")
            time.sleep(0.05)
            if progress_cb:
                progress_cb(100, "Finished")
            return {"value": 42}

        task_id = manager.submit_task("Sample Work", sample_work)
        self.assertTrue(task_id.startswith("task_"))

        # Wait for task to finish
        for _ in range(50):
            status = manager.get_task(task_id)
            if status and status["status"] in ("completed", "failed"):
                break
            time.sleep(0.02)

        final_status = manager.get_task(task_id)
        self.assertIsNotNone(final_status)
        self.assertEqual(final_status["status"], "completed")
        self.assertEqual(final_status["result"], {"value": 42})
        self.assertEqual(final_status["progress"], 100)

    def test_async_task_cancellation(self):
        manager = AsyncTaskManager.get_instance()

        def long_running_task(cancel_event=None):
            for _ in range(100):
                if cancel_event and cancel_event.is_set():
                    return "Cancelled"
                time.sleep(0.05)
            return "Finished"

        task_id = manager.submit_task("Long Task", long_running_task)
        time.sleep(0.02)
        cancelled = manager.cancel_task(task_id)
        self.assertTrue(cancelled)

        status = manager.get_task(task_id)
        self.assertEqual(status["status"], "cancelled")

    def test_bridge_event_emission(self):
        self.mock_window.evaluated_js.clear()
        self.bridge._emit_ui_event("custom_test_event", {"status": "ok", "value": 123})
        custom_events = [js for js in self.mock_window.evaluated_js if "custom_test_event" in js]
        self.assertGreaterEqual(len(custom_events), 1)
        self.assertIn("custom_test_event", custom_events[0])
        self.assertIn('"value": 123', custom_events[0])

    def test_legal_terms_acceptance_atomic(self):
        res = self.bridge.accept_legal_terms(version="2026.1")
        self.assertTrue(res.get("success"))
        status = self.bridge.get_legal_status()
        self.assertTrue(status.get("agreed"))
        self.assertEqual(status.get("agreed_version"), "2026.1")

    def test_check_mod_updates_chunked(self):
        res = self.bridge.check_mod_updates("26.2")
        self.assertTrue(res.get("success"))
        self.assertIn("updates", res)
        self.assertIn("count", res)
        self.assertIsInstance(res["updates"], list)

    def test_store_service_caching(self):
        store = StoreService(self.root_dir)
        # Search test
        res1 = store.search_modrinth(query="sodium", project_type="mod", limit=5)
        self.assertIsInstance(res1, dict)
        # Second call should hit internal cache without error
        res2 = store.search_modrinth(query="sodium", project_type="mod", limit=5)
        self.assertEqual(res1.get("success"), res2.get("success"))

    def test_bridge_async_operations_dispatch(self):
        # 1. check_mod_updates_async
        r1 = self.bridge.check_mod_updates_async("26.2")
        self.assertTrue(r1.get("success"))
        self.assertIn("task_id", r1)

        # 2. run_deep_clean_async
        r2 = self.bridge.run_deep_clean_async(dry_run=True)
        self.assertTrue(r2.get("success"))
        self.assertIn("task_id", r2)

        # 3. run_self_repair_async
        r3 = self.bridge.run_self_repair_async("26.2")
        self.assertTrue(r3.get("success"))
        self.assertIn("task_id", r3)

        # 4. export_instance_zip_async
        r4 = self.bridge.export_instance_zip_async("26.2")
        self.assertTrue(r4.get("success"))
        self.assertIn("task_id", r4)

        # 5. memory trimming bridge
        r5 = self.bridge.trim_process_memory()
        self.assertIsInstance(r5, dict)


if __name__ == "__main__":
    unittest.main()
