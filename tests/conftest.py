# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for hed_utils.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

import atexit
from pathlib import Path
# import pytest
from tempfile import gettempdir

from hed_utils.support.profiler import Profiler

STATS_FILE = Path(gettempdir()).joinpath("conftest_profiler_stats.txt")

_profiler = Profiler()


@atexit.register
def save_stats():
    global _profiler
    _profiler.disable()
    STATS_FILE.write_text(_profiler.get_stats(top=0), encoding="utf-8")


_profiler.enable()
