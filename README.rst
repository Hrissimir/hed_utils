=========
hed_utils
=========


    Personal utils collection for (mostly) automation projects.



What's inside?
==============


    * The following CLI bindings:


        * rkill (recursively kill processes)

            usage: rkill [-h] [-pid PID] [-n NAME] [-p PATTERN] [-y]

            Recursively kill matching processes and their children.

            optional arguments:

                -h, --help  show this help message and exit

                -pid PID    target process id

                -n NAME     target process name

                -p PATTERN  target process name pattern

                -y          confirm the kill


        * csv-search (find matching rows in multiple csv files)

            usage: csv-search [-h] [-v] [-d DIRECTORY] [-o TEXT_REPORT] [-xl EXCEL_REPORT] [-e ENCODING] -t TEXT [-i]

            Find text in CSV files.

            optional arguments:

                -h, --help        show this help message and exit

                -v                sets the log level to DEBUG

                -d DIRECTORY      path to CSV files directory (default: CWD)

                -o TEXT_REPORT    filepath for writing text report

                -xl EXCEL_REPORT  filepath for writing excel report

                -e ENCODING       encoding for opening the CSV files (default: utf-8)

                -t TEXT           the text to find

                -i                if passed search will ignore casing (default: False)


    * The following packages:

        * hed_utils (Package root)

            * cli (Implementation of CLI bindings)

            * selenium (Selenium wrappers & helpers)

            * support (Tools for achieving common tasks)



Installation:
=============


! Dependencies:
---------------


    * psutil

    * tabulate

    * pytz

    * tzlocal

    * bs4

    * pathvalidate

    * requests

    * lxml

    * openpyxl

    * oauth2client

    * gspread

    * selenium



Install from PyPI:
------------------


    * `pip install -U --force hed_utils`



Note
====


This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
