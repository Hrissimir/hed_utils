from unittest import TestCase

from hed_utils.selenium.utils.shared_driver import SharedDriver


class SharedDriverTest(TestCase):

    def setUp(self) -> None:
        SharedDriver.set_instance(None)

    def test_wrapped_driver(self):
        mock_driver = object()
        SharedDriver.set_instance(mock_driver)
        self.assertIs(mock_driver, SharedDriver().wrapped_driver)

    def test_instance_is_shared(self):
        driver1 = SharedDriver()
        driver2 = SharedDriver()
        self.assertIsNone(driver1.wrapped_driver)
        self.assertIsNone(driver2.wrapped_driver)

        instance = object()
        SharedDriver.set_instance(instance)
        self.assertIs(instance, driver1.wrapped_driver)
        self.assertIs(instance, driver2.wrapped_driver)
