#!/usr/bin/env python


import pathlib
import configparser
import sys
import traceback
import re
import dataclasses
import urllib.parse
from functools import partial
from itertools import repeat
from collections import namedtuple
from collections import OrderedDict
from loguru._colorizer import AnsiParser
# Typing
from typing import Iterable
from typing import Tuple
from typing import Literal
from typing import Union
# Own modules
from starter.loggerdef import logger
from starter import errors
from starter import utils
from starter import menu


@dataclasses.dataclass
class Configured_Path():
    internal_name: str
    comment: str
    preconf_path: dataclasses.InitVar[pathlib.Path]
    conf_path: pathlib.Path = None
    def __post_init__(self, preconf_path) -> None:
        self.preconf_path = preconf_path
        self.conf_path = preconf_path


class Proto_Config():
    """
    Preconfigures some essential values
    which often cannot be defined in Config.__init__()
    because of all the checks we do during Config.__init__()
    """
    Log_level = namedtuple("Log_level", "level, default_color")
    log_levels = (
            Log_level(level="UNIMPORTANT", default_color="light-black"),
            Log_level(level="PROCEDURE", default_color="cyan"),
            Log_level(level="INFO", default_color="white"),
            Log_level(level="SUCCESS", default_color="green"),
            Log_level(level="IMPORTANT", default_color="yellow"),
            Log_level(level="WARNING", default_color="light-magenta"),
            Log_level(level="ERROR", default_color="red"),
            Log_level(level="CRITICAL", default_color="RED"),
            )
    Highlight = namedtuple("Highlight", "type, default_color, default_keywords")
    highlight_definitions = (
        Highlight(type="good",
                  default_color="green",
                  default_keywords=", ".join((
                      "installed",
                      "executable", 
                      "running",
                      "successfully",
                      "OK",
                      ))
                 ),
        Highlight(type="bad",
                  default_color="light-red",
                  default_keywords=", ".join((
                      "failed",
                      "unavailable",
                      "stopped",
                      ))
                 ),
        Highlight(type="noteworthy",
                  default_color="yellow",
                  default_keywords=", ".join((
                      ))
                 ),
        Highlight(type="accent",
                  default_color="light-yellow",
                  default_keywords=", ".join((
                      ))
                 ),
        Highlight(type="dim",
                  default_color="light-black",
                  default_keywords=", ".join((
                      ))
                 ),
        Highlight(type="app_version",
                  default_color="light-white",
                  default_keywords=", ".join((
                      ))
                 ),
        Highlight(type="careful",
                  default_color="magenta",
                  default_keywords=", ".join((
                      ))
                 ),
        )
    highlight_keywords = dict()
    _ansi_parser = AnsiParser()
    valid_color_words = (*_ansi_parser._style.keys(), 
                         *_ansi_parser._foreground.keys(),
                         *_ansi_parser._background.keys(),
                        )
    # color_delimiter = re.compile("[, ]{1,2}")
    color_delimiter = re.compile(", ")
    error_regex = re.compile(r"""config_parser\.get.*\(["'](?P<section>\w+)["'], *["'](?P<variable>\w+)["']\)""")


