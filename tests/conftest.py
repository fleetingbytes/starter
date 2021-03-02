#!/usr/bin/env python


import pytest
import pathlib
import string
import random
import logging
from _pytest.logging import caplog as _caplog
from starter.loggerdef import logger


collect_ignore = [
    # "test_utils.py",
    # "test_config_loader.py",
    # "test_entry.py",
    # "test_readme.py",
    # "test_version.py",
    # "test_init.py",
    # "test_menu.py",
    ]


# Making pytest caplog work with loguru
# https://loguru.readthedocs.io/en/stable/resources/migration.html?highlight=pytest#making-things-work-with-pytest-and-caplog
@pytest.fixture
def caplog(_caplog):
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)
    # handler_id = logger.add(PropagateHandler(), level="TRACE", format="{message} {extra}")
    handler_id = logger.add(PropagateHandler(), level="TRACE", format="{message}")
    yield _caplog
    logger.remove(handler_id)


@pytest.fixture
def config_files():
    return pathlib.Path(__file__).parent.absolute() / "config_files"


def random_string(minlen: int, maxlen: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=random.randint(minlen, maxlen)))


def create_file(filename: pathlib.Path, content: str) -> pathlib.Path:
    if filename.exists():
        raise errors.RandomFileAlreadyExistsError("Try again")
    with open(filename, mode="w", encoding="utf-8") as file:
        file.write(content)
    print(f"Created file {filename.name}")
    return filename
