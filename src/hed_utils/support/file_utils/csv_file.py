import csv
import logging
from concurrent.futures import ProcessPoolExecutor
from os import walk
from os.path import abspath, join
from pathlib import Path
from typing import List, Union

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def get_csv_files(folder: Union[str, Path]) -> List[str]:
    """Returns list with absolute paths to CSV files discovered in the given folder."""

    folder = abspath(folder)
    _log.debug("getting CSV files in: '%s'", folder)
    return [join(dirpath, filename)
            for (dirpath, _, filenames) in walk(folder, topdown=False)
            for filename in filenames
            if filename.lower().endswith(".csv")]


def get_csv_rows_containing(file, text, ignorecase, encoding, dialect="excel"):
    """Searches for CSV rows in the file that contain the given text.

    :returns tuple with format: (file, headers, rows) for convenience
    """

    if ignorecase:
        text = text.lower()

    try:
        with open(file, mode="r", encoding=encoding) as fp:
            reader = csv.reader(fp, dialect=dialect)
            try:
                headers, rows = next(reader), []
                for row in reader:
                    for item in row:
                        if ignorecase:
                            if text in item.lower():
                                rows.append(row)
                                break
                        elif text in item:
                            rows.append(row)
                            break

            except StopIteration:
                headers, rows = (), []
    except UnicodeDecodeError:
        _log.exception("Could not read file because of unicode error! File: '%s'", file)
        headers, rows = (), []
    _log.debug("got %5d CSV rows containing '%s' (ignorecase: %s) in file: '%s'", len(rows), text, ignorecase, file)
    return file, headers, rows


def get_csv_files_containing(files, text, ignorecase, encoding, dialect="excel"):
    """Checks the given files for CSV rows having the text, and returns all matching contents.

    The result has format [(file,headers,rows), (file2,headers2,rows2), ...] for convenience."""

    args_len = len(files)
    text_args = args_len * (text,)
    ignorecase_args = args_len * (ignorecase,)
    encoding_args = args_len * (encoding,)
    dialect_args = args_len * (dialect,)

    def on_result(r):
        print(r.result())

    with ProcessPoolExecutor() as pool:
        return [(file, headers, rows)
                for file, headers, rows
                in pool.map(get_csv_rows_containing, files, text_args, ignorecase_args, encoding_args, dialect_args)
                if rows]
