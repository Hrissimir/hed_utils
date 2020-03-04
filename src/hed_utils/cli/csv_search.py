"""
usage: nap_search.py [-h] [-t TEXT] [-d DIRECTORY] [-of OUTPUT_FILE]

Find text in CSV files.

optional arguments:
  -h, --help       show this help message and exit
  -t TEXT          the text to find
  -d DIRECTORY     path to CSV files directory
  -of OUTPUT_FILE  path to result output file

"""
import argparse
import logging
import sys
from collections import namedtuple
from io import StringIO
from os import getcwd
from os.path import abspath, basename

from tabulate import tabulate

from hed_utils.support.file_utils.csv_file import get_csv_files, get_csv_files_containing
from hed_utils.support.file_utils.xlsx_file import xlsx_write_sheets_data
from hed_utils.support.text_tool import normalize
from hed_utils.support.time_tool import Timer

LOG_FORMAT = "%(asctime)s | %(levelname)8s | %(message)s"

Result = namedtuple("Result", "filepath headers rows")

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def _parse_args(args):
    parser = argparse.ArgumentParser(description="Find text in CSV files.")

    parser.add_argument("-v",
                        dest="verbose",
                        action="store_const",
                        const=logging.DEBUG,
                        default=logging.INFO,
                        help="sets the log level to DEBUG")
    parser.add_argument("-d",
                        dest="directory",
                        action="store",
                        type=str,
                        default=getcwd(),
                        help=f"path to CSV files directory (default: CWD)")
    parser.add_argument("-o",
                        dest="text_report",
                        action="store",
                        type=str,
                        default=None,
                        help="filepath for writing text report ")
    parser.add_argument("-xl",
                        dest="excel_report",
                        action="store",
                        type=str,
                        default=None,
                        help="filepath for writing excel report")
    parser.add_argument("-e",
                        dest="encoding",
                        action="store",
                        default="utf-8",
                        help="encoding for opening the CSV files (default: utf-8)")
    parser.add_argument("-t",
                        dest="text",
                        action="store",
                        type=str,
                        required=True,
                        help="the text to find")
    parser.add_argument("-i",
                        dest="ignorecase",
                        action="store_const",
                        const=True,
                        default=False,
                        help="if passed search will ignore casing (default: False)")

    return parser.parse_args(args)


def _generate_excel_report(results: list, file: str):
    if not file:
        _log.warning("no excel report file was set!")
        return

    file = abspath(file)
    _log.info("writing excel report to: '%s'", file)
    sheets_data = [(basename(filepath), headers, rows)
                   for filepath, headers, rows
                   in results]
    xlsx_write_sheets_data(file, sheets_data)


def _generate_text_report(results: list, file: str):
    def _format_result(r):
        filepath, headers, rows = r
        sep = len(filepath) * "="
        return f"\n\n{sep}\n{filepath}:\n\n{tabulate(tabular_data=rows, headers=headers)}\n"

    report = StringIO()

    for result in results:
        details = _format_result(result)
        print(details, file=report)

    print(report.getvalue())

    if file:
        _log.info("writing text report to file: '%s'", file)
        with open(file, mode="w") as fp:
            fp.write(report.getvalue())
    else:
        _log.warning("No text report file was set!")


def _init_logging(level):
    from hed_utils.support import log
    log.init(level=level, log_format=LOG_FORMAT)


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """

    args = _parse_args(args)
    print("search started with args: ", args)

    # extract args
    encoding = args.encoding
    text = normalize(args.text.strip())  # ensure encoding consistency
    directory = abspath(args.directory)
    text_report_path = args.text_report
    excel_report_path = args.excel_report
    verbose = args.verbose
    ignorecase = args.ignorecase

    _init_logging(verbose)

    # measure the program execution time
    search_timer = Timer()
    search_timer.start()

    # perform the search
    csv_files = [file for file in get_csv_files(directory)]
    results = get_csv_files_containing(csv_files, text, ignorecase=ignorecase, encoding=encoding)
    search_timer.stop()

    # generate reports if needed
    if results:
        results.sort(key=(lambda r: len(r[-1])), reverse=True)
        _generate_text_report(results, text_report_path)
        _generate_excel_report(results, excel_report_path)
    else:
        _log.warning("No results were found!")

    rows_count = sum([len(result[-1]) for result in results])
    _log.info("All Done! Found [ %s ] matching rows in [ %s ] different files (took: %.3f s.)",
              rows_count, len(results), search_timer.elapsed)


def run():
    """Entry point for console_scripts"""

    main(sys.argv[1:])
