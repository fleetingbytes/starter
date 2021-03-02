#!/usr/bin/env


import datetime
import starter
import pytest
import pathlib
import sys


@pytest.mark.skipif(pathlib.Path(sys.prefix) != pathlib.Path(r"C:\ProgramData\Anaconda3\envs\starter"), reason="Test only in native enironment")
def test_date():
    starter_date = datetime.datetime.strptime(starter.__date__, "%Y-%m-%d")
    today = datetime.datetime.today()
    assert starter_date.year == today.year, "date.year in `__init__.py` is not current"
    assert starter_date.month == today.month, "date.month in `__init__.py` is not current"
    assert starter_date.day == today.day, "date.day in `__init__.py` is not current"


def test_author():
    assert starter.__author__
    assert isinstance(starter.__author__, str)


def test_author_email():
    assert starter.__author_email__
    assert isinstance(starter.__author_email__, str)
    assert "@" in starter.__author_email__
