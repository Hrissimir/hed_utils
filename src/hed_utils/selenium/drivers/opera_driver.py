import atexit
import logging
from pathlib import Path

from selenium.webdriver import ChromeOptions, Opera

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def get_options(*, headless=False, user_data_dir=None) -> ChromeOptions:
    """Creates a ChromeOptions with some sane defaults."""

    opts = ChromeOptions()

    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-audio-output")
    opts.add_argument("--start-maximized")
    opts.add_argument("--window-size=1920,1080")

    if headless:
        opts.add_argument("headless")

    if user_data_dir:
        user_data_dir_path = Path(user_data_dir).absolute()
        if user_data_dir_path.exists():  # pragma: no cover
            _log.debug("Using existing user-data-dir at: %s", str(user_data_dir_path))
        else:
            _log.debug("Creating user-data-dir at: %s", str(user_data_dir_path))
            user_data_dir_path.mkdir(parents=True, exist_ok=True)
        opts.add_argument(f"user-data-dir={str(user_data_dir_path)}")

    return opts


def create_instance(*, headless=False, auto_quit=True, user_data_dir=None, executable_path=None) -> Opera:
    """Creates Opera webdriver instance using the provided arguments."""

    _log.debug("creating webdriver: Opera(headless=%s, auto_quit=%s, user_data_dir='%s', executable_path='%s')",
               headless, auto_quit, user_data_dir, executable_path)

    options = get_options(headless=headless, user_data_dir=user_data_dir)
    driver = Opera(options=options, executable_path=executable_path)
    _log.debug("created webdriver: Opera")

    if auto_quit:
        atexit.register(driver.quit)

    return driver
