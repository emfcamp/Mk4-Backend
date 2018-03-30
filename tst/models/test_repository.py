from app.models.repository import Repository
import unittest, os, shutil
from unittest.mock import Mock
from ..fixtures.fake_git import FakeGit

class TestRepository(unittest.TestCase):
    def setUp(self):
        self.fake_git = FakeGit()
        self.test_repo_url = self.fake_git.url

        self.mc = Mock()
        self.mc.get = Mock(return_value=None)

        self.repo = Repository(self.test_repo_url, mc=self.mc)

    def tearDown(self):
        shutil.rmtree(self.repo.get_cached_folder())
        self.fake_git.clean_up()

    def test_url(self):
        self.assertEqual(self.repo.url, self.test_repo_url)

    def test_update_creates_git_directory(self):
        self.repo.update()
        self.assertEqual(os.path.isdir(self.repo.get_cached_folder() + "/.git"), True)

    def test_update_bails_if_called_recently(self):
        self.mc.get = Mock(return_value="foo")
        self.repo.update()
        self.assertEqual(os.path.isdir(self.repo.get_cached_folder() + "/.git"), False)

    def test_update_failure(self):
        self.repo = Repository("https://github.com/does/not/exist.git", mc=self.mc)
        with self.assertRaises(Exception) as context:
            self.repo.update()
        self.assertEqual('Repository https://github.com/does/not/exist.git is unavailable or invalid', str(context.exception))

    def test_list_references(self):
        references = self.repo.list_references()
        self.assertEqual(set(references), set(['merge-master', "master", "merge-standard", "merge-conflict"]))

    def test_path_name(self):
        other_repo = Repository(self.test_repo_url)
        self.assertEqual(self.repo.get_path_name(), other_repo.get_path_name())

    def test_get_commit_with_branch(self):
        references = self.repo.get_commit("merge-master")
        self.assertEqual(references.id, "886cca8f867919bc02955c763e7f5108b33084b6")

    def test_get_commit_with_full_hash(self):
        references = self.repo.get_commit("886cca8f867919bc02955c763e7f5108b33084b6")
        self.assertEqual(references.id, "886cca8f867919bc02955c763e7f5108b33084b6")

    def test_get_commit_with_partial_hash(self):
        references = self.repo.get_commit("886cc")
        self.assertEqual(references.id, "886cca8f867919bc02955c763e7f5108b33084b6")

    def test_get_commit_failure(self):
        with self.assertRaises(Exception) as context:
            self.repo.get_commit("ffffff")
        self.assertIn('Reference ffffff not found', str(context.exception))

if __name__ == '__main__':
    unittest.main()
