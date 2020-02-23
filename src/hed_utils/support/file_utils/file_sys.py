import logging
import shutil
import tempfile
from collections import namedtuple
from datetime import datetime
from functools import partial
from multiprocessing import Process
from os import walk
from pathlib import Path
from pprint import pformat
from subprocess import call
from typing import Generator, Union

from hed_utils.support import os_type

Contents = namedtuple("Contents", "dirpath dirnames filenames")

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def format_size(n: int):
    """http://code.activestate.com/recipes/578019
    >>> format_size(10000)
    '9.8K'
    >>> format_size(100001221)
    '95.4M'
    """

    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def time_stamp() -> str:
    """Returns UTC timestamp string suited to use as filename prefix/suffix"""

    return datetime.utcnow().strftime('%Y-%m-%d_%H_%M_%S')


def walk_contents(folder: Union[str, Path], followlinks=False) -> Generator[Contents, None, None]:
    """Recursively walks the given rootpath in bottom-up order, yielding Contents tuples"""

    folder = Path(folder).absolute()
    _log.debug("walking folder contents of: %s", str(folder))

    for dirpath, dirnames, filenames in walk(folder, topdown=False, followlinks=followlinks):
        yield Contents(dirpath, dirnames, filenames)


def walk_files(folder: Union[str, Path]) -> Generator[Path, None, None]:
    """Recursively (bottom-up) walks the given folder's contents, yielding only file-paths."""

    for contents in walk_contents(folder):
        for filename in contents.filenames:
            yield Path(contents.dirpath).joinpath(filename)


def walk_dirs(rootpath: Union[str, Path]) -> Generator[Path, None, None]:
    """Recursively (bottom-up) walks the given folder's contents, yielding only folder-paths."""

    for contents in walk_contents(rootpath):
        for dirname in contents.dirnames:
            yield Path(contents.dirpath).joinpath(dirname)


def delete_file(filepath: Union[str, Path]) -> bool:
    """Deletes file at given location

    Args:
        filepath:               Path to the target file

    Returns:
        obj(bool):          True if the file was deleted (or not existing), False otherwise

    Raises:
        ValueError:         If the 'file' arg evaluates to False
        IsADirectoryError:  If the 'file' arg points to folder
    """

    filepath = Path(filepath).absolute()

    if filepath.exists():
        if filepath.is_file():
            try:
                filepath.unlink()
            except FileNotFoundError:
                pass
        else:
            raise IsADirectoryError(str(filepath))

    if filepath.exists():
        _log.warning("failed to delete file at: '%s'", str(filepath))
        return False
    else:
        _log.debug("deleted file at: '%s'", str(filepath))
        return True


def delete_folder(folder: Union[str, Path], *, inclusive=True) -> bool:
    """Deletes folder contents recursively, starting from the innermost items.

    Args:
        folder:           Path to the target folder
        inclusive(bool):    If True will delete the folder itself after all of it's contents were deleted.

    Returns:
        obj(bool):          True if all targets were deleted, False otherwise.
    """

    def delete_dir(_dirpath: Path):
        if _dirpath.exists():
            try:
                _dirpath.rmdir()
            except FileNotFoundError:
                pass

            return not _dirpath.exists()

    folder = Path(folder).absolute()
    _log.debug("deleting folder at: '%s'", str(folder))

    failed_deletions = list()

    # delete all files
    failed_deletions.extend(filepath for filepath in walk_files(folder) if not delete_file(filepath))

    # delete all folders
    failed_deletions.extend(dirpath for dirpath in walk_dirs(folder) if not delete_dir(dirpath))

    # delete the root if needed
    if inclusive and not delete_dir(folder):
        failed_deletions.append(folder)

    if failed_deletions:
        _log.warning("Failed to delete the following targets:\n%s", pformat(failed_deletions, width=120))

    return not failed_deletions


def prepare_tmp_location(src_path: Union[str, Path]) -> str:
    """Prepares timestamped dir in the system-wide TMP dir"""

    if not src_path:
        raise ValueError()

    src_path = Path(src_path).absolute()
    tmp_dir = Path(tempfile.mkdtemp(prefix=src_path.stem, suffix=f"_{time_stamp()}"))
    tmp_location = tmp_dir.joinpath(src_path.name)
    _log.debug("prepared temp location for: '%s' at: '%s'", str(src_path), str(tmp_location))
    return str(tmp_location)


def copy(src, dst, overwrite=False) -> str:
    src, dst = Path(src).absolute(), Path(dst).absolute()
    _log.debug("copying '%s' to '%s' ...", str(src), str(dst))

    if not src.exists():
        raise FileNotFoundError(src)

    if dst.exists():
        if not overwrite:
            raise FileExistsError(dst)

        can_write = delete_file(dst) if dst.is_file() else delete_folder(dst, inclusive=True)
        if not can_write:
            raise FileExistsError(dst)

    if src.is_file():
        copy_path = shutil.copyfile(str(src), str(dst))
    else:
        copy_path = shutil.copytree(str(src), str(dst))

    _log.debug("copied '%s' to '%s'", str(src), copy_path)

    return copy_path


def copy_to_tmp(src_path) -> str:
    """Copies the src_path contents to a temp location in the system-wide temp dir."""

    return copy(src_path, prepare_tmp_location(src_path), overwrite=True)


def view_file(file: Union[str, Path], safe=False):
    """Attempts to open the target file using the system-default viewer for the file type.
    Args:
        file(str):  absolute path to the target file
        safe(bool): if passed will first copy the file to a temp location

    Returns:
        obj(str):   the path of the opened file.
    """

    filepath = Path(file).absolute()
    _log.debug("viewing file at: '%s'", str(filepath))

    if safe:
        filepath = Path(copy_to_tmp(filepath))

    view_file_cmd = {
        os_type.LINUX: ["xdg-open"],
        os_type.WINDOWS: ["cmd", "/c"],
    }

    view_cmd = view_file_cmd.get(os_type.get_current(), None)
    if not view_cmd:
        raise OSError("Unsupported os!")

    view_cmd.append(str(filepath))
    _log.debug("viewing file by using cmd: '%s'", view_cmd)

    process = Process(target=partial(call, view_cmd), daemon=False)
    process.start()
    process.join(timeout=5)
    process.terminate()


