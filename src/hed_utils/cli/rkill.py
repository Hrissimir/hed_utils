import argparse
import sys

from hed_utils.support import ps_tool


def _parse_args(args):
    parser = argparse.ArgumentParser(description="Recursively kill matching processes and their children.")

    parser.add_argument(dest="value", type=str, help="value to use with the matching strategy")

    parser.add_argument("--kill",
                        dest="kill",
                        action="store",
                        choices={"y", "n"}, default="n",
                        help="should the kill be actually performed (default: n)")

    parser.add_argument("--by", dest="by", action="store",
                        choices={"pid", "name", "pattern"}, default="pattern",
                        help="targets matching strategy (default: pattern)")

    return parser.parse_args(args)


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """

    args = _parse_args(args)

    kill = args.kill
    by = args.by
    value = args.value

    invocation_details = f"'rkill' called with args: kill='{kill}', by='{by}', value='{value}'"
    print(invocation_details)

    funcs_map = {"pid": ps_tool.kill_process_by_pid,
                 "name": ps_tool.kill_processes_by_name,
                 "pattern": ps_tool.kill_processes_by_pattern}

    kill_func = funcs_map[by]
    dry = not (kill.lower() == "y")
    victims = kill_func(value, dry=dry)

    if victims:
        print()
        print(ps_tool.format_processes(victims))
        print(f"\nTotal of [ {len(victims)} ] victims! ( {invocation_details} )")
    else:
        print("rkill: No matching processes!")


def run():
    """Entry point for console_scripts"""

    main(sys.argv[1:])


if __name__ == "__main__":
    run()
