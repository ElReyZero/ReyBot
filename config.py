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


# DYNAMIC PARAMETERS:
# (pulled from the config file)
INITIALIZED = False
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
MAIN_ADMIN_ID = None
DISCORD_TOKEN = None
MAIN_GUILD = None
DEBUG = False

SENTRY_DSN = None

admin_ids = []

#: Contains database parameters.
database = {
    "host": "",
    "name": "",
    "user": "",
    "password": "",
}

genshin_data = {
    "ltuid_v2": "",
    "ltoken_v2": "",
    "ltuid_v2": 0,
    "uuid": 0,
}


SERVICE_ID = None

bot_id = None


def set_config_vars():
    global DISCORD_TOKEN
    DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

    global MAIN_ADMIN_ID
    MAIN_ADMIN_ID = os.environ["MAIN_ADMIN"]
    global admin_ids
    admin_ids = os.environ["ADMIN_IDS"].split(",")
    global MAIN_GUILD
    MAIN_GUILD = os.environ["MAIN_GUILD"]
    global SERVICE_ID
    SERVICE_ID = os.environ["SERVICE_ID"]
    global SENTRY_DSN
    SENTRY_DSN = os.environ["SENTRY_DSN"]

    global database
    database['host'] = os.environ["DB_HOST"]
    database['name'] = os.environ["DB_NAME"]
    database['user'] = os.environ["DB_USER"]
    database['password'] = os.environ["DB_PASSWORD"]
    global genshin_data
    genshin_data['ltuid_v2'] = int(os.environ["GI_LTUID_V2"])
    genshin_data['ltoken_v2'] = os.environ["GI_LTOKEN_V2"]
    genshin_data['ltmid_v2'] = os.environ["GI_LTMID_V2"]
    genshin_data['uuid'] = int(os.environ["GI_UUID"])


def get_config():
    """
    Populate the config data from the config file.
    """
    global INITIALIZED
    if INITIALIZED:
        return

    global PROJECT_PATH
    file = PROJECT_PATH + "/config.cfg"

    try:
        set_config_vars()
    except (KeyError, ValueError):
        if not os.path.isfile(file):
            raise ConfigError(f"{file} not found! "+file)

        config = ConfigParser(inline_comment_prefixes="#")
        try:
            config.read(file)
        except ParsingError as e:
            raise ConfigError(f"Parsing Error in '{file}'\n{e}")

        for section in config.sections():
            for item in config[section]:
                try:
                    os.environ[item.upper()] = config[section][item]
                except TypeError:
                    raise ConfigError(f"Error in '{file}': {item} is not a valid value.")

        set_config_vars()

        for var_name, var_value in globals().items():
            if var_value is None and var_name.isupper():
                raise MissingConfig(f"Missing variable '{var_name}' in '{file}'")
            elif type(var_value) == list and len(var_value) == 0:
                raise MissingConfig(f"Missing '{var_name}' in '{file}'")


    INITIALIZED = True
