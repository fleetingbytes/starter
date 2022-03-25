#!/usr/bin/env python


from re_patterns import Rstr
from starter import version


def test_version():
    version_numbers = version.version.split(".")
    assert len(version_numbers) == 3
    for number in version_numbers:
        try:
            assert type(int(number)) is int
        except ValueError:
            # probably because of "rc1" suffix, e.g. "2.0.1rc1"
            pattern = Rstr(r"\d+").followed_by(r"\D").named("number")
            match = pattern.search(number)
            if match:
                assert type(int(match.group("number"))) is int

