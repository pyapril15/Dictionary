"""
Entry point for initializing and running the dictionary application using OOP principles.
"""

import os
import sys
import subprocess
from typing import Any

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src import AppConfig
from src import MainWindow
from src import Log
from src import UpdateWindow
from src.app_services import check_for_updates, is_version_discontinued, update_for_discontinued


class DictionaryApp:
    """
    Main application class for the dictionary GUI.
    Handles initialization, configuration, and execution using OOP structure.
    """

    def __init__(self) -> None:
        """
        Initializes the application and prepares the main event loop.
        """
        self._config: AppConfig = AppConfig()
        self._app: QApplication = QApplication(sys.argv)
        self._window: MainWindow | None = None
        self.__initialize_app()

    def __initialize_app(self) -> None:
        """
        Set up application metadata, stylesheet, and check for updates.
        """
        self._app.aboutToQuit.connect(self._on_close)
        self._app.setWindowIcon(QIcon(self._config.app_icon_path))
        self.__load_stylesheet()

        Log.info("Application initialized and ready.")

        if is_version_discontinued(self._config):
            Log.warning("This version is discontinued. Forcing update.")
            update_for_discontinued(self._config, self._on_discontinued_found)
        else:
            check_for_updates(self._config, self._on_update_found)

    def __load_stylesheet(self) -> None:
        """
        Load the application's QSS stylesheet from the configured path.
        """
        try:
            with open(self._config.stylesheet, 'r') as f:
                qss = f.read()
            self._app.setStyleSheet(qss)
            Log.info("QSS loaded successfully from: %s", self._config.stylesheet)
        except Exception as e:
            Log.error("Failed to load QSS from %s: %s", self._config.stylesheet, str(e))

    @staticmethod
    def _on_update_found(release_info: dict[str, Any], update_url: str, version_tuple: tuple[str, str]) -> None:
        """
        Callback executed when a newer version is detected.

        Args:
            release_info (dict): Release metadata from GitHub.
            update_url (str): Download URL for the new version.
            version_tuple (tuple): New version as a tuple (major, minor, patch).
        """
        Log.info("Displaying update window...")
        update_dialog = UpdateWindow(release_info, update_url, version_tuple)
        update_dialog.exec()

    @staticmethod
    def _on_close() -> None:
        """
        Callback triggered when the application is about to close.
        """
        Log.info("Application is closing...")

    def run(self) -> None:
        """
        Show the main window and start the application event loop.
        """
        self._window = MainWindow()
        self._window.show()

        Log.info("Application GUI started successfully.")
        try:
            sys.exit(self._app.exec())
        except Exception as e:
            Log.error("Unhandled error in application loop: %s", str(e))

    def _on_discontinued_found(
            self,
            release_info,
            update_url: str,
            version_tuple: [str, str]
    ) -> None:
        """
        Force the user to update the application due to version discontinuation.

        Args:
            release_info (dict): Release metadata.
            update_url (str): URL to the new version.
            version_tuple (tuple): Version information as a tuple.
        """
        update_dialog = UpdateWindow(release_info, update_url, version_tuple, True)

        def handle_close() -> None:
            Log.info("User cancelled mandatory update. Exiting app.")
            sys.exit(0)

        def handle_success() -> None:
            Log.info("Mandatory update successful. Scheduling self-deletion.")
            self._schedule_self_delete()

        update_dialog.update_finished.connect(handle_success)
        update_dialog.rejected.connect(handle_close)
        update_dialog.exec()

    def _schedule_self_delete(self) -> None:
        """
        Generates and executes a batch script to delete the old executable
        and run the updated one after update is complete.
        """
        exe_path = os.path.abspath(sys.argv[0])
        folder = os.path.dirname(exe_path)
        current_version = self._config.app_version
        new_exe = f"Dictionary_{current_version}.exe"
        new_exe_path = os.path.join(folder, new_exe)

        bat_script = f"""@echo off
        timeout /t 2 > NUL
        del "{exe_path}" > NUL 2>&1
        start "" "{new_exe_path}"
        del "%~f0" > NUL 2>&1
        """

        bat_path = os.path.join(folder, "delete_self.bat")
        try:
            with open(bat_path, "w") as f:
                f.write(bat_script)
            Log.info("Self-deletion script written: %s", bat_path)
            subprocess.Popen(["cmd", "/c", bat_path], shell=True)
        except Exception as e:
            Log.error("Failed to create or execute self-deletion script: %s", str(e))

        sys.exit(0)


# === Entry point ===
if __name__ == "__main__":
    app = DictionaryApp()
    app.run()
