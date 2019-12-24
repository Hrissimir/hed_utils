import logging
from collections import namedtuple
from typing import Union, List

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from hed_utils.selenium import defaults
from hed_utils.support.time_tool import Timer

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

Locator = namedtuple("Locator", "by value timeout visible_only required desc")


def new_locator(by, value, timeout=None, visible_only=None, required=None, desc=None):
    timeout = float(defaults.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout)
    visible_only = True if visible_only is None else visible_only
    required = True if required is None else required
    desc = "N/A" if desc is None else desc
    return Locator(by, value, timeout, visible_only, required, desc)


def _find_elements(locator: Locator, context: Union[WebDriver, WebElement]) -> List[WebElement]:
    try:
        return [element
                for element
                in context.find_elements(locator.by, locator.value)
                if (element.is_displayed() if locator.visible_only else True)]
    except defaults.IGNORED_EXCEPTIONS:
        return []


def find_element(locator: Locator, context: Union[WebDriver, WebElement]):
    with Timer() as timer:
        while True:
            elements = _find_elements(locator, context)
            element = elements[0] if elements else None
            timer.stop()
            if element or ((locator.timeout - timer.elapsed) < 0):
                break
            else:
                timer.start()

    if element:
        _log.debug("Found (element): %s in %.03f s.", locator, timer.elapsed)
        return element
    else:
        _log.warning("Not found (element): %s in %.03f s.", locator, timer.elapsed)

    if locator.required:
        raise NoSuchElementException(str(locator))

    return None


def find_elements(locator: Locator, context: Union[WebDriver, WebElement]) -> List[WebElement]:
    with Timer() as timer:
        while True:
            elements = _find_elements(locator, context)
            timer.stop()
            if elements or ((locator.timeout - timer.elapsed) < 0):
                break
            else:
                timer.start()

    if elements:
        _log.debug("Found (elements): %s x %s in %.03f s.", len(elements), locator, timer.elapsed)
        return elements
    else:
        _log.warning("Not found (elements): %s in %.03f s.", locator, timer.elapsed)

    if locator.required:
        raise NoSuchElementException(str(locator))

    return []
