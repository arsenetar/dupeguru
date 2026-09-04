# Unit tests for core.paths pure-python fallback path resolution

import unittest
from pathlib import Path
from core.paths import get_appdata_path, get_cache_path
from hscommon.desktop import special_folder_path, SpecialFolder


class TestPathsResolution(unittest.TestCase):
    def test_get_appdata_path_default(self):
        path = get_appdata_path()
        self.assertIsInstance(path, str)
        self.assertTrue("de-dup" in path or "dupeGuru" in path)

    def test_get_appdata_path_portable(self):
        fake_root = Path("/fake/root")
        path = get_appdata_path(portable=True, project_root=fake_root)
        self.assertEqual(path, "/fake/root/data")

    def test_get_cache_path_default(self):
        path = get_cache_path()
        self.assertIsInstance(path, str)
        self.assertTrue("de-dup" in path or "cache" in path)

    def test_get_cache_path_portable(self):
        fake_root = Path("/fake/root")
        path = get_cache_path(portable=True, project_root=fake_root)
        self.assertEqual(path, "/fake/root/cache")

    def test_hscommon_desktop_special_folder_path_fallback(self):
        appdata = special_folder_path(SpecialFolder.APPDATA)
        cache = special_folder_path(SpecialFolder.CACHE)
        self.assertIsInstance(appdata, str)
        self.assertIsInstance(cache, str)
        self.assertNotEqual(appdata, "/tmp")


if __name__ == "__main__":
    unittest.main()
