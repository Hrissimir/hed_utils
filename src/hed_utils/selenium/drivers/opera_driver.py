import atexit
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from selenium.webdriver import ChromeOptions, Opera

from hed_utils.support import file_utils, os_type

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

VPN_ENABLED_SNAPSHOTS = {
    os_type.LINUX: Path(__file__).parent.joinpath("opera_vpn_enabled_snapshot_linux.zip")
}


def get_options(*, headless=False, user_data_dir=None) -> ChromeOptions:
    opts = ChromeOptions()

    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--start-maximized")
    opts.add_argument("--window-size=1920,1080")

    if headless:
        opts.add_argument("headless")

    if user_data_dir:
        opts.add_argument(f"user-data-dir={str(user_data_dir)}")

    return opts


def create_instance(*, headless=False, auto_quit=True, user_data_dir=None) -> Opera:
    _log.debug("creating webdriver: Opera(headless=%s, auto_quit=%s, user_data_dir='%s')",
               headless, auto_quit, user_data_dir)

    options = get_options(headless=headless, user_data_dir=user_data_dir)
    driver = Opera(options=options)
    _log.debug("created webdriver: Opera")

    if auto_quit:
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
    _log.debug("creating Opera snapshot at: %s", str(dst_zip))

    if dst_zip.exists():
        raise FileExistsError(str(dst_zip))

    with TemporaryDirectory() as tmp_dir:
        user_data_dir = Path(tmp_dir).joinpath("opera_user_data_dir")
        user_data_dir.mkdir()

        driver = create_instance(user_data_dir=str(user_data_dir))
        input("\n\nConfigure the browser settings as needed and press ENTER when done...")
        _log.debug("quitting driver...")
        driver.quit()

        file_utils.zip_dir(user_data_dir, dst_zip, skip_suffixes=[".log"], dry=False)


def use_snapshot(*, src_zip, headless=False, auto_quit=True) -> Opera:
    """Extracts a pre-created .zip snapshot of user-data-dir to a temp dir then creates a driver using it """

    src_zip = Path(src_zip)
    dst_dir = Path(file_utils.prepare_tmp_location("opera_user_data_dir"))
    file_utils.extract_zip(src_zip, dst_dir)

    def clear_dir():
        file_utils.delete_folder(dst_dir)

    atexit.register(clear_dir)

    return create_instance(headless=headless, auto_quit=auto_quit, user_data_dir=str(dst_dir))


def use_vpn_enabled_snapshot(*, headless=False, auto_quit=True) -> Opera:
    """Uses bundled user-data-dir that has dark theme & VPN enabled."""

    src_zip = VPN_ENABLED_SNAPSHOTS.get(os_type.get_current(), None)
    if not src_zip:
        raise OSError(f"Not implemented for {os_type.get_current()}")

    return use_snapshot(src_zip=src_zip, headless=headless, auto_quit=auto_quit)
