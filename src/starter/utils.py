#!/usr/bin/env python


from starter.loggerdef import logger
import pathlib
import functools
import time
from typing import Literal


home_dir_name = "starter"
dir_name = ".starter"
configuration_file_name = "starter_configuration.ini"


archives = (".zip", ".jar")
webapp_archive_masks = tuple(("*" + ext for ext in archives))
Log_level = Literal["UNIMPORTANT", "PROCEDURE", "INFO", "SUCCESS", "IMPORTANT", "WARNING", "ERROR", "CRITICAL"]


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


def timeit(func):
    """
    Decorator which writes how long it took for a
    function to run.
    """
    name = func.__name__
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("Function '{}' executed in {:f} s", name, end - start)
        return result
    return wrapped


def input_path(message) -> pathlib.Path:
    path = pathlib.Path(input(message))
    logger.info("")
    return path


def provide_dir(directory: pathlib.Path) -> pathlib.Path:
    """
    Checks if there is a directory of name `dir_name` in the user home path.
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


def warn(s: str) -> str:
    """
    Creates a string highlighted as warning in log output
    """
    return " ".join(("◊", s))


if __name__ == "__main__":
    pass
