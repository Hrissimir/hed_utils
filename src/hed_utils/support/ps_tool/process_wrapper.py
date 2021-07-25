import logging
from collections import OrderedDict
from datetime import datetime
from operator import itemgetter
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from psutil import AccessDenied
from psutil import Error
from psutil import NoSuchProcess
from psutil import Process
from psutil import TimeoutExpired
from psutil import process_iter
from tabulate import tabulate

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

ATTRIBUTES = (
    "username",
    "create_time",
    "parent_name",
    "ppid",
    "pid",
    "name",
    "exe",
    "cwd",
    "cmdline"
)

PROCESS_ATTRIBUTES = [
    "username",
    "create_time",
    "ppid",
    "pid",
    "name",
    "exe",
    "cwd",
    "cmdline"
]

SORT_KEY = itemgetter(*ATTRIBUTES)


class ProcessWrapper:
    """Wrapper of ``psutil.Process`` data, with some extra methods."""

    username: Optional[str]
    create_time: Optional[datetime]
    parent_name: Optional[str]
    ppid: Optional[int]
    pid: Optional[int]
    name: Optional[str]
    exe: Optional[str]
    cwd: Optional[str]
    cmdline: Optional[List[str]]

    def __init__(self):
        self.username = None
        self.create_time = None
        self.parent_name = None
        self.ppid = None
        self.pid = None
        self.name = None
        self.exe = None
        self.cwd = None
        self.cmdline = None
        self._dict = None
        self._repr = None

    def __repr__(self) -> str:
        if self._repr is None:
            self._repr = (
                    type(self).__name__
                    + "("
                    + ", ".join([f"{k}={v!r}" for k, v in self.as_dict().items()])
                    + ")"
            )
        return self._repr

    def __eq__(self, other):
        if isinstance(other, ProcessWrapper):
            return self.pid == other.pid
        return False

    @classmethod
    def wrap(cls, process: Process) -> Optional["ProcessWrapper"]:

        try:
            data = process.as_dict(attrs=PROCESS_ATTRIBUTES, ad_value=None)
        except Error:
            return None

        if not any(data.values()):
            return None

        try:
            data["parent_name"] = process.parent().name()
        except (AttributeError, Error):
            data["parent_name"] = None

        if data["create_time"]:
            data["create_time"] = datetime.fromtimestamp(int(data["create_time"]))
        else:
            data["create_time"] = None

        try:
            data["ppid"] = int(data["ppid"])
        except ValueError:
            data["ppid"] = None

        try:
            data["pid"] = int(data["pid"])
        except ValueError:
            data["pid"] = None

        if not data["cmdline"]:
            data["cmdline"] = None

        wrapper = cls()
        wrapper.username = data["username"]
        wrapper.create_time = data["create_time"]
        wrapper.parent_name = data["parent_name"]
        wrapper.ppid = data["ppid"]
        wrapper.pid = data["pid"]
        wrapper.name = data["name"]
        wrapper.exe = data["exe"]
        wrapper.cwd = data["cwd"]
        wrapper.cmdline = data["cmdline"]
        return wrapper

    @classmethod
    def wrap_all(cls, processes: Optional[Iterable[Process]] = None) -> List["ProcessWrapper"]:
        processes = processes or process_iter()
        return [cls.wrap(proc) for proc in processes]

    @classmethod
    def wrap_current(cls) -> "ProcessWrapper":
        return cls.wrap(Process())

    @classmethod
    def format_as_table(cls, wrappers: List["ProcessWrapper"], sort=True) -> str:
        rows = [wrapper.as_dict() for wrapper in wrappers if wrapper]
        if sort:
            rows.sort(key=SORT_KEY)
        return tabulate(tabular_data=rows, headers="keys")

    @classmethod
    def rkill(cls, wrappers: List["ProcessWrapper"], dry=True):

        targets = OrderedDict()
        for wrapper in wrappers:
            targets[wrapper.pid] = wrapper
            for child in reversed(wrapper.children()):
                targets[child.pid] = child

        while True:
            initial_size = len(targets)
            for proc in process_iter():
                try:
                    proc_pid, proc_ppid = proc.pid, proc.ppid
                except Error:
                    continue
                if proc_pid in targets:
                    continue
                if proc_ppid in targets:
                    proc_wrapper = ProcessWrapper.wrap(proc)
                    if proc_wrapper:
                        targets[proc_pid] = proc_wrapper
            current_size = len(targets)
            if initial_size == current_size:
                break

        targets_list = list(targets.values())

        if dry:
            return targets_list, targets_list, []

        victims_list = [t for t in targets_list if t.stop()]
        survivors_list = [t for t in targets_list if (t not in victims_list)]
        return targets_list, victims_list, survivors_list

    def as_dict(self) -> Dict[str, str]:

        if self._dict is None:
            self._dict = OrderedDict()
            for key in ATTRIBUTES:
                value = getattr(self, key)
                if value is None:
                    value = ""
                if isinstance(value, int):
                    value = str(value)
                if isinstance(value, datetime):
                    value = value.isoformat()
                if isinstance(value, list):
                    value = " ".join(value)
                if not isinstance(value, str):
                    value = str(value)
                self._dict[key] = value

        return self._dict

    def children(self) -> List["ProcessWrapper"]:
        try:
            current_process = Process(pid=self.pid)
        except Error:
            return []

        result = OrderedDict()
        for child in current_process.children(recursive=True):
            child_wrapper = ProcessWrapper.wrap(child)
            if not child_wrapper:
                continue
            if child_wrapper.pid in result:
                continue
            result[child_wrapper.pid] = child_wrapper

        while True:
            initial_size = len(result)
            for proc in process_iter():
                proc_wrapper = ProcessWrapper.wrap(proc)
                if not proc_wrapper:
                    continue
                if proc_wrapper.pid in result:
                    continue
                if proc_wrapper.ppid in result:
                    result[proc_wrapper.pid] = proc_wrapper
            if initial_size == len(result):
                break

        return list(result.values())

    def _terminate(self) -> bool:
        try:
            process = Process(pid=int(self.pid))
        except NoSuchProcess:
            return True

        try:
            process.terminate()
        except NoSuchProcess:
            return True
        except AccessDenied:
            return False

        try:
            process.wait(5)
        except TimeoutExpired:
            pass

        try:
            return not process.is_running()
        except Error:
            return False

    def _kill(self) -> bool:
        try:
            process = Process(pid=int(self.pid))
        except NoSuchProcess:
            return True

        try:
            process.kill()
        except NoSuchProcess:
            return True
        except AccessDenied:
            return False

        try:
            process.wait(5)
        except TimeoutExpired:
            pass

        try:
            return not process.is_running()
        except Error:
            return False

    def stop(self) -> bool:
        return self._terminate() or self._kill()
