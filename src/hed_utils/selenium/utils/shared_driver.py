import logging
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from hed_utils.selenium.wrappers.driver_wrapper import DriverWrapper
from hed_utils.support.singleton import Singleton

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class SharedDriver(DriverWrapper, metaclass=Singleton):

    def __init__(self):
        super().__init__(None)

    @classmethod
    def set_instance(cls, driver: Optional[WebDriver]):
        _log.debug("setting shared driver instance to: %s", repr(driver))
        cls()._wrapped_driver = driver
