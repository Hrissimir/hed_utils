import logging
from os import walk
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZipInfo

import pyminizip

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def write_zipped_text(dst_zip: str, text: str, password: str, text_file_name="protected.txt"):
    """Writes text to a .txt file and puts it in a password-protected zip.

    Arguments:
        dst_zip(str):           Path for the destination .zip file
        text(str):              The text to be written.
        password(str):          Password that will be used to lock the zip
        text_file_name(str):    Name of the .txt file that will be holding the text inside the archive

    """

    dst_path = Path(dst_zip).absolute()
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory() as tmp_dir:
        txt_file_path = Path(tmp_dir).joinpath(text_file_name)
        txt_file_path.write_text(text)
        file_prefix_in_zip = None
        zip_path = str(dst_path)
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

    src_path = Path(src_zip).absolute()
    with ZipFile(str(src_path), "r") as archive:
        archive.setpassword(bytes(password, "utf-8"))
        with archive.open(text_file_name) as file:
            return file.read().decode("utf-8")


def extract_zip(src_zip, dst_dir, pwd=None):
    src_zip = Path(src_zip).absolute()
    dst_dir = Path(dst_dir).absolute()
    _log.debug("extracting zip: ( %s ) to dir: ( %s )", str(src_zip), str(dst_dir))

    if not src_zip.exists():
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
    src_dir, dst_zip = Path(src_dir).absolute(), Path(dst_zip).absolute()
    _log.debug("zipping dir: '%s' to: '%s", str(src_dir), str(dst_zip))

    if not src_dir.exists():
        raise FileNotFoundError(str(src_dir))
    if not src_dir.is_dir():
        raise NotADirectoryError(str(src_dir))
    if dst_zip.exists():
        raise FileExistsError(str(dst_zip))

    with TemporaryDirectory() as tmp_dir:
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
