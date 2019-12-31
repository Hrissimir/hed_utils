import logging
from pathlib import Path
from string import ascii_letters, digits, whitespace
from typing import Dict, List, Union

from xlrd import open_workbook
from xlwt import XFStyle, Workbook

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


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


def read_xlsx_as_dict(file: str) -> Dict[str, List[Dict[str, Union[int, float, str]]]]:
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


def write_xlsx_from_dict(sheets: Dict[str, List[Dict[str, Union[int, float, str]]]], file: str, *, floatfmt="##0.00"):
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
