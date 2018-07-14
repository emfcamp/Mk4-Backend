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

    def test_scan_uses_memcache_to_avoid_double_processing(self):
        self.mc.get = Mock(return_value=[{'foo':1}, {'bar': 2}, None])
        self.library.scan()
        self.mc.get.assert_called_once_with("library_parse::abc")
        self.assertEqual(self.library.apps, {'foo':1})
        self.assertEqual(self.library.dependencies, {'bar':2})


    def test_scan_calls_hasher_with_correct_parameters(self):
        self.hasher.get_hashes = Mock(return_value={})
        self.library.scan()
        self.hasher.get_hashes.assert_called_once_with(self.path)

    def test_scan_happy_path(self):
        self.hasher.get_hashes = Mock(return_value={
            'app1/main.py': 'abc1',
            'app1/something.gif': 'abc2',
            'app2/main.py': 'abc3',
            'lib/my-lib.py': 'abc4',
            'lib/other-lib.py': 'cde5',
            'shared/some_file.txt': 'ffff'
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
                    'dependencies': ['my-lib', 'other-lib', "shared/some_file.txt"],
                    'built-in': False
                }
            if args[0] == '/some/path/lib/my-lib.py':
                return {
                    'description': 'my-lib',
                    'dependencies': ['lib/other-lib.py']
                }
            if args[0] == '/some/path/lib/other-lib.py':
                return {
                    'description': 'other-lib',
                    'dependencies': []
                }
        self.metadata_parser.parse = Mock(side_effect=metadata_side_effect)
        self.library.scan()
        self.assertEqual(self.library.dependencies, {
            'lib/my-lib.py': {
                'dependencies': ['lib/other-lib.py'],
                'description': 'my-lib',
                'hash': 'abc4',
                'size': 101,
                'files': {'lib/my-lib.py': 'abc4', 'lib/other-lib.py': 'cde5'}
            },
            'lib/other-lib.py': {
                'dependencies': [],
                'description': 'other-lib',
                'hash': 'cde5',
                'size': 101,
                'files': {'lib/other-lib.py': 'cde5'}
            },
            'shared/some_file.txt': {
                'dependencies': [],
                'hash': 'ffff',
                'size': 101,
                'files': {'shared/some_file.txt': 'ffff'}
            }
        })
        self.assertEqual(self.library.apps, {
            'app1': {
                'dependencies': ['lib/my-lib.py'],
                'description': 'foo1',
                'built-in': True,
                'size': 202,
                'files': {
                    'app1/main.py': 'abc1',
                    'app1/something.gif': 'abc2',
                    'lib/my-lib.py': 'abc4',
                    'lib/other-lib.py': 'cde5'
                },
            },
            'app2': {
                'dependencies': ['lib/my-lib.py', 'lib/other-lib.py', 'shared/some_file.txt'],
                'description': 'foo2',
                'built-in': False,
                'size': 101,
                'files': {
                    'app2/main.py': 'abc3',
                    'lib/my-lib.py': 'abc4',
                    'lib/other-lib.py': 'cde5',
                    'shared/some_file.txt': 'ffff'
                }
            }
        })

        self.sizer.get_size.assert_any_call('/some/path/lib/other-lib.py')
        self.sizer.get_size.assert_any_call('/some/path/lib/my-lib.py')
        self.sizer.get_size.assert_any_call('/some/path/app1/main.py')
        self.sizer.get_size.assert_any_call('/some/path/app1/something.gif')
        self.sizer.get_size.assert_any_call('/some/path/app2/main.py')
        self.mc.set.assert_called_once_with("library_parse::abc", [self.library.apps, self.library.dependencies, None])

    def test_scan_lib_depency_failure(self):
        self.hasher.get_hashes = Mock(return_value={
            'lib/my-lib.py': 'abc4'
        })
        def metadata_side_effect(*args, **kwargs):
            if args[0] == '/some/path/lib/my-lib.py':
                return {
                    'description': 'fail',
                    'dependencies': ['lib/some-unkown-lib.py']
                }
        self.metadata_parser.parse = Mock(side_effect=metadata_side_effect)
        self.library.scan()
        self.assertSequenceEqual(self.library.errors, [
            ValidationError('lib/my-lib.py', "Dependencies not found: ['lib/some-unkown-lib.py']")
        ])

    def test_scan_app_main_file_not_found(self):
        self.hasher.get_hashes = Mock(return_value={
            'app1/mainx.py': 'abc4'
        })
        def metadata_side_effect(*args, **kwargs):
            if args[0] == '/some/path/app1/main.py':
                return {
                    'description': 'fail',
                    'dependencies': ['some-unkown-lib']
                }
        self.metadata_parser.parse = Mock(side_effect=metadata_side_effect)
        self.library.scan()
        self.assertSequenceEqual(self.library.errors, [
            ValidationError('app1/main.py', 'main.py file not provided')
        ])

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
        self.library.scan()
        self.assertSequenceEqual(self.library.errors, [
            ValidationError('app1/main.py', "Dependency not found: lib/some-unkown-lib.py")
        ])

    def test_scan_app_size_failure(self):
        self.hasher.get_hashes = Mock(return_value={
            'app1/main.py': 'abc4'
        })
        def metadata_side_effect(*args, **kwargs):
            if args[0] == '/some/path/app1/main.py':
                return {
                    'description': 'foo',
                    'dependencies': []
                }
        self.metadata_parser.parse = Mock(side_effect=metadata_side_effect)
        self.sizer.get_size = Mock(return_value=999999999)
        self.library.scan()
        self.assertSequenceEqual(self.library.errors, [
            ValidationError('app1/main.py', 'App app1 is a total of 999999999 bytes, allowed maximum is 30000')
        ])

    def test_scan_invalid_path(self):
        self.hasher.get_hashes = Mock(return_value={
            'app1/ma$in.py': 'abc'
        })
        self.library.scan()
        self.assertSequenceEqual(self.library.errors, [
            ValidationError('app1/ma$in.py', 'Invalid path')
        ])

    def test_compact_errors(self):
        self.library.errors = [
            ValidationError('foo.py', 'error1'),
            ValidationError('bar.py', 'error2'),
            ValidationError('foo.py', 'error3')
        ]
        self.assertEqual(self.library.get_compact_errors(), {'foo.py': ['error1', 'error3'], 'bar.py': ['error2']})

    def test_get_apps_by_category(self):
        self.library.apps = {
            'app1': {'categories': ["bar", "foo"]},
            'app2': {'categories': ["bar"]},
            'app3': {}
        }
        result = self.library.get_apps_by_category()

        self.assertCountEqual(result['bar'], ['app1', 'app2'])
        self.assertCountEqual(result['foo'], ['app1'])


if __name__ == '__main__':
    unittest.main()
