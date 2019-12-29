import logging
import re
from pathlib import Path
from typing import Optional
from urllib.parse import unquote_plus

import requests
from bs4 import BeautifulSoup
from bs4.dammit import UnicodeDammit
from pathvalidate import sanitize_filename

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def download(url: str, *, parent_dir: Optional[str] = None, file_name: Optional[str] = None) -> str:
    """Retrieves the contents of the target URL and writes them to a local file.

    Args:
        url(str):           the target URL
        parent_dir(str):    the parent folder where the file is to be saved (defaults to cwd)
        file_name(str):     name of the file to be saved. (attempts to guess if None is passed)
    """

    dir_path = Path(parent_dir or Path.cwd())
    dir_path.mkdir(parents=True, exist_ok=True)

    with requests.get(url, allow_redirects=True) as resp:

        if not file_name:
            try:
                content_disposition = resp.headers["content-disposition"]
                file_name = re.findall(r"filename=(.+)", content_disposition)[0]
            except KeyError:
                file_name = unquote_plus(url).strip(" /").split("/")[-1]

        file_name = sanitize_filename(file_name)
        _log.debug(f"downloading [ URL: {url} ] to [ Folder: {parent_dir} ] ( File: {file_name} )")

        file_path = dir_path.joinpath(file_name)
        file_path.write_bytes(resp.content)
        file_size = round(len(resp.content) / (1024 ** 2), 3)
        _log.debug("downloaded file: %s ( %s mb. )", file_path, file_size)

        return str(file_path)


def create_soup(source) -> BeautifulSoup:
    return BeautifulSoup(UnicodeDammit(source).unicode_markup, "lxml")


def get_page_soup(url, params=None, **kwargs) -> BeautifulSoup:
    """Retrieves the page source using the 'requests.get' method,
     then creates and returns a BeautifulSoup object from the response contents"""

    _log.debug("getting page soup of url(%s)...", url)
    with requests.get(url, params, **kwargs) as response:
        return create_soup(response.content)


def get_page_source(url, params=None, **kwargs) -> str:
    """Retrieves the page source using the 'requests.get' method,
    then returns a prettified string version of the page source"""

    _log.debug("getting page source of url(%s)...", url)
    return get_page_soup(url, params, **kwargs).prettify()