class Config(Proto_Config):
    """
    Holds all configuration data readily available as attributes
    """
    @utils.logger_wraps()
    def __init__(self, cfg_path: pathlib.Path, autoconfig: bool) -> None:
        self.path_to_config_file = cfg_path
        self.path_to_home = utils.provide_dir(self.path_to_config_file.parent)
        self.path_to_starter_home = pathlib.Path.home() / utils.home_dir_name
        self._local_sub_dir = Configured_Path(
                internal_name="local_sub_dir",
                comment="Just an example of a subdirectory",
                preconf_path=self.path_to_starter_home / "subdir",
            )
        self.configured_paths = (self._local_sub_dir,
                                )
        self.read_config_and_check_syntax()
        self.parse_config_and_check_values()
        self.set_logging_colors()
        # Let's create convenient highlighting shortcut functions
        # so that we can write e.g. `config.noteworthy(word)` instead of
        # config.highlight(word, config.highlight_noteworthy)
        logger.debug(f"Creating convenient shortcut functions for keyword highlighting:")
        for highlight_definition in self.highlight_definitions:
            setattr(self, 
                    highlight_definition.type, 
                    partial(self.highlight, color_tag=getattr(self, "_".join(("highlight", highlight_definition.type))))
                   )
            logger.debug(f"Config.{highlight_definition.type} = lambda word: Config.highlight(word, Config.highlight_{highlight_definition.type}")
        while (wrong_paths := self.filter_wrong_paths(self.configured_paths)):
            self.wizard(wrong_paths, autoconfig)
            self.create_config_file()
            self.read_config_and_check_syntax()
            self.parse_config_and_check_values()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # Deleting config during development. Comment after release.
        # self.delete_config_file()
        pass
    def reset_parser(self) -> None:
        """
        Erases all data from previous config file parsing attempt by
        creating a new instance of config_parser
        """
        self.config_parser = configparser.ConfigParser(allow_no_value=True)
        self.config_parser.optionxform = str
        logger.trace(f"config_parser reset")
    @utils.logger_wraps()
    def read_config_file(self) -> None:
        """
        Reads current configuration file
        """
        self.reset_parser()
        logger.trace(f"config_parser might raise FileNotFoundError")
        self.config_parser.read_file(open(self.path_to_config_file))
        logger.trace(f"config_parser did not raise FileNotFoundError")
        logger.debug(f"{self.path_to_config_file.name} read successfully")
    @utils.logger_wraps()
    def set_default_highlight(self, 
                              section: Literal["Highlight colors", "Highlight keywords"],
                              attr_prefix: Literal["highlight", "keyword"], 
                              nt_attr: Literal["default_color", "default_keywords"],
                             ) -> None:
        for highlight_definition in self.highlight_definitions:
            variable = "_".join((attr_prefix, highlight_definition.type))
            value = getattr(highlight_definition, nt_attr)
            self.config_parser.set(section, variable, value)
            logger.debug(f"self.config_parser.set({repr(section)}, {repr(variable)}, {repr(value)}")
    def set_default_log_level_colors(self) -> None:
        section = "Log level colors"
        for log_level in self.log_levels:
            variable = "_".join(("log_level", log_level.level.lower()))
            self.config_parser.set(section, variable, log_level.default_color)
            logger.debug(f"self.config_parser.set({repr(section)}, {repr(variable)}, {repr(log_level.default_color)})")
    @utils.logger_wraps()
    def create_config_file(self) -> None:
        """
        Creates the default config file
        """
        self.reset_parser()
        self.config_parser.add_section("Local Paths")
        self.config_parser.set("Local Paths", "# You can write paths in Windows format or Linux/POSIX format.")
        self.config_parser.set("Local Paths", "# A trailing '/' at the end of the final directory in a POSIX path")
        self.config_parser.set("Local Paths", "# or a '\\' at the end of the final directory of a Windows path")
        self.config_parser.set("Local Paths", "# does not interfere with the path parser.")
        self.config_parser.set("Local Paths", "")
        for path in self.configured_paths:
            logger.trace(f"Setting {path.internal_name} to path.conf_path = {str(path.conf_path)} in the config file")
            self.config_parser.set("Local Paths", f"# {path.comment[0].capitalize()}{path.comment[1:]}")
            self.config_parser.set("Local Paths", f"{path.internal_name}", f"{path.conf_path}")
        self.config_parser.add_section("Values")
        self.config_parser.set("Values", "# Some config values")
        self.config_parser.set("Values", "")
        self.config_parser.set("Values", "preset_value", "42")
        self.config_parser.add_section("Log level colors")
        self.config_parser.set("Log level colors", "# Default colors of log levels which are output to the user.")
        self.config_parser.set("Log level colors", "# Acceptable values are the keywords from the AnsiParser class")
        self.config_parser.set("Log level colors", "# in https://github.com/Delgan/loguru/blob/master/loguru/_colorizer.py")
        self.config_parser.set("Log level colors", "# e.g. 'black', 'red', 'green', 'cyan', 'white' ...")
        self.config_parser.set("Log level colors", "# optionally prefixed with 'light-', e.g. 'light-blue', 'light-yellow' etc.")
        self.config_parser.set("Log level colors", "# You can also add style and background, e.g. 'light-green, underline, LIGHT-BLACK'")
        self.config_parser.set("Log level colors", "# Separate the words with a comma and a space.")
        self.config_parser.set("Log level colors", "# Value 'normal' can be used to disable color highlighting.")
        self.config_parser.set("Log level colors", "")
        self.set_default_log_level_colors()
        self.config_parser.add_section("Highlight colors")
        self.config_parser.set("Highlight colors", "# Certain words or substrings in log lines will be highlighted")
        self.config_parser.set("Highlight colors", "# and temporarily override the log line's default color.")
        self.config_parser.set("Highlight colors", "# Use the same color-defining rules as in the section Log level colors")
        self.config_parser.set("Highlight colors", "# to define the colors of each highlight type.")
        self.config_parser.set("Log level colors", "# Value 'normal' can be used to disable color highlighting.")
        self.config_parser.set("Highlight colors", "")
        self.set_default_highlight(section="Highlight colors", attr_prefix="highlight", nt_attr="default_color")
        self.config_parser.add_section("Highlight keywords")
        self.config_parser.set("Highlight keywords", "# Define which words or substrings will be highlighted with which highlight type.")
        self.config_parser.set("Highlight keywords", "# Separate words with a comma and a space.")
        self.config_parser.set("Highlight keywords", "# These keywords are highlighted only in certain predefined output lines")
        self.config_parser.set("Highlight keywords", "# where they are expected, e.g. when retrieved as values from RSI properties.")
        self.config_parser.set("Highlight keywords", "# Defining a keyword here guarantees by no means")
        self.config_parser.set("Highlight keywords", "# that it would also be highlighted in any other output line.")
        self.config_parser.set("Highlight keywords", "# Experts: You can use regular expressions here, but they must not contain ', '")
        self.config_parser.set("Highlight keywords", "# because this is used as a keyword separator. If needed, use '\\ \\,' in the regex.")
        self.config_parser.set("Highlight keywords", "")
        self.set_default_highlight(section="Highlight keywords", attr_prefix="keywords", nt_attr="default_keywords")
        with open(self.path_to_config_file, mode="w", encoding="utf-8") as configfh:
            self.config_parser.write(configfh)
        logger.debug(f"Config file written")
    @utils.logger_wraps()
    def read_config_and_check_syntax(self) -> None:
        while True:
            try:
                self.read_config_file()
                break
            except FileNotFoundError:
                logger.trace(f"FileNotFoundError was raised, handling it")
                logger.opt(raw=True).info("Config file missing, creating new default config file\n")
                self.create_config_file()
                logger.trace(f"Finished handling FileNotFoundError")
                continue
            except UnicodeDecodeError as err:
                raise errors.WrongConfiguration(f"Could not read configuration", err)
            except AttributeError as err:
                # happens when the config file syntax is so currpt that config_parser cannot read it
                raise errors.WrongConfiguration(f"Could not read configuration, file syntax might be wrong", err)
    def check_ipv4(self, parsed: str) -> None:
        assert type(parsed) is str
        addr_parts = parsed.split(".")
        assert len(addr_parts) == 4, "IPv4 address must have four parts"
        for part in addr_parts:
            assert int(part) in range(256), "Each IPv4 address part must be in range 0..256"
    def check_port(self, parsed: int) -> None:
        assert type(parsed) is int
        assert parsed in range(65536), "Port must be in range 0..65536"
    def check_path(self, path: pathlib.Path) -> None:
        """
        Check whether the path is syntactically correct.
        Whether the path exists or not is immaterial.
        We just want to make sure that it does not contain any reserved characters,
        e.g. "*", "?", "|" etc.
        """
        assert path.exists() in (True, False)
    def getpath(self, section: str, value: str) -> pathlib.Path:
        """
        Returns value from config file as pathlib.Path object
        """
        return pathlib.Path(self.config_parser.get(section, value))
    def geturl(self, section: str, raw_url: str) -> urllib.parse.ParseResult:
        """
        Parses a URL and returns urllib ParseResult
        """
        return urllib.parse.urlparse(self.config_parser.get(section, raw_url))
    @utils.logger_wraps()
    def get_and_check_color(self, section: str, value: str) -> Union[str, None]:
        """
        Retrieves a sequence of color words from the config file
        and parses it into valid color tags
        'light-blue, strike, WHITE' -> '<light-blue><strike><WHITE>'
        ignores invalid color words
        """
        colorlist = filter(bool, re.split(self.color_delimiter, self.config_parser.get(section, value)))
        valid_colors = filter(lambda color: color in self.valid_color_words, colorlist)
        result = "".join("".join(("<", color, ">")) for color in valid_colors)
        if result == "":
            result = None
            result = "<normal>"
            logger.opt(colors=False).debug(f"Replaced {value} with {result}")
        return result
    @utils.logger_wraps()
    def check_and_set_keyword_highlight_groups(self, keyword_highlight_group: str) -> None:
        wl = tuple(filter(bool, re.split(self.color_delimiter, self.config_parser.get("Highlight keywords", keyword_highlight_group))))
        setattr(self, keyword_highlight_group, wl)
        for word in wl:
            self.highlight_keywords[word] = keyword_highlight_group.replace("keywords", "highlight")
            logger.debug(f"Config.highlight_keywords[{repr(word)}] = {repr(self.highlight_keywords[word])}")
    @utils.logger_wraps()
    def set_logging_colors(self) -> None:
        for log_level in self.log_levels:
            configured_color = getattr(self, "_".join(("log_level", log_level.level.lower())))
            logger.level(log_level.level, color=configured_color)
            logger.opt(colors=False).debug(f"Setting logger.level({repr(log_level.level)}, color={repr(configured_color)})")
    @utils.logger_wraps()
    def parse_config_and_check_values(self) -> None:
        """
        Parses the configuration files into usable attributes
        and checks whether the values are syntactically correct.
        For example, check if an IPv4 address consists of four chained integers in range(256).
        """
        try:
            self.some_value = self.config_parser.getint("Values", "preset_value")
            for path in self.configured_paths:
                checked_path = self.getpath("Local Paths", path.internal_name)
                self.check_path(checked_path)
                setattr(self, path.internal_name, checked_path)
                logger.trace(f"Config.{path.internal_name} = {str(getattr(self, path.internal_name))}")
                setattr(getattr(self, "_" + path.internal_name), "conf_path", getattr(self, path.internal_name))
                logger.trace(f"Config._{path.internal_name}.conf_path = {str(getattr(self, '_' + path.internal_name).conf_path)}")
            for section, definitions, defattr, prefix in zip(
                    ("Log level colors", "Highlight colors"),
                    (self.log_levels, self.highlight_definitions),
                    ("level", "type"),
                    ("log_level", "highlight"),
                    ):
                for definition in definitions:
                    property = "_".join((prefix, getattr(definition, defattr).lower()))
                    setattr(self, property, self.get_and_check_color(section, property))
                    logger.opt(colors=False).debug(f"Config.{property} = {getattr(self, property)}")
            for keyword_highlight_group in ("_".join((prefix, word)) for prefix, word in zip(repeat("keywords"), map(lambda x: x.type, self.highlight_definitions))):
                self.check_and_set_keyword_highlight_groups(keyword_highlight_group)
        except ValueError as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exc().splitlines()
            section, variable, value = False, False, False
            for line in lines:
                if "config_parser" in line:
                    match = re.search(self.error_regex, line)
                    if match:
                        section = match.group("section")
                        variable = match.group("variable")
            value = lines[-1].split()[-1]
            if section and variable and value:
                message = f"{self.path_to_config_file.name}: '{variable}' in section '{section}' has an unacceptable value of {value}"
                logger.trace(f"Raising WrongConfiguration error because of wrong section/value")
                raise errors.WrongConfiguration(message, err)
            else:
                logger.trace(f"Re-raising ValueError")
                raise
        except configparser.NoOptionError as err:
            logger.trace(f"Raising WrongConfiguration error because of NoOptionError")
            raise errors.WrongConfiguration(f"{self.path_to_config_file.name}: {err.message}", err)
        except configparser.NoSectionError as err:
            logger.trace(f"Raising WrongConfiguration error because of NoSectionError")
            logger.exception(err)
            raise errors.WrongConfiguration(f"{self.path_to_config_file.name}: {err.message}", err)
        except OSError as err:
            # OSError [WinError 123] Occurs when there are reserved characters in a path
            # But Linux and Mac will throw a different kind of OSError
            # So, for now, instead of differentiating the kinds of OSErrors, we'll just reraise them all
            logger.trace(f"Reraising OSError, assuming it is because of bad syntax in path value")
            raise
        except Exception as err:
            logger.trace(f"Raising WrongConfiguration error because of some general Exception")
            logger.exception(err)
            raise errors.WrongConfiguration(f"There is something wrong with {self.path_to_config_file.name}. Please check it carefully or delete it to have it recreated.", err)
    def filter_wrong_paths(self, paths: Iterable[Configured_Path]) -> Tuple[Configured_Path]:
        """
        Returns tuple with all Configured_Paths which don't exist.
        """
        # We need to return a tuple because we need to know the number of wrong paths at all times.
        return tuple(filter(lambda p: not p.conf_path.exists(), paths))
    @utils.logger_wraps()
    def configure_path(self, path: Configured_Path, manually: bool) -> None:
        if manually:
            logger.trace(f"Configuring path {path.internal_name} manually")
            while True:
                try:
                    # Special treatment of ...
                    if False:
                        pass
                    # Normal paths
                    else:
                        logger.trace(f"Normal treatment")
                        input_path = utils.input_path(f"Input path to the {path.comment}: ")
                        created_path = utils.provide_dir(input_path)
                    break
                except OSError as err:
                    # Happens if, for example, a folder or a file cannot be created because it already exists.
                    logger.error(err)
                    continue
        else:
            logger.trace(f"Configuring paths automatically")
            # Special case
            if False:
                pass
            # Normal case
            else:
                created_path = utils.provide_dir(path.conf_path)
        logger.debug(f"created_path {str(created_path)}")
        # update the path in the list of configured paths
        path.conf_path = created_path
        logger.trace(f"_{path.internal_name}.conf_path = {created_path}")
    @utils.logger_wraps()
    def wizard(self, wrong_paths: Tuple[Configured_Path], autoconfig: bool) -> None:
        """
        Configuration wizard helps the user to correct the paths which don't exist
        """
        wiz_menu = menu.Text_Menu(menu_name="Configuration Wizard", heading=r"""
 ____ ____ __ _ ____ _ ____ _  _ ____ ____ ___ _ ____ __ _
 |___ [__] | \| |--- | |__, |__| |--< |--|  |  | [__] | \|
 _  _ _ ___  ____ ____ ___
 |/\| |  /__ |--| |--< |__>
 """)
        heading_was_shown = False
        number_to_word = dict((
            (1, "one"),
            (2, "two"),
            (3, "three"),
            (4, "four"),
            (5, "five"),
            (6, "six"),
            (7, "seven"),
            (8, "eight"),
            (9, "nine"),
            (10, "ten"),
            (11, "eleven"),
            (12, "twelve"),
            ))
        for path in wrong_paths:
            if not heading_was_shown:
                wiz_menu.show_heading("INFO")
                heading_was_shown = True
            reason = (f"{path.internal_name} ({path.conf_path}) does not exist!")
            comment = path.comment
            options = OrderedDict((
                    ("A", f""),
                    ("C", "Create this path automatically"),
                    ("M", "Manually input correct path to use or to create"),
                    ("Q", f"Quit to edit {self.highlight(path.internal_name, self.highlight_noteworthy)} in {self.highlight(self.path_to_config_file.name, self.highlight_noteworthy)} manually"),
                ))
            number_of_remaining_paths = len(wrong_paths) - 1 - wrong_paths.index(path)
            if number_of_remaining_paths >= 2:
                options["A"] = f"Automatically configure this and {self.noteworthy(number_to_word[number_of_remaining_paths])} remaining path settings"
            elif number_of_remaining_paths == 1:
                options["A"] = f"Automatically configure this and {self.noteworthy(number_to_word[number_of_remaining_paths])} remaining path setting"
            else: # number_of_remaining_paths == 0
                del options["A"]
            if autoconfig:
                choice = "C"
            else:
                choice = None
            if not choice:
                wiz_menu.show_reason(reason, "IMPORTANT")
                wiz_menu.show_comment("".join((" " * len(utils.warn("")), comment[0].capitalize() + comment[1:])), "INFO")
                choice = wiz_menu.choose_from(options, "PROCEDURE")
            if choice == "A":
                autoconfig = True
                choice = "C"
            logger.debug(f"Your choice: {choice}")
            if choice == "C":
                self.configure_path(path, manually=False)
            elif choice == "M":
                self.configure_path(path, manually=True)
            elif choice == "Q":
                # create config file to save the progress until now
                self.create_config_file()
                logger.trace(f"Raising WrongConfiguration error")
                raise errors.WrongConfiguration(f"Who needs a wizard, when you can edit `{self.path_to_config_file.name}` yourself, right?", None)
        self.create_config_file()
    @utils.logger_wraps()
    def highlight(self, word: str, color_tag: str) -> str:
        """
        Encloses a given word in color highlighting tags
        e.g.:
        word = 'Hello world!'
        color_tag = <light-green><underline><RED>
        result = <light-green><underline><RED>Hello world!</></></>
        """
        if color_tag is None:
            return word
        return "".join((color_tag, word, color_tag.count("<") * "</>"))
    @utils.logger_wraps()
    def hlkw(self, word: str) -> str:
        """
        Return the word enclosed in its usual color tags.
        `self.highlight_keywords` is a dictary which provides 
        a highlight type for each word or substring.
        If the word cannot be found in this dictionary,
        try to find if the word contains any keyword from this dictionary as
        a substring and color at least the first substring in the word.
        If no keyword or substring can be found in `self.highlight_keywords`, 
        return the word in its original form.
        
        Example 1:
        word = 'installed'
        self.highlight_keywords['installed'] = 'highlight_good'
        self.highlight_good = '<green>'
        self.highlight('installed', self.highlight_good) -> '<green>installed</>'
        result = '<green>installed</>'
        
        Example 2:
        word = 'carapp_orureleasenotes'
        self.highlight_keywords['carapp_orureleasenotes'] -> KeyError (not in dict)
        BUT: self.highlight_keywords['carapp_'] = 'highlight_dim'
        AND: 'carapp_' is a substring of 'carapp_releasenotes'
        self.highlight_dim = '<cyan>'
        self.highlight('carapp_', self.highlight_dim) -> '<cyan>carapp_</>'
        result = '<cyan>carapp_</>orureleasenotes'
        
        Example 3:
        word = 'not in dict'
        self.highlight_keywords dict does not contain this or any substring of it
        reutst = 'not in dict'
        """
        try:
            tag = getattr(self, self.highlight_keywords[word])
            return self.highlight(word, tag)
        except KeyError:
            try:
                for kw in self.highlight_keywords:
                    pattern = re.compile(kw)
                    match = re.search(pattern, word)
                    if match:
                        break
                else:
                    return word
                # Here is what happens if a keyword (regex pattern) was found as substring:
                before = word[:match.span()[0]]
                matched = word[match.span()[0]:match.span()[1]]
                after = word[match.span()[1]:]
                result = "".join([
                    before,
                    self.highlight(matched, getattr(self, self.highlight_keywords[match.re.pattern])),
                    after,
                    ])
                return result
            except Exception as err:
                logger.exception(err)


if __name__ == "__main__":
    pass
