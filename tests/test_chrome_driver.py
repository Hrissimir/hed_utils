from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from selenium.webdriver import Chrome

from hed_utils.selenium import chrome_driver


def test_create_instance():
    with patch("atexit.register", autospec=True)as mock_register:
        driver = chrome_driver.create_instance(headless=True)
        try:
            assert type(driver) is Chrome
            mock_register.assert_called_once_with(driver.quit)
        finally:
            driver.quit()


def test_create_instance_with_downloads_dir():
    with TemporaryDirectory() as tmp_dir:
        downloads_dir = Path(tmp_dir).joinpath("chrome_downloads")
        assert not downloads_dir.exists()
        driver = chrome_driver.create_instance(headless=True, downloads_dir=downloads_dir)
        try:
            assert downloads_dir.exists()
        finally:
            driver.quit()


def test_create_instance_with_user_data_dir():
    with TemporaryDirectory() as tmp_dir:
        user_data_dir = Path(tmp_dir).joinpath("chrome_user_data_dir")
        assert not user_data_dir.exists()
        driver = chrome_driver.create_instance(headless=True, user_data_dir=user_data_dir)
        try:
            assert user_data_dir.exists()
        finally:
            driver.quit()
