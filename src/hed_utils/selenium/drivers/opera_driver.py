import atexit
import logging
import os
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory
from typing import Optional

from selenium.webdriver import ChromeOptions, Remote, Opera

from hed_utils.support import file_tool, os_type

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

VPN_ENABLED_SNAPSHOTS = {
    os_type.LINUX: Path(__file__).parent.joinpath("opera_vpn_enabled_snapshot_linux.zip")
}


def resolve_executable_path() -> Optional[str]:
    executable_path = os.environ.get("webdriver.opera.driver", which("operadriver"))
    executable_path = Path(executable_path or Path.home().joinpath("bin").joinpath("operadriver"))
    executable_path = str(executable_path) if executable_path.exists() else None
    _log.debug("resolved Opera-driver executable path: '%s'", executable_path)
    return executable_path


def resolve_browser_executable_path() -> Optional[str]:
    """ Resolves the path to the opera-browser executable"""

    browser_executable = Path(os.environ.get("webdriver.opera.browser", which("opera")) or "/usr/bin/opera")
    browser_executable = str(browser_executable) if browser_executable.exists() else None
    _log.debug("resolved Opera-browser executable path: '%s'", browser_executable)
    return browser_executable


def get_options(*, headless=False, browser_executable_path=None, user_data_dir=None) -> ChromeOptions:
    opts = ChromeOptions()
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-audio-output")
    opts.add_argument("--start-maximized")
    opts.add_argument("--test-type=UI")
    opts.add_argument("--window-size=1920,1080")

    if headless:
        opts.add_argument("headless")

    if user_data_dir:
        opts.add_argument(f"user-data-dir={str(user_data_dir)}")

    if browser_executable_path:
        opts._binary_location = browser_executable_path

    return opts


def create_instance(*, headless=False, executable_path=None, browser_executable_path=None,
                    user_data_dir=None) -> Remote:
    executable_path = executable_path or resolve_executable_path()
    browser_executable_path = browser_executable_path or resolve_browser_executable_path()
    _log.debug("creating OperaDriver(headless=%s, executable_path='%s', browser_executable='%s', user_data_dir='%s')",
               headless, executable_path, browser_executable_path, user_data_dir)

    options = get_options(headless=headless,
                          browser_executable_path=browser_executable_path,
                          user_data_dir=user_data_dir)
    driver = Opera(executable_path=executable_path, options=options) if executable_path else Opera(options=options)
    _log.debug("created OperaDriver instance!")
    atexit.register(driver.quit)
    return driver


def create_snapshot(dst_zip):  # pragma: no cover
    """Starts Opera browser and pauses to allow manual configuration of the browser.

    When the configuration is done, creates a .zip of the user-data-dir that can be reused in consecutive runs.

    Example configurations:
        - enable Opera VPN.
        - log in to a site.
        - set a theme
    """
    dst_zip = Path(dst_zip).resolve()
    _log.debug("creating Opera user-data-dir snapshot at: %s", str(dst_zip))

    if dst_zip.exists():
        raise FileExistsError(str(dst_zip))

    with TemporaryDirectory() as tmp_dir:
        user_data_dir = Path(tmp_dir).joinpath("opera_user_data_dir")
        user_data_dir.mkdir()

        driver = create_instance(user_data_dir=str(user_data_dir))
        print()
        input("Configure the browser settings as needed and press ENTER when done...")
        print()
        _log.debug("quitting driver")
        driver.quit()

        file_tool.zip_dir(user_data_dir, dst_zip, skip_suffixes=[".log"], dry=False)


def use_snapshot(*, src_zip, headless=False, executable_path=None, browser_executable_path=None) -> Opera:
    """Extracts a pre-created .zip snapshot of user-data-dir to a temp dir then creates a driver using it """

    src_zip = Path(src_zip)
    dst_dir = Path(file_tool.prepare_tmp_location("opera_user_data_dir"))
    file_tool.extract_zip(src_zip, dst_dir)
    return create_instance(headless=headless,
                           executable_path=executable_path,
                           browser_executable_path=browser_executable_path,
                           user_data_dir=str(dst_dir))


def use_vpn_enabled_snapshot(*, headless=False, executable_path=None, browser_executable_path=None) -> Opera:
    """Uses bundled user-data-dir that has dark theme & VPN enabled."""

    src_zip = VPN_ENABLED_SNAPSHOTS.get(os_type.get_current(), None)
    if not src_zip:
        raise OSError(f"Not implemented for {os_type.get_current()}")

    return use_snapshot(src_zip=src_zip,
                        headless=headless,
                        executable_path=executable_path,
                        browser_executable_path=browser_executable_path)
