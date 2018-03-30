from app.models.repository import Repository
import unittest, os, shutil
from unittest.mock import Mock
from ..fixtures.fake_git import FakeGit

class TestCommit (unittest.TestCase):
    def setUp(self):
        self.fake_git = FakeGit()
        self.test_repo_url = self.fake_git.url

        self.mc = Mock()
        self.mc.get = Mock(return_value=None)

        self.repo = Repository(self.test_repo_url, mc=self.mc)

        self.commit_id = "886cca8f867919bc02955c763e7f5108b33084b6"
        self.commit = self.repo.get_commit(self.commit_id)

    def tearDown(self):
        shutil.rmtree(self.repo.get_cached_folder())
        self.fake_git.clean_up()
        self.commit.clean()

    def test_id(self):
        self.assertEqual(self.commit.id, self.commit_id)

    def test_ensure_existence(self):
        # todo test a bit more here
        self.commit.ensure_existence()

    def test_hashes(self):
        hashes = self.commit.get_all_hashes()
        self.assertEqual(hashes, {
            'LICENSE': 'b176e168b20889bb9750bc10dcd4db95dcd85a41',
            'README.md': '7e206a016e3263291cc62fb1c16064f78b741afb',
            'file_1.md': '6200a5d509f1a7914cc94275142303a74b29ca2b',
            'file_2.md': '25326dbf01ec122b03cbd769edb29ecc52e3d25c',
            'file_3.md': 'b6364754202b2cb66237735fbc97aaf886fedf36'
        })
        mc_key = "commit_all_hashes::" + self.commit_id
        self.mc.get.assert_any_call(mc_key)
        self.mc.set.assert_any_call(mc_key, hashes)

    def test_hashes_uses_cached_result(self):
        def side_effect(key):
            if key == "commit_all_hashes::" + self.commit_id:
                return {"foo": "bar"}
            return None
        self.mc.get = Mock(side_effect=side_effect)
        commit = self.repo.get_commit(self.commit_id)
        hashes = commit.get_all_hashes()
        self.assertEqual(hashes, {'foo': 'bar'})

if __name__ == '__main__':
    unittest.main()
