"""Adversarial and Empirical Challenge Test Suite for Milestone 3.

Empirically tests:
1. RFC 4122 UUIDv5 deterministic generation under edge usernames.
2. sync_to_ingame_ias() propagation across multi-instance hierarchies.
3. start_microsoft_browser_auth() PKCE, port fallback, socket lifecycle, callback HTTP handling.
4. cloud_sync_service.py with invalid/expired codes, HTTP errors, timeouts, malformed payloads.
5. Bridge API alias methods (create_offline_account, sync_cloud_code, toggle_mod, open_mods_folder,
   set_active_shader, set_active_resource_pack, set_power_governor, send_rcon_command).
"""

import os
import sys
import json
import uuid
import socket
import time
import shutil
import tempfile
import urllib.request
import urllib.error
import threading
import unittest
from unittest.mock import patch, MagicMock

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'development'))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.auth_service import AuthService
from launcher_core.cloud_sync_service import CloudSyncService
from launcher_core.bridge import LauncherBridgeAPI
from launcher_core.instance_service import InstanceService
from launcher_core.mods_service import ModsService
from launcher_core.shaders_service import ShadersService
from launcher_core.packs_service import PacksService
from launcher_core.rcon_service import RconService


class TestChallengerM3AccountsSyncBridge(unittest.TestCase):
    """Adversarial challenge test suite for Milestone 3."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_challenger_m3_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(self.instances_dir, exist_ok=True)

        # Setup standard and custom instance folders
        self.inst_262 = os.path.join(self.instances_dir, "26.2", "minecraft")
        self.inst_189 = os.path.join(self.instances_dir, "1.8.9", "minecraft")
        self.inst_custom = os.path.join(self.instances_dir, "custom-pvp", "minecraft")
        self.inst_mmc = os.path.join(self.instances_dir, "instance-mmc")
        self.inst_cfg = os.path.join(self.instances_dir, "instance-cfg")

        os.makedirs(self.inst_262, exist_ok=True)
        os.makedirs(self.inst_189, exist_ok=True)
        os.makedirs(self.inst_custom, exist_ok=True)
        os.makedirs(self.inst_mmc, exist_ok=True)
        os.makedirs(self.inst_cfg, exist_ok=True)

        # Pre-seed options.txt in 26.2 to test normal injection path
        with open(os.path.join(self.inst_262, "options.txt"), "w", encoding="utf-8") as f:
            f.write("version:3955\ngameVersion:1.21.4\nresourcePacks:[\"vanilla\"]\n")

        # Write marker files for mmc and cfg instances
        with open(os.path.join(self.inst_mmc, "mmc-pack.json"), "w", encoding="utf-8") as f:
            f.write('{"formatVersion": 1, "components": []}')
        with open(os.path.join(self.inst_cfg, "instance.cfg"), "w", encoding="utf-8") as f:
            f.write("InstanceType=OneSix\nname=CustomCfg\n")

        self.auth = AuthService(self.instances_dir)
        self.cloud_sync = CloudSyncService()

    def tearDown(self):
        if hasattr(self.auth, '_ms_browser_state') and self.auth._ms_browser_state:
            server = self.auth._ms_browser_state.get('server')
            if server:
                try:
                    server.server_close()
                except Exception:
                    pass
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    # =========================================================================
    # 1. RFC 4122 UUIDv5 DETERMINISTIC GENERATION & EDGE USERNAMES
    # =========================================================================

    def test_uuidv5_rfc4122_strict_compliance_and_determinism(self):
        """Verify strict RFC 4122 version 5 variant 1 generation across varied valid inputs."""
        valid_usernames = [
            "AB",                     # Min boundary (2 chars)
            "A123456789012345",       # Max boundary (16 chars)
            "Sir_Ahmed_2026",         # Mixed alphanumeric with underscore
            "ProGamer99",             # CamelCase
            "____",                   # Underscores only
            "123456",                 # Digits only
        ]

        for username in valid_usernames:
            res = self.auth.add_offline_account(username)
            self.assertTrue(res.get("success"), f"Failed for valid username: {username}")
            acc = res.get("account", {})

            # Extract UUID and verify RFC 4122 properties
            uuid_str = acc.get("uuid")
            self.assertIsNotNone(uuid_str)
            parsed_uuid = uuid.UUID(uuid_str)

            # Assert Version 5 (SHA-1 based namespace UUID)
            self.assertEqual(parsed_uuid.version, 5, f"UUID for {username} is not Version 5")
            # Assert RFC 4122 Variant (Variant 1)
            self.assertEqual(parsed_uuid.variant, uuid.RFC_4122, f"UUID for {username} is not RFC 4122")

            # Assert exact determinism against standard library formula
            expected = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"OfflinePlayer:{username}"))
            self.assertEqual(uuid_str, expected)

            # Re-calculating 50 times in a loop must be byte-for-byte identical
            for _ in range(50):
                self.assertEqual(str(uuid.uuid5(uuid.NAMESPACE_DNS, f"OfflinePlayer:{username}")), uuid_str)

    def test_uuidv5_edge_and_malicious_usernames_rejection(self):
        """Verify boundary and invalid usernames are properly rejected."""
        invalid_usernames = [
            ("", "empty username"),
            ("A", "below min length (1 char)"),
            ("A1234567890123456", "above max length (17 chars)"),
            ("User With Spaces", "contains spaces"),
            ("Player#1", "contains hash"),
            ("Steve!", "contains exclamation mark"),
            ("name$value", "contains dollar sign"),
            ("user@email", "contains at sign"),
            ("test-dash", "contains dash"),
            ("gamer🎮", "contains emoji/unicode"),
            ("أحمد", "arabic unicode"),
            ("Ümlaut", "latin-1 unicode"),
            ("'; DROP TABLE accounts; --", "SQL injection string"),
            ("<script>alert(1)</script>", "XSS script payload"),
            ("../../../etc/passwd", "Path traversal payload"),
        ]

        for username, reason in invalid_usernames:
            res = self.auth.add_offline_account(username)
            self.assertFalse(res.get("success"), f"Should reject invalid username: '{username}' ({reason})")
            self.assertIn("error", res)

    def test_account_case_normalization_and_switching(self):
        """Verify case insensitivity when switching existing accounts."""
        res1 = self.auth.add_offline_account("ShadowKnight")
        self.assertTrue(res1.get("success"))
        uuid1 = res1.get("account", {}).get("uuid")

        # Adding same account with lowercase should find existing and switch active without duplicating
        res2 = self.auth.add_offline_account("shadowknight")
        self.assertTrue(res2.get("success"))
        self.assertEqual(res2.get("account", {}).get("uuid"), uuid1)
        self.assertIn("Switched to offline profile", res2.get("message", ""))

        # Verify only 1 account exists in the list
        all_accounts = [a for a in self.auth.accounts if a.get("displayName").lower() == "shadowknight"]
        self.assertEqual(len(all_accounts), 1)

    # =========================================================================
    # 2. IAS SYNC MULTI-INSTANCE PROPAGATION
    # =========================================================================

    def test_ias_multi_instance_simultaneous_propagation(self):
        """Verify sync_to_ingame_ias propagates to all sub-instance directories atomically."""
        # Add multiple accounts
        self.auth.add_offline_account("AlphaUser")
        self.auth.add_offline_account("BetaUser")
        self.auth.add_offline_account("GammaUser", model="slim")
        self.auth.select_account("BetaUser")

        # Explicitly invoke sync_to_ingame_ias
        self.auth.sync_to_ingame_ias()

        # Check root IAS file
        root_ias = os.path.join(self.instances_dir, "ias_accounts.json")
        self.assertTrue(os.path.exists(root_ias), "Root ias_accounts.json missing")

        # Check all instance directories
        expected_paths = [
            root_ias,
            os.path.join(self.inst_262, "ias_accounts.json"),
            os.path.join(self.inst_189, "ias_accounts.json"),
            os.path.join(self.inst_custom, "ias_accounts.json"),
            os.path.join(self.inst_mmc, "ias_accounts.json"),
            os.path.join(self.inst_cfg, "ias_accounts.json"),
        ]

        for p in expected_paths:
            self.assertTrue(os.path.exists(p), f"IAS file missing at: {p}")
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data.get("schemaVersion"), 1)
            self.assertEqual(data.get("active"), "BetaUser")
            self.assertIsInstance(data.get("accounts"), list)
            self.assertEqual(len(data["accounts"]), 3)

            account_names = [a["name"] for a in data["accounts"]]
            self.assertEqual(account_names, ["AlphaUser", "BetaUser", "GammaUser"])

            # Verify schema of each account in IAS
            for acc in data["accounts"]:
                self.assertIn("name", acc)
                self.assertIn("type", acc)
                self.assertIn("uuid", acc)
                self.assertIn("skinUrl", acc)
                self.assertIn("model", acc)
                # Ensure ZERO secret tokens leak into IAS
                self.assertNotIn("access_token", acc)
                self.assertNotIn("refresh_token", acc)
                self.assertNotIn("uhs", acc)
                self.assertNotIn("password", acc)

    def test_ias_sync_deletion_and_switching_lifecycle(self):
        """Verify adding, selecting, and deleting accounts keeps all instance IAS files synchronized."""
        self.auth.add_offline_account("PlayerOne")
        self.auth.add_offline_account("PlayerTwo")
        self.auth.select_account("PlayerTwo")

        # Check active in 26.2
        target_ias = os.path.join(self.inst_262, "ias_accounts.json")
        with open(target_ias, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("active"), "PlayerTwo")

        # Remove PlayerTwo
        del_res = self.auth.remove_account("PlayerTwo")
        self.assertTrue(del_res.get("success"))

        # Verify all instances updated
        with open(target_ias, "r", encoding="utf-8") as f:
            data2 = json.load(f)
        names = [a["name"] for a in data2["accounts"]]
        self.assertNotIn("PlayerTwo", names)
        self.assertEqual(data2.get("active"), "PlayerOne")

    # =========================================================================
    # 3. MICROSOFT OAUTH PKCE & LOOPBACK PORT BINDING
    # =========================================================================

    def test_pkce_generation_and_challenge_math(self):
        """Verify PKCE code_challenge computation conforms to RFC 7636 S256."""
        import base64
        import hashlib

        with patch('webbrowser.open'):
            res = self.auth.start_microsoft_browser_auth()
            self.assertTrue(res.get("success"))
            self.assertIn("auth_url", res)
            self.assertIn("port", res)
            self.assertIn("redirect_uri", res)

            # Inspect internal state
            state = getattr(self.auth, '_ms_browser_state', None)
            self.assertIsNotNone(state)
            verifier = state.get("verifier")
            self.assertIsNotNone(verifier)
            self.assertGreaterEqual(len(verifier), 43, "PKCE verifier too short")

            # Manually calculate challenge from verifier
            digest = hashlib.sha256(verifier.encode("ascii")).digest()
            expected_challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

            auth_url = res["auth_url"]
            self.assertIn(f"code_challenge={expected_challenge}", auth_url)
            self.assertIn("code_challenge_method=S256", auth_url)
            self.assertIn("response_type=code", auth_url)
            self.assertIn(f"redirect_uri=http%3A%2F%2Flocalhost%3A{res['port']}%2F", auth_url)

    def test_microsoft_loopback_port_fallback_when_ports_occupied(self):
        """Verify port fallback mechanism when primary ports (52135, 52136) are occupied."""
        occupied_socks = []
        for p in [52135, 52136]:
            s = None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("127.0.0.1", p))
                s.listen(1)
                occupied_socks.append(s)
            except Exception:
                if s is not None:
                    try:
                        s.close()
                    except Exception:
                        pass

        try:
            with patch('webbrowser.open'):
                res = self.auth.start_microsoft_browser_auth()
                self.assertTrue(res.get("success"))
                bound_port = res.get("port")
                self.assertIsNotNone(bound_port)
                # Empirically record whether fallback succeeded or port was hijacked
                port_hijacked = bound_port in [s.getsockname()[1] for s in occupied_socks]
                if port_hijacked:
                    print(f"\n[EMPIRICAL FINDING] SO_REUSEADDR caused port hijacking on port {bound_port} instead of fallback!")
                self.assertFalse(port_hijacked, f"Port {bound_port} was hijacked despite active listener on same port")
        finally:
            for s in occupied_socks:
                try:
                    s.close()
                except Exception:
                    pass
            occupied_socks.clear()
            if hasattr(self.auth, '_ms_browser_state') and self.auth._ms_browser_state:
                srv = self.auth._ms_browser_state.get('server')
                if srv:
                    try:
                        srv.server_close()
                    except Exception:
                        pass

    def test_microsoft_loopback_callback_http_success_and_error(self):
        """Verify the local HTTP callback handler processes ?code= and ?error= requests."""
        with patch('webbrowser.open'):
            res = self.auth.start_microsoft_browser_auth()
            self.assertTrue(res.get("success"))
            port = res.get("port")

            # Check initial poll status
            poll_init = self.auth.poll_microsoft_browser_auth()
            self.assertFalse(poll_init.get("success"))
            self.assertTrue(poll_init.get("pending"))

            # Send HTTP GET with error to callback server
            error_url = f"http://127.0.0.1:{port}/?error=access_denied&error_description=User_denied_access"
            try:
                req = urllib.request.Request(error_url, headers={"User-Agent": "TestClient"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    body = response.read().decode("utf-8")
                    self.assertEqual(response.status, 200)
                    self.assertIn("Authentication Failed", body)
            except Exception as ex:
                self.fail(f"HTTP request to callback failed: {ex}")

            # Wait briefly for server state to register
            time.sleep(0.2)
            poll_err = self.auth.poll_microsoft_browser_auth()
            self.assertFalse(poll_err.get("success"))
            self.assertIn("error", poll_err, "OAuth error state was not registered in poll response")

    def test_microsoft_browser_auth_timeout_handling(self):
        """Verify poll_microsoft_browser_auth returns timeout when session expires."""
        with patch('webbrowser.open'):
            res = self.auth.start_microsoft_browser_auth()
            self.assertTrue(res.get("success"))

            # Force expire session
            self.auth._ms_browser_state["expires_at"] = time.time() - 10

            poll_timeout = self.auth.poll_microsoft_browser_auth()
            self.assertFalse(poll_timeout.get("success"))
            self.assertIn("timed out", poll_timeout.get("error", "").lower())
            self.assertIsNone(self.auth._ms_browser_state)

    # =========================================================================
    # 4. CLOUD SYNC SERVICE ADVERSARIAL CASES
    # =========================================================================

    def test_cloud_sync_code_validation_boundary_conditions(self):
        """Verify 6-digit sync code input validation on edge cases."""
        invalid_codes = [
            "",
            "1",
            "12",
            "123",
            "1234",
            "12345",
            "1234567",
            "12345678",
            "   ",
            " 12345 ",
            None,
        ]

        for code in invalid_codes:
            res = self.cloud_sync.resolve_6digit_sync_code(code)
            self.assertFalse(res.get("success"), f"Should reject code: '{code}'")
            self.assertIn("Invalid code format", res.get("error", ""))

    def test_cloud_sync_not_found_or_expired_null_response(self):
        """Verify handling of Firebase 'null' string when sync code is expired or non-existent."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b"null"
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            res = self.cloud_sync.resolve_6digit_sync_code("654321")
            self.assertFalse(res.get("success"))
            self.assertIn("not found or expired", res.get("error", ""))

    def test_cloud_sync_network_http_and_url_errors(self):
        """Verify graceful error reporting under network exceptions (HTTPError, URLError, Timeout)."""
        # Test HTTP 500
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="https://rtdb.firebase.com",
                code=500,
                msg="Internal Server Error",
                hdrs={},
                fp=None
            )
            res = self.cloud_sync.resolve_6digit_sync_code("112233")
            self.assertFalse(res.get("success"))
            self.assertIn("Network error", res.get("error", ""))

        # Test URLError / Connection refused
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
            res = self.cloud_sync.resolve_6digit_sync_code("112233")
            self.assertFalse(res.get("success"))
            self.assertIn("Network error", res.get("error", ""))

        # Test Timeout
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError("Connection timed out")
            res = self.cloud_sync.resolve_6digit_sync_code("112233")
            self.assertFalse(res.get("success"))
            self.assertIn("Network error", res.get("error", ""))

    def test_cloud_sync_backup_settings(self):
        """Verify backup_settings_to_cloud payload dispatch and exception resilience."""
        # Success PUT
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'{"status": "ok"}'
            mock_resp.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_resp

            res = self.cloud_sync.backup_settings_to_cloud("user_abc", {"ram_gb": 8, "shader": "extreme"})
            self.assertTrue(res.get("success"))
            self.assertIn("backed up", res.get("message", "").lower())

        # Error PUT
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = Exception("Write permission denied")
            res = self.cloud_sync.backup_settings_to_cloud("user_abc", {"ram_gb": 8})
            self.assertFalse(res.get("success"))
            self.assertIn("Write permission denied", res.get("error", ""))

    # =========================================================================
    # 5. BRIDGE API ALIAS METHODS FULL VERIFICATION
    # =========================================================================

    def test_bridge_all_new_alias_methods(self):
        """Verify each of the newly added bridge API alias methods executes and meets interface contracts."""
        bridge = LauncherBridgeAPI(self.test_dir)
        bridge.auth = self.auth

        # 1. create_offline_account
        res_create = bridge.create_offline_account("BridgeHero", model="slim")
        self.assertTrue(res_create.get("success"))
        acc = res_create.get("account", {})
        self.assertEqual(acc.get("displayName"), "BridgeHero")
        self.assertEqual(acc.get("model"), "slim")
        self.assertEqual(acc.get("accountType"), "offline")

        # 2. sync_cloud_code
        mock_payload = json.dumps({
            "code": "778899",
            "username": "SyncedBridgeHero",
            "skinUrl": "https://mc-heads.net/skin/SyncedBridgeHero",
            "model": "classic"
        }).encode("utf-8")

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = mock_payload
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res_sync = bridge.sync_cloud_code("778899")
            self.assertTrue(res_sync.get("success"))
            self.assertEqual(res_sync.get("account", {}).get("displayName"), "SyncedBridgeHero")

        # 3. toggle_mod (testing dual signature support)
        mods_dir = os.path.join(self.inst_262, "mods")
        os.makedirs(mods_dir, exist_ok=True)
        mod_jar_path = os.path.join(mods_dir, "sodium-fabric.jar")
        with open(mod_jar_path, "wb") as f:
            f.write(b"PK\x05\x06" + b"\x00" * 18)

        # Signature A: toggle_mod(inst_id, mod_filename) -> toggles to .disabled
        res_toggle_a = bridge.toggle_mod("26.2", "sodium-fabric.jar")
        self.assertTrue(res_toggle_a.get("success"))
        self.assertFalse(res_toggle_a.get("enabled"))
        self.assertTrue(os.path.exists(os.path.join(mods_dir, "sodium-fabric.jar.disabled")))

        # Signature B: toggle_mod(filename, enabled_state, inst_id) -> toggles back to enabled
        res_toggle_b = bridge.toggle_mod("sodium-fabric.jar.disabled", True, "26.2")
        self.assertTrue(res_toggle_b.get("success"))
        self.assertTrue(res_toggle_b.get("enabled"))
        self.assertTrue(os.path.exists(os.path.join(mods_dir, "sodium-fabric.jar")))

        # 4. open_mods_folder
        with patch('os.startfile', create=True) as mock_startfile, \
             patch('subprocess.Popen') as mock_popen:
            mock_popen.return_value = unittest.mock.MagicMock()
            res_open_mods = bridge.open_mods_folder("26.2")
            self.assertTrue(res_open_mods.get("success"))
            if sys.platform == "win32":
                self.assertTrue(mock_startfile.called)

        # 5. set_active_shader
        res_shader = bridge.set_active_shader("26.2", "SIR Modern Shader.zip")
        self.assertTrue(res_shader.get("success"))
        shader_file = os.path.join(self.inst_262, "optionsshaders.txt")
        self.assertTrue(os.path.exists(shader_file))
        with open(shader_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("shaderPack=SIR Modern Shader.zip", content)

        # 6. set_active_resource_pack (with pre-seeded options.txt)
        res_pack = bridge.set_active_resource_pack("26.2", "SIR Modern.zip")
        self.assertTrue(res_pack.get("success"))
        opt_file = os.path.join(self.inst_262, "options.txt")
        self.assertTrue(os.path.exists(opt_file))
        with open(opt_file, "r", encoding="utf-8") as f:
            opt_content = f.read()
        self.assertIn('resourcePacks:["file/SIR Modern.zip", "vanilla"]', opt_content)

        # 7. set_power_governor
        res_gov = bridge.set_power_governor("ultra_eco")
        self.assertTrue(res_gov.get("success"))
        self.assertEqual(res_gov.get("mode"), "ultra_eco")
        self.assertEqual(bridge.instances.settings.get("power_mode"), "ultra_eco")

        # 8. send_rcon_command
        res_rcon_tps = bridge.send_rcon_command("/tps")
        self.assertTrue(res_rcon_tps.get("success"))
        self.assertIn("TPS from last 1m", res_rcon_tps.get("response", ""))

        res_rcon_list = bridge.send_rcon_command("/list")
        self.assertTrue(res_rcon_list.get("success"))
        self.assertIn("players online", res_rcon_list.get("response", ""))

        res_rcon_op = bridge.send_rcon_command("/op SuperAdmin")
        self.assertTrue(res_rcon_op.get("success"))
        self.assertIn("Made SuperAdmin a server operator", res_rcon_op.get("response", ""))

        res_rcon_say = bridge.send_rcon_command("/say Server rebooting in 10s")
        self.assertTrue(res_rcon_say.get("success"))
        self.assertIn("Server rebooting in 10s", res_rcon_say.get("response", ""))

    # =========================================================================
    # 6. NON-EXISTENT OPTIONS.TXT RESOURCE PACK INJECTION TEST
    # =========================================================================

    def test_resource_pack_injection_on_missing_options_txt(self):
        """Verify behavior when toggle_pack is called on an instance lacking options.txt."""
        custom_inst_opt = os.path.join(self.inst_custom, "options.txt")
        if os.path.exists(custom_inst_opt):
            os.remove(custom_inst_opt)

        bridge = LauncherBridgeAPI(self.test_dir)
        res = bridge.set_active_resource_pack("custom-pvp", "SIR Modern.zip")
        self.assertTrue(res.get("success"))

        # Check whether options.txt was created or silently skipped
        file_created = os.path.exists(custom_inst_opt)
        if not file_created:
            print("\n[EMPIRICAL FINDING] PacksService.toggle_pack silently skipped creating options.txt on custom-pvp instance!")
        # Record finding in test
        self.assertTrue(file_created, "options.txt should be created if not present when setting active resource pack")


if __name__ == '__main__':
    unittest.main()
