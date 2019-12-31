import errno
import logging
import shutil
import tempfile
from collections import namedtuple
from datetime import datetime
from functools import partial
from multiprocessing import Process
from os import rmdir, walk
from os.path import exists, join
from pathlib import Path
from pprint import pformat
from subprocess import call
from typing import Union

from hed_utils.support import os_type

Folder = namedtuple("Folder", "dirpath dirnames filenames")

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


def get_stamp() -> str:
    """Returns UTC timestamp string suited to use as filename prefix/suffix"""

    return datetime.utcnow().strftime('%Y-%m-%d_%H_%M_%S')


def walk_folders(rootpath: Union[str, Path], followlinks=False):
    """Recursively walks the given rootpath in bottom-up order, yielding Folder named-tuples"""

    root_path = Path(rootpath).absolute()
    if not root_path.exists():
        raise FileNotFoundError(str(root_path))
    if not root_path.is_dir():
        raise NotADirectoryError(str(root_path))

    for dirpath, dirnames, filenames in walk(root_path, topdown=False, followlinks=followlinks):
        yield Folder(dirpath, dirnames, filenames)


def iter_files(rootpath: Union[str, Path]):
    """Recursively iterates the given folder's contents, yielding only file-paths, in a bottom-up manner."""

    for folder in walk_folders(rootpath):
        for name in folder.filenames:
            yield join(folder.dirpath, name)


def iter_folders(rootpath: Union[str, Path]):
    """Recursively iterates the given folder's contents, yielding only folder-paths, in a bottom-up manner."""

    for folder in walk_folders(rootpath):
        for name in folder.dirnames:
            yield join(folder.dirpath, name)


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

    filepath = Path(filepath).absolute()

    if filepath.exists():
        try:
            if not filepath.is_file():
                raise IsADirectoryError(str(filepath))

            filepath.unlink()
        except FileNotFoundError:
            pass

    success = not filepath.exists()

    if success:
        _log.debug("deleted file at: '%s'", str(filepath))
    else:
        _log.warning("failed to delete file at: '%s'", str(filepath))

    return success


def delete_folder(folder: Union[str, Path], *, inclusive=True) -> bool:
    """Deletes folder contents recursively, starting from the innermost items.

    Args:
        folder:             Path to the target folder
        inclusive(bool):    If True will delete the folder itself after all of it's contents were deleted.

    Returns:
        obj(bool):          True if all targets were deleted, False otherwise.
    """

    def delete_dir(dir_path) -> bool:  # helper func for deleting a single folder
        try:
            rmdir(dir_path)
        except FileNotFoundError:
            pass
        except OSError as error:
            if error.errno == errno.ENOTEMPTY:  # not empty
                pass
            raise

        success = not exists(dir_path)
        if success:
            _log.debug("deleted folder at: '%s'", str(dir_path))
        else:
            _log.warning("failed to delete folder at: '%s'", str(dir_path))

        return success

    folder_path = Path(folder).absolute()
    _log.debug("deleting folder (inclusive=%s): %s", inclusive, str(folder_path))

    failed_deletions = []

    # First delete all inner files
    for filepath in iter_files(folder):
        if not delete_file(filepath):
            failed_deletions.append(("file", filepath))

    # Then delete the supposedly empty folders folders
    for dirpath in iter_folders(folder):
        if not delete_dir(dirpath):
            failed_deletions.append(("folder", dirpath))

    if inclusive and (not delete_dir(folder_path)):
        failed_deletions.append(("folder", str(folder_path)))

    if failed_deletions:
        _log.warning("could not delete the following items:\n%s", pformat(failed_deletions, width=120))
        return False

    return True


def prepare_tmp_location(src_path: Union[str, Path]) -> str:
    """Prepares timestamped dir in the system-wide TMP dir"""

    src_path = Path(src_path).absolute()
    tmp_dir = Path(tempfile.mkdtemp(prefix=src_path.stem, suffix=f"_{get_stamp()}"))
    tmp_location = tmp_dir.joinpath(src_path.name)
    _log.debug("prepared temp location for: '%s' at: '%s'", str(src_path), str(tmp_location))
    return str(tmp_location)


def copy(src, dst, overwrite=False) -> str:
    src_path, dst_path = Path(src).absolute(), Path(dst).absolute()
    _log.debug("copying '%s' to '%s' ...", str(src_path), str(dst_path))

    if not src_path.exists():
        raise FileNotFoundError(src_path)

    if dst_path.exists():
        if not overwrite:
            raise FileExistsError(dst_path)

        can_write = delete_file(dst_path) if dst_path.is_file() else delete_folder(dst_path, inclusive=True)
        if not can_write:
            raise FileExistsError(dst_path)

    copy_func = shutil.copyfile if src_path.is_file() else shutil.copytree
    copy_path = copy_func(str(src_path), str(dst_path))
    _log.debug("copied '%s' to '%s'", str(src_path), copy_path)
    return copy_path


def copy_to_tmp(src_path) -> str:
    """Copies the src_path contents to a temp location in the system-wide temp dir."""

    return copy(src_path, prepare_tmp_location(src_path), overwrite=True)


def view_file(path, safe=False):
    """Attempts to open the target file using the system-default viewer for the file type.
    Args:
        path(str):  absolute path to the target file
        safe(bool): if passed will first copy the file to a temp location

    Returns:
        obj(str):   the path of the opened file.
    """

    if (not path) or (not isinstance(path, (str, Path))):
        raise ValueError(f"path must be non-empty string or Path instance! (Was:{path}")

    path = (path if isinstance(path, Path) else Path(path)).absolute()
    _log.debug(f"Attempting to view file at: [ {str(path)} ]")

    path = str(path.resolve())

    if safe:
        path = copy_to_tmp(path)

    view_file_cmd = {
        os_type.LINUX: ["xdg-open"],
        os_type.WINDOWS: ["cmd", "/c"],
    }

    view_cmd = view_file_cmd.get(os_type.get_current(), None)
    if not view_cmd:
        raise OSError("Unsupported os!")

    view_cmd.append(str(path))
    _log.debug(f"viewing file by using cmd: {str(view_cmd)}")

    process = Process(target=partial(call, view_cmd), daemon=False)
    process.start()
    process.join(timeout=5)
    process.terminate()


def write_text(text: str, file, encoding="utf-8"):
    """Writes text contents to a target file, automatically creating parent dirs if needed."""

    filepath = Path(file).absolute()
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(text, encoding=encoding)


def view_text(text: str, encoding="utf-8"):
    """Views a text by first writing it to a temp location,
     then open it with the system handler for the .txt file-type."""

    tmp_file = prepare_tmp_location("text_to_view.txt")
    write_text(text, tmp_file, encoding)
    view_file(tmp_file)
