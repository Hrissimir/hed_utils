"""Helper methods for checking and conversion of param values."""
from os import PathLike
from os import fspath
from os.path import normpath
from pathlib import Path
from typing import Optional
from typing import Union


def string_value(
        name: str,
        value: Optional[str],
        *,
        empty_ok=True,
        none_ok=True,
        strip_whitespace=True,
        strip_quotes=True
) -> Optional[str]:
    """Check and pre-process string param value.

    Args:
        name (str): Param name.
        value (str): Param value.
        none_ok (bool): Accept `None` as valid value.
        empty_ok (bool): Accept empty string as valid value.
        strip_whitespace (bool): Strip whitespace from string start/end.
        strip_quotes (bool): Strip quotes from string start/end.

    Returns:
        str: Processed value according to call params.
             None if value was `None` and `none_ok` == True.

    Raises:
        TypeError: if the value is `None` and `none_ok` == false.
        TypeError: if the value is not a string or None.
        ValueError: if the processed value is empty and `empty_ok` == false.
    """

    def is_quoted(text: str) -> bool:
        """Checks if string value is quoted."""

        if text:
            for ch in "\'\"`":
                if text.startswith(ch) and text.endswith(ch):
                    return True
        return False

    if (value is None) and none_ok:
        return None

    if not isinstance(value, str):
        raise TypeError(name, str, type(value))

    result = value

    strip_whitespace = strip_whitespace or (not empty_ok)

    if strip_whitespace:
        result = result.strip()

    if strip_quotes:
        while is_quoted(result):
            result = result[1:-1]
            if strip_whitespace:
                result = result.strip()

    if result or empty_ok:
        return result
    else:
        raise ValueError(name, value)


def file_path(name: str, value: Union[bytes, str, PathLike], *, readable: bool) -> Path:
    """Check and pre-process file path param value.

    Args:
        name (str): Parameter name.
        value ([bytes, str, PathLike, Path]): Param value.
        readable (bool): Should the value point to existing file.

    Returns:
         Path: file path that is normalized, absolute and resolved.

    Raises:
        TypeError: if the value type is not in (bytes, str, PathLike).
        ValueError: if the value was empty or could not be converted to Path.
        IsADirectoryError: if the resolved path points to existing folder.
        FileNotFoundError: if the file does not exist and `readable` == True.
    """

    if not isinstance(value, (bytes, str, PathLike, Path)):
        raise TypeError(name, (bytes, str, PathLike, Path), type(value))

    path = fspath(value)
    if isinstance(path, bytes):
        try:
            path = path.decode(encoding="utf-8")
        except UnicodeError:
            path = path.decode(encoding="latin-1", errors="ignore")

    path = string_value(name, path, empty_ok=False, none_ok=False)

    try:
        path = Path(normpath(path)).absolute().resolve(strict=False)
    except Exception as ex:
        raise ValueError(name, value) from ex

    if path.exists() and path.is_dir():
        raise IsADirectoryError(name, value, path)

    if readable and (not path.exists()):
        raise FileNotFoundError(name, value, path)

    return path
