from app.models.library import Library
import unittest, os, shutil
from unittest.mock import Mock
from ..fixtures.fake_git import FakeGit
from os.path import *

class TestLibrary(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.mc = Mock()
        self.mc.get = Mock(return_value=None)

        self.commit_id = "abc"
        self.path = normpath(dirname(realpath(__file__)) + "/../fixtures/library/")
        self.library = Library(self.commit_id, self.path, self.mc)

    def test_scan_uses_memcache_to_avoid_double_processing(self):
        self.mc.get = Mock(return_value={'foo':{'type':'app'}})
        self.library.resources
        self.mc.get.assert_called_once_with("library_parse::v2::abc")
        self.assertEqual(self.library.resources, {'foo':{'type':'app'}})


    def test_resources(self):
        self.assertDictEqual(self.library.resources, {'app1': {'bootstraped': True,
                 'categories': ['CategoryForApp1', 'SecondaryCategory'],
                 'dependencies': ['lib/lib1.py', 'lib/lib3.py'],
                 'description': 'Description of App1',
                 'files': {'app1/main.py': 'bbd098b482',
                           'app1/nested/text.txt': '4bc453b53c',
                           'lib/lib1.py': 'ca7f60c52e',
                           'lib/lib3.py': 'c3cfdb21a1',
                           'lib/lib4.py': '6dd887be0d',
                           'lib/lib5.py': '45f83b8aed'},
                 'license': 'MIT',
                 'type': 'app'},
        'app2': {'bootstraped': True,
                 'categories': ['CategoryForApp2', 'SecondaryCategory'],
                 'dependencies': ['lib/lib2.py', 'lib/lib3.py'],
                 'description': 'Description of App2',
                 'files': {'app2/main.py': 'f03144f146',
                           'app2/other_content.txt': '6bb2b25c4c',
                           'app2/some_binary_file.gif': '4e07053274',
                           'lib/lib2.py': '607bb3cf8d',
                           'lib/lib3.py': 'c3cfdb21a1',
                           'shared/foo.txt': '7d865e959b'},
                 'license': 'MIT',
                 'type': 'app'},
        'boot.py': {'files': {'boot.py': 'e47081f1b2'}, 'type': 'root'},
        'lib/lib1.py': {'dependencies': ['lib/lib4.py'],
                        'description': 'this is library 1',
                        'files': {'lib/lib1.py': 'ca7f60c52e',
                                  'lib/lib4.py': '6dd887be0d',
                                  'lib/lib5.py': '45f83b8aed'},
                        'license': 'MIT',
                        'type': 'lib'},
        'lib/lib2.py': {'dependencies': ['shared/foo.txt'],
                        'description': 'this is library 2',
                        'files': {'lib/lib2.py': '607bb3cf8d',
                                  'shared/foo.txt': '7d865e959b'},
                        'license': 'MIT',
                        'type': 'lib'},
        'lib/lib3.py': {'description': 'this is library 3',
                        'files': {'lib/lib3.py': 'c3cfdb21a1'},
                        'license': 'MIT',
                        'type': 'lib'},
        'lib/lib4.py': {'dependencies': ['lib/lib5.py'],
                        'description': 'this is library 4',
                        'files': {'lib/lib4.py': '6dd887be0d',
                                  'lib/lib5.py': '45f83b8aed'},
                        'license': 'MIT',
                        'type': 'lib'},
        'lib/lib5.py': {'description': 'this is library 5',
                        'files': {'lib/lib5.py': '45f83b8aed'},
                        'license': 'MIT',
                        'type': 'lib'},
        'shared/foo.txt': {'files': {'shared/foo.txt': '7d865e959b'},
                           'type': 'shared'}})

    def test_invalid_path(self):
        self.library.path = "fooooooo"
        with self.assertRaises(Exception) as context:
            self.library.resources
        self.assertIn("No such file or directory: 'fooooooo'", str(context.exception))

    def test_categories(self):
        self.assertDictEqual(self.library.categories, {
            'CategoryForApp2': ['app2'],
            'SecondaryCategory': ['app2', 'app1'],
            'CategoryForApp1': ['app1']
        })


if __name__ == '__main__':
    unittest.main()
