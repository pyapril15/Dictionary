"""
Entry point for initializing and running the dictionary application using OOP principles.
"""

import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.app_logic.config import AppConfig
from src.app_logic.main_window import MainWindow
from src.app_logic.logger import logger
from src.app_ui.ui_update_window import UpdateWindow
from src.app_logic.update_logic import check_for_updates


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

        # === Check for updates ===
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


# === Entry point ===
if __name__ == "__main__":
    app = DictionaryApp()
    app.run()
