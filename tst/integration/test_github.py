import unittest
from app.models.github import Github
from unittest.mock import Mock
from app.models.invalid_usage import InvalidUsage


failing_commit = "a72c20ff"
success_commit = "992d00dc0"
success_branch = "success"
failing_pr_branch = "pr/1/merge"
repo = "emfcamp/Mk4-Apps"

class IntegrationTestGithub(unittest.TestCase):
    def setUp(self):
        self.mc = Mock()
        self.mc.get = Mock(return_value=None)
        self.github = Github(repo, self.mc)

    def test_invalid_repo(self):
        with self.assertRaises(InvalidUsage) as context:
            Github("ffff", self.mc)
        self.assertIn("Invalid repo", str(context.exception))

    def test_prs(self):
        prs = self.github.get_prs()
        self.assertTrue(len(prs) > 0)
