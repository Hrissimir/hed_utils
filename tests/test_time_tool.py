import itertools
import re
from datetime import datetime, timedelta
from unittest import TestCase

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


def test_convert_to_tz():
    datetime_utc = time_tool.utc_moment()
    datetime_converted = time_tool.utc_to_tz(datetime_utc, "Europe/Sofia")

    pattern = (
        r"time.struct_time\(tm_year=(\d+), tm_mon=(\d+), tm_mday=(\d+), "
        r"tm_hour=(\d+), tm_min=(\d+), tm_sec=(\d+),.*\)"
    )

    (u_year, u_month, u_day, u_hour, u_minute, u_second) = re.findall(pattern, str(datetime_utc.timetuple()))[0]
    (c_year, c_month, c_day, c_hour, c_minute, c_second) = re.findall(pattern, str(datetime_converted.timetuple()))[0]
    assert u_year == c_year
    assert u_month == c_month
    assert u_minute == c_minute
    assert u_second == u_second
    assert u_day == c_day or int(u_day) == int(c_day) - 1
    assert abs((int(c_hour) - 2) % 24) == int(u_hour)


def test_get_local_tz_name():
    expected_tzname = "Europe/Sofia"
    assert time_tool.get_local_tz_name() == expected_tzname


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
