import configparser
import json
import logging
import os
import inspect
from logging.handlers import TimedRotatingFileHandler

def validate_path(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")
    return True

def read_json_cfg(path):
    with open(path, 'r') as f:
        return json.load(f)

def read_config_ini(path):
    config = configparser.ConfigParser()
    config.read(path)
    result = {}
    for section in config.sections():
        result[section] = {}
        for key, val in config[section].items():
            try:
                result[section][key] = json.loads(val)
            except:
                result[section][key] = val
    return result

def setup_logger(name=None, log_dir='/root/ten_min_range_api/logs', level=logging.INFO):
    if name is None:
        # Get the name of the calling script (without extension)
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = os.path.splitext(os.path.basename(module.__file__))[0] if module and module.__file__ else 'default'

    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding duplicate handlers
    if logger.hasHandlers():
        return logger

    log_file_base = os.path.join(log_dir, f"{name}.log")

    # Rotate logs at midnight with date-based suffix
    rotating_handler = TimedRotatingFileHandler(
        log_file_base,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8',
        utc=False
    )
    rotating_handler.suffix = "%Y-%m-%d"

    formatter = logging.Formatter(
        '%(asctime)s :: %(levelname)s :: %(filename)s :: %(funcName)s :: %(lineno)d :: %(message)s'
    )
    rotating_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(rotating_handler)
    logger.addHandler(stream_handler)

    return logger
