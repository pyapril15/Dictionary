"""
Logger module using OOP principles.
Provides a Singleton LoggerManager for consistent, extendable logging.
"""

import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from threading import Lock
from src.app_logic import AppConfig


class _SingletonMeta(type):
    """
    Thread-safe Singleton metaclass.
    Ensures only one instance of the LoggerManager is created.
    """
    _instances: dict[type, object] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs) -> object:
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class _LoggerManager(metaclass=_SingletonMeta):
    """
    Logger manager class responsible for configuring and providing a shared logger instance.
    Includes rotating file and console handlers.
    """

    def __init__(self) -> None:
        self._config: AppConfig = AppConfig()
        self._logger: Logger = logging.getLogger(self._config.app_name)
        self.__setup_logger()

    def __setup_logger(self) -> None:
        self._logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = RotatingFileHandler(
            filename=self._config.log_file,
            mode='a',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        if not self._logger.handlers:
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

            self._logger.info("=== %s v%s Started ===", self._config.app_name, self._config.app_version)
            self._logger.info("Developer: %s", self._config.developer)
            self._logger.info("Description: %s", self._config.app_description)
            self._logger.info("Log File: %s", self._config.log_file)

    @property
    def logger(self) -> Logger:
        return self._logger


class Log:
    """
    Public logger access class with shortcut static methods.
    Example: Log.info("msg") instead of Log.get().info("msg")
    """

    @staticmethod
    def get() -> Logger:
        return _LoggerManager().logger

    @staticmethod
    def debug(msg: str, *args, **kwargs) -> None:
        Log.get().debug(msg, *args, **kwargs)

    @staticmethod
    def info(msg: str, *args, **kwargs) -> None:
        Log.get().info(msg, *args, **kwargs)

    @staticmethod
    def warning(msg: str, *args, **kwargs) -> None:
        Log.get().warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg: str, *args, **kwargs) -> None:
        Log.get().error(msg, *args, **kwargs)

    @staticmethod
    def critical(msg: str, *args, **kwargs) -> None:
        Log.get().critical(msg, *args, **kwargs)

    @staticmethod
    def exception(msg: str, *args, **kwargs) -> None:
        """
        Shortcut for logging an exception with traceback.
        Should be used inside except blocks.
        """
        Log.get().exception(msg, *args, **kwargs)
