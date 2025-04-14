"""
Logger Manager - Robust and scalable logging system for the application.
Implements Singleton design pattern with abstraction and full OOP principles.
"""

import logging
from abc import ABC, abstractmethod
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Optional

from src.app_logic.app_config import AppConfig
from src.utils.meta import SingletonMeta


class AbstractLoggerManager(ABC):
    """
    Abstract base class for LoggerManager.
    Enforces logger accessor methods.
    """

    @abstractmethod
    def get_logger(self, category: str) -> Optional[Logger]:
        pass

    @property
    @abstractmethod
    def dictionary(self) -> Logger: pass

    @property
    @abstractmethod
    def logic(self) -> Logger: pass

    @property
    @abstractmethod
    def update(self) -> Logger: pass

    @property
    @abstractmethod
    def config(self) -> Logger: pass


class _LoggerManager(AbstractLoggerManager, metaclass=SingletonMeta):
    """
    Concrete implementation of the logger manager using Singleton pattern.
    Handles creation and retrieval of categorized loggers.
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._loggers: Dict[str, Logger] = {}
        self.__initialize_loggers()

    def __initialize_loggers(self) -> None:
        """
        Initializes all categorized loggers from AppConfig.
        """
        for category, path in self._config.all_log_files.items():
            logger_name = f"{category.capitalize()}Logger"
            self._loggers[category] = self.__create_logger(logger_name, path)

    def __create_logger(self, name: str, file_path: Path) -> Logger:
        """
        Creates and configures a logger with both file and console handlers.
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if logger.hasHandlers():
            return logger  # Avoid duplicate handlers

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = RotatingFileHandler(
            filename=file_path,
            mode='a',
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.propagate = False

        logger.info("=== Logger [%s] Initialized ===", name)
        logger.info("App: %s v%s", self._config.app_name, self._config.app_version)
        logger.info("Developer: %s", self._config.developer)
        logger.info("Log File: %s", file_path)

        return logger

    def get_logger(self, category: str) -> Optional[Logger]:
        """
        Retrieve logger by category. Returns None if not found.
        """
        return self._loggers.get(category)

    @property
    def app(self) -> Logger:
        return self._loggers["app"]

    @property
    def dictionary(self) -> Logger:
        return self._loggers["dictionary"]

    @property
    def logic(self) -> Logger:
        return self._loggers["logic"]

    @property
    def update(self) -> Logger:
        return self._loggers["update"]

    @property
    def config(self) -> Logger:
        return self._loggers["config"]


class Log(_LoggerManager):
    """
    Static entry point for categorized logger access.
    Promotes clean usage across the app.

    Example:
        Log.logic.info("Processing started...")
    """

    def __init__(self, config: AppConfig):
        super().__init__(config)
