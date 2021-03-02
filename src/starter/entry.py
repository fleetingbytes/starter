#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK


from __future__ import annotations
import pathlib
import argparse
import argcomplete
import functools
from argcomplete.completers import EnvironCompleter as EC
from argcomplete.completers import ChoicesCompleter as CC
#Own modules
from starter.loggerdef import logger
from starter import utils
from starter import errors
from starter import config_loader


def setup_logging_directory(directory: pathlib.Path) -> pathlib.Path:
    """
    Returns a path to the directory where the logs are saved.
    """
    try:
        path_to_dir = utils.provide_dir(directory)
    except FileExistsError:
        logger.error(f"Failed to create the directory `{str(path_to_dir)}` because it already exists as a file.")
        logger.error(f"Please create the directory `{str(path_to_dir)}`")
    return path_to_dir


path_to_dir = setup_logging_directory(pathlib.Path.home() / utils.dir_name)


# Setup logging files:
logger.add(path_to_dir / "trace.log", level="TRACE", mode="w", encoding="utf-8")
logger.add(path_to_dir / "debug.log", level="DEBUG", mode="w", encoding="utf-8")
logger.add(path_to_dir / "info.log", level="UNIMPORTANT", mode="w", encoding="utf-8")


class OrderedNamespace(argparse.Namespace):
    """
    Custom class for ArgumentParser to be aware of the ordering of command line arguments.
    An argparse.ArgumentParser() using this namespace
    parses command line arguments in a customized way 
    so that order and multiple occurrences of each
    option are taken into account.

    Borrowed from https://stackoverflow.com/questions/7737769/python-argparse-how-to-get-order-of-optional-arguments-from-command-line.
    """
    # Enhanced this so that multiple occurrences of one argument are tracked.
    def __init__(self, **kwargs):
        self.__dict__["_order"] = []
        self.__dict__["_ignore_arg_len"] = 0
        self.__dict__["_any_cli_args"] = False
        super().__init__(**kwargs)
    def __setattr__(self, attr, value):
        super().__setattr__(attr, value)
        if attr in self._order and not self.__dict__["_any_cli_args"]:
            self.__dict__["_any_cli_args"] = True
            self.__dict__["_ignore_arg_len"] = len(self.__dict__["_order"])
        self.__dict__["_order"].append(attr)
    def ordered(self):
        # if no cli arguments were given, return empty tuple
        if self._any_cli_args:
            return ((attr, getattr(self, attr)) for attr in self._order[self._ignore_arg_len:] if not attr.startswith("_"))
        else:
            return ()


def argument_parser() -> argparse.ArgumentParser:
    """
    Creates an argument parser for command line arguments
    """
    parser = argparse.ArgumentParser(description="starter: Command Line Automation of Webapp-related Settings")
    parser.add_argument("--version", action="store_true", help="print out starter version and exit").completer = EC
    parser.add_argument("--autoconfig", action="store_true", help="Configure starter automatically").completer = EC
    parser.add_argument("--something", action="store_true", help="Do something").completer = EC
    return parser


def run(config: config_loader.Config) -> None:
    """
    Runs the program depending on the options given
    in the command line (`config.cli_args.ordered()`).
    """
    for argument, value in config.cli_args.ordered():
        logger.trace(f"Processing option {repr(argument)}, {repr(value)}")
        # cli option --something
        if argument == "something":
            pass


@utils.logger_wraps()
def cli_start(version) -> None:
    """
    Entry point for the starter start from command line
    """
    parser = argument_parser()
    argcomplete.autocomplete(parser)
    cli_args = parser.parse_args(namespace=OrderedNamespace())
    logger.trace(f"Parsed arguments: {cli_args}")
    logger.debug(f"Ordered command line arguments: {tuple(cli_args.ordered())}")
    path_to_config = path_to_dir / utils.configuration_file_name
    try:
        if cli_args.version:
            logger.info(f"{version}")
        with config_loader.Config(path_to_config, cli_args.autoconfig) as config:
            config.cli_args = cli_args
            run(config)
    except errors.WrongConfiguration as err:
        logger.trace(f"Handling WrongConfiguration error (will just type it out for the user)")
        if err.payload is not None:
            logger.error(f"{err.message}: {err.payload.__class__.__name__} {err.payload}")
        logger.error(f"Correct `{str(path_to_config)}` manually or delete it to create a default one.")
    except KeyboardInterrupt as e:
        logger.error(f"Keyboard Interrupt")
    except Exception as err:
        logger.exception(f"Uncaught exception {repr(err)} occurred.")
    finally:
        pass


if __name__ == "__main__":
    pass
