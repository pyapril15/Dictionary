"""
Logger module using OOP principles.
Provides a Singleton LoggerManager for consistent, extendable logging.
"""

import logging
from logging.handlers import RotatingFileHandler
from threading import Lock
from src.app_logic.config import AppConfig


class _SingletonMeta(type):
    """
    Thread-safe Singleton metaclass.
    Ensures only one instance of the LoggerManager is created.
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class _LoggerManager(metaclass=_SingletonMeta):
    """
    Logger manager class responsible for configuring and providing logger instances.
    """

    def __init__(self):
        self._config = AppConfig()
        self._logger = logging.getLogger(self._config.app_name)
        self.__setup_logger()

    def __setup_logger(self):
        """
        Private method to configure logging handlers and format.
        Supports both file and console logging.
        """
        self._logger.setLevel(logging.DEBUG)

        # === Log Format ===
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # === File Handler with Rotation ===
        file_handler = RotatingFileHandler(
            filename=self._config.log_file,
            mode='a',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        # === Console Handler ===
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        if not self._logger.handlers:
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

            # === Log header information once ===
            self._logger.info("=== %s v%s Started ===", self._config.app_name, self._config.app_version)
            self._logger.info("Developer: %s", self._config.developer)
            self._logger.info("Description: %s", self._config.app_description)
            self._logger.info("Log File: %s", self._config.log_file)

    @property
    def logger(self):
        """Public property to access the configured logger."""
        return self._logger


# === Public logger instance for external use ===
logger = _LoggerManager().logger
