import os
import sys
import unittest

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'development'))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.auth_service import AuthService

class TestAuthAndAccounts(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.auth = AuthService(self.root_dir)

    def test_offline_account_creation(self):
        res = self.auth.add_offline_account('SirAhmed_Test2')
        self.assertTrue(res.get('success'))
        acc = res.get('account', {})
        self.assertEqual(acc.get('displayName'), 'SirAhmed_Test2')
        self.assertEqual(acc.get('accountType'), 'offline')
        raw_uuid = acc.get('uuid', '').replace('-', '')
        self.assertEqual(len(raw_uuid), 32)

    def test_get_all_accounts(self):
        res = self.auth.get_all_accounts()
        self.assertIsInstance(res, dict)
        self.assertIn('accounts', res)
        accounts = res['accounts']
        self.assertIsInstance(accounts, list)
        self.assertGreater(len(accounts), 0)

if __name__ == '__main__':
    unittest.main()
