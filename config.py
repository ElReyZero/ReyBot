from configparser import ConfigParser, ParsingError
import os
import pathlib

class ConfigError(Exception):
    """
    Raised when an error occur while reading the config file.
    :param msg: Error message.
    """
    def __init__(self, msg: str):
        self.message = "Error in config file: " + msg
        super().__init__(self.message)

class MissingConfig(Exception):
    """
    Raised when a config value is missing.
    :param msg: Error message.
    """
    def __init__(self, msg: str):
        self.message = "Missing config value: " + msg
        super().__init__(self.message)


## DYNAMIC PARAMETERS:
# (pulled from the config file)

main_admin_id = None
DISCORD_TOKEN = None
admin_ids = []

#: Contains database parameters.
database = {
    "host": "",
    "name": "",
    "user": "",
    "password": ""
}

def get_config():
    """
    Populate the config data from the config file.
    """
    file = f"./config.cfg"

    try:
        global DISCORD_TOKEN
        DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

        global main_admin_id
        main_admin_id = os.environ["MAIN_ADMIN"]
        global admin_ids
        admin_ids = os.environ["ADMIN_IDS"].split(",")

    except KeyError:
        if not os.path.isfile(file):
            raise ConfigError(f"{file} not found! "+file)

        config = ConfigParser(inline_comment_prefixes="#")
        try:
            config.read(file)
        except ParsingError as e:
            raise ConfigError(f"Parsing Error in '{file}'\n{e}")

        _check_section(config, "General", file)

        try:
            DISCORD_TOKEN = config["General"]["discord_token"]
        except KeyError:
            _error_missing(DISCORD_TOKEN, 'General', file)
        except ValueError:
            _error_incorrect(DISCORD_TOKEN, 'General', file)

        try:
            main_admin_id = config["General"]["main_admin_id"]
        except KeyError:
            _error_missing(main_admin_id, 'General', file)
        except ValueError:
            _error_incorrect(main_admin_id, 'General', file)
        
        try:
            admin_ids = config["General"]["admin_ids"].split(",")
        except KeyError:
            _error_missing(admin_ids, 'General', file)
        except ValueError:
            _error_incorrect(admin_ids, 'General', file)


def _check_section(config, section, file):
    if section not in config:
        raise ConfigError(f"Missing section '{section}' in '{file}'")


def _error_missing(field, section, file):
    raise ConfigError(f"Missing field '{field}' in '{section}' in '{file}'")


def _error_incorrect(field, section, file):
    raise ConfigError(f"Incorrect field '{field}' in '{section}' in '{file}'")