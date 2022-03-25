#!/usr/bin/env python


import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class Subparser:
    name: str
    aliases: [list]
    description: Optional[str]
    help: Optional[str]


for _name, _aliases, _help, _description in (
        ("check", [], "check (subcommand help)", "Checks certain things related to a test run"),
        ("config", [], "config (subcommand help)", "Reads or writes starter configuration"),
        ("execute", [], "execute (subcommand help)", "Executes a test"),
        ):
    setattr(sys.modules[__name__], _name, Subparser(_name, _aliases, _help, _description))
