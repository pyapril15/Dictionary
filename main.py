"""
main.py

Entry point for initializing and running the dictionary application using OOP principles.
Handles:
- Application setup (config, icons, QSS)
- Logging initialization
- Version update logic
- Launching the GUI
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.app_logic.app_config import AppConfig
from src.app_logic.log import Log
from src.app_services.github_service import UpdateUtility
from src.app_ui.main_window import MainWindow
from src.app_ui.ui_update_window import UpdateWindow


class DictionaryApp:
    """
    Main application class that encapsulates all logic for launching the dictionary GUI.
    It manages configuration, theming, update handling, and window management.
    """

    def __init__(self, config: AppConfig, log: Log) -> None:
        """
        Initializes the QApplication, configuration, logging, and update logic.

        Args:
            config (AppConfig): Application configuration instance.
            log (Log): Logger manager instance.
        """
        self._config = config
        self._log = log
        self._logger_app = log.app
        self._logger_update = log.update

        try:
            self._logger_app.info("Initializing DictionaryApp instance...")
            self._app: QApplication = QApplication(sys.argv)
            self._window: MainWindow | None = None
            self._update_utility: UpdateUtility = UpdateUtility(config, log)
            self._initialize_app()
        except Exception as e:
            self._logger_app.exception(f"Critical failure during app initialization. {str(e)}")
            sys.exit(1)

    def _initialize_app(self) -> None:
        """
        Perform initial setup tasks: signals, icon, stylesheet, and update check.
        """
        try:
            self._app.aboutToQuit.connect(self._on_close)
            self._app.setWindowIcon(QIcon(self._config.app_icon_path))
            self._logger_app.info("Window icon set from path: %s", self._config.app_icon_path)
            self._load_stylesheet()
        except Exception as e:
            self._logger_app.exception(f"Error during UI setup. {str(e)}")

        try:
            self._logger_app.info("Checking update status...")
            if self._update_utility.is_version_discontinued():
                self._logger_update.warning("Application version is discontinued. Initiating forced update.")
                self._update_utility.update_for_discontinued(self._on_discontinued_found)
            else:
                self._update_utility.check_for_updates(self._on_update_found)
        except Exception as e:
            self._logger_update.exception(f"Failed to check for updates. {str(e)}")

    def _load_stylesheet(self) -> None:
        """
        Load and apply the QSS stylesheet from the config path.
        """
        try:
            with open(self._config.stylesheet, 'r') as f:
                qss = f.read()
            self._app.setStyleSheet(qss)
            self._logger_app.info("Stylesheet loaded successfully: %s", self._config.stylesheet)
        except FileNotFoundError:
            self._logger_app.error("Stylesheet file not found: %s", self._config.stylesheet)
        except PermissionError:
            self._logger_app.error("Permission denied when accessing stylesheet: %s", self._config.stylesheet)
        except Exception as e:
            self._logger_app.exception(f"Unexpected error while loading stylesheet. {str(e)}")

    def _on_update_found(
            self,
            release_info: dict[str, Any],
            update_url: str,
            version_tuple: tuple[str, str]
    ) -> None:
        """
        Callback for optional update availability.

        Args:
            release_info (dict): Metadata of the release.
            update_url (str): URL to download the update.
            version_tuple (tuple): New version as a string pair (new, current).
        """
        try:
            self._logger_update.info("Update available. Displaying update dialog.")
            update_dialog = UpdateWindow(release_info, update_url, version_tuple, False, self._log)
            update_dialog.exec()
        except Exception as e:
            self._logger_update.exception(f"Failed to show optional update dialog. {str(e)}")

    def _on_discontinued_found(
            self,
            release_info: dict[str, Any],
            update_url: str,
            version_tuple: tuple[str, str]
    ) -> None:
        """
        Callback for discontinued version detection (forces update).

        Args:
            release_info (dict): Metadata of the release.
            update_url (str): URL to download the update.
            version_tuple (tuple): New version as a string pair (new, current).
        """
        try:
            self._logger_update.info("Launching forced update dialog.")
            update_dialog = UpdateWindow(release_info, update_url, version_tuple, True, self._log)

            def handle_close() -> None:
                self._logger_update.warning("User declined mandatory update. Exiting application.")
                sys.exit(0)

            def handle_success() -> None:
                self._logger_update.info("Mandatory update finished. Initiating cleanup.")
                self._schedule_self_delete()

            update_dialog.rejected.connect(handle_close)
            update_dialog.update_finished.connect(handle_success)
            update_dialog.exec()
        except Exception as e:
            self._logger_update.exception(f"Error during forced update process. {str(e)}")
            sys.exit(1)

    def _schedule_self_delete(self) -> None:
        """
        Create and execute a batch script to delete the old executable and start the new one.
        """
        exe_path = self._config.exe_dir
        folder = Path(exe_path).parent
        new_exe = f"Dictionary_{self._config.app_version}.exe"
        new_exe_path = Path(folder) / new_exe

        bat_script = f"""@echo off
        timeout /t 2 > NUL
        del "{exe_path}" > NUL 2>&1
        start "" "{new_exe_path}"
        del "%~f0" > NUL 2>&1
        """

        bat_path = Path(folder) / "delete_self.bat"
        try:
            with open(bat_path, "w") as f:
                f.write(bat_script)
            self._logger_app.info("Self-deletion batch script created: %s", bat_path)
            subprocess.Popen(["cmd", "/c", bat_path], shell=True)
        except Exception as e:
            self._logger_app.exception(f"Failed to schedule self-deletion after update. {str(e)}")

        sys.exit(0)

    def _on_close(self) -> None:
        """
        Handles graceful shutdown tasks when the app is closing.
        """
        self._logger_app.info("Application is closing. Performing cleanup...")

    def run(self) -> None:
        """
        Launch the main GUI and start the event loop.
        """
        try:
            self._logger_app.info("Creating and displaying main window.")
            self._window = MainWindow(self._config, self._log)
            self._window.show()
            self._logger_app.info("Main event loop started.")
            sys.exit(self._app.exec())
        except Exception as e:
            self._logger_app.exception(f"Unhandled error in application loop. {str(e)}")
            sys.exit(1)


# === Entry Point ===
if __name__ == "__main__":
    _config = AppConfig()
    _config.ensure_structure()

    _log = Log(_config)

    _logger_app = _log.app
    _logger_config = _log.config

    _logger_app.info("Application launch sequence started.")
    _logger_config.info("Directory structure validated and ready.")

    try:
        app = DictionaryApp(_config, _log)
        app.run()
    except Exception as eApp:
        _logger_app.critical(f"Fatal error in main block. {str(eApp)}", exc_info=True)
        sys.exit(1)
