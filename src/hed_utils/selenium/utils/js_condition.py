import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from hed_utils.selenium import constants
from hed_utils.support.time_tool import Timer

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

PAGE_LOAD_SEQUENCE = {
    "Wait for document ready state": dict(
        script="return document.readyState == 'complete';",
        timeout=10,
        on_success="Wait for jQuery defined",
        on_fail="Wait for jQuery defined",
        confirmations_needed=2,
    ),
    "Wait for jQuery defined": dict(
        script="return !(typeof jQuery === 'undefined' || jQuery === null);",
        timeout=0.5,
        on_success="Wait for jQuery.active defined",
        on_fail="Wait for Angular defined",
        confirmations_needed=1,
    ),
    "Wait for jQuery.active defined": dict(
        script="return !(typeof jQuery.active === 'undefined' || jQuery.active === null);",
        timeout=0.5,
        on_success="Wait for jQuery.active == 0",
        on_fail="Wait for Angular defined",
        confirmations_needed=1,
    ),
    "Wait for jQuery.active == 0": dict(
        script="return window.jQuery.active == 0;",
        timeout=5,
        on_success="Wait for jQuery animations",
        on_fail="Wait for jQuery animations",
        confirmations_needed=2
    ),
    "Wait for jQuery animations": dict(
        script="return jQuery(':animated').length == 0;",
        timeout=5,
        on_success="Wait for Angular defined",
        on_fail="Wait for Angular defined",
        confirmations_needed=2
    ),
    "Wait for Angular defined": dict(
        script="return !(typeof angular === 'undefined' || angular === null);",
        timeout=0.1,
        on_success="Wait for Angular ready",
        on_fail="Wait for Angular5 defined",
        confirmations_needed=1,
    ),
    "Wait for Angular ready": dict(
        script="return angular.element(document).injector().get('$http').pendingRequests.length == 0;",
        timeout=5,
        on_success="Wait for Angular5 defined",
        on_fail="Wait for Angular5 defined",
        confirmations_needed=2
    ),
    "Wait for Angular5 defined": dict(
        script="return (typeof getAllAngularRootElements !== 'undefined') "
               "&& (getAllAngularRootElements()[0].attributes['ng-version'] != undefined);",
        timeout=0.1,
        on_success="Wait for Angular5 ready",
        on_fail=None,
        confirmations_needed=1
    ),
    "Wait for Angular5 ready": dict(
        script="return window.getAllAngularTestabilities().findIndex(x=>!x.isStable()) == -1;",
        timeout=5,
        on_success=None,
        on_fail=None,
        confirmations_needed=2
    )
}


class JsCondition:

    def __init__(self, script: str, confirmations_needed=1):
        self.script = script
        self.confirmations_needed = confirmations_needed
        self.confirmations_received = 0

    def __call__(self, driver):
        if driver.execute_script(self.script):
            self.confirmations_received += 1
        else:
            self.confirmations_received = 0

        return self.confirmations_received == self.confirmations_needed


def wait_for_page_load(driver: WebDriver):
    _log.debug("wait for: page load...")
    if not driver:
        raise ValueError("No WebDriver was available to 'wait_for_page_to_load")

    def wait_for_condition(script, timeout, on_success, on_fail, confirmations_needed):
        condition = JsCondition(script, confirmations_needed)
        try:
            WebDriverWait(driver, timeout, poll_frequency=constants.POLL_FREQUENCY).until(condition)
            return on_success
        except TimeoutException:
            return on_fail

    wait_history = []
    current_state = "Wait for document ready state"

    with Timer() as total_time:

        while True:
            condition_details = PAGE_LOAD_SEQUENCE[current_state]

            with Timer() as current_time:
                next_state = wait_for_condition(**condition_details)

            success = condition_details["on_success"] == next_state
            wait_history.append(f"('{current_state}' -> {success} in {current_time.elapsed:.3f} s.)")

            if not next_state:
                break

            current_state = next_state

    _log.debug("page loaded in %.3f s. %s", total_time.elapsed, ", ".join(wait_history))
