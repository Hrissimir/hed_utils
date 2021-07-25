import argparse
import sys

import hed_utils.support.ps_tool.process_wrapper
from hed_utils.cli.cli_command import CliCommand
from hed_utils.support import ps_tool


class RkillCommand(CliCommand):
    """Recursively kill process and it's children"""

    def __init__(self):
        super().__init__()
        self.args_parser.add_argument("-p",
                                      "--pid",
                                      action="store",
                                      dest="pid",
                                      type=int,
                                      help="target process id")

        self.args_parser.add_argument("-n",
                                      "--name",
                                      action="store",
                                      dest="name",
                                      help="target process name")

        self.args_parser.add_argument("-r",
                                      "--regex",
                                      action="store",
                                      dest="regex",
                                      help="target process name regex pattern")

        self.args_parser.add_argument("-y",
                                      action="store_false",
                                      dest="dry",
                                      help="confirm the kill")

    @property
    def name(self) -> str:
        return "rkill"

    def run(self, *args):
        super().run(*args)
        self.log.debug("started with args: %s", self.args)

        initial_targets = list()

        if self.args.pid:
            wrapper = ps_tool.get_process_by_pid(self.args.pid)
            if wrapper:
                initial_targets.append(wrapper)

        if self.args.name:
            initial_targets.extend(
                ps_tool.get_processes_by_name(self.args.name)
            )

        if self.args.regex:
            initial_targets.extend(
                ps_tool.get_processes_by_pattern(self.args.regex)
            )

        all_targets, all_victims, all_survivors = hed_utils.support.ps_tool.process_wrapper.ProcessWrapper.rkill(
            initial_targets, self.args.dry
        )

        self.log.info("all targets count: %s", len(all_targets))
        self.log.debug("all targets: \n%s", hed_utils.support.ps_tool.process_wrapper.ProcessWrapper.format_as_table(all_targets, sort=False))

        self.log.info("all victims count: %s", len(all_victims))
        self.log.debug("all victims: \n%s", hed_utils.support.ps_tool.process_wrapper.ProcessWrapper.format_as_table(all_victims, sort=False))

        self.log.info("all survivors count: %s", len(all_survivors))
        self.log.debug("all survivors: \n%s", hed_utils.support.ps_tool.process_wrapper.ProcessWrapper.format_as_table(all_survivors, sort=False))


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
        print(hed_utils.support.ps_tool.process_wrapper.ProcessWrapper.format_as_table(victims))
        print(f"\nTotal of [ {len(victims)} ] victims! ( {invocation_details} )")
    else:
        print("rkill: No matching processes!")

    return


def run():
    """Entry point for console_scripts"""

    RkillCommand().run(*sys.argv[1:])


if __name__ == "__main__":
    run()
