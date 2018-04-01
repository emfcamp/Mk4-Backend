from app.util.hasher import Hasher
import unittest, os, shutil
from unittest.mock import Mock
from ..fixtures.fake_git import FakeGit

class TestHasher(unittest.TestCase):
    def setUp(self):
        self.mc = Mock()
        self.mc.get = Mock(return_value=None)

        self.hasher = Hasher(self.mc)
        self.test_path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/../fixtures/library")
        self.mc_key = "get_hashes::" + self.test_path

    def test_hashes(self):
        hashes = self.hasher.get_hashes(self.test_path)
        self.assertEqual(hashes['app2/other_content.txt'], 'b23ba9792bd3944aa8c52c0e25351bf9e6641d74')
        self.assertEqual(len(hashes), 9)

        self.mc.get.assert_any_call(self.mc_key)
        self.mc.set.assert_any_call(self.mc_key, hashes)

    def test_hashes_uses_cached_result(self):
        def side_effect(key):
            if key == self.mc_key:
                return {"foo": "bar"}
            return None
        self.mc.get = Mock(side_effect=side_effect)
        hashes = self.hasher.get_hashes(self.test_path)
        self.assertEqual(hashes, {'foo': 'bar'})

if __name__ == '__main__':
    unittest.main()
