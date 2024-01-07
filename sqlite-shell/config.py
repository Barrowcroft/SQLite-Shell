from configparser import ConfigParser
from os import getcwd, path
from typing import Any

from constants import CONFIG_FILENAME


class Config:
    """Config

    Maintains a global configuration with methods to load and save.
    """

    def __init__(self, directory: str) -> None:
        """__init__

        Initialises the configuration class.
        """

        #  Create config parser.

        self.config = ConfigParser()

        #  If the confguration file does not exist, create it.

        self.config_file_directory = directory

        if not path.exists(path.join(self.config_file_directory, CONFIG_FILENAME)):
            self.create_config()

    def create_config(self) -> None:
        """create_config

        Creates a configuration file with default settings.
        """
        self.config.add_section("config")

        self.config.set("config", "cwd", getcwd())
        self.config.set("config", "echo", "OFF")
        self.config.set("config", "open", "None")
        self.config.set("config", "width", "80")

        self.save_config()

    def load_config(self) -> None:
        """load_settings

        Loads the configuration.
        """
        self.config.read(path.join(self.config_file_directory, CONFIG_FILENAME))

    def save_config(self) -> None:
        """save_config

        Saves the configuration.
        """
        with open(
            path.join(self.config_file_directory, CONFIG_FILENAME), "w"
        ) as config_file:
            self.config.write(config_file)

    def get_config(self, key: str) -> Any:
        """get_config

        Gets the configuration.

        Args:
            key (str): key to get.
        """
        return self.config.get("config", key)

    def set_config(self, key: str, value: Any) -> None:
        """update_config

        Sets the configuration and saves the updated configuration.

        Args:
            key (str): key to set.
            value (Any): updated value.
        """
        self.config.set("config", key, value)
        self.save_config()
