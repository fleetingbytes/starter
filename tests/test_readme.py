#!/usr/bin/env python


import pathlib
import re
import inspect
from starter import entry


def test_readme():
    """
    Tests if every command line option defined in `entry.py` argument_parser()
    is mentioned (documented) in README.md
    """
    ignore_comment = r"(?<!# )parser.*"
    long_form = r"(?P<core>--\w[\w-]*[\w])"
    short_form = r"\W(?P<core>-\w)\W"
    long_form_readme = re.compile(long_form)
    short_form_readme = re.compile(short_form)
    long_form_code = re.compile("".join((ignore_comment, long_form)))
    short_form_code = re.compile("".join((ignore_comment, short_form)))
    lines, _ = inspect.getsourcelines(entry.argument_parser)
    long_forms_defined = set(re.findall(long_form_code, "".join(lines)))
    short_forms_defined = set(re.findall(short_form_code, "".join(lines)))
    print("DEFINED:")
    print(long_forms_defined)
    print(short_forms_defined)
    with open(pathlib.Path(__file__).parent.parent.absolute() / "README.md", encoding="utf-8") as readme_file:
        readme = readme_file.read()
        long_forms_readme = set(re.findall(long_form_readme, readme))
        short_forms_readme = set(re.findall(short_form_readme, readme))
        print("README:")
        print(long_forms_readme)
        print(short_forms_readme)
        assert long_forms_defined - long_forms_readme == set(), f"Readme is missing {long_forms_defined.difference(long_forms_readme)}"
        assert short_forms_defined - short_forms_readme == set(), f"Readme is missing {short_forms_defined.difference(short_forms_readme)}"
