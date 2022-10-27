import logging
from tzlocal import get_localzone
from utils.timezones import get_TZ
from datetime import datetime
import sys
import os
import config as cfg


class ColorFormatter(logging.Formatter):

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    # Formatter will log in local time
    TIMEZONE = get_TZ(get_localzone())

    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m', TIMEZONE),
        (logging.INFO, '\x1b[34;1m', TIMEZONE),
        (logging.WARNING, '\x1b[33;1m', TIMEZONE),
        (logging.ERROR, '\x1b[31m', TIMEZONE),
        (logging.CRITICAL, '\x1b[41m', TIMEZONE),
    ]

    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s',
            f'%Y-%m-%d %H:%M:%S {tz}',
        )
        for level, colour, tz in LEVEL_COLOURS
    }

    def format(self, record) -> logging.Formatter:
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


def define_log() -> tuple[logging.StreamHandler, logging.FileHandler, ColorFormatter]:
    # Logging config, logging outside the github repo
    try:
        os.makedirs(cfg.PROJECT_PATH + '/logs')
    except FileExistsError:
        pass

    log_filename = cfg.PROJECT_PATH + '/logs/bot.log'
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColorFormatter()
    timezone = console_formatter.TIMEZONE
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s %(message)s', f"%Y-%m-%d %H:%M:%S {timezone}")

    # Print debug
    level = logging.DEBUG
    # Print to file, change file everyday at 12:00 Local
    date = datetime(2020, 1, 1, 12)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_filename, when='midnight', atTime=date)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)

    return console_handler, file_handler, console_formatter


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def exception_to_log(log, traceback_message):
    log.error("An exception has ocurred while executing the bot:")
    for line in traceback_message:
        line = line.rstrip().splitlines()
        for splits in line:
            log.error(splits)
