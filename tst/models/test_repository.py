from app.models.repository import Repository

import unittest
from unittest.mock import Mock

class TestRepository(unittest.TestCase):
    def setUp(self):
        self.test_repo_url = "https://github.com/Objectway/gittology.git"

        self.mc = Mock()
        self.mc.get = Mock(return_value=None)

        self.repo = Repository(self.test_repo_url, mc=self.mc)

    def test_url(self):
        self.assertEqual(self.repo.url, self.test_repo_url)

    def test_list_references(self):
        references = self.repo.list_references()
        self.assertEqual(references['merge-master'], '886cca8f867919bc02955c763e7f5108b33084b6')
        mc_key = "repository_list_refererences::" + self.test_repo_url
        self.mc.get.assert_called_once_with(mc_key)
        self.mc.set.assert_called_once_with(mc_key, references, time=60)

    def test_uses_cache_result(self):
        fake_result = {"foo": "bar"}
        self.mc.get = Mock(return_value=fake_result)
        references = self.repo.list_references()
        self.assertEqual(references, fake_result)

    def test_path_name(self):
        other_repo = Repository(self.test_repo_url)
        self.assertEqual(self.repo.get_path_name(), other_repo.get_path_name())

if __name__ == '__main__':
    unittest.main()
