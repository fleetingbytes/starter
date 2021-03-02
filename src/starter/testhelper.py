#!/usr/bin/env python


import pathlib
import random
import string
import re
import sys
from typing import Literal
from typing import Iterable
from starter import utils
from starter import errors
import importlib.resources


class Empty_Class():
    pass


class Fake_Config():
    def __init__(self, local_script_package_dir: pathlib.Path) -> None:
        self.local_script_package_dir = local_script_package_dir
        try:
            # for pytest, config_loader.py is understood as (.../site-packages/)claws/config_loader.py
            config_source = (importlib.resources.files("claws") / "config_loader.py").read_text(encoding="utf-8")
        except FileNotFoundError as err:
            # for pyinstaller package entry_file_path is understood as (.../dist/)claws/claws/entry.py
            config_source = (importlib.resources.files("claws") / ".." / "config_loader.py").read_text(encoding="utf-8")
        fn_pattern = re.compile(r"self\.config_parser\.set\(\S+ \"init_target_script_main_file\", r\"(?P<file_name>.*)\"\)")
        match = re.search(fn_pattern, config_source)
        file_name = match.group("file_name")
        self.init_target_script_main_file = file_name


def rmdir(directory: pathlib.Path) -> None:
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


def create_random_path(parent: pathlib.Path, path_type: Literal["file", "dir"]) -> pathlib.Path:
    """
    Creates random file or directory (according to `path_type`) in `parent` path.
    """
    while True:
        random_file_path = pathlib.Path(parent / "".join(random.choices(string.ascii_letters, k=random.randint(1, 13))))
        if random_file_path.exists():
            continue
        else:
            if path_type == "file":
                random_file_path.touch()
            elif path_type == "dir":
                random_file_path.mkdir()
            else:
                raise errors.WrongPathType(path_type)
        break
    return random_file_path


def provide_file(path: pathlib.Path, content: Iterable) -> pathlib.Path:
    utils.provide_dir(path.parent)
    with path.open(mode="w", encoding="utf-8") as file:
        file.writelines(content)
    return path


def common_path(one: pathlib.Path, other: pathlib.Path) -> int:
    """
    Compares the parts of two Paths,
    returns the number of identical parts from the start
    """
    i = 0
    for part_one, part_other in zip(one.resolve().parts, other.resolve().parts):
        if part_one == part_other:
            i += 1
        else:
            break
    return i


def relative_path(source: pathlib.Path, target: pathlib.Path) -> pathlib.Path:
    """
    Calculates the relative route from source path to target path
    """
    r_source, r_target = source.resolve(), target.resolve()
    if r_source.is_file() and r_source.exists():
        r_source = r_source.parent
    try:
        result = r_target.relative_to(r_source)
    except ValueError:
        n_parts_equal = common_path(source, target)
        result = pathlib.Path("/".join((*(".." for _ in range(len(r_source.parts[n_parts_equal:]))), *r_target.parts[n_parts_equal:])))
    return result


if __name__ == "__main__":
    pass
