import hashlib
from collections import namedtuple
from typing import List, Dict

from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

Location = namedtuple("Location", "x y")

Size = namedtuple("Size", "height width")


class ElementWrapper(WebElement):

    def __init__(self, element: WebElement):
        self._wrapped_element = element.wrapped_element if isinstance(element, ElementWrapper) else element

    def __eq__(self, element):
        return hasattr(element, 'id') and self.id == element.id

    def __hash__(self):
        return int(hashlib.md5(self.id.encode('utf-8')).hexdigest(), 16)

    def __repr__(self):
        element = self.wrapped_element
        return f"{type(self).__name__}(element={repr(element)})"

    def __getitem__(self, name):
        element = self.wrapped_element
        return element.get_attribute(name)

    @property
    def _parent(self):
        return self.wrapped_element._parent

    @property
    def _id(self):
        return self.wrapped_element._id

    @property
    def _w3c(self):
        return self.wrapped_element._w3c

    @property
    def wrapped_element(self) -> WebElement:
        return self._wrapped_element

    @property
    def id(self):
        return self.wrapped_element.id

    @property
    def location_once_scrolled_into_view(self):
        return self.wrapped_element.location_once_scrolled_into_view

    @property
    def size(self) -> Dict[str, int]:
        return self.wrapped_element.size

    @property
    def location(self) -> Dict[str, int]:
        return self.wrapped_element.location

    @property
    def rect(self) -> Dict[str, int]:
        return self.wrapped_element.rect

    @property
    def screenshot_as_base64(self) -> str:
        return self.wrapped_element.screenshot_as_base64

    @property
    def screenshot_as_png(self) -> bytes:
        return self.wrapped_element.screenshot_as_png

    @property
    def tag_name(self) -> str:
        return self.wrapped_element.tag_name

    @property
    def parent(self) -> WebDriver:
        """Internal reference to the WebDriver instance this element was found from."""

        return self.wrapped_element.parent

    @property
    def text(self) -> str:
        """The text of the element."""

        element = self.wrapped_element
        if element.tag_name in {"input", "textarea"}:
            return element.get_attribute("value")

        return element.text or element.get_attribute("innerText")

    @property
    def innerText(self) -> str:
        return self.get_attribute("innerText")

    @property
    def outerHTML(self) -> str:
        """Returns the HTML source code of the element."""

        return self.get_attribute("outerHTML")

    @property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.outerHTML, "lxml")

    @property
    def parent_element(self) -> "ElementWrapper":
        return self.find_element_by_xpath("./..")

    @property
    def child_elements(self) -> List["ElementWrapper"]:
        return self.find_elements_by_xpath("./*")

    def clear(self):
        self.wrapped_element.clear()

    def click(self):
        self.wrapped_element.click()

    def submit(self):
        self.wrapped_element.submit()

    def get_property(self, name):
        return self.wrapped_element.get_property(name)

    def get_attribute(self, name):
        return self.wrapped_element.get_attribute(name)

    def value_of_css_property(self, property_name):
        return self.wrapped_element.value_of_css_property(property_name)

    def is_displayed(self) -> bool:
        return self.wrapped_element.is_displayed()

    def is_enabled(self) -> bool:
        return self.wrapped_element.is_enabled()

    def is_selected(self) -> bool:
        return self.wrapped_element.is_selected()

    def send_keys(self, *value):
        self.wrapped_element.send_keys(*value)

    def screenshot(self, filename) -> bool:
        return self.wrapped_element.screenshot(filename)

    def as_select(self) -> Select:
        return Select(self.wrapped_element)

    def get_location(self) -> Location:
        """Returns the location of the element as named tuple"""

        return Location(**self.wrapped_element.location)

    def get_size(self) -> Size:
        """Returns the Size of the element as named tuple"""

        return Size(**self.wrapped_element.size)

    def hide(self):
        """Applies a CSS style through JS to effectively hide the element from the page."""

        def remove_display_from_style(_style: str) -> str:
            if "display:" in _style:
                start_idx = _style.index("display") + len("display")
                end_idx = (_style.index(";", __start=start_idx) + 1) if (";" in _style) else len(_style) - 1
                return _style[:start_idx] + _style[end_idx:]
            return _style

        element = self.wrapped_element
        style = element.get_attribute("style")
        style = remove_display_from_style(style)
        style = "display: none;" + style
        element.parent.execute_script(f"arguments[0].setAttribute('style', '{style}');", element)

    def hover(self):
        """Hovers the element with the mouse. (Can be used to activate tooltips)."""

        element = self.wrapped_element
        ActionChains(element.parent).move_to_element(element).pause(2).perform()

    def scroll_into_view(self):
        """Scrolls the element into view using JS."""

        element = self.wrapped_element
        element.parent.execute_script("arguments[0].scrollIntoView();", element)

    def find_element_by_id(self, id_) -> "ElementWrapper":
        return ElementWrapper(self.wrapped_element.find_element_by_id(id_))

    def find_elements_by_id(self, id_) -> List["ElementWrapper"]:
        return [ElementWrapper(el) for el in self.wrapped_element.find_elements_by_id(id_)]

    def find_element_by_name(self, name) -> "ElementWrapper":
        return ElementWrapper(self.wrapped_element.find_element_by_name(name))

    def find_elements_by_name(self, name) -> List["ElementWrapper"]:
        return [ElementWrapper(el) for el in self.wrapped_element.find_elements_by_name(name)]

    def find_element_by_link_text(self, link_text) -> "ElementWrapper":
        return ElementWrapper(self.wrapped_element.find_element_by_link_text(link_text))

    def find_elements_by_link_text(self, link_text) -> List["ElementWrapper"]:
        return [ElementWrapper(el) for el in self.wrapped_element.find_elements_by_link_text(link_text)]

    def find_element_by_partial_link_text(self, link_text) -> "ElementWrapper":
        return ElementWrapper(self.wrapped_element.find_element_by_partial_link_text(link_text))

    def find_elements_by_partial_link_text(self, link_text) -> List["ElementWrapper"]:
        return [ElementWrapper(el) for el in self.wrapped_element.find_elements_by_partial_link_text(link_text)]

    def find_element_by_tag_name(self, name) -> "ElementWrapper":
        return ElementWrapper(self.wrapped_element.find_element_by_tag_name(name))

    def find_elements_by_tag_name(self, name) -> List["ElementWrapper"]:
        return [ElementWrapper(el) for el in self.wrapped_element.find_elements_by_tag_name(name)]

    def find_element_by_xpath(self, xpath) -> "ElementWrapper":
        return ElementWrapper(self.wrapped_element.find_element_by_xpath(xpath))

    def find_elements_by_xpath(self, xpath) -> List["ElementWrapper"]:
        return [ElementWrapper(el) for el in self.wrapped_element.find_elements_by_xpath(xpath)]

    def find_element_by_class_name(self, name) -> "ElementWrapper":
        return ElementWrapper(self.wrapped_element.find_element_by_class_name(name))

    def find_elements_by_class_name(self, name) -> List["ElementWrapper"]:
        return [ElementWrapper(el) for el in self.wrapped_element.find_elements_by_class_name(name)]

    def find_element_by_css_selector(self, css_selector) -> "ElementWrapper":
        return ElementWrapper(self.wrapped_element.find_element_by_css_selector(css_selector))

    def find_elements_by_css_selector(self, css_selector) -> List["ElementWrapper"]:
        return [ElementWrapper(el) for el in self.wrapped_element.find_elements_by_css_selector(css_selector)]

    def find_element(self, by=By.ID, value=None) -> "ElementWrapper":
        return ElementWrapper(self.wrapped_element.find_element(by, value))

    def find_elements(self, by=By.ID, value=None) -> List["ElementWrapper"]:
        return [ElementWrapper(el) for el in self.wrapped_element.find_elements(by, value)]
