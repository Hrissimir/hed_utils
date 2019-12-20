import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)8s | %(module)25s:%(lineno)-5s | %(message)s"

LOGGER = logging.getLogger("hed_utils")

debug = LOGGER.debug
error = LOGGER.error
exception = LOGGER.exception
info = LOGGER.info
warning = LOGGER.warning


def add_file_handler(logger: logging.Logger, file: str, level: int = None, log_format: str = None):
    """Creates and attaches file handler to the passed logger."""

    handler = logging.FileHandler(file)
    formatter = logging.Formatter(log_format or LOG_FORMAT)
    handler.setLevel(level or logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def init(level=None, log_format=None, console=True, file=None):
    """Performs basic logging config, then disables selenium-related debug logs"""

    level = level or logging.DEBUG
    log_format = log_format or LOG_FORMAT

    if console:
        logging.basicConfig(level=level, format=log_format, stream=sys.stdout)
    else:
        logging.basicConfig(level=level, format=log_format)

    selenium_logger = logging.getLogger("selenium.webdriver.remote.remote_connection")
    selenium_logger.disabled = True

    urllib3_logger = logging.getLogger("urllib3.connectionpool")
    urllib3_logger.disabled = True

    oauth2client_logger = logging.getLogger("oauth2client.client")
    oauth2client_logger.disabled = True

    if file:
        add_file_handler(logging.getLogger(), file, level, log_format)

    debug("log initialized!")
