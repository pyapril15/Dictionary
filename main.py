"""
Entry point for initializing and running the dictionary application using OOP principles.
"""

import os
import sys
import subprocess
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.app_logic.config import AppConfig
from src.app_logic.main_window import MainWindow
from src.app_logic.logger import logger
from src.app_ui.ui_update_window import UpdateWindow
from src.app_logic.update_logic import check_for_updates, is_version_discontinued, update_for_discontinued


class DictionaryApp:
    """
    Main application class for the dictionary GUI.
    Handles initialization, configuration, and execution using OOP structure.
    """

    def __init__(self):
        self._config = AppConfig()
        self._app = QApplication(sys.argv)
        self._window = None
        self.__initialize_app()

    def __initialize_app(self):
        # Application metadata setup
        self._app.aboutToQuit.connect(self._on_close)
        self._app.setWindowIcon(QIcon(self._config.app_icon_path))
        self.__load_stylesheet()

        logger.info("Application initialized and ready.")

        # === Check if version is discontinued ===
        if is_version_discontinued(self._config):
            logger.warning("This version is discontinued. Forcing update.")
            update_for_discontinued(self._config, self._show_forced_update)
        else:
            check_for_updates(self._config, self._on_update_found)

    def __load_stylesheet(self):
        try:
            with open(self._config.stylesheet, 'r') as f:
                qss = f.read()
            self._app.setStyleSheet(qss)
            logger.info("QSS loaded successfully from: %s", self._config.stylesheet)
        except Exception as e:
            logger.error("Failed to load QSS from %s: %s", self._config.stylesheet, str(e))

    @staticmethod
    def _on_update_found(release_info, update_url, version_tuple):
        """
        Callback executed when a newer version is detected.
        """
        logger.info("Displaying update window...")
        update_dialog = UpdateWindow(release_info, update_url, version_tuple)
        update_dialog.exec()

    @staticmethod
    def _on_close():
        logger.info("Application is closing...")

    def run(self):
        self._window = MainWindow()
        self._window.show()

        logger.info("Application GUI started successfully.")
        try:
            sys.exit(self._app.exec())
        except Exception as e:
            logger.error("Unhandled error in application loop: %s", str(e))

    def _on_discontinued_found(self, release_info, update_url, version_tuple):
        """
        Forces user to update the app when the current version is discontinued.
        """

        update_dialog = UpdateWindow(release_info, update_url, version_tuple)

        def handle_close():
            logger.info("User cancelled mandatory update. Exiting app.")
            sys.exit(0)

        def handle_success():
            logger.info("Mandatory update successful. Scheduling self-deletion.")
            self._schedule_self_delete()

        update_dialog.update_finished.connect(handle_success)
        update_dialog.rejected.connect(handle_close)
        update_dialog.exec()

    def _schedule_self_delete(self):
        """
        Generates and runs a batch script to delete this old app and run the new one.
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
"""

        bat_path = os.path.join(folder, "delete_self.bat")
        try:
            with open(bat_path, "w") as f:
                f.write(bat_script)
            logger.info("Self-deletion script written: %s", bat_path)
            subprocess.Popen(["cmd", "/c", bat_path], shell=True)
        except Exception as e:
            logger.error("Failed to create or execute self-deletion script: %s", str(e))

        sys.exit(0)


# === Entry point ===
if __name__ == "__main__":
    app = DictionaryApp()
    app.run()
