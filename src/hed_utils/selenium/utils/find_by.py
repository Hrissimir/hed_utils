from selenium.webdriver.common.by import By

from hed_utils.selenium.utils.element_finder import ElementFinder, LocatorWrapper
from hed_utils.selenium.utils.shared_driver import SharedDriver


class FindBy:
    """Facade for creation of ElementFinder instances."""

    @staticmethod
    def ID(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=LocatorWrapper(By.ID, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver())

    @staticmethod
    def NAME(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=LocatorWrapper(By.NAME, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver())

    @staticmethod
    def CSS_SELECTOR(
            value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=LocatorWrapper(By.CSS_SELECTOR, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver())

    @staticmethod
    def XPATH(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=LocatorWrapper(By.XPATH, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver())

    @staticmethod
    def TAG_NAME(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=LocatorWrapper(By.TAG_NAME, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver())

    @staticmethod
    def CLASS_NAME(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=LocatorWrapper(By.CLASS_NAME, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver())

    @staticmethod
    def LINK_TEXT(value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=LocatorWrapper(By.LINK_TEXT, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver())

    @staticmethod
    def PARTIAL_LINK_TEXT(
            value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        return ElementFinder(locator=LocatorWrapper(By.PARTIAL_LINK_TEXT, value, timeout, visible_only, required, desc),
                             context=context or SharedDriver())
