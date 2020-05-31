import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import skipIf
from unittest.mock import patch

from selenium.webdriver import Opera

from hed_utils.selenium import opera_driver


@skipIf(not shutil.which("opera"), reason="Opera not installed")
@skipIf(not shutil.which("operadriver"), reason="Opera driver not installed")
def test_create_instance():
    with patch("atexit.register", autospec=True)as mock_register:
        driver = opera_driver.create_instance(headless=True)
        try:
            assert type(driver) is Opera
            mock_register.assert_called_once_with(driver.quit)
        finally:
            driver.quit()


@skipIf(not shutil.which("opera"), reason="Opera not installed")
@skipIf(not shutil.which("operadriver"), reason="Opera driver not installed")
def test_create_instance_with_user_data_dir():
    with TemporaryDirectory() as tmp_dir:
        user_data_dir = Path(tmp_dir).joinpath("opera_user_data_dir")
        assert not user_data_dir.exists()
        driver = opera_driver.create_instance(headless=True, user_data_dir=user_data_dir)
        try:
            assert user_data_dir.exists()
        finally:
            driver.quit()
