from __future__ import annotations
from myapplication.security import CryptoKey
from pathlib import Path
import logging
import platform


def get_logger(name: __name__, level="INFO") -> logger:
    _path = ''
    basedir = Path(__file__).parent.absolute()
    if platform.system() == 'Darwin':
        _path = '{}{}'.format(basedir, '/logs/server.log')
    elif platform.system() == 'Windows':
        _path = '{}{}'.format(basedir, '\\logs\\server.log')
    elif platform.system() == 'Linux':
        _path = '{}{}'.format(basedir, '/logs/server.log')

    possible_logs = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    level = level.upper()
    if level not in possible_logs:
        level = "INFO"

    logger = logging.getLogger(name)
    eval("logger.setLevel(logging.{})".format(level))

    file_handler = logging.FileHandler(_path)
    formatter = logging.Formatter("%(asctime)s LINE=%(lineno)d func_name=%(funcName)s | %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger