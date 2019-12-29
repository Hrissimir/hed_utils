import platform

WINDOWS = "Windows"
LINUX = "Linux"
MAC_OS = "MacOS"
UNKNOWN = "Unknown"


def is_64bit() -> bool:
    return ("64bit" in platform.architecture()) or ("64" in platform.uname().machine)


def is_linux() -> bool:
    return "linux" in platform.uname().system.lower()


def is_mac() -> bool:
    return platform.uname().system.lower() in ("darwin", "macosx", "macos")


def is_windows() -> bool:
    return "windows" in platform.uname().system.lower()


def get_current():
    if is_linux():
        return LINUX
    elif is_mac():
        return MAC_OS
    elif is_windows():
        return WINDOWS
    else:
        return UNKNOWN
