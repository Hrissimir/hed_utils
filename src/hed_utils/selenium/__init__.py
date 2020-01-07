from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from hed_utils.selenium.constants import SELENIUM_EXCEPTIONS, LOGGERS
from hed_utils.selenium.factories import chrome_driver, opera_driver
from hed_utils.selenium.utils import FindBy, SharedDriver, wait_for_page_load
from hed_utils.selenium.wrappers import DriverWrapper, ElementWrapper


def disable_loggers():
    for logger in LOGGERS:
        logger.disabled = True


# prepare live console with single import 'from hed_utils.selenium import *'
__all__ = [
    "By",
    "Keys",  # element.send_keys("COOL!" + Keys.ENTER)
    "SELENIUM_EXCEPTIONS",  # try: ... except SELENIUM_EXCEPTIONS:...
    "disable_loggers",
    "chrome_driver",
    "opera_driver",
    "wait_for_page_load",
    "DriverWrapper",
    "ElementWrapper",
    "SharedDriver",  # SharedDriver.set_instance(chrome_driver.create_instance())
    "FindBy",  # FindBy.NAME("q").send_keys("selenium")
]
