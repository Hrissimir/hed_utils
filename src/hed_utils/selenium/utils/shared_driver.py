import logging
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from hed_utils.selenium.wrappers.driver_wrapper import DriverWrapper

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class SharedDriver(DriverWrapper):
    _SHARED_INSTANCE = None

    def __init__(self):
        super().__init__(None)

    @classmethod
    def set_instance(cls, driver: Optional[WebDriver]):
        _log.debug("setting shared driver instance to: %s", repr(driver))
        cls._SHARED_INSTANCE = driver

    @property
    def wrapped_driver(self) -> WebDriver:
        return self._SHARED_INSTANCE
