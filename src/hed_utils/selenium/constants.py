import inspect
import logging

from selenium.common import exceptions

SELENIUM_EXCEPTIONS = tuple(member
                            for name, member
                            in inspect.getmembers(exceptions, predicate=inspect.isclass))

IGNORED_EXCEPTIONS = SELENIUM_EXCEPTIONS

POLL_FREQUENCY = 0.010  # 10 millis

DEFAULT_WAIT_TIMEOUT = 30.000

ELEMENT_WAIT_TIMEOUT = 15.000  # 15 seconds

ALERT_WAIT_TIMEOUT = 5.000

URL_WAIT_TIMEOUT = 10.000

WINDOW_WAIT_TIMEOUT = 5.00

LOGGERS = [
    logging.getLogger("selenium.webdriver.remote.remote_connection"),
    logging.getLogger("urllib3.connectionpool")
]
