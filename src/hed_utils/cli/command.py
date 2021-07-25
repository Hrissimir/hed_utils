import logging
import sys
from abc import ABC
from abc import abstractmethod
from argparse import ArgumentParser
from argparse import Namespace

LOG_FORMAT = "%(asctime)s | %(levelname)8s | %(name)s | %(message)s"


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

    args.add_argument("--log-format",
                      action="store",
                      type=str,
                      default=LOG_FORMAT,
                      help=f"custom log format. default: '{LOG_FORMAT}'",
                      required=False)


class Command(ABC):
    """Base class for implementing CLI commands"""


    def __init__(self):
        self.log = logging.getLogger(self.name)
        self.args_parser = ArgumentParser(
            prog=self.name,
            description=self.description
        )
        add_logging_args(self.args_parser)


    @property
    @abstractmethod
    def name(self) -> str:
        """Used for invocation from cmd/terminal."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Printed in cmd/terminal help."""
        pass

    @abstractmethod
    def handle_args(self, args: Namespace):
        """Called by ``Command.run`` with parsed CLI args."""
        pass  # command logic goes here

    def run(self, *args):
        """CLI entry-point, called with raw args."""

        _args = self.args_parser.parse_args(args)

        if _args.log_level:
            logging.basicConfig(
                level=_args.log_level,
                format=_args.log_format,
                stream=sys.stdout
            )

        self.handle_args(_args)
