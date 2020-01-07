import logging
from typing import Union, List

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from hed_utils.selenium import defaults
from hed_utils.selenium.wrappers.element_wrapper import ElementWrapper
from hed_utils.support.time_tool import poll_for_result, Timer

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class LocatorWrapper:
    def __init__(self, by, value, timeout=None, visible_only=None, required=None, desc=None):
        self.by = by
        self.value = value
        self.timeout = float(defaults.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout)
        self.visible_only = True if visible_only is None else visible_only
        self.required = True if required is None else required
        self.desc = "N/A" if desc is None else desc

    def __repr__(self):
        return ("LocatorWrapper(by='%s', value='%s', timeout=%d, visible_only=%s, required=%s, desc='%s')" %
                (self.by, self.value, self.timeout, self.visible_only, self.required, self.desc))

    def copy(self, timeout=None, visible_only=None, required=None, desc=None):
        return LocatorWrapper(self.by,
                              self.value,
                              timeout=(self.timeout if timeout is None else timeout),
                              visible_only=(self.visible_only if visible_only is None else visible_only),
                              required=(self.required if required is None else required),
                              desc=(self.desc if desc is None else desc))


def _find_elements(locator: LocatorWrapper, context: Union[WebDriver, WebElement]) -> List[WebElement]:
    try:
        return [element
                for element
                in context.find_elements(locator.by, locator.value)
                if (element.is_displayed() if locator.visible_only else True)]
    except defaults.IGNORED_EXCEPTIONS:
        return []


def find_element(locator: LocatorWrapper, context: Union[WebDriver, WebElement]):
    with Timer() as timer:
        while True:
            elements = _find_elements(locator, context)
            element = elements[0] if elements else None
            timer.stop()
            if element or ((locator.timeout - timer.elapsed) < 0):
                break
            else:
                timer.start()

    if not element:
        _log.warning("Not found (element): %s in %.03f s.", locator, timer.elapsed)
        if locator.required:
            raise NoSuchElementException(str(locator))
    else:
        _log.debug("Found (element): %s in %.03f s.", locator, timer.elapsed)

    return element


def find_elements(locator: LocatorWrapper, context: Union[WebDriver, WebElement]) -> List[WebElement]:
    with Timer() as timer:
        while True:
            elements = _find_elements(locator, context)
            timer.stop()
            if elements or ((locator.timeout - timer.elapsed) < 0):
                break
            else:
                timer.start()

    if not elements:
        _log.warning("Not found (elements): %s in %.03f s.", locator, timer.elapsed)
        if locator.required:
            raise NoSuchElementException(str(locator))
    else:
        _log.debug("Found (elements): %s x %s in %.03f s.", len(elements), locator, timer.elapsed)

    return elements


class ElementFinder(ElementWrapper):

    def __init__(self, locator: LocatorWrapper, context: Union[WebElement, WebDriver]):
        if not isinstance(locator, LocatorWrapper):
            raise TypeError(f"Expected LocatorWrapper instance, got: '{type(locator).__name__}'")
        self.locator = locator
        self.context = context

    def __repr__(self):
        return f"ElementFinder(locator={repr(self.locator)}, context={repr(self.context)})"

    def __iter__(self):
        return self.elements.__iter__()

    def __len__(self):
        return len(self.elements)

    @property
    def wrapped_element(self) -> WebElement:
        return find_element(self.locator, self.context)

    @property
    def elements(self) -> List[WebElement]:
        return find_elements(self.locator, self.context)

    def is_visible(self, timeout=0.5) -> bool:
        locator = self.locator.copy(timeout=timeout, visible_only=True, required=False)
        return find_element(locator, self.context) is not None

    def is_present(self, timeout=0.5) -> bool:
        locator = self.locator.copy(timeout=timeout, visible_only=False, required=False)
        return find_element(locator, self.context) is not None

    def wait_until_gone(self, timeout=None):
        timeout = self.locator.timeout if (timeout is None) else timeout

        if self.is_visible():
            def is_gone() -> bool:
                return not self.is_visible()

            poll_for_result(is_gone, timeout_seconds=timeout, default=TimeoutException)
