from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from hed_utils.selenium.defaults import IGNORED_EXCEPTIONS as SELENIUM_EXCEPTIONS

from hed_utils.selenium.wrappers.driver_wrapper import DriverWrapper
from hed_utils.selenium.drivers.shared_driver import SharedDriver
from hed_utils.selenium.factories import chrome_driver, opera_driver

from hed_utils.selenium.wrappers.element_wrapper import ElementWrapper
from hed_utils.selenium.elements.find_by import FindBy


# prepare live console with single import 'from hed_utils.selenium import *'
__all__ = [
    "By",
    "Keys",  # element.send_keys("COOL!" + Keys.ENTER)
    "SELENIUM_EXCEPTIONS",  # try: ... except SELENIUM_EXCEPTIONS:...
    "chrome_driver",
    "opera_driver",
    "DriverWrapper",
    "SharedDriver",  # SharedDriver.set_instance(chrome_driver.create_instance())
    "ElementWrapper",
    "FindBy",  # FindBy.NAME("q").send_keys("selenium")
]
