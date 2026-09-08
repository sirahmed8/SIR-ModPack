import os
import sys
import json
import uuid
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'development'))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.auth_service import AuthService
from launcher_core.cloud_sync_service import CloudSyncService
from launcher_core.bridge import LauncherBridgeAPI


class TestCloudSyncAndAuth(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_auth_test_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "26.2", "minecraft"), exist_ok=True)
        os.makedirs(os.path.join(self.instances_dir, "1.8.9", "minecraft"), exist_ok=True)
        os.makedirs(os.path.join(self.instances_dir, "custom-test", "minecraft"), exist_ok=True)

        self.auth = AuthService(self.instances_dir)
        self.cloud_sync = CloudSyncService()

    def tearDown(self):
        if hasattr(self.auth, '_ms_browser_state') and self.auth._ms_browser_state.get('server'):
            try:
                self.auth._ms_browser_state['server'].server_close()
            except Exception:
                pass
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_uuidv5_deterministic_generation(self):
        username = "SirAhmed_Pro"
        expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"OfflinePlayer:{username}"))

        res = self.auth.add_offline_account(username)
        self.assertTrue(res.get("success"))
        acc = res.get("account", {})
        self.assertEqual(acc.get("uuid"), expected_uuid)
        self.assertEqual(acc.get("displayName"), username)
        self.assertEqual(acc.get("accountType"), "offline")

        # Calling again should return the existing account without duplicate
        res2 = self.auth.add_offline_account(username)
        self.assertTrue(res2.get("success"))
        self.assertEqual(res2.get("account", {}).get("uuid"), expected_uuid)

    def test_sync_to_ingame_ias_propagation(self):
        self.auth.add_offline_account("PlayerAlpha")
        self.auth.add_offline_account("PlayerBeta")
        self.auth.sync_to_ingame_ias()

        # Root ias_file
        root_ias = os.path.join(self.instances_dir, "ias_accounts.json")
        self.assertTrue(os.path.exists(root_ias))
        with open(root_ias, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("schemaVersion"), 1)
        self.assertIn("accounts", data)
        names = [a.get("name") for a in data["accounts"]]
        self.assertIn("PlayerAlpha", names)
        self.assertIn("PlayerBeta", names)

        # Instance subdirectories
        inst_262_ias = os.path.join(self.instances_dir, "26.2", "minecraft", "ias_accounts.json")
        inst_189_ias = os.path.join(self.instances_dir, "1.8.9", "minecraft", "ias_accounts.json")
        self.assertTrue(os.path.exists(inst_262_ias))
        self.assertTrue(os.path.exists(inst_189_ias))

        with open(inst_262_ias, "r", encoding="utf-8") as f:
            inst_data = json.load(f)
        self.assertEqual(inst_data.get("schemaVersion"), 1)
        self.assertEqual(len(inst_data["accounts"]), len(data["accounts"]))

    def test_microsoft_pkce_auth_port_return(self):
        with patch('webbrowser.open') as mock_wb:
            res = self.auth.start_microsoft_browser_auth()
            self.assertTrue(res.get("success"))
            self.assertIn("auth_url", res)
            self.assertIn("port", res)
            self.assertIn("redirect_uri", res)
            self.assertIsInstance(res["port"], int)
            self.assertGreater(res["port"], 0)
            self.assertEqual(res["redirect_uri"], f"http://localhost:{res['port']}/")
            self.assertIn(f"localhost%3A{res['port']}", res["auth_url"])
            self.assertIn("code_challenge=", res["auth_url"])
            self.assertIn("code_challenge_method=S256", res["auth_url"])

    def test_cloud_sync_code_resolution_path(self):
        # Test code format validation
        inv_res = self.cloud_sync.resolve_6digit_sync_code("123")
        self.assertFalse(inv_res.get("success"))
        self.assertIn("Invalid code", inv_res.get("error"))

        # Test mock successful response
        mock_response_data = json.dumps({
            "code": "849201",
            "userId": "user_123",
            "username": "CloudWarrior",
            "uuid": "4b7b4d1b-c79a-4c9f-859a-2415174092b2",
            "skinUrl": "https://mc-heads.net/skin/CloudWarrior",
            "createdAt": 1725000000,
            "expiresAt": 1725000600,
            "claimed": False
        }).encode("utf-8")

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = mock_response_data
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res = self.cloud_sync.resolve_6digit_sync_code("849201")
            self.assertTrue(res.get("success"))
            self.assertEqual(res.get("profile", {}).get("username"), "CloudWarrior")

    def test_cloud_sync_service_claim_sync_code(self):
        mock_payload = json.dumps({
            "code": "654321",
            "userId": "user_abc",
            "username": "HeroPlayer",
            "uuid": "4b7b4d1b-c79a-4c9f-859a-2415174092b2",
            "skinUrl": "https://mc-heads.net/skin/HeroPlayer",
            "claimed": False
        }).encode("utf-8")

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = mock_payload
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res = self.cloud_sync.claim_sync_code("654321", "HeroPlayer")
            self.assertTrue(res.get("success"))
            self.assertTrue(res.get("claimed"))
            self.assertEqual(res.get("code"), "654321")
            self.assertEqual(res.get("profile", {}).get("username"), "HeroPlayer")

        # Test claiming already claimed code
        mock_claimed_payload = json.dumps({
            "code": "654321",
            "username": "HeroPlayer",
            "claimed": True
        }).encode("utf-8")
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = mock_claimed_payload
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res2 = self.cloud_sync.claim_sync_code("654321")
            self.assertFalse(res2.get("success"))
            self.assertIn("already been claimed", res2.get("error"))

    def test_redeem_sync_code_with_username_support(self):
        mock_payload = json.dumps({
            "code": "998877",
            "username": "WebLinkedUser",
            "skinUrl": "https://mc-heads.net/skin/WebLinkedUser",
            "model": "slim"
        }).encode("utf-8")

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = mock_payload
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res = self.auth.redeem_sync_code("998877")
            self.assertTrue(res.get("success"))
            acc = res.get("account", {})
            self.assertEqual(acc.get("displayName"), "WebLinkedUser")
            self.assertEqual(acc.get("model"), "slim")

    def test_bridge_interface_contracts(self):
        bridge = LauncherBridgeAPI(self.test_dir)
        bridge.auth = self.auth

        # 1. create_offline_account
        res_create = bridge.create_offline_account("BridgePlayer", model="slim")
        self.assertTrue(res_create.get("success"))
        self.assertEqual(res_create.get("account", {}).get("displayName"), "BridgePlayer")

        # 2. sync_cloud_code (mocked)
        mock_payload = json.dumps({
            "code": "112233",
            "name": "SyncCodePlayer",
            "model": "classic"
        }).encode("utf-8")

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = mock_payload
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res_sync = bridge.sync_cloud_code("112233")
            self.assertTrue(res_sync.get("success"))
            self.assertEqual(res_sync.get("account", {}).get("displayName"), "SyncCodePlayer")

    def test_account_removal_and_state_sync(self):
        self.auth.add_offline_account("PlayerToRemove")
        res_del = self.auth.remove_account("PlayerToRemove")
        self.assertTrue(res_del.get("success"))

        names = [a.get("displayName") for a in self.auth.accounts]
        self.assertNotIn("PlayerToRemove", names)

    def test_accounts_manager_module(self):
        from launcher_core.accounts import AccountsManager, generate_offline_uuid, Account
        expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "OfflinePlayer:TestAccountsMgr"))
        self.assertEqual(generate_offline_uuid("TestAccountsMgr"), expected_uuid)

        mgr = AccountsManager(self.test_dir)
        res_add = mgr.add_offline_account("TestAccountsMgr", model="slim")
        self.assertTrue(res_add.get("success"))
        self.assertEqual(res_add.get("account", {}).get("uuid"), expected_uuid)
        self.assertEqual(res_add.get("account", {}).get("model"), "slim")

        # Verify ias_accounts.json written
        ias_path = os.path.join(self.test_dir, "ias_accounts.json")
        self.assertTrue(os.path.exists(ias_path))
        with open(ias_path, "r", encoding="utf-8") as f:
            ias_data = json.load(f)
        self.assertEqual(ias_data.get("active"), "TestAccountsMgr")
        self.assertEqual(len(ias_data.get("accounts", [])), 1)

    def test_skin_studio_service(self):
        from launcher_core.skin_studio_service import SkinStudioService
        sss = SkinStudioService(self.test_dir)
        skins = sss.get_curated_skins()
        capes = sss.get_curated_capes()
        self.assertGreaterEqual(len(skins), 5)
        self.assertGreaterEqual(len(capes), 5)

        with patch('shared_core.runtime.download_file_resilient') as mock_dl:
            res_apply = sss.apply_skin_and_cape("TestSkinUser", model="slim", instance_id="26.2")
            self.assertTrue(res_apply.get("success"))
            self.assertEqual(res_apply.get("username"), "TestSkinUser")
            self.assertEqual(res_apply.get("model"), "slim")


if __name__ == '__main__':
    unittest.main()
