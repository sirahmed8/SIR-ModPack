"""Adversarial Empirical Challenge Test Suite for Milestone 3 (Gen 8).

Validates:
1. ServerService.refresh_all_servers_async executes under 5 seconds with 20+ servers using ThreadPoolExecutor.
2. BridgeAPI._on_cloud_auth_change executes without throwing AttributeError, correctly formats profile JSON, and emits events.
3. Thread safety, timeout resilience, and non-blocking asynchronous properties.
"""

import os
import sys
import json
import time
import inspect
import socket
import threading
import unittest
from unittest.mock import patch, MagicMock

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'development'))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.server_service import ServerService
from launcher_core.bridge import LauncherBridgeAPI


class TestServerServiceRefreshParallel(unittest.TestCase):
    """Empirical verification of parallel server probing performance and architecture."""

    def setUp(self):
        self.service = ServerService()

    def test_server_service_uses_threadpoolexecutor(self):
        """Verify that refresh_all_servers_async explicitly employs ThreadPoolExecutor."""
        source = inspect.getsource(self.service.refresh_all_servers_async)
        self.assertIn("ThreadPoolExecutor", source, "ThreadPoolExecutor must be used in refresh_all_servers_async")
        self.assertIn("max_workers", source, "ThreadPoolExecutor must configure max_workers")

    def test_refresh_all_servers_async_nonblocking_invocation(self):
        """Verify calling refresh_all_servers_async returns control in under 50ms without blocking."""
        t0 = time.perf_counter()
        self.service.refresh_all_servers_async()
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 0.05, f"Invocation took {elapsed:.4f}s; must be immediately non-blocking")

    def test_refresh_25_servers_completes_under_5_seconds_simulated_network(self):
        """Stress-test 25 synthetic servers with controlled network latency to prove ThreadPoolExecutor throughput."""
        # Setup 25 synthetic servers
        custom_catalog = [
            {"name": f"Stress Server {i}", "ip": f"10.0.0.{i}", "port": 25565, "type": "Official", "category": "Competitive", "desc": f"Server {i}"}
            for i in range(1, 26)
        ]
        self.service.public_catalog = custom_catalog
        self.service.cached_results = {}

        # Simulate real socket ping (each taking 60ms) and API query (each taking 80ms)
        # Sequential time for 25 servers would be 25 * (0.06 + 0.08) = 3.5s; with workers=8 it should take ~0.5s.
        def mock_ping(host, port=25565):
            time.sleep(0.06)
            return {"online": True, "latency": 32}

        def mock_fetch(host):
            time.sleep(0.08)
            return {
                "online": True,
                "players_online": 120,
                "players_max": 500,
                "icon_url": f"https://example.com/{host}.png",
                "motd": f"Welcome to {host}",
                "version": "1.21.4"
            }

        completed_event = threading.Event()
        callback_result = []

        def on_done(servers):
            callback_result.extend(servers)
            completed_event.set()

        with patch.object(self.service, 'ping_single_server_live', side_effect=mock_ping), \
             patch.object(self.service, 'fetch_live_mcstatus', side_effect=mock_fetch), \
             patch.object(self.service, 'get_user_saved_servers', return_value=[]):
            
            t0 = time.perf_counter()
            self.service.refresh_all_servers_async(callback=on_done)
            done = completed_event.wait(timeout=5.0)
            elapsed = time.perf_counter() - t0

        self.assertTrue(done, f"Server refresh timed out after {elapsed:.2f}s! Must complete under 5.0 seconds")
        self.assertLess(elapsed, 5.0, f"Server refresh took {elapsed:.2f}s, exceeding the 5-second SLA")
        for i in range(1, 26):
            ip = f"10.0.0.{i}"
            self.assertIn(ip, self.service.cached_results, f"{ip} must be populated in cached_results")
            self.assertTrue(self.service.cached_results[ip]["online"])
            self.assertEqual(self.service.cached_results[ip]["players_online"], 120)

    def test_refresh_all_servers_stress_40_servers_error_resilience(self):
        """Stress-test 40 servers with mixed timeouts, exceptions, and latency under high load."""
        custom_catalog = [
            {"name": f"Mixed Server {i}", "ip": f"192.168.1.{i}", "port": 25565, "type": "Cracked", "category": "Survival", "desc": "Desc"}
            for i in range(1, 41)
        ]
        self.service.public_catalog = custom_catalog
        self.service.cached_results = {}

        def mock_ping_unstable(host, port=25565):
            idx = int(host.split('.')[-1])
            if idx % 4 == 0:
                raise socket.timeout("Socket timed out")
            elif idx % 4 == 1:
                raise ConnectionRefusedError("Connection refused")
            time.sleep(0.04)
            return {"online": True, "latency": 45}

        def mock_fetch_unstable(host):
            idx = int(host.split('.')[-1])
            if idx % 3 == 0:
                raise Exception("HTTP 429 Rate Limited")
            time.sleep(0.04)
            return {"online": True, "players_online": 50, "players_max": 200, "motd": "OK"}

        completed_event = threading.Event()
        with patch.object(self.service, 'ping_single_server_live', side_effect=mock_ping_unstable), \
             patch.object(self.service, 'fetch_live_mcstatus', side_effect=mock_fetch_unstable), \
             patch.object(self.service, 'get_user_saved_servers', return_value=[]):
            
            t0 = time.perf_counter()
            self.service.refresh_all_servers_async(callback=lambda res: completed_event.set())
            done = completed_event.wait(timeout=5.0)
            elapsed = time.perf_counter() - t0

        self.assertTrue(done, f"Stress test timed out after {elapsed:.2f}s!")
        self.assertLess(elapsed, 5.0, f"Stress test took {elapsed:.2f}s, exceeding 5s")

    def test_refresh_live_servers_real_probe_bounded(self):
        """Run against real live server catalog with timeout guard to ensure default catalog completes reliably."""
        completed_event = threading.Event()
        results = []

        def on_done(res):
            results.extend(res)
            completed_event.set()

        t0 = time.perf_counter()
        self.service.refresh_all_servers_async(callback=on_done)
        done = completed_event.wait(timeout=15.0)
        elapsed = time.perf_counter() - t0

        # Note: Live network depends on WAN latency, but under normal conditions it completes promptly
        self.assertTrue(done, "Live server probe did not complete within boundary")
        self.assertGreater(len(results), 0, "Expected server entries in callback results")


