import atexit
import logging
import os
from pathlib import Path
from shutil import which
from typing import Optional

from selenium.webdriver import Chrome, ChromeOptions

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def resolve_executable_path() -> Optional[str]:
    executable = os.environ.get("webdriver.chrome.driver", which("chromedriver"))
    if executable:
        executable_path = Path(executable).resolve()
        executable = str(executable_path) if executable_path.exists() else None
    _log.debug("resolved 'chromedriver' executable path: '%s'", executable)
    return executable


def get_options(*, headless=False, user_data_dir=None, downloads_dir=None) -> ChromeOptions:
    """Creates ChromeOptions with some additional values"""

    opts = ChromeOptions()

    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-audio-output")
    opts.add_argument("--disable-login-animations")
    opts.add_argument("--disable-translate")
    opts.add_argument("--no-experiments")
    opts.add_argument("--start-maximized")
    opts.add_argument("--test-type=UI")
    opts.add_argument("--window-size=1920,1080")

    if headless:
        opts.add_argument("--headless")

    if user_data_dir:
        Path(user_data_dir).mkdir(parents=True, exist_ok=True)
        opts.add_argument(f"user-data-dir={str(user_data_dir)}")

    if downloads_dir:
        Path(downloads_dir).mkdir(parents=True, exist_ok=True)
        prefs = {"profile.default_content_settings.popups": 0,
                 "download.default_directory": downloads_dir}
        opts.add_experimental_option("prefs", prefs)

    return opts


def create_instance(*, headless=False, executable_path=None, user_data_dir=None, downloads_dir=None) -> Chrome:
    executable_path = executable_path or resolve_executable_path()
    _log.debug("creating chrome-driver (headless=%s, executable_path='%s', user_data_dir='%s', downloads_dir='%s')",
               headless, executable_path, user_data_dir, downloads_dir)

    options = get_options(headless=headless, user_data_dir=user_data_dir, downloads_dir=downloads_dir)
    driver = Chrome(executable_path=executable_path, options=options) if executable_path else Chrome(options=options)
    _log.debug("created ChromeDriver instance!")
    atexit.register(driver.quit)
    return driver
