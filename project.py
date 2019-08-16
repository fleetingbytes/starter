import pathlib
import configparser
import logging
import logging.config
import logging_conf

# setup logging
logging.config.dictConfig(logging_conf.dict_config)
logger = logging.getLogger(__name__)


class Config():
    def __init__(self, config: configparser.ConfigParser) -> None:
        self.config = config
        self.path_to_data = pathlib.Path(self.config.get("Paths", "path_to_data"))


def read_config_file(path_to_config_file: pathlib.Path, cfgparser: configparser.ConfigParser) -> configparser.ConfigParser:
    """
    Reads current configuration file or creates a new one with a default configuration
    """
    try:
        cfgparser.read_file(open(path_to_config_file))
        logger.debug(f"{path_to_config_file} read")
        return cfgparser
    except FileNotFoundError:
        logger.info("config file missing, creating a new one")
        return create_config_file(path_to_config_file, cfgparser)


def create_config_file(path_to_config_file: pathlib.Path, cfgparser: configparser.ConfigParser) -> configparser.ConfigParser:
    logger.debug("creating cfg")
    cfgparser.add_section("Paths")
    cfgparser.set("Paths", f"# Set the absolute paths.")
    cfgparser.set("Paths", "path_to_data", f"{pathlib.Path.cwd()}")
    with open(path_to_config_file, mode="w", encoding="utf-8") as configfh:
        cfgparser.write(configfh)
    return read_config_file(path_to_config_file, cfgparser)


def read_or_create_config(path_to_config_file: pathlib.Path) -> configparser.ConfigParser:
    config_parser = configparser.ConfigParser(allow_no_value=True)
    config_parser.optionxform = str
    parsed_config = read_config_file(pathlib.Path(path_to_config_file), config_parser)
    config = Config(parsed_config)
    return config


def debug_delete_config(path_to_configfile: pathlib.Path) -> None:
    """
    Serves debugging purposes. Deletes the config file.
    """
    logger.debug("Deleting config file")
    if path_to_configfile.is_file():
        path_to_configfile.unlink()
    logger.debug("Config file deleted")


if __name__ == "__main__":
    logger.debug("Program started")
    path_to_config_file = pathlib.Path("config.ini")
    config = read_or_create_config(path_to_config_file)
    logger.info(f"Path to data: {config.path_to_data}")
    debug_delete_config(path_to_config_file)
    logger.debug("Program ended")
