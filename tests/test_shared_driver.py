from unittest import TestCase

from hed_utils.selenium.utils.shared_driver import SharedDriver


class SharedDriverTest(TestCase):

    def setUp(self) -> None:
        SharedDriver.set_driver(None)

    def test_singleton(self):
        driver1 = SharedDriver()
        driver2 = SharedDriver.get_instance()
        driver3 = SharedDriver().get_instance()
        self.assertIs(driver1, driver2)
        self.assertIs(driver3, driver2)

    def test_wrapped_driver(self):
        mock_driver = object()
        SharedDriver.set_driver(mock_driver)
        shared_driver = SharedDriver()
        self.assertIs(mock_driver, shared_driver.wrapped_driver)
        shared_driver2 = SharedDriver()
        self.assertIs(mock_driver, shared_driver2.wrapped_driver)
