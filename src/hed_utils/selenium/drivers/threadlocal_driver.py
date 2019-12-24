import logging
import threading
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from hed_utils.selenium.drivers.driver_wrapper import DriverWrapper

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class ThreadLocalDriver(DriverWrapper):
    _storage = threading.local()

    def __init__(self):
        super().__init__(None)

    @classmethod
    def set_instance(cls, instance: Optional[WebDriver]):
        _log.debug("setting thread-local driver to: %s", repr(instance))
        cls._storage.instance = instance

    @property
    def wrapped_driver(self) -> WebDriver:
        if hasattr(self._storage, "instance"):
            self._storage.instance = None

        return self._storage.instance
