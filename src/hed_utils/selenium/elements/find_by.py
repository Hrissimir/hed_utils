import logging

from selenium.webdriver.common.by import By

from hed_utils.selenium.drivers.threadlocal_driver import ThreadLocalDriver
from hed_utils.selenium.elements.element_finder import ElementFinder
from hed_utils.selenium.elements.locator import new_locator

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class FindBy:
    """Facade for creation of ElementFinder instances."""

    driver = ThreadLocalDriver()

    @classmethod
    def ID(cls, value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        locator = new_locator(By.ID, value, timeout, visible_only, required, desc),
        context = context or cls.driver
        return ElementFinder(locator, context)

    @classmethod
    def NAME(
            cls, value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        locator = new_locator(By.NAME, value, timeout, visible_only, required, desc),
        context = context or cls.driver
        return ElementFinder(locator, context)

    @classmethod
    def CSS_SELECTOR(
            cls, value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        locator = new_locator(By.CSS_SELECTOR, value, timeout, visible_only, required, desc),
        context = context or cls.driver
        return ElementFinder(locator, context)

    @classmethod
    def XPATH(
            cls, value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        locator = new_locator(By.XPATH, value, timeout, visible_only, required, desc),
        context = context or cls.driver
        return ElementFinder(locator, context)

    @classmethod
    def TAG_NAME(
            cls, value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        locator = new_locator(By.TAG_NAME, value, timeout, visible_only, required, desc),
        context = context or cls.driver
        return ElementFinder(locator, context)

    @classmethod
    def CLASS_NAME(
            cls, value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        locator = new_locator(By.CLASS_NAME, value, timeout, visible_only, required, desc),
        context = context or cls.driver
        return ElementFinder(locator, context)

    @classmethod
    def LINK_TEXT(
            cls, value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        locator = new_locator(By.LINK_TEXT, value, timeout, visible_only, required, desc),
        context = context or cls.driver
        return ElementFinder(locator, context)

    @classmethod
    def PARTIAL_LINK_TEXT(
            cls, value, *, timeout=None, visible_only=None, required=None, desc=None, context=None) -> ElementFinder:
        locator = new_locator(By.PARTIAL_LINK_TEXT, value, timeout, visible_only, required, desc),
        context = context or cls.driver
        return ElementFinder(locator, context)
