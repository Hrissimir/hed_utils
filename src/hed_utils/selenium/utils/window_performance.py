import logging
from collections import namedtuple
from time import perf_counter
from typing import Any, Dict, List, Tuple

from selenium.webdriver.remote.webdriver import WebDriver
from tabulate import tabulate

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

Event = namedtuple("Event", "name start end")

TIMING_EVENTS = {
    "unload": ("unloadEventStart", "unloadEventEnd"),
    "redirect": ("redirectStart", "redirectEnd"),
    "domain": ("domainLookupStart", "domainLookupEnd"),
    "connect": ("connectStart", "connectEnd"),
    "request": ("requestStart", "responseStart"),
    "response": ("responseStart", "responseEnd"),
    "dom": ("domLoading", "domComplete"),
    "load": ("loadEventStart", "loadEventEnd"),
    "navigation": ("navigationStart", "loadEventEnd")
}


def get_timings(driver: WebDriver) -> Dict[str, int]:
    def _get_duration(start: str, end: str) -> int:
        try:
            event_end = driver.execute_script(f"return window.performance.timing.{end};")
            event_start = driver.execute_script(f"return window.performance.timing.{start};")
            return event_end - event_start
        except TypeError:
            return -1

    return {event: _get_duration(start_var, end_var)
            for event, (start_var, end_var)
            in TIMING_EVENTS.items()}


def timing_events_completed(driver: WebDriver) -> bool:
    return all([(duration >= 0)
                for name, duration
                in get_timings(driver).items()])


def get_performance_entries(driver: WebDriver) -> List[Dict[str, Any]]:
    return driver.execute_script("return window.performance.getEntries();")


def _busy_wait(duration):
    end_time = perf_counter() + duration
    while perf_counter() < end_time:
        continue


def wait_for_timing_events(
        driver: WebDriver, timeout=10, poll_frequency=0.01, confirmations_needed=3) -> Dict[str, int]:
    remaining = timeout
    start = perf_counter()
    confirmations_received = 0
    while (remaining > 0) and (confirmations_received < confirmations_needed):
        _busy_wait(poll_frequency)
        if timing_events_completed(driver):
            confirmations_received += 1
        else:
            confirmations_received = 0
        end = perf_counter()
        remaining = remaining - (end - start)
        start = end

    return get_timings(driver)


def wait_for_performance_entries(
        driver: WebDriver, timeout=5, poll_frequency=0.025, confirmations_needed=4) -> List[Dict[str, Any]]:
    confirmations_received = 0
    remaining = timeout
    start = perf_counter()
    known_entries = get_performance_entries(driver)
    while (remaining > 0) and (confirmations_received < confirmations_needed):
        _busy_wait(poll_frequency)
        current_entries = get_performance_entries(driver)
        if known_entries == current_entries:
            confirmations_received += 1
        else:
            confirmations_received = 0
            known_entries = current_entries
        end = perf_counter()
        remaining = remaining - (end - start)
        start = end

    return known_entries


def _format_timings(timings: Dict[str, int]) -> str:
    return tabulate(list(timings.items()), headers="NAME DURATION".split())


def _format_entries(entries: List[Dict[str, Any]]) -> str:
    return tabulate(tabular_data=entries, headers="keys")


def get_load_stats(driver: WebDriver, url: str) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:
    _log.info("getting load stats of url: '%s'", url)
    driver.get(url)
    _log.info("waiting for timing events to complete...")
    timings = wait_for_timing_events(driver)
    _log.info("timing events completed:\n%s", _format_timings(timings))
    entries = wait_for_performance_entries(driver)
    _log.info("performance entries stopped changing:\n%s", _format_entries(entries))
    return timings, entries


def main():
    from hed_utils.selenium import chrome_driver, SharedDriver
    from hed_utils.support import log
    log.init(logging.DEBUG)

    driver = chrome_driver.create_instance()
    SharedDriver.set_instance(driver)

    urls = ["https://youtube.com",
            "https://facebook.com",
            "https://stackoverflow.com"]

    for url in urls:
        get_load_stats(SharedDriver(), url)


if __name__ == '__main__':
    main()
