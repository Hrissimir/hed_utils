"""This module contains helper methods for dealing with excel files.
        Credits: https://realpython.com/openpyxl-excel-spreadsheets-python/
"""
import logging
import re
from copy import copy
from pathlib import Path
from typing import List

from openpyxl.styles import fonts

# dirty hack to change the default font used by openpyxl
_custom_font = copy(fonts.DEFAULT_FONT)
_custom_font.name = "Consolas"
fonts.DEFAULT_FONT = _custom_font

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, NamedStyle, Side
from openpyxl.worksheet.worksheet import Worksheet

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

_INVALID_SHEET_TITLE_REGEX = re.compile(r"[\\*?:/\[\]]")


def _sanitize_sheet_title(text: str) -> str:
    """Strips the text and transforms it into valid worksheet title by replacing the invalid chars with underscore"""

    _log.debug("sanitizing sheet title '%s' ...", text)
    text = text.strip()
    return _INVALID_SHEET_TITLE_REGEX.sub("_", text) if _INVALID_SHEET_TITLE_REGEX.search(text) else text


def _apply_header_style(sheet: Worksheet):
    """Applies header style to the first row in the sheet."""

    _log.debug("applying header style to sheet: %s", sheet)
    style = NamedStyle(name="header")
    style.font = Font(name="Consolas", bold=True)
    style.border = Border(bottom=Side(border_style="thin"))
    style.alignment = Alignment(horizontal="center", vertical="center")

    header_row = sheet[1]
    for cell in header_row:
        try:
            cell.style = style
        except ValueError as err:
            if "Style header exists already" in str(err):
                cell.style = "header"
            else:
                raise


def _auto_filter(sheet: Worksheet):
    """Adds auto-filter to all columns in the sheet"""

    _log.debug("adding auto-filters to sheet: %s", sheet)
    sheet.auto_filter.ref = sheet.dimensions


def _freeze_header(sheet: Worksheet):
    """Freezes the first row in the sheet"""

    _log.debug("freezing header in sheet: %s", sheet)
    sheet.freeze_panes = "A2"


def _optimize_columns_width(sheet: Worksheet):
    """Optimizes the columns widths to match the contents"""

    _log.debug("optimizing columns width in sheet: %s", sheet)
    dims = {}
    for row in sheet.rows:
        for cell in row:
            if cell.value:
                dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))

    for col, value in dims.items():
        sheet.column_dimensions[col].width = value + 1


def _append_sheet_data(workbook: Workbook, title, headers, rows) -> Worksheet:
    """Creates new Worksheet in the Workbook, then fills-in the data and applies styling to the header"""

    _log.debug("appending [%s] rows of sheet data with title '%s' and headers: %s", len(rows), title, headers)

    effective_title = _sanitize_sheet_title(title)
    if effective_title != title:
        _log.warning("transformed invalid sheet title '%s' to valid one: '%s'", title, effective_title)

    sheet = workbook.create_sheet(title=effective_title)

    sheet.append(headers)
    _apply_header_style(sheet)

    for row in rows:
        sheet.append(row)

    return sheet


def xlsx_workbook_from_sheets_data(sheets_data: List[tuple], *, auto_filter=True, freeze_header=True) -> Workbook:
    """Creates openpyxl.Workbook instance and populates it using multiple sheets data.

    Adds filters and freezes header by default.

    :argument sheets_data
        List containing tuples, each describing sheet data, with the following format
        [(sheet1_title, sheet1_headers, sheet1_rows), (sheet2_title, sheet2_headers, sheet2_rows), ...]

    :argument auto_filter
        If True will add auto-filters in all of the created sheets

    :argument freeze_header
        If True will freeze the header row in every sheet

    :returns
        the populated openpyxl.Workbook instance
    """

    _log.debug("creating Workbook and filling it with [ %s ] sheets data ...", len(sheets_data))
    workbook = Workbook()

    zero_sheet = workbook.active
    workbook.remove(zero_sheet)

    for title, headers, rows in sheets_data:
        sheet = _append_sheet_data(workbook, title, headers, rows)

        _optimize_columns_width(sheet)

        if auto_filter:
            _auto_filter(sheet)

        if freeze_header:
            _freeze_header(sheet)

    return workbook


def xlsx_write_sheets_data(file: str, sheets_data: List[tuple], *, auto_filter=True, freeze_header=True) -> str:
    """Writes multiple sheets data to .xlsx file. Adds filters and freezes header by default.

    :argument file
        Filepath pointing to where the data should be written.
        (.xlsx is automatically appended if missing)

    :argument sheets_data
        List containing tuples, each describing sheet data, with the following format
        [(sheet1_title, sheet1_headers, sheet1_rows), (sheet2_title, sheet2_headers, sheet2_rows), ...]

    :argument auto_filter
        If True will add auto-filters in all of the created sheets

    :argument freeze_header
        If True will freeze the header row in every sheet

    :returns
        absolute path to the file where the data was written
    """

    if not file.endswith(".xlsx"):
        file = file + ".xlsx"

    file = str(Path(file).absolute())
    _log.debug("writing sheets data to .xlsx file at: '%s', auto-filter: %s, freeze-header: %s",
               file, auto_filter, freeze_header)

    workbook = xlsx_workbook_from_sheets_data(sheets_data, auto_filter=auto_filter, freeze_header=freeze_header)
    workbook.save(file)

    _log.debug("done writing sheets data to .xlsx file: '%s' !", file)
    return file
