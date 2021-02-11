#!/usr/bin/env python


from loguru import logger
import pathlib
import configparser
import sys
import traceback
import re
import dataclasses
if sys.version_info < (3, 9):
    import importlib_resources as ilres
else:
    import importlib.resources as ilres
from collections import OrderedDict
# Typing
import urllib.parse
from typing import Iterable
from typing import Tuple
# Own modules
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


class Config():
    """
    Holds all confituration data readily available as attributes
    """
    @utils.logger_wraps()
    def __init__(self, cfg_path: pathlib.Path, autoconfig: bool) -> None:
        self.error_regex = re.compile(r"""config_parser\.get.*\(["'](?P<section>\w+)["'], *["'](?P<variable>\w+)["']\)""")
        self.path_to_config_file = cfg_path
        self.path_to_home = utils.provide_dir(self.path_to_config_file.parent)
        self.path_to_starter_home = pathlib.Path.home() / utils.home_dir_name
        self._subdir_dir = Configured_Path(
                internal_name="subdir_dir",
                comment="example subdir",
                preconf_path=self.path_to_starter_home / "subdir",
            )
        self.configured_paths = (self._subdir_dir,
                                )
        self.read_config_and_check_syntax()
        self.parse_config_and_check_values()
        while (wrong_paths := self.filter_wrong_paths(self.configured_paths)):
            self.wizard(wrong_paths, autoconfig)
            self.create_config_file()
            self.read_config_and_check_syntax()
            self.parse_config_and_check_values()
    @utils.logger_wraps()
    def __enter__(self):
        return self
    @utils.logger_wraps()
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # Deleting config during development. Comment after release.
        # self.delete_config_file()
        pass
    @utils.logger_wraps()
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
                logger.info("Config file missing, creating new default config file")
                self.create_config_file()
                logger.trace(f"Finished handling FileNotFoundError")
                continue
            except UnicodeDecodeError as err:
                raise errors.WrongConfiguration(f"Could not read configuration", err)
            except AttributeError as err:
                # happens when the config file syntax is so currpt that config_parser cannot read it
                raise errors.WrongConfiguration(f"Could not read configuration, file syntax might be wrong", err)
    @utils.logger_wraps()
    def check_path(self, path: pathlib.Path) -> None:
        """
        Check whether the path is syntactically correct.
        Whether the path exists or not is immaterial.
        We just want to make sure that it does not contain any reserved characters,
        e.g. "*", "?", "|" etc.
        """
        assert path.exists() in (True, False)
    @utils.logger_wraps()
    def getpath(self, section: str, value: str) -> pathlib.Path:
        """
        Returns value from config file as pathlib.Path object
        """
        return pathlib.Path(self.config_parser.get(section, value))
    @utils.logger_wraps()
    def geturl(self, section: str, raw_url: str) -> urllib.parse.ParseResult:
        """
        Parses a URL and returns urllib ParseResult
        """
        return urllib.parse.urlparse(self.config_parser.get(section, raw_url))
    @utils.logger_wraps()
    def parse_config_and_check_values(self) -> None:
        """
        Parses the configuration files into usable attributes
        and checks whether the values are syntactically correct.
        For example, check if an IPv4 address consists of four chained integers in range(256).
        """
        try:
            for path in self.configured_paths:
                checked_path = self.getpath("Local Paths", path.internal_name)
                self.check_path(checked_path)
                setattr(self, path.internal_name, checked_path)
                logger.trace(f"Config.{path.internal_name} = {str(getattr(self, path.internal_name))}")
                setattr(getattr(self, "_" + path.internal_name), "conf_path", getattr(self, path.internal_name))
                logger.trace(f"Config._{path.internal_name}.conf_path = {str(getattr(self, '_' + path.internal_name).conf_path)}")
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
                logger.debug(f"Raising WrongConfiguration error because of wrong section/value")
                raise errors.WrongConfiguration(message, err)
            else:
                logger.debug(f"Re-raising ValueError")
                raise
        except configparser.NoOptionError as err:
            logger.debug(f"Raising WrongConfiguration error because of NoOptionError")
            raise errors.WrongConfiguration(f"{self.path_to_config_file.name}: {err.message}", err)
        except configparser.NoSectionError as err:
            logger.debug(f"Raising WrongConfiguration error because of NoSectionError")
            logger.exception(err)
            raise errors.WrongConfiguration(f"{self.path_to_config_file.name}: {err.message}", err)
        except OSError as err:
            # OSError [WinError 123] Occurs when there are reserved characters in a path
            # But Linux and Mac will throw a different kind of OSError
            # So, for now, instead of differentiating the kinds of OSErrors, we'll just reraise them all
            logger.debug(f"Reraising OSError, assuming it is because of bad syntax in path value")
            raise
        except Exception as err:
            logger.debug(f"Raising WrongConfiguration error because of some general Exception")
            raise errors.WrongConfiguration(f"There is something wrong with {self.path_to_config_file.name}. Please check it carefully or delete it to have it recreated.", err)
    @utils.logger_wraps()
    def filter_wrong_paths(self, paths: Iterable[Configured_Path]) -> Tuple[Configured_Path]:
        """
        Returns tuple with all Configured_Paths which don't exist.
        """
        # We need to return a tuple because we need to know the number of wrong paths at all times.
        return tuple(filter(lambda p: not p.conf_path.exists(), paths))
    @utils.logger_wraps()
    def configure_path(self, path: Configured_Path, manually: bool) -> None:
        if manually:
            logger.debug(f"Configuring path {path.internal_name} manually")
            while True:
                try:
                    # Path which requires special treatment
                    if False:
                        logger.debug(f"Special treatment")
                        pass
                    # Normal paths
                    else:
                        logger.debug(f"Normal treatment")
                        input_path = utils.input_path(f"Input path to the {path.comment[0].capitalize()}{path.comment[1:]}: ")
                        created_path = utils.provide_dir(input_path)
                    break
                except OSError as err:
                    # Happens if, for example, a folder or a file cannot be created because it already exists.
                    logger.error(err)
                    continue
        else:
            logger.debug(f"Configuring paths automatically")
            created_path = utils.provide_dir(path.conf_path)
        logger.trace(f"created_path {str(created_path)}")
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
        for path in wrong_paths:
            if not heading_was_shown:
                wiz_menu.show_heading()
                heading_was_shown = True
            reason = (f"{path.internal_name} ({path.conf_path}) does not exist!")
            comment = path.comment
            options = OrderedDict((
                    ("A", f"Automatically configure this and {len(wrong_paths) - 1 - wrong_paths.index(path)} remaining path settings"),
                    ("C", "Create this path automatically"),
                    ("M", "Manually input correct path to use or to create"),
                    ("Q", f"Quit to edit `{path.internal_name}` in {self.path_to_config_file.name} manually"),
                ))
            if autoconfig:
                choice = "C"
            else:
                choice = None
            if not choice:
                wiz_menu.show_reason(reason)
                wiz_menu.show_comment("".join((" " * len(utils.warn("")), comment[0].capitalize() + comment[1:])))
                choice = wiz_menu.choose_from(options)
            if choice == "A":
                autoconfig = True
                choice = "C"
            logger.success(f"Your choice: {choice}")
            if choice == "C":
                self.configure_path(path, manually=False)
            elif choice == "M":
                self.configure_path(path, manually=True)
            elif choice == "Q":
                logger.debug(f"Raising WrongConfiguration error")
                raise errors.WrongConfiguration(f"Who needs a wizard, when you can edit `{self.path_to_config_file.name}` yourself, right?", None)
        self.create_config_file()


if __name__ == "__main__":
    pass
