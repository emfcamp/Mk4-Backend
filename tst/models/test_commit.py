from app.models.repository import Repository
import unittest, os, shutil
from unittest.mock import Mock
from ..fixtures.fake_git import FakeGit

class TestCommit (unittest.TestCase):
    def setUp(self):
        self.fake_git = FakeGit()

        self.mc = Mock()
        self.mc.get = Mock(return_value=None)

        self.repo = Repository(self.fake_git.url, mc=self.mc)

        self.commit_id = "886cca8f867919bc02955c763e7f5108b33084b6"
        self.commit = self.repo.get_commit(self.commit_id)

    def notearDown(self):
        shutil.rmtree(self.repo.path)
        self.fake_git.clean_up()
        self.commit.clean_up()

    def test_id(self):
        self.assertEqual(self.commit.id, self.commit_id)

    def test_fetch(self):
        self.commit.fetch()
        self.assertTrue(os.path.exists(self.commit.path + "/file_1.md"));

if __name__ == '__main__':
    unittest.main()
