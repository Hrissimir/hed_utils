import argparse
import sys

from hed_utils.support import ps_tool


def _parse_args(args):
    parser = argparse.ArgumentParser(description="Recursively kill matching processes and their children.")

    parser.add_argument("-pid", dest="pid", action="store", type=int, help="target process id")
    parser.add_argument("-n", dest="name", action="store", help="target process name")
    parser.add_argument("-p", dest="pattern", action="store", help="target process name pattern")
    parser.add_argument("-y", dest="dry", action="store_const", const=False, default=True, help="confirm the kill")

    return parser.parse_args(args)


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """

    args = _parse_args(args)

    pid = args.pid
    name = args.name
    pattern = args.pattern
    dry = args.dry

    invocation_details = f"pid={pid}, name='{name}', pattern='{pattern}', dry={dry}"
    print(f"rkill called: {invocation_details}")

    victims = []
    if pid:
        victims.extend(ps_tool.kill_process_by_pid(pid, dry=dry))
    if name:
        victims.extend(ps_tool.kill_processes_by_name(name, dry=dry))
    if pattern:
        victims.extend(ps_tool.kill_processes_by_pattern(pattern, dry=dry))

    if victims:
        print()
        print(ps_tool.format_processes(victims))
        print(f"\nTotal of [ {len(victims)} ] victims! ( {invocation_details} )")
    else:
        print("rkill: No matching processes!")

    return


def run():
    """Entry point for console_scripts"""

    main(sys.argv[1:])


if __name__ == "__main__":
    run()
