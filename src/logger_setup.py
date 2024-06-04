import os
import logging
import config


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    create_directory(config.LOGS_DIR)
    create_log_file(config.LOG_FILE_PATH)

    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(str(config.LOG_FILE_PATH))

    c_handler.setLevel(logging.WARNING)
    f_handler.setLevel(logging.DEBUG)

    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


def create_directory(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def create_log_file(path):
    if not path.exists():
        path.touch()


logger = setup_logger()
