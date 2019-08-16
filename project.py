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


def read_config_file(path_to_config_file: pathlib.Path) -> configparser.ConfigParser:
    """
    Reads current configuration file or creates a new one with a default configuration
    """
    config_parser = configparser.ConfigParser(allow_no_value=True)
    config_parser.optionxform = str
    try:
        config_parser.read_file(open(path_to_config_file))
        logger.debug(f"{path_to_config_file} read")
        return Config(config_parser)
    except FileNotFoundError:
        logger.info("config file missing")
        return create_config_file(path_to_config_file, config_parser)


def create_config_file(path_to_config_file: pathlib.Path, config_parser: configparser.ConfigParser) -> configparser.ConfigParser:
    logger.debug(f"creating {path_to_config_file}")
    config_parser.add_section("Paths")
    config_parser.set("Paths", f"# Set the absolute paths.")
    config_parser.set("Paths", "path_to_data", f"{pathlib.Path.cwd()}")
    with open(path_to_config_file, mode="w", encoding="utf-8") as configfh:
        config_parser.write(configfh)
    return read_config_file(path_to_config_file)


def debug_delete_config(path_to_configfile: pathlib.Path) -> None:
    """
    Serves debugging purposes. Deletes the config file.
    """
    if path_to_configfile.is_file():
        path_to_configfile.unlink()
        logger.debug("Config file deleted")


if __name__ == "__main__":
    logger.debug("Program started")
    path_to_config_file = pathlib.Path("config.ini")
    config = read_config_file(path_to_config_file)
    logger.info(f"Path to data: {config.path_to_data}")
    debug_delete_config(path_to_config_file)
    logger.debug("Program ended")
