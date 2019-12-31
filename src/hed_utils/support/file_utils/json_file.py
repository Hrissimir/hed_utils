import json
import logging
from pathlib import Path

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


def read_json(src_file):
    src_path = Path(src_file).absolute()
    _log.debug("reading JSON contents from: %s", src_path)

    if not src_path.exists():
        raise FileNotFoundError(src_path)
    if not src_path.is_file():
        raise IsADirectoryError(src_path)

    with src_path.open("rb") as in_file:
        return json.load(in_file)


def write_json(dst_file, obj, *, skipkeys=False, indent=4):
    filepath = Path(dst_file).absolute()
    _log.debug("writing (%s) object to .json at '%s'", type(obj).__name__, filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open("w") as out_file:
        json.dump(obj, out_file, skipkeys=skipkeys, indent=indent)
