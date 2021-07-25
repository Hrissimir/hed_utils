import logging
import re
from itertools import chain
from collections import OrderedDict
from datetime import datetime
from operator import itemgetter
from os.path import basename

from typing import Dict
from typing import Iterable
from typing import List
from typing import Union
from typing import Optional

from psutil import AccessDenied
from psutil import Error
from psutil import NoSuchProcess
from psutil import Process
from psutil import TimeoutExpired
from psutil import process_iter
from tabulate import tabulate
from hed_utils.support import checked_param
from hed_utils.support.ps_tool.process_wrapper import ProcessWrapper
_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def get_process_by_pid(pid: int) -> Optional[Process]:
    """Returns process with the given PID or None."""

    try:
        return Process(pid=pid)
    except Error:
        return None


def get_processes_by_name(name: str) -> List[Process]:
    """Returns all processes with the given name (case-insensitive)."""

    name = name.strip().lower()
    result = list()
    for proc in process_iter():
        try:
            data = proc.as_dict(
                attrs=["name", "exe", "cmdline"],
                ad_value=None
            )
        except Error:
            continue

        proc_name = data["name"].strip() if data["name"] else None
        if proc_name and (name == proc_name.lower()):
            result.append(proc)
            continue

        proc_exe = data["exe"].strip() if data["exe"] else None
        if proc_exe and (name == basename(proc_exe).strip().lower()):
            result.append(proc)
            continue

        proc_cmdline = data["cmdline"][0].strip() if data["cmdline"] else None
        if proc_cmdline and (name == basename(proc_cmdline).strip().lower()):
            result.append(proc)
            continue

    return result


def get_processes_by_regex(pattern: str) -> List[Process]:
    """Returns all processes whose name matches the given regex pattern."""

    pattern = re.compile(pattern, flags=re.IGNORECASE)
    result = list()
    for proc in process_iter():
        try:
            data = proc.as_dict(
                attrs=["name", "exe", "cmdline"],
                ad_value=None
            )
        except Error:
            continue

        proc_name = data["name"].strip() if data["name"] else None
        if proc_name and pattern.findall(proc_name):
            result.append(proc)
            continue

        proc_exe = data["exe"].strip() if data["exe"] else None
        if proc_exe and pattern.findall(basename(proc_exe).strip()):
            result.append(proc)
            continue

        proc_cmdline = data["cmdline"][0].strip() if data["cmdline"] else None
        if proc_cmdline and pattern.findall(basename(proc_cmdline).strip()):
            result.append(proc)
            continue

    return result


def get_processes(
        *,
        pid: Optional[Union[int, str]] = None,
        name: Optional[str] = None,
        regex: Optional[str] = None) -> List[Process]:

    result = list()

    pid = checked_param.int_value("pid", pid, min_allowed=0)
    if pid is not None:
        proc = get_process_by_pid(pid)
        if proc:
            result.append(proc)

    name = checked_param.string_value("name", name)
    if name:
        result.extend(get_processes_by_name(name))

    regex = checked_param.string_value("regex", regex)
    if regex:
        result.extend(get_processes_by_regex(regex))

    return result


def kill_process(process: Process) -> bool:

    if not process.is_running():
        return True

    try:
        process.terminate()
        process.wait(5)
    except NoSuchProcess:
        return True
    except (AccessDenied, TimeoutExpired):
        pass

    if not process.is_running():
        return True

    try:
        process.kill()
        process.wait(5)
    except NoSuchProcess:
        return True
    except (AccessDenied, TimeoutExpired):
        pass

    return not process.is_running()


def kill_processes(
        *,
        pid: Optional[Union[int, str]] = None,
        name: Optional[str] = None,
        regex: Optional[str] = None):

    initial_targets = get_processes(pid=pid, name=name, regex=regex)
    deduced_targets = list()
    for proc in initial_targets:
        if proc in deduced_targets:
            continue
        for child in reversed(proc.children()):
            if child not in deduced_targets:
                deduced_targets.append(child)
        deduced_targets.append(proc)

    _log.info("kill_processes - deduced %s targets!", len(deduced_targets))
    deduced_targets_data = ProcessWrapper.wrap_all(deduced_targets)
    deduced_targets_table = ProcessWrapper.format_as_table(deduced_targets_data, sort=False)
    _log.debug("kill_processes - deduced targets:\n%s", deduced_targets_table)

    victims = list()
    for target, target_data in zip(deduced_targets, deduced_targets_data):
        if kill_process(target) and target_data:
            victims.append(target_data)

    _log.info("kill_processes - killed %s victims", len(victims))
    _log.debug("kill_process - victims:\n%s", ProcessWrapper.format_as_table(victims))