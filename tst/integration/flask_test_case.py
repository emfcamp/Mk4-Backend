from main import app
import unittest
import json

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        None

    def get_json(self, path):
        return json.loads(self.get(path))

    def get(self, path):
        return self.client.get(path).get_data(as_text=True)
