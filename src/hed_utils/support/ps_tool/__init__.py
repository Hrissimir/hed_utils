import logging
import re
from os.path import basename
from typing import Iterable
from typing import List
from typing import Optional

import psutil
from psutil import Error
from psutil import Process
from psutil import process_iter

from hed_utils.support.ps_tool import ProcessWrapper
from hed_utils.support.ps_tool.process_wrapper import ProcessWrapper

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def get_processes_by_name(name: str) -> List[ProcessWrapper]:
    """Searches for processes with the given name, case-insensitive."""

    name = name.strip().lower()
    return [process
            for process
            in ProcessWrapper.wrap_all()
            if (process.name == name
                or (process.exe and basename(process.exe).lower() == name)
                or (process.cmdline and process.cmdline[0].lower() == name))]


def get_processes_by_pattern(pattern: str) -> List[ProcessWrapper]:
    """Gets processes matching the given regex pattern"""

    pattern = re.compile(pattern, flags=re.IGNORECASE)
    return [process
            for process
            in ProcessWrapper.wrap_all()
            if (pattern.findall(process.name)
                or (process.exe and pattern.findall(basename(process.exe)))
                or (process.cmdline and pattern.findall(process.cmdline[0])))]


def get_process_by_pid(pid) -> Optional[ProcessWrapper]:
    """Finds and returns process with the given pid or None."""

    try:
        return ProcessWrapper.wrap(Process(pid=int(pid)))
    except (ValueError, Error):
        return None


def terminate_process(pid: int) -> bool:  # pragma: no cover
    try:
        target = psutil.Process(pid)
        target.terminate()
        target.wait(1)
    except (psutil.TimeoutExpired, psutil.AccessDenied):
        return False
    except psutil.NoSuchProcess:
        return True
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
    except (psutil.TimeoutExpired, psutil.AccessDenied):
        return False
    except psutil.NoSuchProcess:
        return True

    try:
        return not target.is_running()
    except psutil.Error:
        return False


def _prepare_targets(initial_targets: Iterable[ProcessWrapper]) -> List[ProcessWrapper]:
    current_pid = psutil.Process().pid  # avoid suicide

    targets = dict()
    for target in initial_targets:

        target_pid = target.pid
        if (target_pid == current_pid) or (target_pid in targets):
            continue

        targets[target_pid] = target
        for child in target.children():

            child_pid = child.pid
            if (child_pid == current_pid) or (child_pid in targets):
                continue

            targets[child_pid] = child

    while True:
        initial_size = len(targets)

        for process in process_iter():

            try:
                process_pid, process_ppid = process.pid, process.ppid
            except Error:
                continue

            if (process_pid == current_pid) or (process_pid in targets):
                continue

            if process_ppid in targets:
                details = ProcessWrapper.wrap(process)
                if details:
                    targets[process_pid] = details

        if len(targets) == initial_size:
            break

    return list(reversed(targets.values()))


def rkill(targets: List[ProcessWrapper], dry=True) -> List[ProcessWrapper]:
    """Recursively kill the process, starting with it's children."""

    targets = _prepare_targets(targets)

    if targets:
        _log.info("The following processes are marked for killing:\n\n%s", ProcessWrapper.format_as_table(targets))

    if dry:
        _log.info("This run was DRY, so non of them was touched!")
        return targets

    victims = [t for t in targets if t.stop()]
    survivors = [t for t in targets if (t not in victims)]
    if survivors:
        _log.warning("Could not kill the following processes:\n\n%s", ProcessWrapper.format_as_table(survivors))

    return victims


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
