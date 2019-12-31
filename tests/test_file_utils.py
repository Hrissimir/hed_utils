from unittest import TestCase

from hed_utils.support.file_utils import file_sys


class FileSysTest(TestCase):
    def test_format_size(self):
        self.assertEqual(file_sys.format_size(10000), "9.8K")
        self.assertEqual(file_sys.format_size(100001221), "95.4M")
        self.assertEqual(file_sys.format_size(2), "2B")
