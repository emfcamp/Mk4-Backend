from app.models.library import Library
import unittest, os, shutil
from unittest.mock import Mock
from ..fixtures.fake_git import FakeGit
from os.path import *

class TestLibraryIntegration(unittest.TestCase):
    def setUp(self):
        self.mc = Mock()
        self.mc.get = Mock(return_value=None)

        self.commit_id = "abc"
        self.path = normpath(dirname(realpath(__file__)) + "/../fixtures/library/")
        self.library = Library(self.commit_id, self.path, self.mc)

    def test_scan(self):
        self.library.scan()
        print(self.library.libs)
        self.assertEqual(set(self.library.libs.keys()), set(["lib1", "lib2", "lib3", "lib4", "lib5"]))


if __name__ == '__main__':
    unittest.main()
