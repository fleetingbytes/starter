#!/usr/bin/env python


import sys
from starter import version
from starter import entry


def starter():
    sys.exit(entry.cli_start(version.version))


if __name__ == "__main__":
    starter()
