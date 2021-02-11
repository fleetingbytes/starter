#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK


import sys
import pathlib
import argparse
import argcomplete
import functools
from argcomplete.completers import EnvironCompleter as EC
from itertools import filterfalse
from loguru import logger
# Own modules
from starter import errors
from starter import utils
from starter import config_loader
from starter import version


# Setup logging part 1
logger = logger.opt(colors=True)
logger.opt = functools.partial(logger.opt, colors=True)
logger.remove()


def setup_logging_directory(directory: pathlib.Path) -> pathlib.Path:
    """
    Returns a logger and a path to directory where the logs are saved
    """
    try:
        path_to_dir = utils.provide_dir(directory)
    except FileExistsError:
        logger.error(f"Failed to create the directory `{str(path_to_dir)}` because it already exists as a file.")
        logger.error(f"Please create the directory `{str(path_to_dir)}`")
    return path_to_dir


path_to_dir = setup_logging_directory(pathlib.Path.home() / utils.dir_name)


# Setup logging part 2
logger.add(path_to_dir / "trace.log", level="TRACE", mode="w", encoding="utf-8")
logger.add(path_to_dir / "debug.log", level="DEBUG", mode="w", encoding="utf-8")
logger.add(path_to_dir / "info.log", level="INFO", mode="w", encoding="utf-8")
logger.add(sys.stdout, level="INFO", format="<level>{message}</level>")


def argument_parser() -> argparse.ArgumentParser:
    """
    Creates an argument parser for command line arguments
    """
    parser = argparse.ArgumentParser(description="starter")
    parser.add_argument("-v", "--version", action="store_true", help="print out starter version and exit").completer = EC
    parser.add_argument("--autoconfig", action="store_true", help="Configure starter automatically").completer = EC
    return parser


@utils.logger_wraps()
def run(config: config_loader.Config) -> None:
    logger.trace("Trace message")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.success("Success message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")


@utils.logger_wraps()
def cli_start(version) -> None:
    """
    Entry point for any component start from the commmand line
    """
    parser = argument_parser()
    argcomplete.autocomplete(parser)
    cli_args = parser.parse_args()
    logger.trace(f"Parsed arguments: {cli_args}")
    path_to_config = path_to_dir / utils.configuration_file_name
    try:
        if cli_args.version:
            logger.info(f"{version}")
        else:
            with config_loader.Config(path_to_config, cli_args.autoconfig) as config:
                config.cli_args = cli_args
                run(config)
    except errors.WrongConfiguration as err:
        logger.error(err.message)
    except Exception as err:
        logger.exception(f"Uncaught exception {repr(err)} occurred.")


if __name__ == "__main__":
    pass
