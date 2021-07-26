import sys
from argparse import Namespace

from hed_utils.cli.arguments import create_parser
from hed_utils.cli.arguments import string_value
from hed_utils.support import ps_tool


def _parse_args(*args) -> Namespace:
    parser = create_parser(
        name="rkill",
        description="Recursively kill matching processes and their children."
    )
    parser.add_argument("--pid", action="store", type=int, help="process pid")
    parser.add_argument("--name", action="store", type=string_value, help="process name")
    parser.add_argument("--regex", action="store", type=string_value, help="process name pattern")
    parser.add_argument("-y", dest="dry", action="store_false", help="confirm the kill")

    return parser.parse_args(*args)


def main(*args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """

    args = _parse_args(*args)
    print(f"rkill: called with args {args}")

    targets = list()
    if args.pid:
        targets.append(ps_tool.get_process_by_pid(args.pid))
    if args.name:
        targets.extend(ps_tool.get_processes_by_name(args.name))
    if args.regex:
        targets.extend(ps_tool.get_processes_by_pattern(args.regex))

    targets = [_ for _ in targets if _]
    victims = ps_tool.rkill(targets, args.dry)
    if victims:
        print(ps_tool.format_processes(victims))
        print(f"\nrkill: stopped [ {len(victims)} ] processes!")
    else:
        print("rkill: no process was stopped!")


def run():
    """Entry point for console_scripts"""

    main(sys.argv[1:])


if __name__ == "__main__":
    run()
