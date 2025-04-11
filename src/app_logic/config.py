"""
Configuration module using Singleton pattern and OOP principles.
Handles application settings, paths, metadata, and ensures necessary structure.
"""

import os
import sys
from pathlib import Path
from threading import Lock


class _SingletonMeta(type):
    """
    Thread-safe Singleton metaclass used to enforce a single instance across the app.
    """
    _instances: dict[type, object] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs) -> object:
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class _BaseConfig(metaclass=_SingletonMeta):
    """
    Base configuration class for internal use.
    Initializes app paths, metadata, and structure. Enforced as singleton.
    """

    def __init__(self) -> None:
        self._is_frozen: bool = hasattr(sys, "_MEIPASS") or getattr(sys, 'frozen', False)

        # App install directory (used for static resources like icons/styles)
        self._base_dir: Path = Path(__file__).resolve().parent.parent.parent
        self._resources_dir: Path = self._base_dir / "resources"
        self._app_icon_path: Path = self._resources_dir / "icons" / "app_icon.ico"
        self._search_icon_path: Path = self._resources_dir / "icons" / "search_icon.svg"
        self._stylesheet_path: Path = self._resources_dir / "styles" / "stylesheet.qss"

        # Runtime directory (for logs, saved data)
        if self._is_frozen:
            self._runtime_dir: Path = Path(os.getenv("LOCALAPPDATA", Path.home())) / "DictionaryApp"
        else:
            self._runtime_dir: Path = self._base_dir

        self._data_dir: Path = self._runtime_dir / "data"
        self._logs_dir: Path = self._runtime_dir / "logs"
        self._dictionary_file: Path = self._data_dir / "dictionary.json"
        self._log_file: Path = self._logs_dir / "dictionary.log"

        # Metadata
        self._app_name: str = "Dictionary"
        self._app_version: str = "1.0.0"
        self._app_description: str = "A desktop GUI dictionary powered by WordNet."
        self._developer: str = "Praveen Yadav"

        # Runtime flags
        self._debug_mode: bool = not self._is_frozen
        self._default_theme: str = "light"

        self.__ensure_structure()

    def __ensure_structure(self) -> None:
        """Ensures required folders and files exist."""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._logs_dir.mkdir(parents=True, exist_ok=True)

        if not self._dictionary_file.exists():
            self._dictionary_file.write_text('{}')
        if not self._log_file.exists():
            self._log_file.touch()

    # === Properties ===

    @property
    def is_frozen(self) -> bool:
        """Whether the app is running in a frozen (packaged) state."""
        return self._is_frozen

    @property
    def base_dir(self) -> Path:
        """Application base directory (installation/static files)."""
        return self._base_dir

    @property
    def runtime_dir(self) -> Path:
        """User-local runtime directory (logs, saved data)."""
        return self._runtime_dir

    @property
    def data_dir(self) -> Path:
        """Path to data directory."""
        return self._data_dir

    @property
    def logs_dir(self) -> Path:
        """Path to logs directory."""
        return self._logs_dir

    @property
    def dictionary_file(self) -> Path:
        """Path to dictionary JSON file."""
        return self._dictionary_file

    @property
    def log_file(self) -> Path:
        """Path to log file."""
        return self._log_file

    @property
    def resources_dir(self) -> Path:
        """Path to app resources directory."""
        return self._resources_dir

    @property
    def app_icon_path(self) -> str:
        """Path to app icon (as string)."""
        return str(self._app_icon_path)

    @property
    def search_icon_path(self) -> str:
        """Path to search icon (as string)."""
        return str(self._search_icon_path)

    @property
    def stylesheet(self) -> str:
        """Path to QSS stylesheet file (as string)."""
        return str(self._stylesheet_path)

    @property
    def app_name(self) -> str:
        """Application name."""
        return self._app_name

    @property
    def app_version(self) -> str:
        """Current application version."""
        return self._app_version

    @property
    def app_description(self) -> str:
        """Short description of the app."""
        return self._app_description

    @property
    def developer(self) -> str:
        """Name of the developer."""
        return self._developer

    @property
    def debug_mode(self) -> bool:
        """Flag indicating if app is in debug mode."""
        return self._debug_mode

    @property
    def default_theme(self) -> str:
        """Default UI theme name."""
        return self._default_theme


class AppConfig(_BaseConfig):
    """
    Public-facing configuration class. Safe to use throughout the app.
    Provides read-only access to application config data.
    """
