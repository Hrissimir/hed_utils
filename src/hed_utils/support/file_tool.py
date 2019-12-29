import json
import logging
import shutil
import tempfile
from datetime import datetime
from functools import partial
from multiprocessing import Process
from os import walk
from pathlib import Path
from pprint import pformat
from string import ascii_letters, digits, whitespace
from subprocess import call
from typing import Dict, List, Union
from zipfile import ZipFile, ZipInfo

import pyminizip
from xlrd import open_workbook
from xlwt import XFStyle, Workbook

from hed_utils.support import text_tool, os_type

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def get_stamp() -> str:
    """Returns UTC timestamp string suited to use as filename prefix/suffix"""

    return datetime.utcnow().strftime('%Y-%m-%d_%H_%M_%S')


def prepare_tmp_location(src_path: Union[str, Path]) -> str:
    """Prepares timestamped dir in system-wide TMP dir"""
    src_path = Path(src_path).resolve()
    tmp_path = Path(tempfile.mkdtemp(prefix="tmp_dir_", suffix=f"_{get_stamp()}")).joinpath(src_path.name)
    _log.debug("deduced temp location of [ %s ] as  [%s]", str(src_path), str(tmp_path))
    return str(tmp_path)


def delete_file(file: Union[str, Path]) -> bool:
    """Deletes file at given location

    Args:
        file:   Path to the target file

    Returns:
        obj(bool):   True if the file was deleted (or not existing), False otherwise
    """

    if not file:
        raise ValueError()

    file_path = Path(file)

    if not file_path.exists():
        return True

    if not file_path.is_file():
        raise IsADirectoryError(str(file))

    file.unlink()
    _log.debug("deleted file: %s", str(file))

    return not file.exists()


def delete_folder(folder: Union[str, Path], *, inclusive=True) -> bool:
    """Deletes folder contents recursively, starting from the innermost items.

    Args:
        folder:             Path to the target folder
        inclusive(bool):     If True will delete the folder itself after all of it's contents were deleted.

    Returns:
        obj(bool):           True if all targets were deleted, False otherwise.
    """

    folder_path = Path(folder).resolve()
    _log.debug("deleting folder (inclusive=%s): %s", inclusive, str(folder_path))

    if not folder_path.exists():
        raise FileNotFoundError(str(folder_path))
    if not folder_path.is_dir():
        raise NotADirectoryError(str(folder_path))

    failed_deletions = []
    deletion_targets = list(sorted(folder_path.glob("**/*"), reverse=True))
    if inclusive:
        deletion_targets.append(folder_path)

    for target in deletion_targets:
        if not target.exists():
            continue
        try:
            if target.is_file():
                target.unlink()
            else:
                target.rmdir()
        except:
            _log.exception("error deleting: %s", str(target))
        finally:
            if target.exists():
                details = ("file: " if target.is_file() else "dir : ") + str(target)
                failed_deletions.append(details)

    if failed_deletions:
        _log.warning("could not delete the following items:\n%s", pformat(failed_deletions, width=120))
        return False

    return True


def copy(src, dst, overwrite=False) -> str:
    src_path, dst_path = Path(src).resolve(), Path(dst).resolve()
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


def write_text(text, file):
    """Writes text contents to a target file.
    Create parent dirs automatically, and tries to guess encoding if needed"""

    path = Path(file)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        contents = text.encode(encoding="utf-8")
    except UnicodeEncodeError:
        try:
            contents = text.encode(encoding="latin1")
        except UnicodeEncodeError:
            normalized = text_tool.normalize(text)
            contents = normalized.encode(encoding="utf-8", errors="ignore")

    with path.open(mode="wb") as out_file:
        out_file.write(contents)


def view_text(text: str):
    """Views a text by first writing it to a temp location,
     then open it with the system handler for the type."""

    tmp_file = prepare_tmp_location("text_to_view.txt")
    write_text(text, tmp_file)
    view_file(tmp_file)


