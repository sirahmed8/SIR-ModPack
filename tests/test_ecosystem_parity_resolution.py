import unittest
import os
import shutil
import tempfile
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'development')))

from launcher_core.mods_service import ModsService
from launcher_core.instance_service import InstanceService
from launcher_core.auth_service import AuthService
from launcher_core.video_preset_service import VideoPresetService


class TestEcosystemParityResolution(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.instances_dir = os.path.join(self.test_dir, 'instances')
        os.makedirs(self.instances_dir, exist_ok=True)
        self.mods_service = ModsService(self.test_dir)
        self.instance_service = InstanceService(self.test_dir, self.instances_dir)
        self.auth_service = AuthService(self.test_dir)
        self.video_preset_service = VideoPresetService(self.instances_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_mod_dependency_check_and_auto_resolution(self):
        inst_dir = os.path.join(self.instances_dir, '26.2', 'minecraft', 'mods')
        os.makedirs(inst_dir, exist_ok=True)

        dummy_mod_zip = os.path.join(inst_dir, 'test_addon.jar')
        import zipfile
        with zipfile.ZipFile(dummy_mod_zip, 'w') as z:
            z.writestr('fabric.mod.json', json.dumps({
                'id': 'test_addon',
                'name': 'Test Addon',
                'version': '1.0.0',
                'depends': {
                    'cloth-config': '>=15.0.0'
                }
            }))

        res = self.mods_service.check_mod_dependencies('test_addon.jar', '26.2')
        self.assertTrue(res['has_missing'])
        self.assertEqual(len(res['missing']), 1)
        self.assertEqual(res['missing'][0]['id'], 'cloth-config')

    def test_ram_settings_precedence_and_silent_warnings(self):
        self.instance_service.save_settings({'ram_gb': 6})
        self.assertEqual(self.instance_service.settings.get('ram_gb'), 6)
        self.assertEqual(self.instance_service.settings.get('ram_allocated_gb'), 6)

        inst_dir = os.path.join(self.instances_dir, '26.2-ultra')
        mc_dir = os.path.join(inst_dir, 'minecraft')
        cfg_dir = os.path.join(mc_dir, 'config')
        os.makedirs(cfg_dir, exist_ok=True)
        mem_cfg = os.path.join(cfg_dir, 'memorysettings.json')
        with open(mem_cfg, 'w', encoding='utf-8') as f:
            json.dump({'disableWarnings': False}, f)

        inst_dict = {'id': 'sir-26-ultra', 'instance_id': '26.2-ultra', 'version': '26.2'}
        self.instance_service.heal_instance_if_needed(inst_dict, inst_dir, mc_dir, '26.2')

        with open(mem_cfg, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertTrue(data.get('disableWarnings', {}).get('disableWarnings'))

    def test_auth_token_retention_in_public_account(self):
        account = self.auth_service._public_account(
            account_id='msa_123',
            name='OfficialPlayer',
            account_type='microsoft',
            profile_id='uuid_123',
            uuid_value='uuid_123',
            skin_url='https://mc-heads.net/skin/OfficialPlayer',
            model='classic',
            access_token='EwB_TEST_TOKEN_12345',
            refresh_token='M.R3_REFRESH_TOKEN'
        )
        self.assertEqual(account.get('accessToken'), 'EwB_TEST_TOKEN_12345')
        self.assertEqual(account.get('token'), 'EwB_TEST_TOKEN_12345')
        self.assertEqual(account.get('accountType'), 'microsoft')

    def test_video_presets_unlimited_fps_and_vsync_off(self):
        inst_dir = os.path.join(self.instances_dir, '26.2-ultra')
        mc_dir = os.path.join(inst_dir, 'minecraft')
        os.makedirs(mc_dir, exist_ok=True)

        res = self.video_preset_service.apply_video_preset('26.2-ultra', 'ultra')
        self.assertTrue(res.get('success'))

        options_file = os.path.join(inst_dir, 'options.txt')
        if not os.path.exists(options_file):
            options_file = os.path.join(mc_dir, 'options.txt')
        
        with open(options_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('maxFramerate:260', content)
        self.assertIn('enableVsync:false', content)
        self.assertIn('fullscreen:true', content)


if __name__ == '__main__':
    unittest.main()
