"""This module contains base stuff for implementing CLI command."""

import logging
import sys
from abc import ABC
from abc import abstractmethod
from argparse import ArgumentParser
from argparse import ArgumentTypeError
from argparse import Namespace
from pathlib import Path
from typing import Optional

from hed_utils.support import checked_param

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class CliArg:
    """Defines parsing and validation for different types of CLI args."""

    @staticmethod
    def writable_file_path(value) -> Path:
        """Returns normalized, absolute and resolved Path to existing file."""

        try:
            return checked_param.file_path(
                "writable_file_path", value, readable=False
            )
        except Exception:
            raise ArgumentTypeError()

    @staticmethod
    def string_value(value) -> str:
        """Returns string stripped from any whitespace and quotes."""

        try:
            return checked_param.string_value(
                "string_value", value, empty_ok=False, none_ok=False
            )
        except Exception:
            raise ArgumentTypeError()


def add_logging_args(parser: ArgumentParser):
    """Add group of logging-related arguments to parser."""

    args = parser.add_argument_group("Logging related")

    args.add_argument("-v",
                      "--verbose",
                      action="store_const",
                      const=logging.INFO,
                      dest="log_level",
                      help="set the logging level to INFO.")

    args.add_argument("-vv",
                      "--very-verbose",
                      action="store_const",
                      const=logging.DEBUG,
                      dest="log_level",
                      help="set the logging level to DEBUG.",
                      required=False)

    args.add_argument("-nc",
                      "--no-console",
                      action="store_true",
                      help="disable log output to console.",
                      required=False)

    args.add_argument("--log-fmt",
                      action="store",
                      type=CliArg.string_value,
                      default="%(asctime)s | %(levelname)8s | %(name)s: %(message)s",
                      help="custom log-line format string.",
                      required=False)

    args.add_argument("--log-file",
                      action="store",
                      type=CliArg.writable_file_path,
                      default=None,
                      help="path to log file. unaffected by -nc.",
                      required=False)


def init_logging(log_level, log_fmt, log_file, no_console):
    """Initialize the global logging settings."""

    logging.basicConfig(
        level=log_level,
        format=log_fmt,
        stream=(None if no_console else sys.stdout),
    )

    if log_file:
        handler = logging.FileHandler(str(log_file))
        handler.setLevel(log_level)
        formatter = logging.Formatter(fmt=log_fmt)
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)


class CliCommand(ABC):
    """Base CLI command class."""

    def __init__(self):
        self.args: Optional[Namespace] = None
        self.args_parser = ArgumentParser(prog=self.name, description=self.description)
        add_logging_args(self.args_parser)
        self.log = logging.getLogger(type(self).__name__)

    @property
    @abstractmethod
    def name(self) -> str:
        """Program name used for invocation from CLI."""

        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief command description printed in CLI help."""

        pass

    @abstractmethod
    def run(self, *args):
        """Command entry-point, called with the CLI params."""

        args = self.args_parser.parse_args(args)
        init_logging(
            args.log_level, args.log_fmt, args.log_file, args.no_console
        )
        self.args = args
