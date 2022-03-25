#!/usr/bin/env python


import dataclasses
import sys
from typing import Optional
from typing import Union
from typing import Mapping
from typing import Iterable
from typing import Type
from starter import choices


@dataclasses.dataclass
class Argument:
    short: Optional[str] = None
    long: Optional[str] = None
    name: Optional[str] = None
    action: Optional[str] = None
    type: Optional[Type] = None
    nargs: Optional[str] = None
    metavar: Optional[str] = None
    dest: Optional[str] = None
    const: Optional[str] = None
    choices: Union[Iterable[str], Iterable[int], None] = None
    required: Optional[bool] = None
    help: Optional[str] = None
    args: tuple = dataclasses.field(init=False)
    kwargs: Mapping[str, Union[str, Type, Iterable[str], Iterable[int], None]] = dataclasses.field(init=False)
    def __post_init__(self):
        if self.name is None:
            self.args = tuple(" ".join(filter(lambda x: x is not None, (self.short, self.long))).split(" "))
        else:
            self.args = (self.name, )
        self.__name__ = self.__create_name__()
        self.kwargs = dict(
                (k, v) for k, v in self.__dict__.items() 
                if not k.startswith("_") and k not in ("args", "short", "long", "name") and v is not None
                )
    def __create_name__(self):
        if self.dest is not None:
            attr = "dest"
        elif self.name is not None:
            attr = "name"
        elif self.long is not None:
            attr = "long"
        else:
            attr = "short"
        return getattr(self, attr).replace("--", "").replace("-", "_")


version = Argument(
        short="-v",
        long="--version",
        action="store_true",
        help="print out starter version",
        )
thing_to_check = Argument(
        name="thing_to_check",
        type=str,
        help="Thing you want to check",
        )
test_suite = Argument(
        name="test_suite",
        type=str,
        help="Test suite to execute",
        )
abort_early = Argument(
        short="-x",
        long="--abort-early",
        action="store_true",
        help="Aborts the test run as soon as an error is encountered",
        )
list_config = Argument(
        short="-l",
        long="--list",
        action="store_true",
        help="Lists all configuration values",
        )
