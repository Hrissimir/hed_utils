import logging
from contextlib import contextmanager
from typing import List

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.html5.application_cache import ApplicationCache
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.mobile import Mobile
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from hed_utils.selenium import constants
from hed_utils.selenium.utils import js_condition
from hed_utils.support import os_type

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class DriverWrapper(WebDriver):

    def __init__(self, driver):
        self._wrapped_driver = driver.wrapped_driver if isinstance(driver, DriverWrapper) else driver

    def __repr__(self) -> str:
        return f"{type(self).__name__}(instance={repr(self.wrapped_driver)})"

    def __enter__(self):
        _log.debug("entering DriverWrapper context...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _log.debug("exiting DriverWrapper context...")
        self.quit()

    @contextmanager
    def file_detector_context(self, file_detector_class, *args, **kwargs):
        yield from self.wrapped_driver.file_detector_context(file_detector_class, *args, **kwargs)

    @property
    def file_detector(self):
        return self.wrapped_driver.file_detector

    @file_detector.setter
    def file_detector(self, detector):
        self.wrapped_driver.file_detector = detector

    @property
    def orientation(self):
        return self.wrapped_driver.orientation

    @orientation.setter
    def orientation(self, value):
        _log.debug("driver: setting orientation '%s'", value)
        self.wrapped_driver.orientation = value

    @property
    def wrapped_driver(self) -> WebDriver:
        return self._wrapped_driver

    @property
    def actions(self) -> ActionChains:
        return ActionChains(self.wrapped_driver)

    @property
    def page_soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.page_source, "lxml")

    @property
    def body_element(self) -> WebElement:
        return self.find_element_by_tag_name("body")

    @property
    def application_cache(self) -> ApplicationCache:
        return self.wrapped_driver.application_cache

    @property
    def current_url(self) -> str:
        return self.wrapped_driver.current_url

    @property
    def current_window_handle(self) -> str:
        return self.wrapped_driver.current_window_handle

    @property
    def window_handles(self) -> List[str]:
        return self.wrapped_driver.window_handles

    @property
    def desired_capabilities(self):
        return self.wrapped_driver.desired_capabilities

    @property
    def log_types(self) -> List[str]:
        log_types = self.wrapped_driver.log_types
        _log.debug("driver: available log types - %s", log_types)
        return log_types

    @property
    def mobile(self) -> Mobile:
        return self.wrapped_driver.mobile

    @property
    def name(self) -> str:
        return self.wrapped_driver.name

    @property
    def page_source(self) -> str:
        return self.wrapped_driver.page_source

    @property
    def switch_to(self) -> SwitchTo:
        return self.wrapped_driver.switch_to

    @property
    def title(self) -> str:
        return self.wrapped_driver.title

    def switch_to_active_element(self) -> WebElement:
        _log.debug("driver: switch to active element")
        return self.switch_to.active_element

    def switch_to_alert(self) -> Alert:
        _log.debug("driver: switch to alert")
        return self.switch_to.alert

    def switch_to_default_content(self):
        _log.debug("driver: switch to default content")
        self.switch_to.default_content()

    def switch_to_frame(self, frame_reference):
        _log.debug("driver: switch to frame '%s'", frame_reference)
        self.switch_to.frame(frame_reference)

    def switch_to_window(self, window_name):
        _log.debug("driver: switch to window: '%s'", window_name)
        self.switch_to.window(window_name)

    def open_new_tab(self):
        _log.debug("driver: open new tab and switch to it")
        current_handles = self.window_handles
        key = Keys.COMMAND if os_type.is_mac() else Keys.CONTROL
        self.body_element.send_keys(key + "t")
        self.wait_for_new_window(current_handles)
        self.switch_to_window(self.window_handles[-1])

    def close(self):
        _log.debug("driver: close current window")
        driver = self.wrapped_driver
        current_handle = driver.current_window_handle
        other_handles = [handle for handle in driver.window_handles if handle != current_handle]
        if not other_handles:
            _log.warning("can't close the last window!")
            return
        driver.close()
        self.wait_for_number_of_windows_to_be(len(other_handles))
        driver.switch_to.window(other_handles[-1])

    def quit(self):
        _log.debug("driver: quit...")
        self.wrapped_driver.quit()

    def back(self, wait_for_page_load=True):
        _log.debug("driver navigation: Back (wait_for_page_load=%s)", wait_for_page_load)
        self.wrapped_driver.back()
        if wait_for_page_load:
            self.wait_for_page_load()

    def forward(self, wait_for_page_load=True):
        _log.debug("driver navigation: Forward (wait_for_page_load=%s)", wait_for_page_load)
        self.wrapped_driver.forward()
        if wait_for_page_load:
            self.wait_for_page_load()

    def refresh(self, wait_for_page_load=True):
        _log.debug("driver navigation: Refresh (wait_for_page_load=%s)", wait_for_page_load)
        self.wrapped_driver.back()
        if wait_for_page_load:
            self.wait_for_page_load()

    def get(self, url, *, wait_for_url_change=False, wait_for_page_load=True):
        _log.debug("driver navigation: Get ( url='%s', wait_for_url_change=%s, wait_for_page_load=%s)",
                   url, wait_for_url_change, wait_for_page_load)

        url_before_change = self.current_url
        self.wrapped_driver.get(url)

        if wait_for_url_change:
            self.wait_for_url_change(url_before_change)

        if wait_for_page_load:
            self.wait_for_page_load()

        _log.debug("url after navigation: '%s'", self.current_url)

    def get_log(self, log_type):
        """
        Gets the log for a given log type

        :Args:
         - log_type: type of log that which will be returned

        :Usage:
            driver.get_log('browser')
            driver.get_log('driver')
            driver.get_log('client')
            driver.get_log('server')
        """

        _log.debug("driver: getting log '%s'", log_type)
        return self.wrapped_driver.get_log(log_type)

    def add_cookie(self, cookie_dict):
        _log.debug("driver: add cookie %s", cookie_dict)
        self.wrapped_driver.add_cookie(cookie_dict)

    def get_cookies(self) -> List[dict]:
        cookies = self.wrapped_driver.get_cookies()
        _log.debug("got cookies: %s", cookies)
        return cookies

    def get_cookie(self, name):
        cookie = self.wrapped_driver.get_cookie(name)
        _log.debug("got cookie: name='%s', cookie='%s'", name, cookie)
        return cookie

    def delete_cookie(self, name):
        _log.debug("driver: delete cookie '%s'", name)
        self.wrapped_driver.delete_cookie(name)

    def delete_all_cookies(self):
        _log.debug("driver: delete all cookies")
        self.wrapped_driver.delete_all_cookies()

    def execute(self, driver_command, params=None):
        _log.debug("execute driver command: '%s' (params=%s)", driver_command, params)
        return self.wrapped_driver.execute(driver_command, params)

    def execute_script(self, script, *args):
        _log.debug("execute script: '%s' (args: %s)", script, args)
        return self.wrapped_driver.execute_script(script, *args)

    def execute_async_script(self, script, *args):
        _log.debug("execute async script: '%s' (args: %s)", script, args)
        return self.wrapped_driver.execute_async_script(script, *args)

    def scroll_page(self, x: int, y: int):
        _log.debug("driver: scroll page by: x=%s, y=%s", x, y)
        self.wrapped_driver.execute_script(f"document.scrollingElement.scrollBy({x},{y});")

    def implicitly_wait(self, time_to_wait):
        _log.warning("driver: implicitly-wait %s (you should not be using this)", time_to_wait)
        self.wrapped_driver.implicitly_wait(time_to_wait)

    def set_script_timeout(self, time_to_wait):
        _log.debug("driver: script timeout %s", time_to_wait)
        self.wrapped_driver.set_script_timeout(time_to_wait)

    def set_page_load_timeout(self, time_to_wait):
        _log.debug("driver: page load timeout %s", time_to_wait)
        self.wrapped_driver.set_page_load_timeout(time_to_wait)

    def maximize_window(self):
        _log.debug("driver: maximize window")
        self.wrapped_driver.maximize_window()

    def minimize_window(self):
        _log.debug("driver: minimize window")
        self.wrapped_driver.minimize_window()

    def fullscreen_window(self):
        _log.debug("driver: fullscreen window")
        self.wrapped_driver.fullscreen_window()

    def get_screenshot_as_file(self, filename):
        _log.debug("driver: getting screenshot as file '%s'", filename)
        return self.wrapped_driver.get_screenshot_as_file(filename)

    def get_screenshot_as_png(self):
        _log.debug("driver: getting screenshot as png...")
        return self.wrapped_driver.get_screenshot_as_png()

    def get_screenshot_as_base64(self):
        _log.debug("driver: getting screenshot as base64...")
        return self.wrapped_driver.get_screenshot_as_base64()

    def save_screenshot(self, filename) -> bool:
        _log.debug("driver: save screenshot - '%s'", filename)
        success = self.wrapped_driver.save_screenshot(filename)
        if success:
            _log.debug("driver: screenshot saved successfully!")
        else:
            _log.warning("driver: failed to save screenshot!")
        return success

    def save_page_source(self, filename) -> bool:
        _log.debug("driver: save page source - '%s'", filename)
        try:
            with open(filename, mode="xb") as out:
                out.write(self.page_soup.prettify(encoding="utf-8"))
            _log.debug("driver: page source saved successfully!")
            return True
        except IOError:
            _log.warning("driver: failed to save page source!")
            return False

    def set_window_size(self, width, height, windowHandle='current'):
        _log.debug("driver: set window size (width=%s, height=%s, windowHandle='%s')", width, height, windowHandle)
        self.wrapped_driver.set_window_size(width, height, windowHandle)

    def get_window_size(self, windowHandle='current'):
        size = self.wrapped_driver.get_window_size(windowHandle)
        _log.debug("driver: got window size for '%s' %s", windowHandle, size)
        return size

    def set_window_position(self, x, y, windowHandle='current'):
        _log.debug("driver: set window position (x=%s, y=%s, windowHandle='%s')", x, y, windowHandle)
        self.wrapped_driver.set_window_position(x, y, windowHandle)

    def get_window_position(self, windowHandle='current'):
        position = self.wrapped_driver.get_window_position(windowHandle)
        _log.debug("driver: got window position for '%s' %s", windowHandle, position)
        return position

    def get_window_rect(self):
        rect = self.wrapped_driver.get_window_rect()
        _log.debug("driver: got window rect %s", rect)
        return rect

    def is_visible(self, locator, timeout=0.5) -> bool:
        try:
            return self.wait_for_visible_element(locator, timeout) is not None
        except TimeoutException:
            return False

    def is_present(self, locator, timeout=0.5):
        try:
            return self.wait_for_element(locator, timeout) is not None
        except TimeoutException:
            return False

    def click(self, locator, timeout=None):
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("driver: click %s timeout=%s", locator, timeout)

        try:
            element = self.wait_for_clickable_element(locator, timeout)
        except TimeoutException:
            element = self.wait_for_visible_element(locator, 0.1)

        element.click()

    def hover(self, locator, timeout=None):
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("driver: hover %s timeout=%s", locator, timeout)
        element = self.wait_for_visible_element(locator, timeout)
        self.actions.move_to_element(element).pause(2).perform()

    def set_window_rect(self, x=None, y=None, width=None, height=None):
        _log.debug("driver: set window rect (x=%s, y=%s, width=%s, height=%s)", x, y, width, height)
        self.wrapped_driver.set_window_rect(x, y, width, height)

    def wait(self, timeout=None, *, poll_frequency=None, ignored_exceptions=None) -> WebDriverWait:
        timeout = constants.DEFAULT_WAIT_TIMEOUT if timeout is None else timeout
        poll_frequency = constants.POLL_FREQUENCY if poll_frequency is None else poll_frequency
        ignored_exceptions = constants.IGNORED_EXCEPTIONS if ignored_exceptions is None else ignored_exceptions
        return WebDriverWait(self.wrapped_driver, timeout, poll_frequency, ignored_exceptions)

    def wait_for_new_window(self, current_handles, timeout=None):
        _log.debug("wait for: new window (current_handles=%s)", current_handles)
        timeout = constants.WINDOW_WAIT_TIMEOUT if timeout is None else timeout
        return self.wait(timeout).until(EC.new_window_is_opened(current_handles))

    def wait_for_number_of_windows_to_be(self, expected_number, timeout=None):
        timeout = constants.WINDOW_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for: number of windows to be '%s' timeout=%s", expected_number, timeout)
        return self.wait(timeout).until(EC.number_of_windows_to_be(expected_number))

    def wait_for_url_change(self, url_before_change: str, timeout=None):
        _log.debug("wait for: URL change url_before_change='%s'", url_before_change)
        timeout = constants.URL_WAIT_TIMEOUT if timeout is None else timeout
        return self.wait(timeout).until(EC.url_changes(url_before_change))

    def wait_for_url_contains(self, part: str, timeout=None):
        _log.debug("wait for: URL contains part='%s'", part)
        timeout = constants.URL_WAIT_TIMEOUT if timeout is None else timeout
        return self.wait(timeout).until(EC.url_contains(part))

    def wait_for_url_matches(self, pattern: str, timeout=None):
        _log.debug("wait for: URL matches pattern='%s'", pattern)
        timeout = constants.URL_WAIT_TIMEOUT if timeout is None else timeout
        return self.wait(timeout).until(EC.url_matches(pattern))

    def wait_for_page_load(self):
        js_condition.wait_for_page_load(self.wrapped_driver)

    def wait_for_alert(self, timeout=None) -> Alert:
        timeout = constants.ALERT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for alert: timeout=%s", timeout)
        return self.wait(timeout).until(EC.alert_is_present())

    def wait_for_element(self, locator, timeout=None) -> WebElement:
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for element: locator=%s, timeout=%s", locator, timeout)
        return self.wait(timeout).until(EC.presence_of_element_located(locator))

    def wait_for_visible_element(self, locator, timeout=None) -> WebElement:
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for visible element: locator=%s, timeout=%s", locator, timeout)
        return self.wait(timeout).until(EC.visibility_of_element_located(locator))

    def wait_for_elements(self, locator, timeout=None) -> List[WebElement]:
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for elements: locator=%s, timeout=%s", locator, timeout)
        return self.wait(timeout).until(EC.presence_of_all_elements_located(locator))

    def wait_for_visible_elements(self, locator, timeout=None) -> List[WebElement]:
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for visible elements: locator=%s, timeout=%s", locator, timeout)
        return self.wait(timeout).until(EC.visibility_of_any_elements_located(locator))

    def wait_for_clickable_element(self, locator, timeout=None) -> WebElement:
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for clickable element: locator=%s, timeout=%s", locator, timeout)
        return self.wait(timeout).until(EC.element_to_be_clickable(locator))

    def wait_for_invisibility_of_element(self, element, timeout=None):
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for invisibility of element: timeout=%s", timeout)
        return self.wait(timeout).until(EC.invisibility_of_element(element))

    def wait_for_invisibility_of_element_located(self, locator, timeout=None):
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for invisibility of element located: %s timeout=%s", locator, timeout)
        return self.wait(timeout).until(EC.invisibility_of_element_located(locator))

    def wait_for_staleness_of(self, element, timeout=None):
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for staleness of element: timeout=%s", timeout)
        return self.wait(timeout).until(EC.staleness_of(element))

    def wait_for_text_to_be_present_in_element(self, locator, text, timeout=None):
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for text to be present in element: locator=%s, text='%s', timeout=%s", locator, text, timeout)
        return self.wait(timeout).until(EC.text_to_be_present_in_element(locator, text))

    def wait_for_text_to_be_present_in_element_value(self, locator, text, timeout=None):
        timeout = constants.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout
        _log.debug("wait for text to be present in element value: locator=%s, text='%s', timeout=%s",
                   locator, text, timeout)
        return self.wait(timeout).until(EC.text_to_be_present_in_element_value(locator, text))

    def find_element(self, by=By.ID, value=None) -> WebElement:
        return self.wrapped_driver.find_element(by=by, value=value)

    def find_element_by_class_name(self, name) -> WebElement:
        return self.wrapped_driver.find_element_by_class_name(name)

    def find_element_by_css_selector(self, css_selector) -> WebElement:
        return self.wrapped_driver.find_element_by_css_selector(css_selector)

    def find_element_by_id(self, id_) -> WebElement:
        return self.wrapped_driver.find_element_by_id(id_)

    def find_element_by_link_text(self, link_text) -> WebElement:
        return self.wrapped_driver.find_element_by_link_text(link_text)

    def find_element_by_name(self, name) -> WebElement:
        return self.wrapped_driver.find_element_by_name(name)

    def find_element_by_partial_link_text(self, link_text) -> WebElement:
        return self.wrapped_driver.find_element_by_partial_link_text(link_text)

    def find_element_by_tag_name(self, name) -> WebElement:
        return self.wrapped_driver.find_element_by_tag_name(name)

    def find_element_by_xpath(self, xpath) -> WebElement:
        return self.wrapped_driver.find_element_by_xpath(xpath)

    def find_elements(self, by=By.ID, value=None) -> List[WebElement]:
        return self.wrapped_driver.find_elements(by=by, value=value)

    def find_elements_by_class_name(self, name) -> List[WebElement]:
        return self.wrapped_driver.find_elements_by_class_name(name)

    def find_elements_by_css_selector(self, css_selector) -> List[WebElement]:
        return self.wrapped_driver.find_elements_by_css_selector(css_selector)

    def find_elements_by_id(self, id_) -> List[WebElement]:
        return self.wrapped_driver.find_elements_by_id(id_)

    def find_elements_by_link_text(self, text) -> List[WebElement]:
        return self.wrapped_driver.find_elements_by_link_text(text)

    def find_elements_by_name(self, name) -> List[WebElement]:
        return self.wrapped_driver.find_elements_by_name(name)

    def find_elements_by_partial_link_text(self, link_text) -> List[WebElement]:
        return self.wrapped_driver.find_elements_by_partial_link_text(link_text)

    def find_elements_by_tag_name(self, name) -> List[WebElement]:
        return self.wrapped_driver.find_elements_by_tag_name(name)

    def find_elements_by_xpath(self, xpath) -> List[WebElement]:
        return self.wrapped_driver.find_elements_by_xpath(xpath)