class TestBridgeCloudAuthInstantReflection(unittest.TestCase):
    """Empirical verification of Google OAuth instant reflection and UI event emission."""

    def setUp(self):
        self.bridge = LauncherBridgeAPI()

    def test_on_cloud_auth_change_without_window_no_attribute_error(self):
        """Verify _on_cloud_auth_change handles headless/null-window execution without throwing AttributeError."""
        self.bridge.window = None
        test_profile = {
            "name": "Ahmed Gamer",
            "email": "ahmed@example.com",
            "picture": "https://lh3.googleusercontent.com/a/test_avatar",
            "uid": "google-oauth2-100200300"
        }
        # Must execute cleanly with 0 exceptions
        try:
            self.bridge._on_cloud_auth_change(test_profile)
        except AttributeError as e:
            self.fail(f"_on_cloud_auth_change raised unexpected AttributeError: {e}")
        except Exception as e:
            self.fail(f"_on_cloud_auth_change raised unexpected Exception: {e}")

    def test_on_cloud_auth_change_with_mock_window_evaluates_js_and_formats_json(self):
        """Verify _on_cloud_auth_change correctly formats JSON and calls window.evaluate_js."""
        mock_window = MagicMock()
        mock_window.evaluate_js = MagicMock()
        mock_window.restore = MagicMock()
        mock_window.show = MagicMock()
        self.bridge.window = mock_window

        test_profile = {
            "name": "Sir Pro \u2728",
            "email": "player@sirmodpack.com",
            "picture": "https://sirmodpack.com/avatar.png",
            "uid": "usr_998877",
            "extra_quotes": 'He said "Hello"',
            "unicode_text": "مرحبا بالعالم"
        }

        self.bridge._on_cloud_auth_change(test_profile)

        # Verify evaluate_js was called synchronously for window.onCloudAuthSuccess
        calls = mock_window.evaluate_js.call_args_list
        auth_success_calls = [c for c in calls if "window.onCloudAuthSuccess" in c[0][0]]
        self.assertGreater(len(auth_success_calls), 0, "window.onCloudAuthSuccess was never evaluated!")

        js_code = auth_success_calls[0][0][0]
        self.assertTrue(js_code.startswith("if (window.onCloudAuthSuccess) window.onCloudAuthSuccess("))
        
        # Extract the JSON payload from the JS call and parse it
        json_str = js_code[len("if (window.onCloudAuthSuccess) window.onCloudAuthSuccess("):-2]
        parsed_payload = json.loads(json_str)
        self.assertEqual(parsed_payload, test_profile, "Formatted JSON in evaluate_js must exactly round-trip to original profile")

        # Verify window.restore and window.show were called to foreground window
        mock_window.restore.assert_called()
        mock_window.show.assert_called()

    def test_emit_ui_event_dispatches_events(self):
        """Verify both sir_cloud_auth_changed and cloud_auth_changed custom events are dispatched."""
        mock_window = MagicMock()
        evaluated_scripts = []
        event_dispatched = threading.Event()

        def mock_eval(code):
            evaluated_scripts.append(code)
            if len(evaluated_scripts) >= 2:
                event_dispatched.set()

        mock_window.evaluate_js = MagicMock(side_effect=mock_eval)
        self.bridge.window = mock_window

        profile = {"email": "test@test.com", "name": "Tester"}
        self.bridge._on_cloud_auth_change(profile)

        # Wait for asynchronous daemon thread to dispatch custom events
        event_dispatched.wait(timeout=2.0)

        all_scripts = " ".join(evaluated_scripts)
        self.assertIn("sir_cloud_auth_changed", all_scripts, "CustomEvent 'sir_cloud_auth_changed' was not dispatched")
        self.assertIn("cloud_auth_changed", all_scripts, "CustomEvent 'cloud_auth_changed' was not dispatched")

    def test_emit_to_js_method_alias_exists_and_functional(self):
        """Verify emit_to_js exists as an explicit method on LauncherBridgeAPI and acts as compatibility alias."""
        self.assertTrue(hasattr(self.bridge, 'emit_to_js'), "LauncherBridgeAPI must have emit_to_js method")
        self.assertTrue(callable(getattr(self.bridge, 'emit_to_js')), "emit_to_js must be callable")

        mock_window = MagicMock()
        evaluated = []
        ev = threading.Event()

        def side_effect(code):
            evaluated.append(code)
            ev.set()

        mock_window.evaluate_js = MagicMock(side_effect=side_effect)
        self.bridge.window = mock_window

        self.bridge.emit_to_js("custom_test_event", {"status": "ok", "value": 42})
        ev.wait(timeout=2.0)

        self.assertGreater(len(evaluated), 0)
        self.assertIn("custom_test_event", evaluated[0])
        self.assertIn('"status": "ok"', evaluated[0])


if __name__ == '__main__':
    unittest.main()
