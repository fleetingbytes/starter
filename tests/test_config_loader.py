#!/usr/bin/env python


import pathlib
import re
import inspect
import pytest
import urllib.parse
import configparser
from collections import namedtuple
from starter import errors
from starter import config_loader
from starter import utils
from starter import testhelper


def test_config_loader():
    test_home = utils.provide_dir(pathlib.Path.home() / "starter_test")
    test_config_file_path = test_home / "test_config.ini"
    regex = re.compile(r""" {8}self\.(?P<attr>\w+) ?= ?self\..*(?P<method>get.*?)\(""")
    source_lines, _ = inspect.getsourcelines(config_loader.Config.parse_config_and_check_values)
    types = dict((
        ("get", str),
        ("getint", int),
        ("getpath", pathlib.Path),
        ("getfloat", float),
        ("geturl", urllib.parse.ParseResult),
        ))
    with config_loader.Config(test_config_file_path, autoconfig=True) as config:
        for line in source_lines:
            match = regex.search(line)
            if match:
                attr, method = match.group("attr"), match.group("method")
                assert isinstance(config.__getattribute__(attr), types[method])
    testhelper.rmdir(test_home)


def test_config_loader_raises_errors(config_files):
    Err = namedtuple("Err", "path, msg_substring, payload_inst")
    cfgerrors = (
            Err(path=config_files / "wrong_value.ini",
                msg_substring="unacceptable value",
                payload_inst=ValueError),
            Err(path=config_files / "no_option.ini",
                msg_substring="",
                payload_inst=configparser.NoOptionError),
            Err(path=config_files / "no_section.ini",
                msg_substring="",
                payload_inst=configparser.NoSectionError),
            )
    for cfgerror in cfgerrors:
        with pytest.raises(errors.WrongConfiguration) as err:
            with config_loader.Config(cfgerror.path, autoconfig=False):
                pass
            assert err.message
            assert cfgerror.msg_substring in err.message
            assert isinstance(err.payload, cfgerror.payload_inst)
