import csv
import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Generator, Union

from hed_utils.support.file_utils.file_sys import walk_files

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def walk_csv_files(folder: Union[str, Path]) -> Generator[Path, None, None]:
    """Yields absolute paths to CSV files discovered in the given folder."""

    _log.debug("walking CSV files in folder: '%s'", folder)
    for filepath in walk_files(folder):
        for suffix in filepath.suffixes:
            if suffix.lower() == ".csv":
                yield filepath
                break


def csv_file_contains(file: Union[str, Path], text: str, *, ignorecase=True, encoding="utf-8", dialect="excel") -> bool:
    """Checks if a CSV file contains the text in any of it's rows"""

    file = Path(file).absolute()
    text = text.lower() if ignorecase else text
    is_present = False

    with file.open(mode="r", encoding=encoding) as fp:
        reader = csv.reader(fp, dialect=dialect)
        try:
            for row in reader:
                is_in_row = False

                for item in row:
                    item_text = item.lower() if ignorecase else item
                    if text in item_text:
                        is_in_row = True
                        break

                if is_in_row:
                    is_present = True
                    break

        except StopIteration:
            pass

    _log.debug("CSV file contains text '%s': [ %s ] (ignorecase: %s, file: '%s')",
               text, is_present, ignorecase, str(file))
    return is_present


def walk_csv_files_containing(folder: Union[str, Path],
                              text: str,
                              *,
                              ignorecase=True,
                              encoding="utf-8",
                              dialect="excel") -> Generator[Path, None, None]:
    """Walks the folder recursively, yielding paths to CSV files containing the given text"""

    _log.debug("walking CSV files containing '%s' in folder: '%s'", folder, text)
    for filepath in walk_csv_files(folder):
        if csv_file_contains(filepath, text, ignorecase=ignorecase, encoding=encoding, dialect=dialect):
            yield filepath


def csv_search_in_file(file: Union[str, Path],
                       text: str,
                       ignorecase=True,
                       encoding="utf-8",
                       dialect="excel"):
    """Searches in the file for CSV rows containing the text. Returns tuple (abspath, headers, matching_rows)"""

    file = Path(file).absolute()
    text = text.lower() if ignorecase else text
    _log.debug("searching for CSV rows containing '%s', ignorecase: %s in '%s'", text, ignorecase, str(file))

    with file.open(mode="r", encoding=encoding) as fp:
        reader = csv.reader(fp, dialect=dialect)
        headers, rows = next(reader, tuple()), []
        if headers:
            try:
                for row in reader:

                    for item in row:
                        item_text = item.lower() if ignorecase else item

                        if text in item_text:
                            rows.append(row)
                            break

            except StopIteration:
                pass

    file = str(file)
    _log.debug("got [ %s ] matching rows in file: '%s'! Headers: %s", len(rows), file, headers)
    return file, headers, rows


def csv_search_in_folder(folder: Union[str, Path],
                         text: str,
                         ignorecase=True,
                         encoding="utf-8",
                         dialect="excel"):
    """Performs a parallel search for all CSV files in the folder containing the given text,
    yielding tuples with the format: (filepath, headers, matching_rows)"""

    target_files = list(walk_csv_files_containing(
        folder, text, ignorecase=ignorecase, encoding=encoding, dialect=dialect))
    text_args = [text] * len(target_files)
    ignorecase_args = [ignorecase] * len(target_files)
    encoding_args = [encoding] * len(target_files)
    dialect_args = [dialect] * len(target_files)

    with ProcessPoolExecutor() as pool:
        for file, headers, rows in pool.map(csv_search_in_file,
                                            target_files,
                                            text_args,
                                            ignorecase_args,
                                            encoding_args,
                                            dialect_args):
            if rows:
                yield file, headers, rows
