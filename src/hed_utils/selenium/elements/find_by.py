from selenium.webdriver.common.by import By

from hed_utils.selenium.utils.shared_driver import SharedDriver
from hed_utils.selenium.elements.element_finder import ElementFinder
from hed_utils.selenium.elements.locator import new_locator


class FindBy:
    """Facade for creation of ElementFinder instances."""

    @staticmethod
    def ID(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=new_locator(By.ID, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver.get_instance())

    @staticmethod
    def NAME(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=new_locator(By.NAME, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver.get_instance())

    @staticmethod
    def CSS_SELECTOR(
            value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=new_locator(By.CSS_SELECTOR, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver.get_instance())

    @staticmethod
    def XPATH(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=new_locator(By.XPATH, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver.get_instance())

    @staticmethod
    def TAG_NAME(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=new_locator(By.TAG_NAME, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver.get_instance())

    @staticmethod
    def CLASS_NAME(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=new_locator(By.CLASS_NAME, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver.get_instance())

    @staticmethod
    def LINK_TEXT(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=new_locator(By.LINK_TEXT, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver.get_instance())

    @staticmethod
    def PARTIAL_LINK_TEXT(
            value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=new_locator(By.PARTIAL_LINK_TEXT, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver.get_instance())
