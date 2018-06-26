from .flask_test_case import FlaskTestCase

import unittest

class IntegrationTestRepo(FlaskTestCase):
    def setUp(self):
        super(IntegrationTestRepo, self).setUp()
        self.url = "https://github.com/marekventur/emfcamp-2018-example-badge-store.git"

    def test_references(self):
        data = self.get_json("/repo/%s/" % self.url)
        self.assertEqual(set(data['refs']), set(['master', 'test-branch']))

    def test_checkout_with_error(self):
        data = self.get_json("/repo/%s/ref/%s" % (self.url, "d816b06e0c58b15a7453480d165020d784f9dde6"))
        self.assertEqual(set(data['errors']['homescreen/main.py']), set([
            "description metadata field is required but not found",
            "license metadata field is required but not found"
        ]))

    def test_repo_entry(self):
        data = self.get_json("/repo/%s/ref/%s" % (self.url, "36fb0a853292d61a96438e9c2a307eac1478c4cb"))
        self.assertEqual(data['apps']['app_library']['description'], 'updates and installs apps. To publish apps use https://badge.emfcamp.org')

    def test_categories(self):
        data = self.get_json("/repo/%s/ref/%s/categories/" % (self.url, "36fb0a853292d61a96438e9c2a307eac1478c4cb"))
        self.assertEqual(data['Other'], ['home', 'sponsors'])

    def test_install(self):
        data = self.get_json("/repo/%s/ref/%s/install/home,snake/" % (self.url, "36fb0a853292d61a96438e9c2a307eac1478c4cb"))
        self.assertTrue('home' in data)
        self.assertTrue('snake' in data)
        self.assertEqual(data['home']['home/draw_name.py'], 'c35b3b81e4b3e1cea3d09409ed1309e3d211b988')

    def test_app_info(self):
        data = self.get_json("/repo/%s/ref/%s/app/snake/" % (self.url, "36fb0a853292d61a96438e9c2a307eac1478c4cb"))
        self.assertEqual(data['description'], 'Snake!')




if __name__ == '__main__':
    unittest.main()
