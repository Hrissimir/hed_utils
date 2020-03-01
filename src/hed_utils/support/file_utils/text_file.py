import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Union

from hed_utils.support.file_utils.file_sys import prepare_tmp_location, view_file

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def text_in_lines(file: Union[str, Path], text: str, ignorecase=True, encoding="utf-8") -> bool:
    """Checks file contains the text in any of it's lines"""

    if ignorecase:
        text = text.lower()

    with open(file, mode="r", encoding=encoding) as fp:
        for line in fp:
            if ignorecase:
                if text in line.lower():
                    return True
            else:
                if text in line:
                    return True
    return False


def _check_file(file, text, ignorecase, encoding):
    return file, text_in_lines(file, text, ignorecase, encoding)


def iter_files_containing_text_in_lines(files, text, ignorecase, encoding):
    """Searches files that contain the given text in any of their lines, and yields the ones that do."""

    file_args = tuple(files)
    args_count = len(file_args)
    text_args = (text,) * args_count
    ignorecase_args = (ignorecase,) * args_count
    encoding_args = (encoding,) * args_count

    with ProcessPoolExecutor() as pool:
        for file, is_match in pool.map(_check_file, file_args, text_args, ignorecase_args, encoding_args):
            if is_match:
                yield file


def view_text(text: str, encoding="utf-8"):
    """Views a text by first writing it to a temp location,
     then open it with the system handler for the .txt file-type."""

    _log.debug("viewing text (%s chars) ...", len(text))
    tmp_file = prepare_tmp_location("text_to_view.txt")
    write_text(text, tmp_file, encoding)
    view_file(tmp_file)


def write_text(text: str, file: Union[str, Path], encoding="utf-8"):
    """Writes text contents to a target file, automatically creating parent dirs if needed."""

    filepath = Path(file).absolute()
    _log.debug("writing text (%s chars) to file: '%s' ...", len(text), str(filepath))
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(text, encoding=encoding)
