#!/usr/bin/env python


import pytest
from pathlib import Path
from starter import utils
from starter.loggerdef import logger


def test_logger_wraps(caplog):
    for level in utils.Log_level.__args__:
        for entry in (True, False):
            for exit in (True, False):
                @utils.logger_wraps(entry=entry, exit=exit, level=level)
                def simple_func(i: int, more: str="predefined"):
                    return f"{i + i} and {more[1:]}{more[1:]}"
                expected_number = "42"
                expected_word = "xyzzy"
                with caplog.at_level(logger.level(level).no):
                    caplog.clear()
                    simple_func(int(expected_number), more=expected_word)
                if entry:
                    assert "Entering" in caplog.text
                    assert expected_number in caplog.text
                    assert expected_word in caplog.text
                else:
                    assert "Entering" not in caplog.text
                    assert expected_number not in caplog.text
                    assert expected_word not in caplog.text
                if exit:
                    assert "Exiting" in caplog.text
                    assert str(int(expected_number) * 2) in caplog.text
                    assert f"{expected_word[1:]}{expected_word[1:]}" in caplog.text
                else:
                    assert "Exiting" not in caplog.text
                    assert str(int(expected_number) * 2) not in caplog.text
                    assert f"{expected_word[1:]}{expected_word[1:]}" not in caplog.text


def rmdir(directory: Path) -> None:
    """
    Recursively removes a directory.
    Borrowed from https://stackoverflow.com/a/49782093/9235421 
    """
    for item in directory.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()
    directory.rmdir()


def test_provide_dir():
    if utils.test_dir.exists():
        rmdir(utils.test_dir)
    created_dir = utils.provide_dir(utils.test_dir)
    assert isinstance(created_dir, Path)
    assert created_dir.is_dir()
    assert created_dir.exists()
    rmdir(created_dir)
