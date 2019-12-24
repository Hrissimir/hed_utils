import logging
from typing import Union, List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from hed_utils.selenium.elements.element_wrapper import ElementWrapper
from hed_utils.selenium.elements.locator import Locator, find_element, find_elements
from hed_utils.support.time_tool import poll_for_result

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class ElementFinder(ElementWrapper):

    def __init__(self, locator: Locator, context: Union[WebElement, WebDriver]):
        if not isinstance(locator, Locator):
            raise TypeError(f"Expected Locator instance, got: '{type(locator).__name__}'")
        self.locator = locator
        self.context = context

    def __repr__(self):
        return f"ElementFinder(locator={repr(self.locator)}, context={repr(self.context)})"

    @property
    def wrapped_element(self) -> WebElement:
        return find_element(self.locator, self.context)

    @property
    def elements(self) -> List[WebElement]:
        return find_elements(self.locator, self.context)

    def is_visible(self, timeout=0.5) -> bool:
        locator = self.locator._replace(timeout=timeout, visible_only=True, required=False)
        return find_element(locator, self.context) is not None

    def is_present(self, timeout=0.5) -> bool:
        locator = self.locator._replace(timeout=timeout, visible_only=False, required=False)
        return find_element(locator, self.context) is not None

    def wait_until_gone(self, timeout=None):
        timeout = self.locator.timeout if (timeout is None) else timeout

        if self.is_visible():
            def is_gone() -> bool:
                return not self.is_visible()

            poll_for_result(is_gone, timeout_seconds=timeout, default=TimeoutException)
