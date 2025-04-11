"""
app_logic package initializer.

This package contains core business logic modules for the Dictionary application,
including configuration, logging, dictionary management, GitHub update services, and update handling.
"""

from .config import AppConfig
from .logger import Log
from .dictionary import Dictionary
from .update_manager import UpdateManager
from .main_window import MainWindow

__all__ = [
    "AppConfig",
    "Log",
    "Dictionary",
    "UpdateManager",
    "MainWindow"
]
