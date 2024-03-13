# test_suite.py

import unittest
from ast_parser import remove_comments

class TestRemoveComments(unittest.TestCase):
    def test_remove_single_line_comment(self):
        source_code = 'print("Hello, world!")  # This is a comment'
        expected_output = 'print("Hello, world!")  '
        self.assertEqual(remove_comments(source_code), expected_output)

    def test_remove_multi_line_comment(self):
        source_code = '''
        def add(a, b):
            \"\"\"This is a docstring.\"\"\"
            return a + b  # This is a comment
        '''
        expected_output = '''
        def add(a, b):
            return a + b  
        '''
        self.assertEqual(remove_comments(source_code), expected_output)

    def test_remove_mixed_comments(self):
        source_code = '''
        # This is a single-line comment
        def subtract(a, b):
            \"\"\"This is a docstring.\"\"\"
            # This is another single-line comment
            return a - b  # This is a comment
        '''
        expected_output = '''
        
        def subtract(a, b):
            return a - b  
        '''
        self.assertEqual(remove_comments(source_code), expected_output)

    def test_no_comments(self):
        source_code = 'print("No comments here")'
        expected_output = 'print("No comments here")'
        self.assertEqual(remove_comments(source_code), expected_output)

if __name__ == '__main__':
    unittest.main()