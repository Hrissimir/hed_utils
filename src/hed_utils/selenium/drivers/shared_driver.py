import logging
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from hed_utils.selenium.drivers.driver_wrapper import DriverWrapper
from hed_utils.support.singleton import Singleton

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class SharedDriver(DriverWrapper, metaclass=Singleton):

    def __init__(self):
        super().__init__(None)

    @classmethod
    def set_driver(cls, driver: Optional[WebDriver]):
        _log.debug("setting thread-local driver instance to: %s", repr(driver))
        cls()._wrapped_driver = driver

    @classmethod
    def get_instance(cls) -> "SharedDriver":
        return cls()
