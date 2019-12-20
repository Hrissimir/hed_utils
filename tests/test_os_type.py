from unittest import TestCase

from hed_utils.support.os_type import OsType


class OsTypeTest(TestCase):

    def test_only_one_os_type_is_true(self):
        answers = list()
        answers.append(OsType.is_windows())
        answers.append(OsType.is_linux())
        answers.append(OsType.is_mac())
        positive_count = len([b for b in answers if b])
        self.assertEqual(positive_count, 1)

    def test_get_current(self):
        self.assertIn(OsType.get_current(), OsType)
        self.assertTrue(OsType.is_64bit())
