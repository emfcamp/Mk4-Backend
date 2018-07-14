from .flask_test_case import FlaskTestCase

import unittest

class IntegrationTestHttp(FlaskTestCase):
    def setUp(self):
        super(IntegrationTestHttp, self).setUp()
        self.url = "marekventur/emfcamp-2018-example-badge-store"

    def test_references(self):
        data = self.get_json("/refs?repo=%s" % self.url)
        self.assertTrue("master" in data['refs'])
        self.assertTrue("test-branch" in data['refs'])

    def test_refs_checkout_with_error(self):
        data = self.get_json("/library?repo=%s&ref=%s" % (self.url, "01d7e3f"))
        self.assertEqual(set(data['errors']['home/main.py']), set([
            "docstring metadata field is required but not found"
        ]))

    def test_check_checkout_with_error(self):
        data = self.get_json("/check?repo=%s&ref=%s" % (self.url, "01d7e3f"))
        self.assertEqual(set(data['errors']['home/main.py']), set([
            "docstring metadata field is required but not found"
        ]))

    def test_check_succeed(self):
        data = self.get_json("/check?repo=%s&ref=%s" % (self.url, "successful-pr"))
        self.assertTrue(data['pass'])

    def test_checkout_with_different_branch(self):
        data = self.get_json("/library?repo=%s&ref=%s" % (self.url, "successful-pr"))
        self.assertEqual(data['apps']['my_game']['docstring'], "My game");

    def test_github_merge_commit(self):
        data = self.get_json("/check?repo=%s&ref=%s" % (self.url, "pr/1/merge"))
        self.assertTrue(data['errors']['home/main.py']);

    def test_repo_entry(self):
        data = self.get_json("/library?repo=%s&ref=%s" % (self.url, "52d8ded"))
        self.assertEqual(data['apps']['app_library']['docstring'], 'updates and installs apps. To publish apps use https://badge.emfcamp.org')

    def test_categories(self):
        data = self.get_json("/apps?repo=%s&ref=%s" % (self.url, "52d8ded"))
        self.assertEqual(set(data['Other']), set(['home', 'sponsors']))

    def test_install(self):
        data = self.get_json("/install?repo=%s&ref=%s&apps=home,snake" % (self.url, "52d8ded"))
        self.assertTrue('home' in data)
        self.assertTrue('snake' in data)
        self.assertEqual(data['home']['home/draw_name.py'], 'c35b3b81e4b3e1cea3d09409ed1309e3d211b988')

    def test_app_info(self):
        data = self.get_json("/app?repo=%s&ref=%s&app=snake" % (self.url, "52d8ded"))
        print(data)
        self.assertEqual(data['docstring'], 'Snake!')


if __name__ == '__main__':
    unittest.main()
