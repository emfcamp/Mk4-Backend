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
        data = self.get_json("/library?repo=%s&ref=%s" % (self.url, "d816b06e0c58b15a7453480d165020d784f9dde6"))
        self.assertEqual(set(data['errors']['homescreen/main.py']), set([
            "description metadata field is required but not found",
            "license metadata field is required but not found"
        ]))

    def test_check_checkout_with_error(self):
        data = self.get_json("/check?repo=%s&ref=%s" % (self.url, "d816b06e0c58b15a7453480d165020d784f9dde6"))
        self.assertEqual(set(data['errors']['homescreen/main.py']), set([
            "description metadata field is required but not found",
            "license metadata field is required but not found"
        ]))

    def test_check_succeed(self):
        data = self.get_json("/check?repo=%s&ref=%s" % (self.url, "description"))
        self.assertTrue(data['pass'])

    def test_checkout_with_different_branch(self):
        data = self.get_json("/library?repo=%s&ref=%s" % (self.url, "description"))
        self.assertEqual(data['apps']['app_library']['description'], "distinct description");

    def test_github_merge_commit(self):
        data = self.get_json("/check?repo=%s&ref=%s" % (self.url, "pr/1/merge"))
        self.assertTrue(data['errors']['my_new_app/main.py']);

    def test_repo_entry(self):
        data = self.get_json("/library?repo=%s&ref=%s" % (self.url, "36fb0a853292d61a96438e9c2a307eac1478c4cb"))
        self.assertEqual(data['apps']['app_library']['description'], 'updates and installs apps. To publish apps use https://badge.emfcamp.org')

    def test_categories(self):
        data = self.get_json("/apps?repo=%s&ref=%s" % (self.url, "36fb0a853292d61a96438e9c2a307eac1478c4cb"))
        self.assertEqual(data['Other'], ['home', 'sponsors'])

    def test_install(self):
        data = self.get_json("/install?repo=%s&ref=%s&apps=home,snake" % (self.url, "36fb0a853292d61a96438e9c2a307eac1478c4cb"))
        self.assertTrue('home' in data)
        self.assertTrue('snake' in data)
        self.assertEqual(data['home']['home/draw_name.py'], 'c35b3b81e4b3e1cea3d09409ed1309e3d211b988')

    def test_app_info(self):
        data = self.get_json("/app?repo=%s&ref=%s&app=snake" % (self.url, "36fb0a853292d61a96438e9c2a307eac1478c4cb"))
        self.assertEqual(data['description'], 'Snake!')


if __name__ == '__main__':
    unittest.main()
