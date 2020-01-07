from unittest import TestCase

from hed_utils.selenium.utils.shared_driver import SharedDriver


class SharedDriverTest(TestCase):

    def setUp(self) -> None:
        SharedDriver.set_instance(None)

    def test_singleton(self):
        driver1 = SharedDriver()
        driver2 = SharedDriver()
        self.assertIs(driver1, driver2)

    def test_wrapped_driver(self):
        mock_driver = object()
        SharedDriver.set_instance(mock_driver)
        self.assertIs(mock_driver, SharedDriver().wrapped_driver)
