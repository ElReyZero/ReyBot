from configparser import ConfigParser, ParsingError
import os

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

MAIN_ADMIN_ID = None
DISCORD_TOKEN = None
MAIN_GUILD = None
DEBUG = False
admin_ids = []

#: Contains database parameters.
database = {
    "host": "",
    "name": "",
    "user": "",
    "password": "",
}

genshin_data = {
    "ltuid": "",
    "ltoken": "",
    "uuid": 0
}

connections = None

def get_config():
    """
    Populate the config data from the config file.
    """
    file = f"./config.cfg"
    linux_file = f"/home/ReyBot/config.cfg"

    try:
        global DISCORD_TOKEN
        DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

        global MAIN_ADMIN_ID
        MAIN_ADMIN_ID = os.environ["MAIN_ADMIN"]
        global admin_ids
        admin_ids = os.environ["ADMIN_IDS"].split(",")
        global MAIN_GUILD
        MAIN_GUILD = os.environ["MAIN_GUILD"]

        global database
        database['host'] = os.environ["DB_HOST"]
        global genshin_data
        genshin_data['ltuid'] = os.environ["GI_LTUID"]
        genshin_data['ltoken'] = os.environ["GI_LTOKEN"]
        genshin_data['uuid'] = int(os.environ["GI_UUID"])
    except (KeyError, ValueError):
        using_linux = False
        if os.path.isfile(linux_file):
            using_linux = True
        elif not os.path.isfile(file):
            raise ConfigError(f"{file} not found! "+file)


        config = ConfigParser(inline_comment_prefixes="#")
        try:
            if using_linux:
                config.read(linux_file)
            else:
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
            MAIN_ADMIN_ID = config["General"]["main_admin_id"]
        except KeyError:
            _error_missing(MAIN_ADMIN_ID, 'General', file)
        except ValueError:
            _error_incorrect(MAIN_ADMIN_ID, 'General', file)

        try:
            admin_ids = config["General"]["admin_ids"].split(",")
        except KeyError:
            _error_missing(admin_ids, 'General', file)
        except ValueError:
            _error_incorrect(admin_ids, 'General', file)

        _check_section(config, "Database", file)

        try:
            MAIN_GUILD = config["General"]["main_guild"]
        except KeyError:
            _error_missing(MAIN_GUILD, 'General', file)
        except ValueError:
            _error_incorrect(MAIN_GUILD, 'General', file)

        try:
            database['host'] = config["Database"]["host"]
        except KeyError:
            _error_missing('host', 'Database', file)
        except ValueError:
            _error_incorrect('host', 'Database', file)

        _check_section(config, "Genshin", file)

        try:
            genshin_data['ltuid'] = config["Genshin"]["ltuid"]
        except KeyError:
            _error_missing('ltuid', 'Genshin', file)
        except ValueError:
            _error_incorrect('ltuid', 'Genshin', file)

        try:
            genshin_data['ltoken'] = config["Genshin"]["ltoken"]
        except KeyError:
            _error_missing('ltoken', 'Genshin', file)
        except ValueError:
            _error_incorrect('ltoken', 'Genshin', file)

        try:
            genshin_data['uuid'] = int(config["Genshin"]["uuid"])
        except KeyError:
            _error_missing('uuid', 'Genshin', file)
        except ValueError:
            _error_incorrect('uuid', 'Genshin', file)

    global DEBUG
    try:
        DEBUG = os.environ["REYBOT_DEBUG"]
    except KeyError:
        try:
            DEBUG = bool(config["General"]["debug"])
        except KeyError:
            pass
        except ValueError:
            _error_incorrect('debug', 'General', file)


def _check_section(config, section, file):
    if section not in config:
        raise ConfigError(f"Missing section '{section}' in '{file}'")


def _error_missing(field, section, file):
    raise ConfigError(f"Missing field '{field}' in '{section}' in '{file}'")


def _error_incorrect(field, section, file):
    raise ConfigError(f"Incorrect field '{field}' in '{section}' in '{file}'")