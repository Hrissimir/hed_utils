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
    opts.add_argument("--disable-audio-output")
    opts.add_argument("--start-maximized")
    opts.add_argument("--window-size=1920,1080")

    if headless:
        opts.add_argument("--headless")

    if user_data_dir:
        user_data_dir_path = Path(user_data_dir).absolute()
        if user_data_dir_path.exists():  # pragma: no cover
            _log.debug("Using existing user-data-dir at: %s", str(user_data_dir_path))
        else:
            _log.debug("Creating user-data-dir at: %s", str(user_data_dir_path))
            user_data_dir_path.mkdir(parents=True, exist_ok=True)
        opts.add_argument(f"user-data-dir={str(user_data_dir_path)}")

    if downloads_dir:
        downloads_dir_path = Path(downloads_dir)
        if downloads_dir_path.exists():  # pragma: no cover
            _log.debug("Using existing downloads-dir at: %s", str(downloads_dir_path))
        else:
            _log.debug("Creating downloads-dir at: %s", str(downloads_dir_path))
            downloads_dir_path.mkdir(parents=True, exist_ok=True)

        prefs = {"profile.default_content_settings.popups": 0,
                 "download.default_directory": str(downloads_dir_path)}
        opts.add_experimental_option("prefs", prefs)

    return opts


def create_instance(*,
                    headless=False,
                    auto_quit=True,
                    user_data_dir=None,
                    downloads_dir=None,
                    executable_path="chromedriver") -> Chrome:
    """Creates a Chrome webdriver instance, whose .quit() method will be automatically called at program exit."""

    _log.debug("creating webdriver: Chrome(headless=%s, auto_quit=%s, user_data_dir='%s', downloads_dir='%s')",
               headless, auto_quit, user_data_dir, downloads_dir)

    options = get_options(headless=headless, user_data_dir=user_data_dir, downloads_dir=downloads_dir)

    driver = Chrome(executable_path=executable_path, options=options)
    _log.debug("created webdriver instance: Chrome")

    if auto_quit:
        atexit.register(driver.quit)

    return driver
