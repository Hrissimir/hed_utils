from unittest import TestCase

from hed_utils.selenium.drivers.shared_driver import SharedDriver


class SharedDriverTest(TestCase):

    def setUp(self) -> None:
        SharedDriver.set_instance(None)

    def test_set_get_instance(self):
        mock_instance = object()
        SharedDriver.set_instance(mock_instance)
        self.assertIs(mock_instance, SharedDriver.get_instance())

    def test_wrapped_driver(self):
        mock_instance = object()
        SharedDriver.set_instance(mock_instance)
        shared_driver = SharedDriver()
        self.assertIs(mock_instance, shared_driver.wrapped_driver)
        shared_driver2 = SharedDriver()
        self.assertIs(shared_driver.wrapped_driver, shared_driver2.wrapped_driver)
