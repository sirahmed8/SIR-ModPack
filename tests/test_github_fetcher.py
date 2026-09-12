import os
import sys
import unittest
from unittest.mock import patch, MagicMock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEV_DIR = os.path.join(ROOT_DIR, "development")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from shared_core.github_fetcher import GitHubDeltaFetcher, sha256_file


class TestGitHubDeltaFetcher(unittest.TestCase):
    def setUp(self):
        self.fetcher = GitHubDeltaFetcher(root_dir=ROOT_DIR)

    def test_load_local_manifest(self):
        manifest = self.fetcher.load_local_manifest()
        self.assertIsInstance(manifest, dict)
        self.assertIn("files", manifest)
        self.assertTrue(len(manifest["files"]) > 0)

    def test_ensure_single_file_existing(self):
        # A file that definitely exists
        test_file = os.path.join(ROOT_DIR, "development", "shared_core", "github_fetcher.py")
        h = sha256_file(test_file)
        self.assertTrue(len(h) == 64)
        ok = self.fetcher.ensure_single_file("development/shared_core/github_fetcher.py", test_file, expected_hash=h)
        self.assertTrue(ok)

    @patch("urllib.request.urlopen")
    def test_fetch_file_mock_download(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers.get.return_value = "11"
        mock_response.read.side_effect = [b"mock content", b""]
        mock_urlopen.return_value.__enter__.return_value = mock_response

        dest = os.path.join(ROOT_DIR, "tests", "temp_fetch_test.txt")
        try:
            ok = self.fetcher.fetch_file("test/file.txt", dest)
            self.assertTrue(ok)
            self.assertTrue(os.path.isfile(dest))
            with open(dest, "rb") as f:
                self.assertEqual(f.read(), b"mock content")
        finally:
            if os.path.exists(dest):
                os.remove(dest)


if __name__ == "__main__":
    unittest.main()
