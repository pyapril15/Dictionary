"""
Configuration Manager - Handles all application settings, paths, and environment setup.
Implements robust Singleton and full OOP design with abstraction and encapsulation.
"""

import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from src.utils.meta import SingletonMeta


class ConfigurationNotInitializedError(Exception):
    """
    Raised when a configuration property is accessed before initialization.
    """
    pass


class AbstractConfigManager(ABC):
    """
    Abstract base class enforcing interface for application configuration.
    Promotes loose coupling and strict access control.
    """

    @property
    @abstractmethod
    def app_name(self) -> str: pass

    @property
    @abstractmethod
    def app_version(self) -> str: pass

    @property
    @abstractmethod
    def developer(self) -> str: pass

    @property
    @abstractmethod
    def base_dir(self) -> Path: pass

    @property
    @abstractmethod
    def exe_dir(self) -> Path: pass

    @property
    @abstractmethod
    def runtime_dir(self) -> Path: pass

    @property
    @abstractmethod
    def data_dir(self) -> Path: pass

    @property
    @abstractmethod
    def logs_dir(self) -> Path: pass

    @property
    @abstractmethod
    def dictionary_file(self) -> Path: pass

    @property
    @abstractmethod
    def app_icon_path(self) -> str: pass

    @property
    @abstractmethod
    def search_icon_path(self) -> str: pass

    @property
    @abstractmethod
    def stylesheet(self) -> str: pass

    @property
    @abstractmethod
    def debug_mode(self) -> bool: pass

    @property
    @abstractmethod
    def all_log_files(self) -> Dict[str, Path]: pass


class _ConfigManager(AbstractConfigManager, metaclass=SingletonMeta):
    """
    Concrete implementation of application configuration.
    Sets up paths, environment details, and ensures directory structure.
    Structure creation must be triggered explicitly via ensure_structure().
    """

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return

        self.__is_frozen = getattr(sys, 'frozen', False)
        self.__structure_ready = False

        self.__initialize_paths()
        self.__initialize_metadata()

        self.__initialized = True

    def __initialize_paths(self) -> None:
        self.__base_dir = Path(__file__).resolve().parent.parent.parent
        self.__exe_dir = Path(sys.argv[0]).resolve()
        self.__resources_dir = self.__base_dir / "resources"
        self.__app_icon_path = self.__resources_dir / "icons" / "app_icon.ico"
        self.__search_icon_path = self.__resources_dir / "icons" / "search_icon.svg"
        self.__stylesheet_path = self.__resources_dir / "styles" / "stylesheet.qss"

        self.__runtime_dir = (
            Path(os.getenv("LOCALAPPDATA", Path.home())) / "DictionaryApp"
            if self.__is_frozen else self.__base_dir
        )
        self.__data_dir = self.__runtime_dir / "data"
        self.__logs_dir = self.__runtime_dir / "logs"
        self.__dictionary_file = self.__data_dir / "dictionary.json"

        self.__log_files: Dict[str, Path] = {
            "app": self.__logs_dir / "app.log",
            "dictionary": self.__logs_dir / "dictionary.log",
            "logic": self.__logs_dir / "logic.log",
            "update": self.__logs_dir / "update.log",
            "config": self.__logs_dir / "config.log",
        }

    def __initialize_metadata(self) -> None:
        self.__app_name = "Dictionary"
        self.__app_version = "1.0.0"
        self.__developer = "Praveen Yadav"
        self.__debug_mode = not self.__is_frozen
        self.__default_theme = "light"

    def ensure_structure(self) -> None:
        """
        Explicitly creates required runtime folders and files.
        Must be called before accessing runtime paths.
        """
        self.__data_dir.mkdir(parents=True, exist_ok=True)
        self.__logs_dir.mkdir(parents=True, exist_ok=True)

        if not self.__dictionary_file.exists():
            self.__dictionary_file.write_text('{}', encoding='utf-8')

        for path in self.__log_files.values():
            path.touch(exist_ok=True)

        self.__structure_ready = True

    def __check_initialized(self):
        if not self.__structure_ready:
            raise ConfigurationNotInitializedError(
                "Configuration structure not initialized. Call `ensure_structure()` first."
            )

    # === Public Property Getters ===

    @property
    def app_name(self) -> str:
        return self.__app_name

    @property
    def app_version(self) -> str:
        return self.__app_version

    @property
    def developer(self) -> str:
        return self.__developer

    @property
    def base_dir(self) -> Path:
        return self.__base_dir

    @property
    def exe_dir(self) -> Path:
        return self.__exe_dir

    @property
    def runtime_dir(self) -> Path:
        self.__check_initialized()
        return self.__runtime_dir

    @property
    def data_dir(self) -> Path:
        self.__check_initialized()
        return self.__data_dir

    @property
    def logs_dir(self) -> Path:
        self.__check_initialized()
        return self.__logs_dir

    @property
    def dictionary_file(self) -> Path:
        self.__check_initialized()
        return self.__dictionary_file

    @property
    def app_icon_path(self) -> str:
        return str(self.__app_icon_path)

    @property
    def search_icon_path(self) -> str:
        return str(self.__search_icon_path)

    @property
    def stylesheet(self) -> str:
        return str(self.__stylesheet_path)

    @property
    def debug_mode(self) -> bool:
        return self.__debug_mode

    @property
    def default_theme(self) -> str:
        return self.__default_theme

    @property
    def all_log_files(self) -> Dict[str, Path]:
        self.__check_initialized()
        return self.__log_files.copy()


class AppConfig(_ConfigManager):
    """
    Public-facing application config access point.
    Provides safe, read-only interface to app configuration.
    """
    pass
