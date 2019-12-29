import inspect

from selenium.common import exceptions

ALERT_WAIT_TIMEOUT = 5.000

DEFAULT_WAIT_TIMEOUT = 30.000

ELEMENT_WAIT_TIMEOUT = 15.000  # 15 seconds

WINDOW_WAIT_TIMEOUT = 5.00

URL_WAIT_TIMEOUT = 10.000

POLL_FREQUENCY = 0.010  # 10 millis

IGNORED_EXCEPTIONS = tuple(
    member
    for name, member
    in inspect.getmembers(exceptions, predicate=inspect.isclass)
)
