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
"""

import logging
from typing import List

from gspread import authorize, Cell, Client, Spreadsheet, Worksheet, SpreadsheetNotFound, WorksheetNotFound
from oauth2client.service_account import ServiceAccountCredentials

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def create_client_using_json(filepath) -> Client:
    _log.debug("creating Client using JSON auth-file: '%s'", filepath)
    return authorize(ServiceAccountCredentials.from_json_keyfile_name(filename=filepath,
                                                                      scopes=["https://spreadsheets.google.com/feeds",
                                                                              "https://www.googleapis.com/auth/drive"]))


def open_spreadsheet(title, json_filepath) -> Spreadsheet:
    client = create_client_using_json(json_filepath)
    try:
        _log.debug("opening Spreadsheet with title: '%s' ...", title)
        return client.open(title)
    except SpreadsheetNotFound as err:
        _log.exception("SpreadsheetNotFound: '%s'! %s", title, err)
        raise ValueError("No such Spreadsheet!", title) from err


def open_worksheet(*, spreadsheet_title, worksheet_title, json_filepath) -> Worksheet:
    spreadsheet = open_spreadsheet(spreadsheet_title, json_filepath)
    try:
        _log.debug("opening Worksheet with title: '%s'...", worksheet_title)
        return spreadsheet.worksheet(worksheet_title)
    except WorksheetNotFound:
        _log.warning("creating missing worksheet with title: '%s'", worksheet_title)
        return spreadsheet.add_worksheet(worksheet_title, rows=100, cols=26)


def convert_values_to_cells(values: List[list], *, start_row=1, start_col=1) -> List[Cell]:
    _log.debug("converting values to cells...")
    return [Cell(row=row_idx, col=col_idx, value=value)
            for row_idx, row in enumerate(values, start=start_row)
            for col_idx, value in enumerate(row, start=start_col)]


def set_worksheet_values(worksheet: Worksheet, values: List[list]):
    _log.debug("clearing worksheet: %s ...", worksheet)
    worksheet.clear()
    cells = convert_values_to_cells(values)
    _log.debug("updating worksheet values...")
    worksheet.update_cells(cells)
    _log.debug("worksheet values has been set!")


def append_worksheet_values(worksheet: Worksheet, values: List[list]):
    _log.debug("appending %s rows values to worksheet...", len(values))

    cells = convert_values_to_cells(values, start_row=len(worksheet.col_values(1)) + 1)
    worksheet.add_rows(len(values))
    worksheet.update_cells(cells)
