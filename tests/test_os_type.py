from unittest import TestCase

from hed_utils.support import os_type


class OsTypeTest(TestCase):

    def test_only_one_os_type_is_true(self):
        answers = list()
        answers.append(os_type.is_windows())
        answers.append(os_type.is_linux())
        answers.append(os_type.is_mac())
        positive_count = len([b for b in answers if b])
        self.assertEqual(positive_count, 1)

    def test_get_current(self):
        self.assertTrue(os_type.is_64bit())
        self.assertIn(os_type.get_current(), [os_type.LINUX, os_type.WINDOWS, os_type.MAC_OS])
