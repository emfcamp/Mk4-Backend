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


if __name__ == '__main__':
    unittest.main()
