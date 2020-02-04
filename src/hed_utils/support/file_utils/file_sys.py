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

Contents = namedtuple("Contents", "rootdir dirnames filenames")

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


def walk_contents(rootpath: Union[str, Path], followlinks=False) -> Generator[Contents, None, None]:
    """Recursively walks the given rootpath in bottom-up order, yielding Folder named-tuples"""

    if not rootpath:
        raise ValueError()

    rootpath = Path(rootpath)

    if not rootpath.exists():
        raise FileNotFoundError(str(rootpath))

    if not rootpath.is_dir():
        raise NotADirectoryError(str(rootpath))

    for rootdir, dirnames, filenames in walk(rootpath, topdown=False, followlinks=followlinks):
        yield Contents(rootdir, dirnames, filenames)


def walk_files(rootpath: Union[str, Path]) -> Generator[Path, None, None]:
    """Recursively (bottom-up) walks the given folder's contents, yielding only file-paths."""

    for contents in walk_contents(rootpath):
        for file in contents.filenames:
            yield Path(contents.rootdir).joinpath(file)


def walk_dirs(rootpath: Union[str, Path]) -> Generator[Path, None, None]:
    """Recursively (bottom-up) walks the given folder's contents, yielding only folder-paths."""

    for contents in walk_contents(rootpath):
        for folder in contents.dirnames:
            yield Path(contents.rootdir).joinpath(folder)


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

    if not filepath:
        raise ValueError()

    filepath = Path(filepath)

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


def delete_folder(rootpath: Union[str, Path], *, inclusive=True) -> bool:
    """Deletes folder contents recursively, starting from the innermost items.

    Args:
        rootpath:           Path to the target folder
        inclusive(bool):    If True will delete the folder itself after all of it's contents were deleted.

    Returns:
        obj(bool):          True if all targets were deleted, False otherwise.
    """

    def delete_dir(dirpath: Path):
        if dirpath.exists():
            try:
                dirpath.rmdir()
            except FileNotFoundError:
                pass

            return not dirpath.exists()

    if not rootpath:
        raise ValueError()

    rootpath = Path(rootpath)

    failed_deletions = list()

    # delete all files
    failed_deletions.extend(file for file in walk_files(rootpath) if not delete_file(file))

    # delete all folders
    failed_deletions.extend(dir_ for dir_ in walk_dirs(rootpath) if not delete_dir(dir_))

    # delete the root if needed
    if inclusive and not delete_dir(rootpath):
        failed_deletions.append(rootpath)

    if failed_deletions:
        _log.warning("Failed to delete the following targets:\n%s", pformat(failed_deletions, width=120))

    return not failed_deletions


def prepare_tmp_location(src_path: Union[str, Path]) -> str:
    """Prepares timestamped dir in the system-wide TMP dir"""

    if not src_path:
        raise ValueError()

    src_path = Path(src_path)
    tmp_dir = Path(tempfile.mkdtemp(prefix=src_path.stem, suffix=f"_{time_stamp()}"))
    tmp_location = tmp_dir.joinpath(src_path.name)
    _log.debug("prepared temp location for: '%s' at: '%s'", str(src_path), str(tmp_location))
    return str(tmp_location)


def copy(src, dst, overwrite=False) -> str:
    _log.debug("copying '%s' to '%s' ...", src, dst)
    if (not src) or (not dst):
        raise ValueError()

    src_path, dst_path = Path(src), Path(dst)

    if not src_path.exists():
        raise FileNotFoundError(src_path)

    if dst_path.exists():
        if not overwrite:
            raise FileExistsError(dst_path)

        can_write = delete_file(dst_path) if dst_path.is_file() else delete_folder(dst_path, inclusive=True)
        if not can_write:
            raise FileExistsError(dst_path)

    if src_path.is_file():
        copy_path = shutil.copyfile(str(src_path), str(dst_path))
    else:
        copy_path = shutil.copytree(str(src_path), str(dst_path))

    _log.debug("copied '%s' to '%s'", str(src_path), copy_path)
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

    if not file:
        raise ValueError()

    filepath = Path(file)
    _log.debug("Attempting to view file at: [ %s ]", str(filepath))

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
    _log.debug("viewing file by using cmd: %s", view_cmd)

    process = Process(target=partial(call, view_cmd), daemon=False)
    process.start()
    process.join(timeout=5)
    process.terminate()


def write_text(text: str, file, encoding="utf-8"):
    """Writes text contents to a target file, automatically creating parent dirs if needed."""

    filepath = Path(file)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(text, encoding=encoding)


def view_text(text: str, encoding="utf-8"):
    """Views a text by first writing it to a temp location,
     then open it with the system handler for the .txt file-type."""

    tmp_file = prepare_tmp_location("text_to_view.txt")
    write_text(text, tmp_file, encoding)
    view_file(tmp_file)
