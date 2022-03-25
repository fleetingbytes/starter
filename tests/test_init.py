#!/usr/bin/env


import starter
import pytest
import pathlib
import sys
import datetime


@pytest.mark.skipif(pathlib.Path(sys.prefix).stem != "tama", reason="Test only in native enironment")
def test_date():
    starter_date = starter.__release_date__
    assert isinstance(starter_date, datetime.date), "__release_date__ must be instance of datetime.date"
    today = datetime.datetime.today()
    assert starter_date.year == today.year, "date.year in `__init__.py` is not current"
    assert starter_date.month == today.month, "date.month in `__init__.py` is not current"
    assert starter_date.day == today.day, "date.day in `__init__.py` is not current"


def test_strings():
    for text in (starter.__author__,
                 starter.__author_email__,
                 starter.__maintainer__,
                 starter.__maintainer_email__,
                 starter.__repository__,
                ):
        assert text
        assert isinstance(text, str)


def test_emails():
    for mail in (starter.__author_email__,
                 starter.__maintainer_email__,
                ):
        assert "@" in mail

