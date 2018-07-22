from app.util.resources import *
import unittest
from os.path import *

class TestResourceScanner(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.path = normpath(dirname(realpath(__file__)) + "/../fixtures/library/")

    def test_get_resources(self):
        result = get_resources(self.path)
        self.assertDictEqual(result,
            {
                "app1": {"type": "app", "files": {"app1/main.py": None, "app1/nested/text.txt": None}},
                "app2": {"type": "app", "files": {"app2/main.py": None, "app2/other_content.txt": None, "app2/some_binary_file.gif": None}},
                "lib/lib1.py": {"type": "lib", "files": {"lib/lib1.py": None}},
                "lib/lib2.py": {"type": "lib", "files": {"lib/lib2.py": None}},
                "lib/lib3.py": {"type": "lib", "files": {"lib/lib3.py": None}},
                "lib/lib4.py": {"type": "lib", "files": {"lib/lib4.py": None}},
                "lib/lib5.py": {"type": "lib", "files": {"lib/lib5.py": None}},
                "shared/foo.txt": {"type": "shared", "files": {"shared/foo.txt": None}},
                "boot.py": {"type": "root", "files": {"boot.py": None}}
            }
        )

    def test_add_hashes(self):
        resources = {
            "app1": {"type": "app", "files": {"app1/main.py": None, "app1/nested/text.txt": None}},
            "app2": {"type": "app", "files": {"app2/main.py": None, "app2/other_content.txt": None, "app2/some_binary_file.gif": None}},
        }
        expected = {
            "app1": {"type": "app", "files": {"app1/main.py": "bbd098b482", "app1/nested/text.txt": "4bc453b53c"}},
            "app2": {"type": "app", "files": {"app2/main.py": "f03144f146", "app2/other_content.txt": "6bb2b25c4c", "app2/some_binary_file.gif": "4e07053274"}},
        }
        add_hashes(self.path, resources)
        self.assertEqual(resources, expected)

    def test_add_metadata(self):
        resources = {
            "app1": {"type": "app", "files": {"app1/main.py": None, "app1/nested/text.txt": None}},
            "app2": {"type": "app", "files": {"app2/main.py": None, "app2/other_content.txt": None, "app2/some_binary_file.gif": None}},
            "lib/lib1.py": {"type": "lib", "files": {"lib/lib1.py": None}},
            "shared/foo.txt": {"type": "shared", "files": {"shared/foo.txt": None}},
            "boot.py": {"type": "root", "files": {"boot.py": None}}
        }
        expected = {
            "app1": {
                'bootstraped': True,
                "type": "app",
                'categories': ['CategoryForApp1', 'SecondaryCategory'],
                'dependencies': ['lib/lib1.py', 'lib/lib3.py'],
                'description': 'Description of App1',
                'license': 'MIT',
                "files": {"app1/main.py": None, "app1/nested/text.txt": None}
            },
            "app2": {
                "type": "app",
                'bootstraped': True,
                'categories': ['CategoryForApp2', 'SecondaryCategory'],
                'dependencies': ['lib/lib2.py', 'lib/lib3.py'],
                'license': 'MIT',
                'description': 'Description of App2',
                "files": {"app2/main.py": None, "app2/other_content.txt": None, "app2/some_binary_file.gif": None}},
            "lib/lib1.py": {
                "type": "lib",
                'dependencies': ['lib/lib4.py'],
                'description': 'this is library 1',
                'license': 'MIT',
                "files": {"lib/lib1.py": None}
            },
            "shared/foo.txt": {"type": "shared", "files": {"shared/foo.txt": None}},
            "boot.py": {"type": "root", "files": {"boot.py": None}}
        }
        add_metadata(self.path, resources)
        self.assertEqual(resources, expected)

    def test_resolve_dependencies(self):
        resources = {
            "app1": {
                        "dependencies": ["lib/lib1.py"],
                        "files": {"app1/main.py": None, "app1/nested/text.txt": None}
                    },
            "app2": {"files": {"app2/main.py": None}},
            "lib/lib1.py": {"dependencies": ["shared/foo.txt", "lib/lib2.py"], "files": {"lib/lib1.py": None}},
            "lib/lib2.py": {"dependencies": ["shared/foo.txt", "lib/lib1.py"], "files": {"lib/lib2.py": None}},
            "shared/foo.txt": {"type": "shared", "files": {"shared/foo.txt": None}},
            "boot.py": {"type": "root", "files": {"boot.py": None}}
        }
        expected = {
            "app1": {
                "dependencies": ["lib/lib1.py"],
                "files": {"app1/main.py": None, "app1/nested/text.txt": None, "lib/lib1.py": None, "lib/lib2.py": None, "shared/foo.txt": None}
            },
            "app2": {"files": {"app2/main.py": None}},
            "lib/lib1.py": {"dependencies": ["shared/foo.txt", "lib/lib2.py"], "files": {"lib/lib1.py": None, "lib/lib2.py": None, "shared/foo.txt": None}},
            "lib/lib2.py": {"dependencies": ["shared/foo.txt", "lib/lib1.py"], "files": {"lib/lib1.py": None, "lib/lib2.py": None, "shared/foo.txt": None}},
            "shared/foo.txt": {"type": "shared", "files": {"shared/foo.txt": None}},
            "boot.py": {"type": "root", "files": {"boot.py": None}}
        }
        resolve_dependencies(resources)
        self.assertEqual(resources, expected)

    def test_resolve_dependencies_with_error(self):
        resources = {
            "app1": {
                        "dependencies": ["lib/lib1.py"],
                        "files": {"app1/main.py": None}
                    },
        }
        expected = {
            "app1": {
                "dependencies": ["lib/lib1.py"],
                "files": {"app1/main.py": None},
                'errors': ['Dependency lib/lib1.py not found']
            }
        }
        resolve_dependencies(resources)
        self.assertEqual(resources, expected)


if __name__ == '__main__':
    unittest.main()
