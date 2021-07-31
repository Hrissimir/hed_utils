"""Helper module for processing CLI args."""
import logging
import sys
from argparse import ArgumentParser
from argparse import ArgumentTypeError
from math import inf
from pathlib import Path

from hed_utils.support import text_tool


def string_value(arg: str) -> str:
    """Process string argument value."""

    value = text_tool.strip_quotes(arg).strip()
    if not value:
        raise ArgumentTypeError()
    return value


def int_value(*, min_value=-inf, max_value=inf):
    """Convert string arg to int belonging to a given range."""

    def parse(arg: str):
        value = string_value(arg)
        try:
            value = int(value)
        except ValueError as e:
            raise ArgumentTypeError from e

        if not (min_value <= value <= max_value):
            raise ArgumentTypeError(value, (min_value, max_value))
        return value

    return parse


def path_value(arg: str) -> Path:
    """Converts string argument to Path value."""

    value = string_value(arg)
    try:
        return Path(value).absolute().resolve().expanduser()
    except ValueError as e:
        raise ArgumentTypeError() from e


def output_file_path(arg: str) -> Path:
    """Process and convert string to writable output-file Path."""

    path = path_value(arg)
    if path.exists() and path.is_dir():
        raise ArgumentTypeError(IsADirectoryError)
    return path


def input_file_path(arg: str) -> Path:
    """Process and convert string to readable file-path."""

    path = input_file_path(arg)
    if not path.exists():
        raise ArgumentTypeError(FileNotFoundError)
    return path


def output_folder_path(arg: str) -> Path:
    """Convert string arg to writable folder Path."""

    path = path_value(arg)
    if path.exists() and (not path.is_dir()):
        raise ArgumentTypeError(NotADirectoryError)
    return path


def input_folder_path(arg: str) -> Path:
    """Convert string arg to readable folder Path."""

    path = output_folder_path(arg)
    if not path.exists():
        raise ArgumentTypeError(FileNotFoundError)
    return path


def create_parser(name: str, description: str) -> ArgumentParser:
    """Creates and returns ArgumentParser with logging args support."""

    parser = ArgumentParser(prog=name, description=description)
    group = parser.add_argument_group(description="logging related")
    group.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.INFO,
        dest="log_level",
        help="set log level to INFO")
    group.add_argument(
        "-vv",
        "--very-verbose",
        action="store_const",
        const=logging.DEBUG,
        dest="log_level",
        help="set log level to DEBUG")
    group.add_argument(
        "--log-format",
        action="store",
        default="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        type=string_value,
        help="set custom log format")

    parse_args_func = parser.parse_args

    def parse_args_and_init_logging(*args):
        args = parse_args_func(*args)
        logging.basicConfig(
            level=args.log_level,
            format=args.log_format,
            stream=sys.stdout)
        return args

    parser.parse_args = parse_args_and_init_logging
    return parser
