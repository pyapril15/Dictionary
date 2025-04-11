"""
Top-level package initializer for the Dictionary App.
This exposes primary components for easy external access.
"""

from .app_logic import AppConfig, Log, Dictionary, UpdateManager, MainWindow
from .app_services import github_service
from .app_ui import Ui_Form, UpdateWindow

__all__ = [
    "AppConfig",
    "Log",
    "Dictionary",
    "MainWindow",
    "UpdateManager",
    "github_service",
    "Ui_Form",
    "UpdateWindow"
]
