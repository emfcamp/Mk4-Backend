from app.util.validation_error import ValidationError
import unittest

class TestValidationError(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(ValidationError("foo.py", "error"), ValidationError("foo.py", "error"))
        self.assertNotEqual(ValidationError("foo.py", "error"), ValidationError("foo2.py", "error"))
        self.assertNotEqual(ValidationError("foo.py", "error"), ValidationError("foo.py", "error2"))

    def test_string(self):
        self.assertEqual(str(ValidationError("foo.py", "error")), "Validation Error for foo.py: error")


if __name__ == '__main__':
    unittest.main()
