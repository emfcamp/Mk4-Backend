from .flask_test_case import FlaskTestCase

import unittest

class IntegrationTestIndex(FlaskTestCase):
    def test_root(self):
        data = self.get_json("/")
        assert data['hello'] == 'world'


if __name__ == '__main__':
    unittest.main()
