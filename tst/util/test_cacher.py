from app.util.cacher import cacher
import unittest
from os.path import *
from uuid import uuid4

class TestCacher(unittest.TestCase):
    def setUp(self):
        self.args = []

    def test(self):
        func = cacher(self.f, str(uuid4()))
        self.assertEqual(func("xyz"), "xyz")
        self.assertEqual(func("xyz"), "xyz")
        self.assertEqual(func("abc"), "abc")
        self.assertEqual(len(self.args), 2)


    def test_namespace(self):
        func1 = cacher(self.f, str(uuid4()))
        func2 = cacher(self.f, str(uuid4()))
        self.assertEqual(func1("xyz"), "xyz")
        self.assertEqual(func2("xyz"), "xyz")
        self.assertEqual(len(self.args), 2)


    def f(self, a):
        self.args.append(a)
        return a

if __name__ == '__main__':
    unittest.main()
