import logging
from configparser import ConfigParser
from io import StringIO
from pathlib import Path

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def format_parser(parser: ConfigParser) -> str:
    """Formats the given ConfigParser contents to a printable string."""

    buffer = StringIO()
    parser.write(buffer)
    return buffer.getvalue()


def format_section(section_name: str, parser: ConfigParser) -> str:
    """Formats ConfigParser section to printable string."""

    buffer = StringIO(initial_value="\n")
    print(f"[{section_name}]", file=buffer)

    section = parser[section_name]
    for key in section.keys():
        print(f"{key} = {section[key]}", file=buffer)

    return buffer.getvalue()


def parse_file(src_file: str, parser_cls=ConfigParser, interpolation=None, **parser_kwargs) -> ConfigParser:
    filepath = Path(src_file).absolute()
    _log.debug("parsing config: src_file='%s', parser_cls=%s, interpolation=%s, **parser_kwargs=%s",
               str(filepath), parser_cls.__name__, repr(interpolation), parser_kwargs)

    parser = parser_cls(interpolation=interpolation, **parser_kwargs)
    with filepath.open(mode="r") as configfile:
        parser.read_file(configfile)

    return parser


def write_config(parser: ConfigParser, dst_file: str):
    filepath = Path(dst_file).absolute()
    _log.debug("writing config to: '%s'", str(filepath))

    if not isinstance(parser, ConfigParser):
        raise TypeError(f"Expected ConfigParser instance, got: '{type(parser).__name__}'")

    filepath.write_text(format_parser(parser), encoding="utf-8")
