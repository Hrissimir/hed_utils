"""Unit-tests for module hed_utils.support.checked_param"""
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional
from unittest import TestCase

from hed_utils.support.checked_param import file_path
from hed_utils.support.checked_param import string_value


class StringValueTest(TestCase):
    """Unit tests for the checked_param.string_value method."""

    def test_bad_type(self):
        """Verify error is raised if value is having bad type."""

        name = "bad_type"
        value = object()
        with self.assertRaises(TypeError) as ctx:
            string_value(name, value)  # noqa
        self.assertTupleEqual((name, str, object), ctx.exception.args)

    def test_empty_ok_true(self):
        """Verify NO error is raised if value is empty and empty_ok == True."""

        param_name = "empty-but-ok"
        param_value = ""
        self.assertEqual("", string_value(param_name, param_value))

    def test_empty_ok_false(self):
        """Verify error is raised if value is empty and empty_ok == False."""

        param_name = "empty-but-not-ok"
        with self.assertRaises(ValueError) as ctx:
            string_value(param_name, "", empty_ok=False)
        self.assertTupleEqual((param_name, ""), ctx.exception.args)

        with self.assertRaises(ValueError) as ctx:
            string_value(
                param_name,
                " \t \n ",
                strip_whitespace=False,
                empty_ok=False
            )
        self.assertTupleEqual((param_name, " \t \n "), ctx.exception.args)

    def test_none_ok_true(self):
        """Verify NO error is raised if value is None and none_ok == True."""

        param_name = "none-but-ok"
        param_value = None
        self.assertIsNone(string_value(param_name, param_value, none_ok=True))

    def test_none_ok_false(self):
        """Verify error is raised if value is None and none_ok == False."""

        param_name = "none-but-not-ok"
        param_value = None
        with self.assertRaises(TypeError) as ctx:
            string_value(param_name, param_value, none_ok=False)
        self.assertTupleEqual((param_name, str, type(None)), ctx.exception.args)

    def test_strip_whitespace_true(self):
        """Verify value is stripped when strip_whitespace == True."""

        param_name = "whitespace-and-stripped"
        param_value = " \n \r \t "
        result = string_value(param_name, param_value, strip_whitespace=True)
        self.assertEqual("", result)
        with self.assertRaises(ValueError) as ctx:
            string_value(
                param_name, param_value, strip_whitespace=True, empty_ok=False
            )
        self.assertTupleEqual((param_name, param_value), ctx.exception.args)

    def test_strip_whitespace_false(self):
        """Verify value is not stripped when strip_whitespace == False."""

        param_name = "whitespace-but-not-stripped"
        param_value = " \n \r \t "
        result = string_value(param_name, param_value, strip_whitespace=False)
        self.assertEqual(param_value, result)

    def test_strip_quotes_false(self):
        """Verify value is stripped accordingly when strip_quotes == False."""

        self.assertEqual(
            "\"\n \r \t\"",
            string_value(
                name="quoted-whitespace-with-spacing",
                value=" \"\n \r \t\" ",
                strip_quotes=False,
                strip_whitespace=True
            )
        )

        self.assertEqual(
            " \"\n \r \t\" ",
            string_value(
                name="quoted-whitespace-with-spacing",
                value=" \"\n \r \t\" ",
                strip_quotes=False,
                strip_whitespace=False
            )
        )

    def test_strip_quotes_true(self):
        """Verify value is stripped accordingly when strip_quotes == True."""

        self.assertEqual(
            " \"\n \r \t\" ",
            string_value(
                name="quoted-whitespace-with-spacing",
                value=" \"\n \r \t\" ",
                strip_quotes=True,
                strip_whitespace=False,
                empty_ok=True
            )
        )

        self.assertEqual(
            "",
            string_value(
                name="quoted-whitespace-with-spacing",
                value=" \"\n \r \t\" ",
                strip_quotes=True,
                strip_whitespace=True,
                empty_ok=True
            )
        )

        with self.assertRaises(ValueError) as ctx:
            string_value(
                name="quoted-whitespace-with-spacing",
                value=" \"\n \r \t\" ",
                strip_quotes=True,
                strip_whitespace=True,
                empty_ok=False
            )

        self.assertTupleEqual(
            ("quoted-whitespace-with-spacing", " \"\n \r \t\" "),
            ctx.exception.args
        )


class FilePathTest(TestCase):
    temp_dir: Optional[TemporaryDirectory]
    temp_dir_path: Optional[Path]

    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory(prefix=self.__class__.__name__)
        self.temp_dir_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir_path = None
        try:
            self.temp_dir.cleanup()
        except Exception:  # noqa
            logging.error("tearDown error!", exc_info=True)
        finally:
            self.temp_dir = None

    def test_bytes_value(self):
        """Verify bytes value can be processed."""

        original_path = self.temp_dir_path / "file.txt"
        name = "bytes_value"
        value = str(original_path).encode("utf-8")
        self.assertEqual(
            original_path, file_path(name, value, readable=False)
        )

        with self.assertRaises(FileNotFoundError) as ctx:
            file_path(name, value, readable=True)
        self.assertTupleEqual((name, value), ctx.exception.args)

    def test_str_value(self):
        """Verify str value can be processed."""

        original_path = self.temp_dir_path / "file.txt"
        name = "str_value"
        value = str(original_path)
        self.assertEqual(
            original_path, file_path(name, value, readable=False)
        )

        with self.assertRaises(FileNotFoundError) as ctx:
            file_path(name, value, readable=True)
        self.assertTupleEqual((name, value), ctx.exception.args)

    def test_path_value(self):
        """Verify Path value can be processed."""

        original_path = self.temp_dir_path / "file.txt"
        name = "path_value"
        value = original_path
        self.assertEqual(
            original_path, file_path(name, value, readable=False)
        )

        with self.assertRaises(FileNotFoundError) as ctx:
            file_path(name, value, readable=True)
        self.assertTupleEqual((name, value), ctx.exception.args)
