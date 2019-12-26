import atexit
import logging
from pathlib import Path

from selenium.webdriver import Chrome, ChromeOptions

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def get_options(*, headless=False, user_data_dir=None, downloads_dir=None) -> ChromeOptions:
    """Creates ChromeOptions with some additional values"""

    opts = ChromeOptions()

    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-audio-output")
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


def create_instance(*, headless=False, auto_quit=True, user_data_dir=None, downloads_dir=None) -> Chrome:
    _log.debug("creating webdriver: Chrome(headless=%s, auto_quit=%s, user_data_dir='%s', downloads_dir='%s')",
               headless, auto_quit, user_data_dir, downloads_dir)

    options = get_options(headless=headless, user_data_dir=user_data_dir, downloads_dir=downloads_dir)
    driver = Chrome(options=options)
    _log.debug("created webdriver instance: Chrome")

    if auto_quit:
        atexit.register(driver.quit)

    return driver
