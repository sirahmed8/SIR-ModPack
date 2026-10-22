"""Unit tests for Controlify compatibility patcher."""
import os
import sys
import tempfile
import unittest
import zipfile

DEV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "development")
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.controlify_compat import (
    patch_controlify_jar,
    patch_all_controlify_jars,
    FANCYMENU_COMPAT_CLASS,
    FANCYMENU_TARGET_BYTES,
    FANCYMENU_REPLACEMENT_BYTES,
    ACTION_CLASS,
    ACTION_TARGET_BYTES,
    ACTION_REPLACEMENT_BYTES,
)


class TestControlifyCompat(unittest.TestCase):
    def test_nonexistent_file(self):
        self.assertFalse(patch_controlify_jar("nonexistent_path_to_jar.jar"))

    def test_jar_without_classes(self):
        with tempfile.NamedTemporaryFile(suffix=".jar", delete=False) as tf:
            tf_path = tf.name
        try:
            with zipfile.ZipFile(tf_path, "w") as zf:
                zf.writestr("some/other/Class.class", b"data")
            self.assertFalse(patch_controlify_jar(tf_path))
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)

    def test_patch_success_and_idempotency(self):
        with tempfile.NamedTemporaryFile(suffix=".jar", delete=False) as tf:
            tf_path = tf.name
        try:
            fake_fancymenu = b"prefix" + FANCYMENU_TARGET_BYTES + b"suffix"
            fake_action = b"prefix" + ACTION_TARGET_BYTES + b"suffix"
            with zipfile.ZipFile(tf_path, "w") as zf:
                zf.writestr(FANCYMENU_COMPAT_CLASS, fake_fancymenu)
                zf.writestr(ACTION_CLASS, fake_action)

            # First patch should succeed
            self.assertTrue(patch_controlify_jar(tf_path))

            # Inspect contents
            with zipfile.ZipFile(tf_path, "r") as zf:
                fm_data = zf.read(FANCYMENU_COMPAT_CLASS)
                act_data = zf.read(ACTION_CLASS)
                self.assertIn(FANCYMENU_REPLACEMENT_BYTES, fm_data)
                self.assertNotIn(FANCYMENU_TARGET_BYTES, fm_data)
                self.assertIn(ACTION_REPLACEMENT_BYTES, act_data)
                self.assertNotIn(ACTION_TARGET_BYTES, act_data)

            # Second patch should be idempotent and return False
            self.assertFalse(patch_controlify_jar(tf_path))
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)


if __name__ == "__main__":
    unittest.main()
