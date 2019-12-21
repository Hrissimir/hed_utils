import cProfile
import logging
from io import StringIO
from pstats import Stats

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

_profile = None


def init():
    global _profile
    _log.debug("initializing profiler...")
    _profiler = cProfile.Profile()


def enable():
    global _profile
    _log.debug("enabling profiler...")
    _profile.enable()


def disable():
    global _profile
    _log.debug("disabling profiler...")
    _profile.disable()


def get_stats(sort_by="cumtime", top=50):
    global _profile
    _log.debug("collecting profiler stats...")
    buffer = StringIO()
    stats = Stats(_profile, stream=buffer).strip_dirs().sort_stats(sort_by)
    stats.print_stats(top)
    return buffer.getvalue()


def get_callees() -> str:
    global _profile
    _log.debug("collecting profiler callees...")
    buffer = StringIO()
    stats = Stats(_profile, stream=buffer).strip_dirs()
    stats.print_callees()
    return buffer.getvalue()


def get_callers() -> str:
    global _profile
    _log.debug("collecting profiler callers...")
    buffer = StringIO()
    stats = Stats(_profile, stream=buffer).strip_dirs()
    stats.print_callers()
    return buffer.getvalue()
