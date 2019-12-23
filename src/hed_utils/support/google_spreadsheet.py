"""
Target 'Spreadsheet' setup instructions:

    1. Go to https://console.developers.google.com/
    2. Login with the google account that is to be owner of the 'Spreadsheet'.
    3. At the top-left corner, there is a drop-down right next to the "Google APIs" text
    4. Click the drop-down and a modal-dialog will appear, then click "NEW PROJECT" at it's top-right
    5. Name the project relevant to how the sheet is to be used, don't select 'Location*', just press 'CREATE'
    6. Open the newly created project from the same drop-down as in step 3.
    7. There should be 'APIs' area with a "-> Go to APIs overview" at it's bottom - click it
    8. A new page will load having '+ ENABLE APIS AND SERVICES' button at the top side's middle - click it
    9. A new page will load having a 'Search for APIs & Services' input - use it to find and open 'Google Drive API'
    10. In the 'Google Drive API' page click "ENABLE" - you'll be redirected back to the project's page
    11. There will be a new 'CREATE CREDENTIALS' button at the top - click it
    12. Setup the new credentials as follows:
        - Which API are you using? -> 'Google Drive API'
        - Where will you be calling the API from? -> 'Web server (e.g. node.js, Tomcat)
        - What data will you be accessing? -> 'Application data'
        - Are you planning to use this API with App Engine or Compute Engine? -> No, I'm not using them.
    13. Click the blue button 'What credentials do I need', will take you to 'Add credentials to you project' page
    14. Setup the credentials as follows:
        - Service account name:  {whatever name you type is OK, as long the input accepts it}
        - Role: Project->Editor
        - Key type: JSON
    15. Press the blue 'Continue' button, and a download of the credentials secrets file will begin (store it safe)
    16. Close the modal and go back to the project 'Dashboard' using the left-side navigation panel
    17. Repeat step 8.
    18. Search for 'Google Sheets API', then open the result and click the blue 'ENABLE' button
    19. Open the downloaded secrets.json file and copy the value of the 'client_email'
    20. Using the same google account as in step 2. , go to the normal google sheets and create & open the 'Spreadsheet'
        - do a final renaming to the spreadsheet now to avoid coding issues in future
    21. 'Share' the document with the email copied in step 19., giving it 'Edit' permissions
        - you might want to un-tick 'Notify people' before clicking 'Send' as it's a service email you're sharing with
        - 'Send' will change to 'OK' upon un-tick, but we're cool with that - just click it.

    You are now ready to use this class for retrieving 'Spreadsheet' handle in the code!

    NOTES:

        !!! DO NOT INCLUDE THE SECRETS JSON FILE IN YOUR PROJECT !!!
            - Store it on the system that will be executing the code, and provide the path to it during runtime.

        You might want to pre-populate the sheet header row and delete the excessive columns manually to avoid issues.

        Make sure you installed dependencies:
            - pip install gspread oauth2client

        To discover more usage details just copy this file contents inside IDE and check what the autocomplete shows.

    Example:

        spreadsheet = google_spreadsheet.connect(spreadsheet_name="...", json_auth_file="...")
        sheet1 = spreadsheet.get_worksheet(0)
        print(sheet1.title)
        print(sheet1.row_values(1))  # 1-based index
        print(sheet1.get_all_records())  # returns a list of dicts representing the rows data (first row acts as keys)
        values = [ ... , ... , ...]
        sheet1.append_row(values)
"""

import logging
import random
from pathlib import Path
from pprint import pformat
from typing import Optional, List

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from hed_utils.support.time_tool import busy_wait

SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

PAUSES_AFTER_ROW_APPEND = [1, 1.1, 1.2, 1.3, 1.4]  # google says 100 requests per 100 seconds, so we wait a bit.

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def connect(spreadsheet_name: str, json_auth_file: str) -> gspread.models.Spreadsheet:
    """Authenticates with Google and returns spreadsheet handle."""

    _credentials = ServiceAccountCredentials.from_json_keyfile_name(json_auth_file, SCOPE)
    _client = gspread.authorize(_credentials)
    _spreadsheet = _client.open(spreadsheet_name)
    return _spreadsheet


def get_possible_connect_error(spreadsheet_name: str, json_auth_file: str) -> Optional[str]:
    """Attempts to connect to the spreadsheet and returns None on success.

    If any error occurred during the connection attempt, a proper message will be returned."""

    auth_file_path = Path(json_auth_file)
    if not auth_file_path.exists():
        return f".json auth file not present at: '{auth_file_path}'"

    try:
        connect(spreadsheet_name, json_auth_file)
    except Exception as connection_error:
        return f"Could not open spreadsheet: '{spreadsheet_name}'! Reason: '{connection_error}'"


def get_possible_append_row_error(*,
                                  spreadsheet_name: str,
                                  json_auth_file: str,
                                  worksheet_index: int,
                                  row_len: int) -> Optional[str]:
    """ Connects to the spreadsheet and checks if the target worksheet contains enough columns to receive such row.

    Will return any error message if present or None if such row can be appended seamlessly"""

    auth_file_path = Path(json_auth_file)
    if not auth_file_path.exists():
        return f".json auth file not present at: '{auth_file_path}'"

    try:
        spreadsheet = connect(spreadsheet_name, json_auth_file)
    except Exception as connection_error:
        return f"Could not open spreadsheet: '{spreadsheet_name}'! Reason: '{connection_error}'"

    try:
        worksheet = spreadsheet.get_worksheet(worksheet_index)
    except Exception as worksheet_error:
        return f"Could not get worksheet with index: '{worksheet_index}'! Reason: '{worksheet_error}'"

    columns_count = worksheet.col_count
    if columns_count < row_len:
        return f"Row with length: '{row_len}' won't fit in a worksheet with '{columns_count}' columns!"

    return None


def append_rows_to_worksheet(rows: List[List[str]], worksheet: gspread.models.Worksheet):
    """Helper func to slowly append rows because Google only allows 100 requests per 100 seconds when using for free"""

    _log.info("appending '%s' rows to worksheet: '%s'", len(rows), worksheet.title)

    busy_wait(2)

    failed_rows = []

    for i, values in enumerate(rows, start=1):

        # wait a random bit to ensure usage time-quota will be met
        pause = random.choice(PAUSES_AFTER_ROW_APPEND)

        try:
            _log.info("appending row ( %s / %s ) - %s", i, len(rows), values)
            worksheet.append_row(values)
            busy_wait(pause)
        except:
            _log.exception("error while appending row!")
            failed_rows.append(values)
            busy_wait(pause)

    if failed_rows:
        _log.error("failed to append the following rows:\n%s", pformat(failed_rows))
