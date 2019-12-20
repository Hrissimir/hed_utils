import re
import time
from datetime import datetime, timedelta
from timeit import default_timer as now
from typing import Union, Optional

import pytz
import tzlocal


def parse_numeric_timestamp(value: Union[int, float, str], target_fmt="%Y-%m-%d %H:%M:%S") -> str:
    """Format 'Seconds'-based timestamp to a human readable text form.

    Arguments:
        value(float,str):   The numeric stamp value. Can be int,float,str and it's converted to float later
        target_fmt(str):    The desired result format.
    Returns:
        obj(str):           The timestamp converted to date-time string accordingly.
    """

    if not isinstance(value, (int, float, str)):
        raise TypeError(value)

    if not isinstance(value, float):
        value = float(value)

    if value <= 0:
        raise ValueError(value)

    return datetime.fromtimestamp(value).strftime(target_fmt)


def get_timestamp_float() -> float:
    """Returns a float timestamp based on epochi seconds"""

    return datetime.timestamp(datetime.now())


def utc_moment() -> datetime:
    """Returns utc datetime instance with proper tzinfo"""

    return datetime.utcnow().replace(tzinfo=pytz.utc)


def get_local_tz_name() -> str:
    """Returns the time-zone name of the current system."""

    return tzlocal.get_localzone().zone


def localize(naive_datetime: datetime, tz_name: Optional[str] = None) -> datetime:
    """Creates tz-aware datetime instance from the passed one."""

    tz_name = tz_name or get_local_tz_name()
    tz = pytz.timezone(tz_name)
    return tz.localize(naive_datetime)


def get_local_datetime() -> datetime:
    """Returns a tz-aware instance with tz set to the current system tz"""

    return localize(datetime.now())


def utc_to_tz(datetime_utc: datetime, tz_name: Optional[str] = None) -> datetime:
    """Converts utc-tz-aware datetime to local-tz-aware datetime, enabling accurate time calculations"""

    return datetime_utc.astimezone(pytz.timezone(tz_name))


class TimedeltaParser:
    WEEK_COMPONENTS = "weeks week w w.".split(" ")
    _week_matches = "|".join([c[1:] for c in WEEK_COMPONENTS])
    WEEKS_PATTERN = f"([\\d]+) ?w(?:{_week_matches})?"

    DAY_COMPONENTS = "days day d d.".split(" ")
    _day_matches = "|".join([c[1:] for c in DAY_COMPONENTS])
    DAYS_PATTERN = f"([\\d]+) ?d(?:{_day_matches})?"

    HOUR_COMPONENTS = "hours hour hrs h hrs. h.".split(" ")
    _hour_matches = "|".join([c[1:] for c in HOUR_COMPONENTS])
    HOURS_PATTERN = f"([\\d]+) ?h(?:{_hour_matches})?"

    MINUTE_COMPONENTS = "minutes mins min m min. m.".split(" ")
    _minute_matches = "|".join([c[1:] for c in MINUTE_COMPONENTS])
    MINUTES_PATTERN = f"([\\d]+) ?m(?:{_minute_matches})?"

    SECOND_COMPONENTS = "seconds second secs sec s sec. s.".split(" ")
    _second_matches = "|".join([c[1:] for c in SECOND_COMPONENTS])
    SECONDS_PATTERN = f"([\\d]+) ?s(?:{_second_matches})?"

    @classmethod
    def get_weeks_component(cls, text: str) -> int:
        text = text.replace(".", "")
        matches = re.findall(cls.WEEKS_PATTERN, text)
        return int(matches[0]) if (len(matches) == 1) else 0

    @classmethod
    def get_days_component(cls, text: str) -> int:
        text = text.replace(".", "")
        matches = re.findall(cls.DAYS_PATTERN, text)
        return int(matches[0]) if (len(matches) == 1) else 0

    @classmethod
    def get_hours_component(cls, text: str) -> int:
        text = text.replace(".", "")
        matches = re.findall(cls.HOURS_PATTERN, text)
        return int(matches[0]) if (len(matches) == 1) else 0

    @classmethod
    def get_minutes_component(cls, text) -> int:
        matches = re.findall(cls.MINUTES_PATTERN, text)
        return int(matches[0]) if (len(matches) == 1) else 0

    @classmethod
    def get_seconds_component(cls, text) -> int:
        matches = re.findall(cls.SECONDS_PATTERN, text)
        return int(matches[0]) if (len(matches) == 1) else 0

    @classmethod
    def parse(cls, text: str) -> timedelta:
        text = text.replace("ago", "").strip()
        seconds = cls.get_seconds_component(text)
        minutes = cls.get_minutes_component(text)
        hours = cls.get_hours_component(text)
        days = cls.get_days_component(text)
        weeks = cls.get_weeks_component(text)
        return timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks)


def countdown_timer(duration_seconds: Union[int, float]):
    """Creates a callable indicating if the duration has elapsed since it's creation.

    Arguments:
        duration_seconds(int,float):    The duration after which the callable should start returning True

    Returns:
        Callable whose boolean result will indicate if the duration had elapsed.

    Example:
        >>> has_elapsed = countdown_timer(1)

        >>> while not has_elapsed(): continue
    """

    end_time = now() + duration_seconds

    def elapsed():
        return now() > end_time

    return elapsed


class Timer:
    """Credits to recipe 13.13 in 'Python Cookbook, Third Edition' by David Beazley and Brian K. Jones"""

    def __init__(self, func=time.perf_counter):
        self.elapsed = 0.0
        self._func = func
        self._start = None

    def start(self):
        if self._start is not None:
            raise RuntimeError('Already started')
        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError('Not started')
        end = self._func()
        self.elapsed += end - self._start
        self._start = None

    def reset(self):
        self.elapsed = 0.0

    @property
    def is_running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        if self.is_running:
            self.stop()
