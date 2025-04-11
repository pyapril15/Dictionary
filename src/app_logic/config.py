"""
Configuration module using Singleton pattern and OOP principles.
Handles application settings, paths, metadata, and ensures necessary structure.
"""

import os
import sys
from pathlib import Path
from threading import Lock


class _SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class _BaseConfig(metaclass=_SingletonMeta):
    def __init__(self):
        self._is_frozen = hasattr(sys, "_MEIPASS") or getattr(sys, 'frozen', False)

        # === App Directory (static files: icons, .qss, etc.) ===
        """
        if self._is_frozen:
            self._base_dir = Path(sys.executable).resolve().parent.parent
        else:
            self._base_dir = Path(__file__).resolve().parent.parent.parent
        """
        self._base_dir = Path(__file__).resolve().parent.parent.parent

        self._resources_dir = self._base_dir / "resources"
        self._app_icon_path = self._resources_dir / "icons" / "app_icon.ico"
        self._search_icon_path = self._resources_dir / "icons" / "search_icon.svg"
        self._stylesheet_path = self._resources_dir / "styles" / "stylesheet.qss"

        # === Runtime Directory (user data, logs) ===
        if self._is_frozen:
            self._runtime_dir = Path(os.getenv("LOCALAPPDATA", Path.home())) / "DictionaryApp"
        else:
            self._runtime_dir = self._base_dir

        self._data_dir = self._runtime_dir / "data"
        self._logs_dir = self._runtime_dir / "logs"
        self._dictionary_file = self._data_dir / "dictionary.json"
        self._log_file = self._logs_dir / "dictionary.log"

        # === App Metadata ===
        self._app_name = "Dictionary"
        self._app_version = "1.0.0"
        self._app_description = "A desktop GUI dictionary powered by WordNet."
        self._developer = "Praveen Yadav"

        # === Flags ===
        self._debug_mode = not self._is_frozen
        self._default_theme = "light"

        self.__ensure_structure()

    def __ensure_structure(self):
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._logs_dir.mkdir(parents=True, exist_ok=True)

        if not self._dictionary_file.exists():
            self._dictionary_file.write_text('{}')
        if not self._log_file.exists():
            self._log_file.touch()

    # --- Accessors ---

    @property
    def is_frozen(self): return self._is_frozen

    @property
    def base_dir(self): return self._base_dir  # For static files
    @property
    def runtime_dir(self): return self._runtime_dir  # For user-generated data

    @property
    def data_dir(self): return self._data_dir
    @property
    def logs_dir(self): return self._logs_dir
    @property
    def dictionary_file(self): return self._dictionary_file
    @property
    def log_file(self): return self._log_file

    @property
    def resources_dir(self): return self._resources_dir
    @property
    def app_icon_path(self): return str(self._app_icon_path)
    @property
    def search_icon_path(self): return str(self._search_icon_path)
    @property
    def stylesheet(self): return str(self._stylesheet_path)

    @property
    def app_name(self): return self._app_name
    @property
    def app_version(self): return self._app_version
    @property
    def app_description(self): return self._app_description
    @property
    def developer(self): return self._developer

    @property
    def debug_mode(self): return self._debug_mode
    @property
    def default_theme(self): return self._default_theme

class AppConfig(_BaseConfig):
    """Public-facing configuration class for safe, read-only access."""

    # --- Directory Access ---
    @property
    def base_dir(self): return self._base_dir

    @property
    def data_dir(self): return self._data_dir

    @property
    def logs_dir(self): return self._logs_dir

    @property
    def resources_dir(self): return self._resources_dir

    # --- File Paths ---
    @property
    def dictionary_file(self): return self._dictionary_file

    @property
    def log_file(self): return self._log_file

    # --- UI Resources ---
    @property
    def app_icon_path(self): return str(self._app_icon_path)

    @property
    def search_icon_path(self): return str(self._search_icon_path)

    @property
    def stylesheet(self): return str(self._stylesheet_path)

    # --- App Metadata ---
    @property
    def app_name(self): return self._app_name

    @property
    def app_version(self): return self._app_version

    @property
    def app_description(self): return self._app_description

    @property
    def developer(self): return self._developer

    # --- Runtime Flags ---
    @property
    def debug_mode(self): return self._debug_mode

    @property
    def default_theme(self): return self._default_theme
