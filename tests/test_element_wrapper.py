from random import randint
from unittest import TestCase
from unittest.mock import MagicMock, call

from bs4 import BeautifulSoup
from ddt import ddt, data
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from hed_utils.selenium.wrappers.element_wrapper import ElementWrapper


@ddt
class ElementWrapperTest(TestCase):

    def setUp(self) -> None:
        self.mock_element = MagicMock(spec=WebElement)
        self.element_wrapper = ElementWrapper(self.mock_element)

    def tearDown(self) -> None:
        self.mock_element = None

    # Tests for the extra functionality in ElementWrapper

    def test_inner_text(self):
        expected_text = "element text"
        self.mock_element.get_attribute.return_value = expected_text
        actual_text = self.element_wrapper.innerText
        self.assertIs(expected_text, actual_text)
        self.mock_element.get_attribute.assert_called_once_with("innerText")

    def test_outer_html(self):
        expected_value = "<div> innerText </div>"
        self.mock_element.get_attribute.return_value = expected_value
        actual_value = self.element_wrapper.outerHTML
        self.assertIs(expected_value, actual_value)
        self.mock_element.get_attribute.assert_called_once_with("outerHTML")

    def test_soup(self):
        element_source = "<div> innerText </div>"
        self.mock_element.get_attribute.return_value = element_source
        expected_soup = BeautifulSoup(element_source, "lxml")
        actual_soup = self.element_wrapper.soup
        self.assertEqual(expected_soup, actual_soup)

    def test_parent_element(self):
        expected_parent = object()
        self.mock_element.find_element_by_xpath.return_value = expected_parent
        actual_parent = self.element_wrapper.parent_element
        self.assertIsInstance(actual_parent, ElementWrapper)
        self.assertIs(expected_parent, actual_parent.wrapped_element)
        self.mock_element.find_element_by_xpath.assert_called_once_with("./..")

    def test_child_elements(self):
        expected_children = [object(), object()]
        self.mock_element.find_elements_by_xpath.return_value = expected_children

        actual_children = self.element_wrapper.child_elements
        for expected_child, actual_child in zip(expected_children, actual_children):
            self.assertIsInstance(actual_child, ElementWrapper)
            self.assertIs(expected_child, actual_child.wrapped_element)

        self.mock_element.find_elements_by_xpath.assert_called_once_with("./*")

    def test_scroll_into_view(self):
        mock_parent = MagicMock(spec=WebDriver)
        self.mock_element.parent = mock_parent
        self.element_wrapper.scroll_into_view()
        mock_parent.execute_script.assert_called_once_with("arguments[0].scrollIntoView();", self.mock_element)

    # Tests for standard WebElement methods bellow:

    def test_eq(self):
        mock_id = str(randint(1, 999999999))
        self.mock_element.id = mock_id
        other_element = WebElement(None, mock_id)
        self.assertEqual(self.element_wrapper, other_element)

    def test_hash(self):
        mock_id = str(randint(1, 999999999))
        self.mock_element.id = mock_id
        other_element = WebElement(None, mock_id)
        self.assertEqual(hash(self.element_wrapper), hash(other_element))

    def test_private_id(self):
        mock_id = str(randint(1, 999999999))
        self.mock_element._id = mock_id
        self.assertEqual(mock_id, self.element_wrapper._id)

    def test_private_parent(self):
        mock_parent = object()
        self.mock_element._parent = mock_parent
        self.assertEqual(mock_parent, self.element_wrapper._parent)

    def test_private_w3c(self):
        mock_value = object()
        self.mock_element._w3c = mock_value
        self.assertEqual(mock_value, self.element_wrapper._w3c)

    def test_wrapped_element(self):
        self.assertIs(self.element_wrapper.wrapped_element, self.mock_element)

    def test_location(self):
        expected_location = object()
        self.mock_element.location = expected_location
        actual_location = self.element_wrapper.location
        self.assertIs(expected_location, actual_location)

    def test_location_once_scrolled_into_view(self):
        expected_location = object()
        self.mock_element.location_once_scrolled_into_view = expected_location
        actual_location = self.element_wrapper.location_once_scrolled_into_view
        self.assertIs(expected_location, actual_location)

    def test_id(self):
        expected_value = object()
        self.mock_element.id = expected_value
        actual_value = self.element_wrapper.id
        self.assertIs(expected_value, actual_value)

    def test_parent(self):
        expected_parent = object()
        self.mock_element.parent = expected_parent
        actual_parent = self.element_wrapper.parent
        self.assertIs(expected_parent, actual_parent)

    def test_rect(self):
        expected_rect = object()
        self.mock_element.rect = expected_rect
        actual_rect = self.element_wrapper.rect
        self.assertIs(expected_rect, actual_rect)

    def test_screenshot_as_base64(self):
        expected_screenshot = object()
        self.mock_element.screenshot_as_base64 = expected_screenshot
        actual_screenshot = self.element_wrapper.screenshot_as_base64
        self.assertIs(expected_screenshot, actual_screenshot)

    def test_screenshot_as_png(self):
        expected_screenshot = object()
        self.mock_element.screenshot_as_png = expected_screenshot
        actual_screenshot = self.element_wrapper.screenshot_as_png
        self.assertIs(expected_screenshot, actual_screenshot)

    def test_size(self):
        expected_size = object()
        self.mock_element.size = expected_size
        actual_size = self.element_wrapper.size
        self.assertIs(expected_size, actual_size)

    def test_tag_name(self):
        expected_value = object()
        self.mock_element.tag_name = expected_value
        actual_value = self.element_wrapper.tag_name
        self.assertIs(expected_value, actual_value)

    def test_text(self):
        expected_value = object()
        self.mock_element.text = expected_value
        actual_value = self.element_wrapper.text
        self.assertIs(expected_value, actual_value)

    def test_clear(self):
        self.element_wrapper.clear()
        self.mock_element.clear.assert_called_once_with()

    def test_click(self):
        self.element_wrapper.click()
        self.mock_element.click.assert_called_once_with()

    def test_submit(self):
        self.element_wrapper.submit()
        self.mock_element.submit.assert_called_once_with()

    def test_screenshot(self):
        filename = "screenshot-filename"
        expected_result = object()
        self.mock_element.screenshot.return_value = expected_result
        actual_result = self.element_wrapper.screenshot(filename)
        self.assertIs(expected_result, actual_result)
        self.mock_element.screenshot.assert_called_once_with(filename)

    def test_send_keys(self):
        keys = "input text" + Keys.ENTER
        self.mock_element.send_keys.side_effect = None
        self.element_wrapper.send_keys(keys)
        self.mock_element.send_keys.assert_called_once_with(keys)

    def test_get_attribute(self):
        expected_value = object()
        self.mock_element.get_attribute.return_value = expected_value
        attribute_name = "attr-name"
        actual_value = self.element_wrapper.get_attribute(attribute_name)
        self.assertIs(expected_value, actual_value)
        self.mock_element.get_attribute.assert_called_once_with(attribute_name)

    def test_get_property(self):
        expected_value = object()
        self.mock_element.get_property.return_value = expected_value
        property_name = "prop-name"
        actual_value = self.element_wrapper.get_property(property_name)
        self.assertIs(expected_value, actual_value)
        self.mock_element.get_property.assert_called_once_with(property_name)

    def test_value_of_css_property(self):
        expected_value = object()
        self.mock_element.value_of_css_property.return_value = expected_value
        property_name = "prop-name"
        actual_value = self.element_wrapper.value_of_css_property(property_name)
        self.assertIs(expected_value, actual_value)
        self.mock_element.value_of_css_property.assert_called_once_with(property_name)

    def test_is_displayed(self):
        expected_state = object()
        self.mock_element.is_displayed.return_value = expected_state
        actual_state = self.element_wrapper.is_displayed()
        self.assertIs(expected_state, actual_state)
        self.mock_element.is_displayed.assert_called_once_with()

    def test_is_enabled(self):
        expected_state = object()
        self.mock_element.is_enabled.return_value = expected_state
        actual_state = self.element_wrapper.is_enabled()
        self.assertIs(expected_state, actual_state)
        self.mock_element.is_enabled.assert_called_once_with()

    def test_is_selected(self):
        expected_state = object()
        self.mock_element.is_selected.return_value = expected_state
        actual_state = self.element_wrapper.is_selected()
        self.assertIs(expected_state, actual_state)
        self.mock_element.is_selected.assert_called_once_with()

    def test_find_element(self):
        by = object()
        locator = object()
        expected_element = object()
        self.mock_element.find_element.return_value = expected_element

        # assert discovered elements are returned as ElementWrapper instance
        actual_result = self.element_wrapper.find_element(by, locator)
        self.assertIsInstance(actual_result, ElementWrapper)
        self.assertIs(expected_element, actual_result.wrapped_element)

        # assert the .find_element call is delegated to the wrapped element
        expected_calls = [call(by, locator)]
        actual_calls = self.mock_element.find_element.mock_calls
        self.assertListEqual(expected_calls, actual_calls)

    def test_find_elements(self):
        by = object()
        locator = object()
        expected_element_1 = object()
        expected_element_2 = object()
        expected_elements = [expected_element_1, expected_element_2]
        self.mock_element.find_elements.return_value = expected_elements

        # assert discovered elements are returned as ElementWrapper instances
        actual_result = self.element_wrapper.find_elements(by, locator)
        for actual_element, expected_element in zip(actual_result, expected_elements):
            self.assertIsInstance(actual_element, ElementWrapper)
            self.assertIs(actual_element.wrapped_element, expected_element)

        # assert the .find_element call is delegated to the wrapped element
        expected_calls = [call(by, locator)]
        actual_calls = self.mock_element.find_elements.mock_calls
        self.assertListEqual(expected_calls, actual_calls)

    @data("find_element_by_class_name",
          "find_element_by_css_selector",
          "find_element_by_id",
          "find_element_by_link_text",
          "find_element_by_name",
          "find_element_by_partial_link_text",
          "find_element_by_tag_name",
          "find_element_by_xpath")
    def test_find_element_by(self, method_name):
        locator = object()
        expected_element = object()

        mock_method = getattr(self.mock_element, method_name)
        mock_method.return_value = expected_element

        # assert discovered elements are returned as ElementWrapper instance
        target_method = getattr(self.element_wrapper, method_name)

        actual_result = target_method(locator)
        self.assertIsInstance(actual_result, ElementWrapper)
        self.assertIs(expected_element, actual_result.wrapped_element)

        # assert the .find_element call is delegated to the wrapped element
        expected_calls = [call(locator)]
        actual_calls = mock_method.mock_calls
        self.assertListEqual(expected_calls, actual_calls)

    @data("find_elements_by_class_name",
          "find_elements_by_css_selector",
          "find_elements_by_id",
          "find_elements_by_link_text",
          "find_elements_by_name",
          "find_elements_by_partial_link_text",
          "find_elements_by_tag_name",
          "find_elements_by_xpath")
    def test_find_elements_by(self, method_name):

        locator = object()
        expected_element_1 = object()
        expected_element_2 = object()
        expected_elements = [expected_element_1, expected_element_2]
        mock_method = getattr(self.mock_element, method_name)
        mock_method.return_value = expected_elements

        # assert discovered elements are returned as ElementWrapper instances
        target_method = getattr(self.element_wrapper, method_name)
        actual_result = target_method(locator)
        for actual_element, expected_element in zip(actual_result, expected_elements):
            self.assertIsInstance(actual_element, ElementWrapper)
            self.assertIs(actual_element.wrapped_element, expected_element)

        # assert the .find_element call is delegated to the wrapped element
        expected_calls = [call(locator)]
        actual_calls = mock_method.mock_calls
        self.assertListEqual(expected_calls, actual_calls)
