from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from hed_utils.selenium.defaults import IGNORED_EXCEPTIONS as SELENIUM_EXCEPTIONS

from hed_utils.selenium.drivers import (
    chrome_driver,
    opera_driver,
    DriverWrapper,
    ThreadLocalDriver
)

from hed_utils.selenium.elements import (
    Locator,
    ElementWrapper,
    ElementFinder,
    FindBy
)


# prepare live console with single import 'from hed_utils.selenium import *'
__all__ = [
    "By",
    "Keys",  # element.send_keys("COOL!" + Keys.ENTER)
    "SELENIUM_EXCEPTIONS",  # try: ... except SELENIUM_EXCEPTIONS:...
    "chrome_driver",
    "opera_driver",
    "DriverWrapper",
    "ThreadLocalDriver",  # ThreadLocalDriver.set_instance(chrome_driver.create_instance())
    "Locator",
    "ElementWrapper",
    "ElementFinder",
    "FindBy",  # FindBy.NAME("q").send_keys("selenium")
]
