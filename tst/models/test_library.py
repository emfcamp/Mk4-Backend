from app.models.library import Library
from app.util.validation_error import ValidationError
import unittest, os, shutil
from unittest.mock import Mock
from ..fixtures.fake_git import FakeGit
from os.path import *

class TestLibrary(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 10000

        self.mc = Mock()
        self.mc.get = Mock(return_value=None)

        self.hasher = Mock()
        self.metadata_parser = Mock()
        self.sizer = Mock()
        self.sizer.get_size = Mock(return_value=101)

        self.commit_id = "abc"
        self.path = "/some/path"
        self.library = Library(self.commit_id, self.path, mc=self.mc, hasher=self.hasher, metadata_parser=self.metadata_parser, sizer=self.sizer)

    def test_scan_calls_hasher_with_correct_parameters(self):
        self.hasher.get_hashes = Mock(return_value={})
        #self.metadata_parser.parse =
        self.library.scan()

        self.hasher.get_hashes.assert_called_once_with(self.path)

    def test_scan_happy_path(self):
        self.hasher.get_hashes = Mock(return_value={
            'app1/main.py': 'abc1',
            'app1/something.gif': 'abc2',
            'app2/main.py': 'abc3',
            'libs/my-lib.py': 'abc4',
            'libs/other-lib.py': 'cde5'
        })
        def metadata_side_effect(*args, **kwargs):
            if args[0] == '/some/path/app1/main.py':
                return {
                    'description': 'foo1',
                    'dependencies': ['my-lib'],
                    'built-in': True
                }
            if args[0] == '/some/path/app2/main.py':
                return {
                    'description': 'foo2',
                    'dependencies': ['my-lib', 'other-lib'],
                    'built-in': False
                }
            if args[0] == '/some/path/libs/my-lib.py':
                return {
                    'description': 'my-lib',
                    'dependencies': ['other-lib']
                }
            if args[0] == '/some/path/libs/other-lib.py':
                return {
                    'description': 'other-lib',
                    'dependencies': []
                }
        self.metadata_parser.parse = Mock(side_effect=metadata_side_effect)
        self.library.scan()
        self.assertEqual(self.library.libs, {
            'my-lib': {
                'dependencies': ['other-lib'],
                'description': 'my-lib',
                'hash': 'abc4',
                'size': 101,
                'files': {'libs/my-lib.py': 'abc4', 'libs/other-lib.py': 'cde5'}
            },
            'other-lib': {
                'dependencies': [],
                'description': 'other-lib',
                'hash': 'cde5',
                'size': 101,
                'files': {'libs/other-lib.py': 'cde5'}
            }
        })
        self.assertEqual(self.library.apps, {
            'app1': {
                'dependencies': ['my-lib'],
                'description': 'foo1',
                'built-in': True,
                'size': 202,
                'files': {
                    'app1/main.py': 'abc1',
                    'app1/something.gif': 'abc2',
                    'libs/my-lib.py': 'abc4',
                    'libs/other-lib.py': 'cde5'
                },
            },
            'app2': {
                'dependencies': ['my-lib', 'other-lib'],
                'description': 'foo2',
                'built-in': False,
                'size': 101,
                'files': {
                    'app2/main.py': 'abc3',
                    'libs/my-lib.py': 'abc4',
                    'libs/other-lib.py': 'cde5'
                }
            }
        })

        self.sizer.get_size.assert_any_call('/some/path/libs/other-lib.py')
        self.sizer.get_size.assert_any_call('/some/path/libs/my-lib.py')
        self.sizer.get_size.assert_any_call('/some/path/app1/main.py')
        self.sizer.get_size.assert_any_call('/some/path/app1/something.gif')
        self.sizer.get_size.assert_any_call('/some/path/app2/main.py')

    def test_scan_lib_depency_failure(self):
        self.hasher.get_hashes = Mock(return_value={
            'libs/my-lib.py': 'abc4'
        })
        def metadata_side_effect(*args, **kwargs):
            if args[0] == '/some/path/libs/my-lib.py':
                return {
                    'description': 'fail',
                    'dependencies': ['some-unkown-lib']
                }
        self.metadata_parser.parse = Mock(side_effect=metadata_side_effect)
        with self.assertRaisesRegexp(ValidationError, 'Validation Error for libs/my-lib.py: Dependency not found: some-unkown-lib'):
            self.library.scan()

    def test_scan_app_depency_failure(self):
        self.hasher.get_hashes = Mock(return_value={
            'app1/main.py': 'abc4'
        })
        def metadata_side_effect(*args, **kwargs):
            if args[0] == '/some/path/app1/main.py':
                return {
                    'description': 'fail',
                    'dependencies': ['some-unkown-lib']
                }
        self.metadata_parser.parse = Mock(side_effect=metadata_side_effect)
        with self.assertRaisesRegexp(ValidationError, 'Validation Error for app1/main.py: Dependency not found: some-unkown-lib'):
            self.library.scan()

    def test_scan_app_size_failure(self):
        self.hasher.get_hashes = Mock(return_value={
            'app1/main.py': 'abc4'
        })
        def metadata_side_effect(*args, **kwargs):
            if args[0] == '/some/path/app1/main.py':
                return {
                    'description': 'fail',
                    'dependencies': ['some-unkown-lib']
                }
        self.metadata_parser.parse = Mock(side_effect=metadata_side_effect)
        self.sizer.get_size = Mock(return_value=4004)
        with self.assertRaisesRegexp(ValidationError, 'Validation Error for app1/main.py: App app1 is a total of 4004 bytes, allowed maximum is 4000'):
            self.library.scan()

    def test_scan_validation_lib_filename(self):
        self.hasher.get_hashes = Mock(return_value={
            'libs/invalid.pyx': 'abc'
        })
        with self.assertRaisesRegexp(ValidationError, 'Validation Error for libs/invalid.pyx: Library file validation failed: libs/invalid.pyx is not a valid library file name'):
            self.library.scan()

    def test_scan_invalid_path(self):
        self.hasher.get_hashes = Mock(return_value={
            'app1/ma$in.py': 'abc'
        })
        with self.assertRaisesRegexp(ValidationError, 'Validation Error for app1/ma\$in.py: Invalid path'):
            self.library.scan()

if __name__ == '__main__':
    unittest.main()
