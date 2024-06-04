import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from src.dictionary_manager import ensure_wordnet_downloaded, create_directory, create_dictionary_file
import config
from src.main_window import MainWindow
from src.logger_setup import logger

try:
    ensure_wordnet_downloaded()
    logger.info("WordNet downloaded successfully")
except Exception as e:
    logger.error(f"Error downloading WordNet: {e}")
    sys.exit(1)

try:
    create_directory(config.DATA_DIR)
    create_directory(config.LOGS_DIR)
    create_dictionary_file(config.DICTIONARY_PATH)
    logger.info("Dictionary file created successfully")
except Exception as e:
    logger.error(f"Failed to create dictionary file: {e}")
    sys.exit(1)


def load_stylesheet(obj, file_path):
    try:
        with file_path.open("r") as f:
            qss = f.read()
        obj.setStyleSheet(qss)
        logger.info(f"Stylesheet loaded successfully from {file_path}")
    except Exception as e:
        logger.error(f"Failed to load stylesheet from {file_path}: {e}")


def log_application_close():
    logger.info("Application closed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(log_application_close)
    load_stylesheet(app, config.STYLESHEET_PATH)
    app.setWindowIcon(QIcon(str(config.APP_ICON_PATH)))  # Convert Path to string
    window = MainWindow()
    window.show()
    logger.info("Application started")

    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Error during application execution: {e}")
