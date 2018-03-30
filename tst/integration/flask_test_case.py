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
        response = self.client.get(path)
        return json.loads(response.get_data(as_text=True))
