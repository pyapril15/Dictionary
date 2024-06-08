"""
Module for initializing and running the dictionary application.
"""

import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from src.dictionary import ensure_wordnet_downloaded
from src.config import APP_ICON_PATH, STYLE_SHEET
from src.main_window import MainWindow
from src.logger import logger


def load_stylesheet(obj, file_path):
    """
    Load and apply QSS stylesheet to the given application.

    Args:
        obj: The QApplication object.
        file_path (str): Path to the QSS stylesheet file.
    """
    try:
        with open(file_path, 'r') as f:
            qss = f.read()
        obj.setStyleSheet(qss)
        logger.info("QSS loaded successfully from %s", file_path)
    except Exception as e:
        logger.error("Failed to load QSS from %s: %s", file_path, str(e))


def log_application_close():
    """
    Log application closure event.
    """
    logger.info("Application closed")


if __name__ == "__main__":
    # Ensure WordNet data is downloaded
    ensure_wordnet_downloaded()

    # Create and configure the QApplication instance
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(log_application_close)
    app.setWindowIcon(QIcon(APP_ICON_PATH))

    # Load the application stylesheet
    load_stylesheet(app, STYLE_SHEET)

    # Create and display the main window
    window = MainWindow()
    window.show()

    logger.info("Application started")

    try:
        # Execute the application event loop
        sys.exit(app.exec())
    except Exception as e:
        logger.error("Error during application execution: %s", str(e))
