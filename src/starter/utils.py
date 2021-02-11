#!/usr/bin/env python


from loguru import logger
import pathlib
import functools
import time


program_name = home_dir_name = "starter"
dir_name = "".join((".", program_name))
configuration_file_name = "starter_configuration.ini"


def logger_wraps(*, entry=True, exit=True, level="TRACE"):
    def wrapper(func):
        name = func.__name__
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result
        return wrapped
    return wrapper


def timeit(func):
    name = func.__name__
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.trace("Function '{}' executed in {:f} s", name, end - start)
        return result
    return wrapped


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
                logger.info(f"Created directory {str(directory)}")
                break
            except FileNotFoundError:
                provide_dir(directory.parent)
                continue
            except FileExistsError:
                logger.trace(f"{directory} already exists")
                break
    return directory


def warn(s: str) -> str:
    """
    Creates a string highlighted as warning in log output
    """
    return " ".join(("◊", s))