def read_json(src_file):
    src_path = Path(src_file).resolve()
    _log.debug("reading JSON contents from: %s", src_path)

    if not src_path.exists():
        raise FileNotFoundError(src_path)
    if not src_path.is_file():
        raise IsADirectoryError(src_path)

    with src_path.open("rb") as in_file:
        contents = in_file.read()

    try:
        return json.loads(contents.decode(encoding="utf-8"))
    except UnicodeDecodeError:
        return json.loads(contents.decode(encoding="latin1"))


def write_json(dst_file, obj):
    dst_path = Path(dst_file).resolve()
    _log.debug("writing (%s) object to .json at '%s'", type(obj).__name__, dst_path)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        contents = json.dumps(obj).encode(encoding="utf-8")
    except UnicodeEncodeError:
        contents = json.dumps(obj).encode(encoding="latin1")

    with dst_path.open("wb") as out_file:
        out_file.write(contents)


def write_zipped_text(dst_zip: str, text: str, password: str, text_file_name="protected.txt"):
    """Writes text to a .txt file and puts it in a password-protected zip.

    Arguments:
        dst_zip(str):           Path for the destination .zip file
        text(str):              The text to be written.
        password(str):          Password that will be used to lock the zip
        text_file_name(str):    Name of the .txt file that will be holding the text inside the archive

    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        txt_file_path = Path(tmp_dir).joinpath(text_file_name)
        txt_file_path.write_bytes(text.encode("utf-8"))
        file_prefix_in_zip = None
        zip_path = str(Path(dst_zip))
        pyminizip.compress(str(txt_file_path), file_prefix_in_zip, zip_path, password, 9)


def read_zipped_text(src_zip: str, password: str, text_file_name="protected.txt") -> str:
    """Reads text that was written to a .zip file using .write_zipped_text

    Arguments:
        src_zip(str):           Path to the .zip
        password(str):          Password to be used for unlocking the zip
        text_file_name(str):    The name of the file that holds the text inside the zip

    Returns:
        obj(str):               The text that was written.
    """

    zip_path = str(Path(src_zip))
    with ZipFile(zip_path, "r") as archive:
        archive.setpassword(bytes(password, "utf-8"))
        with archive.open(text_file_name) as file:
            return file.read().decode("utf-8")


def extract_zip(src_zip, dst_dir, pwd=None):
    src_zip = Path(src_zip).resolve()
    dst_dir = Path(dst_dir)
    _log.debug("extracting zip: ( %s ) to dir: ( %s )", str(src_zip), str(dst_dir))
    if not src_zip:
        raise FileNotFoundError(str(src_zip))
    if dst_dir.exists() and (not dst_dir.is_dir()):
        raise NotADirectoryError(str(dst_dir))
    else:
        dst_dir.mkdir(parents=True, exist_ok=True)

    with ZipFile(str(src_zip)) as archive:
        archive.extractall(path=str(dst_dir), pwd=pwd)

    _log.debug("extraction complete!")


def zip_dir(src_dir, dst_zip, *, skip_suffixes=None, dry=False):
    _sep = 50 * "-"

    skip_suffixes = skip_suffixes or []
    src_dir, dst_zip = Path(src_dir), Path(dst_zip)
    _log.debug("zipping dir: '%s' to: '%s", str(src_dir), str(dst_zip))

    if not src_dir.exists():
        raise FileNotFoundError(str(src_dir))
    if not src_dir.is_dir():
        raise NotADirectoryError(str(src_dir))
    if dst_zip.exists():
        raise FileExistsError(str(dst_zip))

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_zip_path = Path(tmp_dir).joinpath(dst_zip.name)

        with ZipFile(str(tmp_zip_path), mode="w") as zip_out:
            for root, dirs, files in walk(src_dir):
                root = Path(root)

                for folder in dirs:
                    folder = root.joinpath(folder)

                    # add empty folders to the zip
                    if not list(folder.iterdir()):
                        _log.debug(_sep)
                        folder_name = f"{str(folder.relative_to(src_dir))}/"
                        _log.debug("empty dir: '%s'", folder_name)

                        if dry:
                            continue

                        zip_out.writestr(ZipInfo(folder_name), "")

                for file in files:
                    file = root.joinpath(file)
                    _log.debug(_sep)
                    _log.debug("adding:  '%s'", str(file))

                    should_skip = None
                    for suffix in file.suffixes:
                        if suffix in skip_suffixes:
                            should_skip = suffix
                            break

                    if should_skip:
                        _log.debug("skipped [%s]: %s", should_skip, str(file))
                        continue

                    arcname = str(file.relative_to(src_dir))
                    _log.debug("arcname: '%s'", arcname)

                    if dry:
                        continue

                    zip_out.write(str(file), arcname=arcname)

        if not dry:
            dst_zip.write_bytes(tmp_zip_path.read_bytes())

        tmp_zip_path.unlink()


def _normalize_sheet_name(name) -> str:
    if isinstance(name, float):
        name = f"{name:.02f}"
    elif not isinstance(name, str):
        name = str(name)

    name_chars = []
    for char in name:
        if (char in ascii_letters) or (char in digits):
            name_chars.append(char)
        elif char in whitespace:
            name_chars.append(" ")
        else:
            name_chars.append("_")

    name_normalized = "".join(name_chars)

    _log.debug("normalized sheet name '%s' to '%s'", name, name_normalized)
    return name_normalized


def read_excel_as_dicts(file: str) -> Dict[str, List[Dict[str, Union[int, float, str]]]]:
    """Reads excel file to a dictionary with the format {sheet_name: sheet_data_dict}"""

    if (not isinstance(file, str)) or (not file):
        raise ValueError(f"file must be a non-empty string! (was: [{file}])")

    file = str(Path(file).absolute())
    _log.debug("reading excel sheets from: [%s] ...", file)

    result = dict()

    with open_workbook(file) as workbook:

        for worksheet in workbook.sheets():

            result[worksheet.name] = []
            headers = [worksheet.cell_value(0, column_index) for column_index in range(worksheet.ncols)]

            for row_index in range(1, worksheet.nrows):
                row_data = {headers[column_index]: worksheet.cell_value(row_index, column_index)
                            for column_index
                            in range(worksheet.ncols)}

                result[worksheet.name].append(row_data)

    return result


def write_excel_from_dict(sheets: Dict[str, List[Dict[str, Union[int, float, str]]]], file: str, *, floatfmt="##0.00"):
    """ Writes multiple sheets data to a file.

    The column names for each sheet are the keys of the first dict record.
    Automatically suffixes the file name with .xlsx if missing
    Automatically transforms the sheet names to valid strings

    Arguments:
        sheets(dict)    A dict with format { "sheet name": [ sheet records as dicts ] }
        file(str)       The output destination file
        floatfmt(str)   Format for float cells

    Returns:
        dst_path(str)  Absolute path to the output file

    """

    if (not isinstance(file, str)) or (not file):
        raise ValueError(f"file must be a non-empty string! (was: [{file}])")

    dst_path = str(Path(file if file.endswith(".xlsx") else f"{file}.xlsx").absolute())
    _log.debug("writing excel sheets to: [ %s ] ...", file)

    float_format = XFStyle()
    float_format.num_format_str = floatfmt
    output_workbook = Workbook()

    for sheet_name, sheet_records in sheets.items():
        sheet_name = _normalize_sheet_name(sheet_name)
        sheet = output_workbook.add_sheet(sheet_name)
        sheet.show_headers = True
        columns = list(sheet_records[0].keys())

        # write the headers
        for column_index, column_name in enumerate(columns):
            sheet.write(0, column_index, column_name)

        # write the records
        for row_index, record in enumerate(sheet_records):
            for column_index, column_name in enumerate(columns):
                value = record[column_name]
                if isinstance(value, float):
                    sheet.write(row_index + 1, column_index, value, float_format)
                else:
                    sheet.write(row_index + 1, column_index, value)

    output_workbook.save(dst_path)

    return dst_path
