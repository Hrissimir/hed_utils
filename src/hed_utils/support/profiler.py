import cProfile
import logging
from io import StringIO
from pstats import Stats

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class Profiler:
    def __init__(self):
        _log.debug("initializing profiler...")
        self._profile = cProfile.Profile()
        self._is_enabled = False

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    def enable(self):
        _log.debug("enabling profiler...")
        if self.is_enabled:
            raise Exception("Already enabled!")
        self._profile.enable()
        self._is_enabled = True

    def disable(self):
        if not self.is_enabled:
            raise Exception("Already disabled!")
        self._profile.disable()
        self._is_enabled = False
        _log.debug("disabled profiler")

    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable()

    def get_stats(self, *, strip_dirs=True, sort_by="cumtime", top=50) -> str:
        _log.debug(f"generating profiler stats report... (strip_dirs={strip_dirs}, sort_by='{sort_by}', top={top})")
        if self.is_enabled:
            raise Exception("Can't create stats, because profiler is still enabled!")

        buffer = StringIO()
        stats = Stats(self._profile, stream=buffer)

        if strip_dirs:
            stats = stats.strip_dirs()

        if sort_by:
            stats = stats.sort_stats(sort_by)

        if top:
            stats.print_stats(top)
        else:
            stats.print_stats()

        return buffer.getvalue()
