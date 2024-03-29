import itertools
import re
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import Mock, call

import pytest

from hed_utils.support import time_tool
from hed_utils.support.time_tool import TimedeltaParser


def test_parse_stamp():
    fmt = "%Y-%m-%d %H:%M:%S"
    stamp = time_tool.get_timestamp_float()
    result = time_tool.parse_numeric_timestamp(stamp, fmt)
    assert re.fullmatch(r"[\d]{4}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}:[\d]{2}", result)


def test_parse_tamp_raises():
    with pytest.raises(TypeError):
        time_tool.parse_numeric_timestamp(None)

    with pytest.raises(ValueError):
        time_tool.parse_numeric_timestamp("-23")

    with pytest.raises(ValueError):
        time_tool.parse_numeric_timestamp(-2)

    with pytest.raises(ValueError):
        time_tool.parse_numeric_timestamp(-1.2)


def test_get_local_tz_name():
    assert "Europe" in time_tool.get_local_tz_name()


def test_get_local_datetime():
    local_dt = time_tool.get_local_datetime()
    assert isinstance(local_dt, datetime)


class TestTimedeltaParser(TestCase):
    DATA_SET = list(itertools.product(
        TimedeltaParser.WEEK_COMPONENTS,
        TimedeltaParser.DAY_COMPONENTS,
        TimedeltaParser.HOUR_COMPONENTS,
        TimedeltaParser.MINUTE_COMPONENTS,
        TimedeltaParser.SECOND_COMPONENTS)
    )

    def test_parse(self):
        text_template = "1{0} 2 {1} 3{2} 4{3} 5 {4}"
        expected_value = timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5)

        for item in self.DATA_SET:
            time_text = text_template.format(*item)
            parsed_value = TimedeltaParser.parse(time_text)

            assert parsed_value == expected_value


def test_busy_wait():
    """Tests waiter.stopwatch as side-effect"""

    from timeit import default_timer as now

    duration = 0.2

    start = now()
    time_tool.busy_wait(duration)
    took = now() - start

    took_vs_duration_percent = (took / duration) * 100
    assert took_vs_duration_percent > 99.999


def test_poll_for_result_returns_result():
    obj = object()

    def func():
        return obj

    assert time_tool.poll_for_result(func, timeout_seconds=1) is obj


def test_poll_for_result_returns_default_on_timeout():
    obj = object()

    def func():
        return False

    result = time_tool.poll_for_result(func, timeout_seconds=0.1, default=obj)
    assert result is obj


def test_poll_for_result_raises_default_on_timeout():
    def func():
        return False

    with pytest.raises(TimeoutError):
        time_tool.poll_for_result(func, timeout_seconds=0.1, default=TimeoutError)

    with pytest.raises(RuntimeError):
        err = RuntimeError()
        time_tool.poll_for_result(func, timeout_seconds=0.1, default=err)


def test_poll_for_result_propagate_poll_errors():
    mock_func = Mock()
    mock_func.side_effect = RuntimeError
    with pytest.raises(RuntimeError):
        time_tool.poll_for_result(mock_func, timeout_seconds=0.1, ignore_errors=False)


def test_poll_for_result_ignore_all_poll_errors():
    mock_func = Mock()
    mock_func.side_effect = RuntimeError
    time_tool.poll_for_result(mock_func, timeout_seconds=0.1)


def test_poll_for_result_ignore_specific_poll_errors():
    mock_func = Mock()

    mock_func.side_effect = RuntimeError
    time_tool.poll_for_result(mock_func, timeout_seconds=0.1, ignore_errors=[RuntimeError])

    mock_func.side_effect = OSError
    with pytest.raises(OSError):
        time_tool.poll_for_result(mock_func, timeout_seconds=0.1, ignore_errors=[RuntimeError])


def test_poll_for_result_passes_args_kwargs():
    expected_call = call(1, 2, 3, fourth=4)
    args = (1, 2, 3)
    kwargs = dict(fourth=4)
    mock_func = Mock()
    time_tool.poll_for_result(mock_func, timeout_seconds=0.1, args=args, kwargs=kwargs)
    assert mock_func.mock_calls[0] == expected_call
