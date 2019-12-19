import logging
import re
from collections import namedtuple
from datetime import datetime
from operator import attrgetter
from os.path import basename
from typing import List, Optional, Iterable

import psutil
from tabulate import tabulate

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

KEYS = ["create_time", "pid", "ppid", "name", "exe", "cmdline"]
"""List of attributes to collect when retrieving process details from psutil."""

ProcessDetails = namedtuple("ProcessDetails", KEYS)
"""Named tuple used for caching process details of psutil.Process"""


def normalize_details(details: ProcessDetails, *, timefmt="%m.%d-%H:%M:%S", maxcmdlen=100) -> ProcessDetails:
    name = details.name.lower()
    create_time = datetime.fromtimestamp(int(details.create_time)).strftime(timefmt)
    cmdline = (" ".join(details.cmdline) if details.cmdline else "")[:maxcmdlen]
    return details._replace(name=name, create_time=create_time, cmdline=cmdline)


def format_processes(processes: List[ProcessDetails], *, timefmt="%m.%d-%H:%M:%S", maxcmdlen=100) -> str:
    """Formats a list of ProcessDetails named-tuples as text table."""

    data = [normalize_details(process, timefmt=timefmt, maxcmdlen=maxcmdlen)
            for process
            in processes]

    return tabulate(data, headers=[key.upper() for key in KEYS], showindex=1)


def iter_processes():
    """Yields ProcessDetails named-tuples created from psutil.process_iter().

    Storing psutil.Process details in ProcessDetails named-tuple is done to avoid exceptions,
    that are raised from psutil upon interaction with psutil.Process objects when the process is reused.
    Using this approach also proved to perform better for common tasks."""

    for process in psutil.process_iter(attrs=KEYS):
        yield ProcessDetails(**process.info)


def get_processes_by_name(name: str) -> List[ProcessDetails]:
    """Searches for processes with the given name, case-insensitive."""

    name = name.strip().lower()
    return [process
            for process
            in iter_processes()
            if (process.name == name
                or (process.exe and basename(process.exe).lower() == name)
                or (process.cmdline and process.cmdline[0].lower() == name))]


def get_processes_by_pattern(pattern: str) -> List[ProcessDetails]:
    """Gets processes matching the given regex pattern"""

    pattern = re.compile(pattern, flags=re.IGNORECASE)
    return [process for process in iter_processes()
            if (pattern.findall(process.name)
                or (process.exe and pattern.findall(basename(process.exe)))
                or (process.cmdline and pattern.findall(process.cmdline[0])))]


def get_process_by_pid(pid) -> Optional[ProcessDetails]:
    """Finds and returns process with the given pid or None."""

    pid = int(pid)
    for process in iter_processes():
        if process.pid == pid:
            return process


def terminate_process(pid: int) -> bool:  # pragma: no cover
    try:
        target = psutil.Process(pid)
        target.terminate()
        target.wait(1)
    except psutil.NoSuchProcess:
        return True
    except psutil.TimeoutExpired:
        return False
    try:
        return not target.is_running()
    except psutil.Error:
        return False


def kill_process(pid: int) -> bool:  # pragma: no cover
    if terminate_process(pid):
        return True
    try:
        target = psutil.Process(pid)
        target.kill()
        target.wait(1)
    except psutil.NoSuchProcess:
        return True
    except psutil.TimeoutExpired:
        return False
    try:
        return not target.is_running()
    except psutil.Error:
        return False


def _prepare_victims(initial_targets: Iterable[ProcessDetails]):
    current_pid = psutil.Process().pid  # avoid suicide
    victims = {target.pid: target
               for target
               in initial_targets
               if target.pid != current_pid}

    while True:
        initial_size = len(victims)

        for process in iter_processes():
            if (process.pid in victims) or (process.pid == current_pid):
                continue
            elif process.ppid in victims:
                victims[process.pid] = process

        if len(victims) == initial_size:
            break

    return list(sorted(victims.values(), key=attrgetter("create_time"), reverse=True))


def rkill(targets: List[ProcessDetails], dry=True) -> List[ProcessDetails]:
    """Recursively kill the process, starting with it's children."""

    victims = _prepare_victims(targets)

    if victims:
        _log.info("The following processes are marked for killing:\n\n%s", format_processes(victims))

    if dry:
        _log.info("This run was DRY, so non of them was touched!")
        return victims

    survivors = [v for v in victims if not kill_process(v.pid)]
    if survivors:
        _log.warning("Could not kill the following processes:\n\n%s", format_processes(survivors))

    return [v for v in victims if v not in survivors]


def kill_process_by_pid(pid, *, dry=True):
    target = get_process_by_pid(int(pid))
    return rkill([target], dry=dry) if target else []


def kill_processes_by_name(name, *, dry=True):
    targets = get_processes_by_name(name)
    _log.debug("got %s initial targets for name: '%s'", len(targets), name)
    return rkill(targets, dry=dry)


def kill_processes_by_pattern(pattern, *, dry=True):
    targets = get_processes_by_pattern(pattern)
    _log.debug("got %s initial targets for pattern: '%s'", len(targets), pattern)
    return rkill(targets, dry=dry)
