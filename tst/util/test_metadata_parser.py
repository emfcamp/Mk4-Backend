from app.util.metadata_parser import MetadataParser
from app.util.validation_error import ValidationError
import unittest, os, shutil
from os.path import *

class TestMetadataParser (unittest.TestCase):
    def setUp(self):
        self.parser = MetadataParser()
        self.rules = {
            'description': {'type': 'string', 'required': True, 'min': 5, 'max': 20},
            'categories': {'type': 'list', 'required': True, 'min': 1, 'max': 3},
            'dependencies': {'type': 'list', 'default': [], 'max': 10},
            'built-in': {'type': 'boolean', 'default': False},
            'license': {'type': 'string'}
        }

    def test_parse_with_metadata(self):
        result = self.parser.parse_str("""### description: Description of App1
### categories: CategoryForApp1, SecondaryCategory
### dependencies: lib2, lib3

# A normal comment

print("###somepython")
""", "foo.py", self.rules)

        self.assertDictEqual(result, {
            'description': 'Description of App1',
            'categories': ['CategoryForApp1', 'SecondaryCategory'],
            'built-in': False,
            'dependencies': ['lib2', 'lib3']
        });

    def test_parse_string_too_short(self):
        result = self.parser.parse_str("""### description: s
### categories: CategoryForApp1, SecondaryCategory
### dependencies: lib2, lib3
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError("foo.py", "description metadata field has a minimum length of 5, provided: 1")
        ])

    def test_parse_string_too_long(self):
        result = self.parser.parse_str("""### description: aasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdf
### categories: CategoryForApp1, SecondaryCategory
### dependencies: lib2, lib3
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'description metadata field has a maximum length of 20, provided: 45')
        ])

    def test_parse_list_too_short(self):
        result = self.parser.parse_str("""### description: Some description
### categories:
### dependencies: lib2, lib3
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'categories metadata field has a minimum length of 1, provided: 0')
        ])

    def test_parse_list_too_long(self):
        result = self.parser.parse_str("""### description: Some description
### categories: c1,c2,c3,c4
### dependencies: lib2, lib3
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'categories metadata field has a maximum length of 3, provided: 4')
        ])

    def test_parse_list_too_long(self):
        result = self.parser.parse_str("""### description: Some description
### categories: c1,c2,c3,c4
### dependencies: lib2, lib3
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'categories metadata field has a maximum length of 3, provided: 4')
        ])

    def test_parse_default(self):
        result = self.parser.parse_str("""### description: Some description
### categories: c1
""", "foo.py", self.rules)
        self.assertEqual(result['dependencies'], [])

    def test_parse_boolean_yes(self):
        result = self.parser.parse_str("""### description: Some description
### categories: c1
### built-in: yes
""", "foo.py", self.rules)
        self.assertEqual(result['built-in'], True)

    def test_parse_boolean_no(self):
        result = self.parser.parse_str("""### description: Some description
### categories: c1
### built-in: NO
""", "foo.py", self.rules)
        self.assertEqual(result['built-in'], False)

    def test_parse_boolean_error(self):
        result = self.parser.parse_str("""### description: Some description
### categories: c1
### built-in: something
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'built-in metadata field has to be a boolean, please provide \'yes\' or \'no\'')
        ])

    def test_parse_required_error(self):
        result = self.parser.parse_str("""### description: Some description""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', 'categories metadata field is required but not found')
        ])

    def test_parse_invalid_field_error(self):
        result = self.parser.parse_str("""### description: Some description
### foo: something
### categories: c1
### built-in: NO
""", "foo.py", self.rules)
        self.assertEqual(result, [
            ValidationError('foo.py', "foo is not an allowed metadata field: ['built-in', 'categories', 'dependencies', 'description', 'license']")
        ])

    def test_parse_with_file(self):
        result = self.parser.parse(normpath(dirname(realpath(__file__)) + "/../fixtures/library/app1/main.py"), 'app1/main.py', self.rules)
        print(result)
        self.assertEqual(result['description'], 'Description of App1');


if __name__ == '__main__':
    unittest.main()
