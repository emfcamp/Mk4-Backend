from app.models.cache_folder import CacheFolder
import shutil, tempfile, os

import unittest

class TestCacheFolder(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cf = CacheFolder(path=self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_default_relative_path(self):
        cf = CacheFolder()
        self.assertIn("/badgestore-cache", cf.path);

    def test_folder_gets_created(self):
        new_path = str(self.cf.get("foo"))
        self.assertIn("/foo", new_path);
        self.assertTrue(os.path.isdir(new_path));

    def test_exists(self):
        self.assertFalse(self.cf.exists("something"));
        self.cf.get("something")
        self.assertTrue(self.cf.exists("something"));





if __name__ == '__main__':
    unittest.main()
