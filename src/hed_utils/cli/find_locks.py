"""CLI command for finding locking processes of file or folder."""
import sys
from pathlib import Path
from typing import List
from hed_utils.cli.cli_command import CliArg
from hed_utils.cli.cli_command import CliCommand
from hed_utils.support.ps_tool import ProcessWrapper

class FindLocks(CliCommand):
    """Find processes that are locking file/folder and preventing deletion."""

    def __init__(self):
        super().__init__()
        self.args_parser.add_argument(
            "-p",
            "--path",
            action="store",
            dest="path",
            type=CliArg.existing_path,
            default=Path.cwd(),
            help="path to existing location. defaults to CWD.")

    @property
    def name(self) -> str:
        return "find-locks"

    def run(self, *args):
        super().run(*args)
        path:Path = self.args.path
        self.log.info("searching for locking processes of '%s'", path)

        if path.is_file():
            locks = self.find_file_locks(path)
        else:
            locks = find_dir_locks(path)

    def find_file_locks(self, file_path:Path)->List[ProcessWrapper]:
        pass
    def find_dir_locks(self, dir_path: Path)->List[ProcessWrapper]:
        pass

def run():
    """Entry point of console scripts."""

    FindLocks().run(*sys.argv[1:])
