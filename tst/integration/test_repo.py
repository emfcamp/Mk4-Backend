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
        self.assertEqual(data['errors'][0], {
            "message": "description metadata field is required but not found",
            "name": "updater/main.py"
        })


if __name__ == '__main__':
    unittest.main()
