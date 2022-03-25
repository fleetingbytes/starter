#!/usr/bin/env python


import functools
import os
from pathlib import Path
from typing import Literal
from starter.loggerdef import logger


home_dir_name = "starter"
test_dir_name = "pytest"
configuration_file_name = "starter.toml"
log_dir = Path(os.getenv("appdata")) / home_dir_name
tmp_dir = Path(os.getenv("tmp")) / home_dir_name
test_dir = tmp_dir / test_dir_name


Log_level = Literal["TRACE", "DEBUG", "UNIMPORTANT", "PROCEDURE", "INFO", "SUCCESS", "IMPORTANT", "WARNING", "ERROR", "CRITICAL"]


def logger_wraps(*, entry=True, exit=True, level="TRACE"):
    """
    Decorator factory which returns the function
    wrapped with a wrapper reporting entry, or exit
    of a function on the specified log level
    """
    def wrapper(func):
        name = func.__name__
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(colors=False, depth=1)
            if entry:
                logger_.log(level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result
        return wrapped
    return wrapper


def provide_dir(directory: Path) -> Path:
    """
    Checks if `directory` already exists.
    If not, it will try to create one. 
    """
    if directory.exists() and directory.is_dir():
        logger.trace(f"Found directory {str(directory)}")
    else:
        while True:
            try:
                directory.mkdir()
                logger.success(f"Created directory {str(directory)}")
                break
            except FileNotFoundError:
                provide_dir(directory.parent)
                continue
            except FileExistsError:
                logger.debug(f"{directory} already exists")
                break
    return directory
