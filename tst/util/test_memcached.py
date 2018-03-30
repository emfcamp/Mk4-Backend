from app.util import memcached
import unittest
import uuid

class TestMemcached(unittest.TestCase):
    def test_set_then_get(self):
        val = uuid.uuid4().hex
        memcached.shared.set("a", val)
        self.assertEqual(memcached.shared.get("a"), val)

if __name__ == '__main__':
    unittest.main()
