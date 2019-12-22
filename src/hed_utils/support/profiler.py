import cProfile
import logging
from io import StringIO
from pathlib import Path
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
        _log.debug("disabling profiler...")
        if not self.is_enabled:
            raise Exception("Already disabled!")
        self._profile.disable()
        self._is_enabled = False

    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable()

    def generate_report(self, *, strip_dirs=True, sort_by="cumtime", top=50, callees=True, callers=True) -> str:
        _log.debug("generating profiler report... "
                   f"(strip_dirs={strip_dirs}, sort_by='{sort_by}', top={top}, callees={callees}, callers={callers})")

        if self.is_enabled:
            raise Exception("Profiler is enabled!")

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

        if callees:
            buffer.write("\nCallees:\n")
            if top:
                stats.print_callees(top)
            else:
                stats.print_callees()

        if callers:
            buffer.write("\nCallers:\n")
            if top:
                stats.print_callers(top)
            else:
                stats.print_callers()

        return buffer.getvalue()

    def write_report(self, file, *, strip_dirs=True, sort_by="cumtime", top=50, callees=True, callers=True):
        file_path = Path(file).resolve()
        _log.debug("writing profiler report to file: '%s'", str(file_path))
        report = self.generate_report(strip_dirs=strip_dirs,
                                      sort_by=sort_by,
                                      top=top,
                                      callees=callees,
                                      callers=callers)
        file_path.write_text(report, encoding="utf-8")
