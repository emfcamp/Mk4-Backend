from app.util.sizer import Sizer
import shutil, tempfile, os
from unittest.mock import Mock
import unittest

class TestSizer(unittest.TestCase):
    def setUp(self):
        self.mc = Mock()
        self.mc.get = Mock(return_value=None)
        self.sizer = Sizer(self.mc)

    def test_default_relative_path(self):
        path = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + "/../fixtures/library/app1/main.py")
        self.assertEqual(self.sizer.get_size(path), 320)

if __name__ == '__main__':
    unittest.main()
