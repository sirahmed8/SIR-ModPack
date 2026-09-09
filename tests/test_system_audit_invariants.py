import os
import json
import unittest
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestSystemAuditInvariants(unittest.TestCase):
    """Guarantees system hygiene, zero dead clones, clean prototypes, and manifest integrity."""

    def test_root_prism_clone_absent(self):
        root_prism = os.path.join(ROOT_DIR, "PrismLauncher-develop")
        self.assertFalse(os.path.exists(root_prism), "PrismLauncher-develop clone should not exist in project root")

    def test_obsolete_dist_folders_absent(self):
        for folder in ["dist", "dist_build"]:
            path = os.path.join(ROOT_DIR, folder)
            self.assertFalse(os.path.exists(path), f"Obsolete build folder {folder} should not exist in root")

    def test_legacy_server_prototypes_absent(self):
        server_dir = os.path.join(ROOT_DIR, "server")
        conflicting_files = ["SIR Server Studio.exe", "SIR Server Manager.exe", "sir_server_studio.py"]
        for f in conflicting_files:
            path = os.path.join(server_dir, f)
            self.assertFalse(os.path.exists(path), f"Legacy prototype {f} should not exist in server/")

    def test_orphaned_bin_files_absent(self):
        bin_dir = os.path.join(ROOT_DIR, "bin")
        for orphan in ["vc_redist", "prismlauncher_updater.exe", "prismlauncher_filelink.exe"]:
            path = os.path.join(bin_dir, orphan)
            self.assertFalse(os.path.exists(path), f"Orphaned binary/folder {orphan} should not exist in bin/")

    def test_blclient_cache_absent(self):
        bl_dir = os.path.join(ROOT_DIR, "assets", "blclient")
        for cfile in ["assets.json", "cache.dat"]:
            path = os.path.join(bl_dir, cfile)
            self.assertFalse(os.path.exists(path), f"Badlion cache file {cfile} should be purged")

    def test_source_assets_mods_purged_configs_retained(self):
        sa_dir = os.path.join(ROOT_DIR, "source_assets")
        if os.path.exists(sa_dir):
            for sub in ["atm10", "fabulously_optimized", "rlcraft", "simply_smooth"]:
                mods_path = os.path.join(sa_dir, sub, "mods")
                self.assertFalse(os.path.exists(mods_path), f"source_assets/{sub}/mods should be purged of dead jars")
                config_path = os.path.join(sa_dir, sub, "config")
                if os.path.exists(os.path.join(sa_dir, sub)):
                    self.assertTrue(os.path.exists(config_path), f"source_assets/{sub}/config should be preserved")

    def test_delta_manifest_integrity_and_new_mods(self):
        manifest_path = os.path.join(ROOT_DIR, "delta_manifest.json")
        self.assertTrue(os.path.exists(manifest_path), "delta_manifest.json must exist")
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("files", data)
        files = data["files"]
        self.assertGreater(len(files), 2500)

        # Verify key deployed mods are present with valid SHA-256 hashes
        expected_mod_keys = [
            "krypton",
            "resourcify",
            "NoChatReports",
            "replaymod",
            "nvidium",
            "fabric-api",
            "fabric-language-kotlin",
            "placeholder-api",
            "modmenu",
            "sodium",
            "cloth-config"
        ]
        found_keys = set()
        for rel_path, meta in files.items():
            rel_lower = rel_path.lower()
            for key in expected_mod_keys:
                if key.lower() in rel_lower:
                    found_keys.add(key)
                    self.assertIn("sha256", meta)
                    self.assertEqual(len(meta["sha256"]), 64)

        self.assertTrue(len(found_keys) >= 7, f"Expected majority of core mods in manifest, found: {found_keys}")

    def test_drive_d_free_space_threshold(self):
        total, used, free = shutil.disk_usage(ROOT_DIR)
        free_gb = free / (1024 ** 3)
        if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
            self.assertGreaterEqual(free_gb, 1.0, f"CI disk free space must be >= 1 GB, currently {free_gb:.2f} GB")
        elif ROOT_DIR.upper().startswith("D:"):
            min_free = 17.0 if (os.path.isdir(os.path.join(ROOT_DIR, "website-next", "out")) and os.path.isdir(os.path.join(ROOT_DIR, "dist_apps"))) else 18.0
            self.assertGreaterEqual(free_gb, min_free, f"Drive D free space must be >= {min_free} GB, currently {free_gb:.2f} GB")
        else:
            self.assertGreaterEqual(free_gb, 1.0, f"Disk free space must be >= 1 GB, currently {free_gb:.2f} GB")

if __name__ == '__main__':
    unittest.main()
