#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK


import argcomplete
import argparse
import os
import sys
import codecs
from starter import arguments
from starter import subparsers as subp


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers()
    parser_check = sp.add_parser(
            subp.check.name,
            aliases=subp.check.aliases,
            help=subp.check.help,
            description=subp.check.description,
            )
    parser_config = sp.add_parser(
            subp.config.name,
            aliases=subp.config.aliases,
            help=subp.config.help,
            description=subp.config.description,
            )
    parser_execute = sp.add_parser(
            subp.execute.name,
            aliases=subp.execute.aliases,
            help=subp.execute.help,
            description=subp.execute.description,
            )
    parser.add_argument(*arguments.version.args, **arguments.version.kwargs)
    parser_check.add_argument(*arguments.thing_to_check.args, **arguments.thing_to_check.kwargs)
    parser_config.add_argument(*arguments.list_config.args, **arguments.list_config.kwargs)
    parser_execute.add_argument(*arguments.test_suite.args, **arguments.test_suite.kwargs)
    parser_execute.add_argument(*arguments.abort_early.args, **arguments.abort_early.kwargs)
    return parser


def run(args: argparse.Namespace) -> None:
    from starter import entry
    entry.main(args)


def just_args(args: argparse.Namespace) -> None:
    print(f"{args}")


def main():
    parser = argument_parser()
    output_stream=None
    if "_ARGCOMPLETE_POWERSHELL" in os.environ:
        output_stream = codecs.getwriter("utf-8")(sys.stdout.buffer)
    argcomplete.autocomplete(parser, output_stream=output_stream)
    args = parser.parse_args()
    sys.exit(run(args))
    # sys.exit(just_args(args))


if __name__ == "__main__":
    main()
