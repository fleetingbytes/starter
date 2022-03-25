#!/usr/bin/env python


from pathlib import Path
from argparse import Namespace
from starter import utils
from starter.loggerdef import logger


def setup_logging_directory(directory: Path) -> Path:
    """
    Returns a path to the directory where the logs are saved.
    """
    try:
        path_to_dir = utils.provide_dir(directory)
    except FileExistsError:
        logger.error(f"Failed to create the directory `{str(path_to_dir)}` because it already exists as a file.")
        logger.error(f"Please create the directory `{str(path_to_dir)}`")
    return path_to_dir


path_to_dir = setup_logging_directory(utils.log_dir)


# Setup logging files:
logger.add(path_to_dir / "trace.log", level="TRACE", mode="w", encoding="utf-8")
logger.add(path_to_dir / "debug.log", level="DEBUG", mode="w", encoding="utf-8")
logger.add(path_to_dir / "info.log", level="UNIMPORTANT", mode="w", encoding="utf-8")


def main(args: Namespace) -> None:
    logger.info(args)
