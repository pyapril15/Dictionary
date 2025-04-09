"""
Module for managing the main application window using OOP principles.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QCompleter, QListWidgetItem, QMessageBox

from src.app_logic.dictionary import dictionary_manager
from src.app_logic.config import AppConfig
from src.app_logic.logger import logger
from src.app_ui.ui_main_window import Ui_Form


class MainWindow(QWidget):
    """
    Main application window for the Dictionary App.
    Handles UI interactions, word search, and display logic.
    """

    def __init__(self):
        """
        Initialize the main window and its components.
        """
        super().__init__()

        self._config = AppConfig()  # Singleton for path configs
        self._ui = Ui_Form()  # Load generated UI
        self._definitions = {}  # Local cache from manager

        self.__setup_ui()
        self.__connect_signals()
        self.__load_definitions()
        self.__init_completer()

    def __setup_ui(self):
        """
        Private: Initialize UI elements.
        """
        self._ui.setupUi(self)
        self._ui.search_item_btn.setIcon(QIcon(self._config.search_icon_path))
        self._ui.search_item_btn.setDisabled(True)

    def __connect_signals(self):
        """
        Private: Connect UI signals to their corresponding slots.
        """
        self._ui.search_item.textChanged.connect(self._on_text_changed)
        self._ui.search_item_btn.clicked.connect(self._on_search_clicked)

    def __load_definitions(self):
        """
        Private: Load saved dictionary definitions from DictionaryManager.
        """
        try:
            self._definitions = dictionary_manager.load_definitions()
            logger.info("Definitions loaded into main window.")
        except Exception as e:
            logger.error("Failed to load definitions: %s", str(e))
            QMessageBox.critical(self, "Error", "Failed to load dictionary definitions.")

    def __init_completer(self):
        """
        Private: Set up autocompletion using dictionary keys.
        """
        completer = QCompleter(self._definitions.keys(), self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._ui.search_item.setCompleter(completer)

    def _on_text_changed(self, text):
        """
        Protected: React to text input changes.
        Disables search button if word exists in dictionary.
        """
        self._ui.listWidget.clear()
        text = text.strip()

        if text:
            if text in self._definitions:
                self._display_definitions(self._definitions[text])
                self._ui.search_item_btn.setDisabled(True)
            else:
                self._ui.search_item_btn.setDisabled(False)

    def _on_search_clicked(self):
        """
        Protected: Triggered when search button is clicked.
        """
        word = self._ui.search_item.text().strip()
        if not word:
            return

        if word in self._definitions:
            self._display_definitions(self._definitions[word])
            return

        try:
            definitions = dictionary_manager.fetch_definitions(word)
            if definitions:
                dictionary_manager.add_definition(word, definitions)
                self._definitions[word] = definitions
                self.__init_completer()
                self._display_definitions(definitions)
                logger.info("Fetched and added new definition for: %s", word)
            else:
                self._ui.listWidget.addItem(QListWidgetItem("No definitions found."))
                logger.warning("No definitions found for: %s", word)
        except Exception as e:
            logger.error("Failed to fetch definition for '%s': %s", word, str(e))
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def _display_definitions(self, definitions):
        """
        Protected: Populate the list widget with formatted definitions and examples.
        """
        self._ui.listWidget.clear()
        for idx, definition in enumerate(definitions, 1):
            item_text = f"{idx}. {definition['definition']}\n"
            if definition.get("examples"):
                item_text += "   Examples:\n"
                for ex in definition['examples']:
                    item_text += f"   - {ex}\n"
            self._ui.listWidget.addItem(QListWidgetItem(item_text))
