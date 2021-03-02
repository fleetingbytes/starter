#!/usr/bin/env python


from starter import version


def test_version():
    version_numbers = version.version.split(".")
    assert len(version_numbers) == 3
    for number in version_numbers:
        assert type(int(number)) is int
