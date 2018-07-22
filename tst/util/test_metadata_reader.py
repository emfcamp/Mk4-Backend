from app.util.metadata_reader import read_metadata, ParseException
import unittest, io

class TestHeaderReader(unittest.TestCase):
    def test_docstring_only(self):
        s = io.StringIO('''"""bar"""''')
        output = read_metadata(s)
        self.assertEqual(output, {'doc': "bar"})

    def test_docstring_with_leading_whitespace(self):
        s = io.StringIO('''  \t"""foo\nbar"""  \t\r\n''')
        output = read_metadata(s)
        self.assertEqual(output, {'doc': "foo\nbar"})

    def test_error_invalid_docstring(self):
        s = io.StringIO('''"not a docstring"''')
        with self.assertRaises(ParseException) as context:
            read_metadata(s)
        self.assertIn("Docstring delimiter expected", str(context.exception))

    def test_string_var(self):
        s = io.StringIO('''"""docstring""" \n ___foo___="bar"''')
        output = read_metadata(s)
        self.assertEqual(output, {'doc': "docstring", 'foo': 'bar'})

    def test_invalid_string(self):
        s = io.StringIO('''"""docstring""" \n ___string___ = "bar''')
        with self.assertRaises(ParseException) as context:
            output = read_metadata(s)
        self.assertIn("Invalid string or not terminated: bar", str(context.exception))

    def test_full_file(self):
        s = io.StringIO('''"""docstring""" \n ___foo___="bar"\n___other___='whatever'\n\nimport xyz # some comment''')
        output = read_metadata(s)
        self.assertEqual(output, {'doc': "docstring", 'foo': 'bar', 'other': 'whatever'})

    def test_invalid_key_not_balanced(self):
        s = io.StringIO('''"""docstring""" \n ___foo__="bar"''')
        with self.assertRaises(ParseException) as context:
            output = read_metadata(s)
        self.assertIn("Invalid key: ___foo__", str(context.exception))

    def test_invalid_key_early_quote(self):
        s = io.StringIO('''"""docstring""" \n ___foo="bar"''')
        with self.assertRaises(ParseException) as context:
            output = read_metadata(s)
        self.assertIn("Invalid key: ___foo", str(context.exception))

    def test_invalid_key_eof(self):
        s = io.StringIO('''"""docstring""" \n ___foobar''')
        with self.assertRaises(ParseException) as context:
            output = read_metadata(s)
        self.assertIn("Invalid key: ___foobar", str(context.exception))

    def test_int(self):
        s = io.StringIO('''"""docstring""" \n ___int___ = 123''')
        output = read_metadata(s)
        self.assertEqual(output, {'doc': "docstring", 'int': 123})

    def test_invalid_int(self):
        s = io.StringIO('''"""docstring""" \n ___int___ = 123k''')
        with self.assertRaises(ParseException) as context:
            output = read_metadata(s)
        self.assertIn("Invalid int: 123k", str(context.exception))

    def test_boolean(self):
        s = io.StringIO('''"""docstring""" \n ___yes___ = True\n___no___=False''')
        output = read_metadata(s)
        self.assertEqual(output, {'doc': "docstring", 'yes': True, 'no': False})

    def test_invalid_boolean(self):
        s = io.StringIO('''"""docstring""" \n ___yes___ = TRUE''')
        with self.assertRaises(ParseException) as context:
            output = read_metadata(s)
        self.assertIn("Invalid boolean ('True' expected, 'TRUE' found)", str(context.exception))

    def test_list_empty(self):
        s = io.StringIO('''"""docstring""" \n ___list___ = []''')
        output = read_metadata(s)
        self.assertEqual(output, {'doc': "docstring", 'list': []})

    def test_single_list_element(self):
        s = io.StringIO('''"""docstring""" \n ___list___ = ["foo"]''')
        output = read_metadata(s)
        self.assertEqual(output, {'doc': "docstring", 'list': ["foo"]})

    def test_complex_list(self):
        s = io.StringIO('''"""docstring""" \n ___list___ = ["foo", True, [], [False, 'bar']]''')
        output = read_metadata(s)
        self.assertEqual(output, {'doc': "docstring", 'list': ["foo", True, [], [False, "bar"]]})

    def test_invalid_list(self):
        s = io.StringIO('''"""docstring""" \n ___list___ = [[]''')
        with self.assertRaises(ParseException) as context:
            output = read_metadata(s)
        self.assertIn("Expected comma, got ''", str(context.exception))

    def test_invalid_list_with_missing_comma(self):
        s = io.StringIO('''"""docstring""" \n ___list___ = ["foo" "bar"]''')
        with self.assertRaises(ParseException) as context:
            output = read_metadata(s)
        self.assertIn("Expected comma, got '\"'", str(context.exception))

if __name__ == '__main__':
    unittest.main()
