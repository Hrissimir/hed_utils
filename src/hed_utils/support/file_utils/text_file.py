import logging
from pathlib import Path
from typing import Union

from hed_utils.support.file_utils.file_sys import prepare_tmp_location, view_file

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def file_contains_line(file: Union[str, Path], text: str, *, encoding="utf-8", ignorecase=True) -> bool:
    """Checks if the file contains the given text in any of it's lines"""

    filepath = Path(file).absolute()
    text = text.lower() if ignorecase else text
    is_present = False
    with filepath.open(mode="r", encoding=encoding) as fp:
        for file_line in fp:
            file_line = file_line.lower() if ignorecase else file_line
            if text in file_line:
                is_present = True
                break

    _log.debug("line containing '%s' in file '%s' (ignorecase=%s) was present: [ %s ]",
               text, str(filepath), ignorecase, is_present)

    return is_present


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
