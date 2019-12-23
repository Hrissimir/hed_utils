import logging
from configparser import ConfigParser
from io import StringIO
from pathlib import Path
from typing import List
from unittest import mock

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def print_section(section_name: str, config: ConfigParser):
    assert isinstance(section_name, str), f"Expected string, Got {type(section_name).__name__}"
    assert bool(section_name), "Section name was empty"
    assert isinstance(config, ConfigParser), f"Expected ConfigParser, Got: '{type(config).__name__}'"

    print()
    print(f"[{section_name}]")
    section = config[section_name]
    for key in section.keys():
        print(f"{key} = {section[key]}")


def format_section(section_name: str, config: ConfigParser) -> str:
    with mock.patch("sys.stdout", new=StringIO()) as fake_out:
        print_section(section_name, config)
        return fake_out.getvalue()


def print_config(config: ConfigParser):
    for section_name in config.keys():
        print_section(section_name, config)


def format_config(config: ConfigParser) -> str:
    with mock.patch("sys.stdout", new=StringIO()) as fake_out:
        print_config(config)
        return fake_out.getvalue()


def read_config(file: str, interpolation=None) -> ConfigParser:
    _log.info("reading config (interpolation=%s) from file: '%s'", interpolation, file)

    file_path = str(Path(file))
    config = ConfigParser(interpolation=interpolation)
    with open(file_path, "r") as configfile:
        config.read_file(configfile)

    _log.info("done reading config from '%s' got:\n%s", file_path, format_config(config))
    return config


def write_config(config: ConfigParser, file: str):
    assert isinstance(config, ConfigParser), f"Expected ConfigParser, Got: '{type(config).__name__}'"

    file_path = Path(file)
    _log.info("writing config to file: '%s'", file_path)
    with file_path.open(mode="wb") as out:
        out.write(format_config(config).encode("utf-8"))
    _log.debug("done writing config to: '%s'", file_path)


class ConfigSection:
    def __init__(self, section_name: str, section_keys: List[str], config: ConfigParser):
        if not isinstance(section_name, str):
            raise TypeError(f"Section name must be string, was: {type(section_name).__name__}")
        if not section_name:
            raise ValueError("Section name was empty string")
        if not isinstance(section_keys, list):
            raise TypeError("Section keys must be list")
        for i, key in enumerate(section_keys):
            if not isinstance(key, str):
                raise TypeError("All section keys must be strings, "
                                f"got {type(key).__name__} at index {i}! {section_keys}")
        if not isinstance(config, ConfigParser):
            raise TypeError(f"Config must be ConfigParser instance, was: {type(config).__name__}")

        self.section_name = section_name
        self.section_keys = section_keys
        self.config = config

    def __repr__(self):
        try:
            section = self.get_section()
            data = {key: section.get(key) for key in self.section_keys}
            return f"ConfigSection(name='{self.section_name}', data={data})"
        except:
            return f"{type(self).__name__}(name='{self.section_name}', keys={self.section_keys})"

    def __str__(self):
        return format_section(self.section_name, self.config)

    def get_section(self):
        try:
            return self.config[self.section_name]
        except KeyError as kerr:
            raise RuntimeError(f"No '{self.section_name}' section present in config!") from kerr

    def assert_valid(self):
        try:
            section = self.get_section()
        except RuntimeError as rerr:
            raise AssertionError() from rerr

        actual_keys = list(section.keys())
        missing_keys = [key for key in self.section_keys if (key not in actual_keys)]

        if missing_keys:
            raise AssertionError(f"The following section keys were missing: {missing_keys} (from {self.section_keys})")
