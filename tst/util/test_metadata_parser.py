from app.util.metadata_parser import MetadataParser
from app.util.validation_error import ValidationError
import unittest, os, shutil
from os.path import *

class TestMetadataParser (unittest.TestCase):
    def setUp(self):
        self.parser = MetadataParser()
        self.rules = {
            'docstring': {'type': 'docstring', 'min': 5, 'max': 20},
            'license': {'type': 'string'},
            'categories': {'type': 'list', 'required': True, 'min': 1, 'max': 3},
            'dependencies': {'type': 'list', 'default': [], 'max': 10},
            'launchable': {'type': 'boolean', 'default': True},
            'bootstrapped': {'type': 'boolean', 'default': False}
        }

    def test_parse_with_metadata(self):
        result = self.parser.parse_str("""\"\"\"Line1
Line2\"\"\"
___categories___   = ["CategoryForApp1", "SecondaryCategory"]
___dependencies___ = ["lib2", "lib3"]
___license___      = "MIT"

\"\"\" Not a docstring\"\"\"
# A normal comment

print("###somepython")
""", "foo.py", self.rules)

        self.assertDictEqual(result, {
            'docstring': 'Line1\nLine2',
            'categories': ['CategoryForApp1', 'SecondaryCategory'],
            'launchable': True,
            'bootstrapped': False,
            'license': "MIT",
            'dependencies': ['lib2', 'lib3']
        });

    def test_parse_string_too_short(self):
        result = self.parser.parse_str("""\"\"\"s\"\"\"
___categories___ = ["CategoryForApp1", "SecondaryCategory"]
___dependencies___ = ["lib2", "lib3"]
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError("foo.py", "docstring metadata field has a minimum length of 5, provided: 1")
        ])

    def test_parse_string_too_long(self):
        result = self.parser.parse_str("""\"\"\"aasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdf\"\"\"
___categories___ = ["CategoryForApp1", "SecondaryCategory"]
___dependencies___ = ["lib2", "lib3"]
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'docstring metadata field has a maximum length of 20, provided: 45')
        ])

    def test_parse_list_too_short(self):
        result = self.parser.parse_str("""\"\"\"Some description\"\"\"
___categories___ = []
___dependencies___ = ["lib2", "lib3"]
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'categories metadata field has a minimum length of 1, provided: 0')
        ])

    def test_parse_list_too_long(self):
        result = self.parser.parse_str("""\"\"\"Some description\"\"\"
___categories___ = ["c1", "c2", "c3", "c4"]
___dependencies___ = ["lib2", "lib3"]
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'categories metadata field has a maximum length of 3, provided: 4')
        ])

    def test_parse_list_not_string(self):
        result = self.parser.parse_str("""\"\"\"Some description\"\"\"
___categories___ = ["c1", True]
___dependencies___ = ["lib2", "lib3"]
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'categories metadata list element True has to be a string (surrounded by quotes)')
        ])

    def test_parse_default(self):
        result = self.parser.parse_str("""\"\"\"Some description\"\"\"
___categories___ = ["c1"]
""", "foo.py", self.rules)
        self.assertEqual(result['dependencies'], [])

    def test_parse_boolean_yes(self):
        result = self.parser.parse_str("""\"\"\"Some description\"\"\"
___categories___ = ["c1"]
___launchable___ = True
""", "foo.py", self.rules)
        self.assertEqual(result['launchable'], True)

    def test_parse_boolean_no(self):
        result = self.parser.parse_str("""\"\"\"Some description\"\"\"
___categories___ = ["c1"]
___launchable___ = False
""", "foo.py", self.rules)
        self.assertEqual(result['launchable'], False)

    def test_parse_boolean_error(self):
        result = self.parser.parse_str("""\"\"\"Some description\"\"\"
___categories___ = ["c1"]
___launchable___ = something
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'launchable metadata field has to be a boolean, please provide \'True\' or \'False\'')
        ])

    def test_parse_required_error(self):
        result = self.parser.parse_str("""\"\"\"Some description\"\"\"""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'categories metadata field is required but not found')
        ])


if __name__ == '__main__':
    unittest.main()
