from .flask_test_case import FlaskTestCase

import unittest

class IntegrationTestRepo(FlaskTestCase):

    def setUp(self):
        super(IntegrationTestRepo, self).setUp()
        self.url = "https://github.com/marekventur/emfcamp-2018-example-badge-store.git"

    def test_references(self):
        data = self.get_json("/repo/%s/" % self.url)
        assert data['refs'] == ['master', 'test-branch']


if __name__ == '__main__':
    unittest.main()
