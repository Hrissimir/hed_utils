import platform
from enum import Enum, unique


@unique
class OsType(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MAC_OS = "MacOS"

    @staticmethod
    def is_64bit() -> bool:
        return ("64bit" in platform.architecture()) or ("64" in platform.uname().machine)

    @staticmethod
    def is_linux() -> bool:
        return "linux" in platform.uname().system.lower()

    @staticmethod
    def is_mac() -> bool:
        return platform.uname().system in ("Darwin", "macosx")

    @staticmethod
    def is_windows() -> bool:
        return "windows" in platform.uname().system.lower()

    @staticmethod
    def get_current() -> "OsType":  # pragma: no cover
        if OsType.is_linux():
            return OsType.LINUX
        if OsType.is_mac():
            return OsType.MAC_OS
        if OsType.is_windows():
            return OsType.WINDOWS

        raise OSError("Unknown OS!")
