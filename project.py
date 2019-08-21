import pathlib
import configparser
import logging
import logging.config
import logging_conf

# setup logging
logging.config.dictConfig(logging_conf.dict_config)
logger = logging.getLogger(__name__)


class Config():
    """
    Holds all confituration data readily available as attributes
    """
    def __init__(self, path_to_config_file: pathlib.Path) -> None:
        self.path_to_config_file = path_to_config_file
        self.read_config_file()
    def read_config_file(self) -> None:
        """
        Reads current configuration file or creates a new one with a default configuration
        """
        self.config_parser = configparser.ConfigParser(allow_no_value=True)
        self.config_parser.optionxform = str
        try:
            self.config_parser.read_file(open(self.path_to_config_file))
            logger.debug(f"{self.path_to_config_file} read")
            self.parse()
        except FileNotFoundError:
            logger.info("config file missing")
            self.create_config_file()
    def create_config_file(self) -> None:
        """
        Creates the default config file
        """
        logger.debug(f"creating {self.path_to_config_file}")
        self.config_parser.add_section("Paths")
        self.config_parser.set("Paths", "# Set the absolute paths.")
        self.config_parser.set("Paths", "path_to_data", f"{pathlib.Path.cwd()}")
        with open(self.path_to_config_file, mode="w", encoding="utf-8") as configfh:
            self.config_parser.write(configfh)
        self.read_config_file()
    def delete_config_file(self) -> None:
        """
        Serves debugging purposes. Deletes the config file.
        """
        if self.path_to_config_file.is_file():
            self.path_to_config_file.unlink()
            logger.debug("Config file deleted")
    def parse(self):
        self.path_to_data = pathlib.Path(self.config_parser.get("Paths", "path_to_data"))


if __name__ == "__main__":
    logger.debug("Program started")
    path_to_config_file = pathlib.Path("config.ini")
    config = Config(path_to_config_file)
    logger.info(f"Path to data: {config.path_to_data}")
    config.delete_config_file()
    logger.debug("Program ended")
