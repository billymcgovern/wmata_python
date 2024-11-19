import logging
import functools
import re

from . import colors

LOGGER = logging.getLogger(__name__)

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class CustomStreamFormatter(logging.Formatter):
    def format(self, record):
        # Customize the format of the log message here
        fmt = f'{record.getMessage()}'
        if logging.INFO == record.levelno:
            return colors.BOLD('[+] ') + fmt
        elif logging.WARNING == record.levelno:
            return colors.BOLD(colors.YELLOW('[-] ')) + fmt
        elif logging.ERROR == record.levelno:
            return colors.BOLD(colors.RED('[-] ')) + fmt

        return fmt


class CustomFileFormatter(logging.Formatter):
    def format(self, record):
        # Customize the format of the log message here
        fmt = f'{record.levelname}: {record.filename} {record.funcName}:{record.lineno} - {record.getMessage()}'

        return ansi_escape.sub('', fmt)


def add_file_handler(path, debug=False):
    file_handler = logging.FileHandler(path)
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    file_handler.setLevel(level)
    file_handler.setFormatter(CustomFileFormatter())
    LOGGER.addHandler(file_handler)


def get_logger(path=None, init=False):
    if not init:
        return LOGGER

    if path:
        add_file_handler(path)

    logging.PRINT = 21
    logging.addLevelName(logging.PRINT, 'PRINT')
    LOGGER.print = functools.partial(LOGGER.log, logging.PRINT)

    LOGGER.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(CustomStreamFormatter())
    LOGGER.addHandler(stream_handler)

    return LOGGER
