"""
Module for managing the main application window using OOP principles.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QCompleter, QListWidgetItem, QMessageBox

from src.app_logic import Dictionary
from src.app_logic import AppConfig
from src.app_logic import Log
from src.app_ui import Ui_Form

from typing import Dict, List, Any, Optional


class MainWindow(QWidget):
    """
    Main application window for the Dictionary App.
    Handles UI interactions, word search, and display logic.
    """

    def __init__(self) -> None:
        """
        Initialize the main window and its components.
        """
        super().__init__()

        self._config: AppConfig = AppConfig()
        self._ui: Ui_Form = Ui_Form()
        self._definitions: Dict[str, List[Dict[str, Any]]] = {}
        self._current_word: Optional[str] = None

        self.__setup_ui()
        self.__connect_signals()
        self.__load_definitions()
        self.__init_completer()

    def __setup_ui(self) -> None:
        """
        Private: Initialize and configure UI elements.
        """
        self._ui.setupUi(self)
        self._ui.search_item_btn.setIcon(QIcon(self._config.search_icon_path))
        self._ui.search_item_btn.setDisabled(True)

    def __connect_signals(self) -> None:
        """
        Private: Connect UI widget signals to corresponding methods (slots).
        """
        self._ui.search_item.textChanged.connect(self._on_text_changed)
        self._ui.search_item_btn.clicked.connect(self._on_search_clicked)

    def __load_definitions(self) -> None:
        """
        Private: Load cached definitions into the local dictionary from DictionaryManager.
        """
        try:
            self._definitions = Dictionary.load_definitions()
            Log.info("Definitions loaded into main window.")
        except Exception as e:
            Log.error("Failed to load definitions: %s", str(e))
            QMessageBox.critical(self, "Error", "Failed to load dictionary definitions.")

    def __init_completer(self) -> None:
        """
        Private: Initialize autocompletion based on current dictionary words.
        """
        completer = QCompleter(sorted(self._definitions.keys(), key=str.lower), self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._ui.search_item.setCompleter(completer)

    def _on_text_changed(self, text: str) -> None:
        """
        Protected: React to changes in the search bar.
        Updates UI and enables search button if the word is not cached.

        Args:
            text (str): Text entered into the search bar.
        """
        self._ui.listWidget.clear()
        text = text.strip()

        if text:
            if text in self._definitions:
                self._display_definitions(self._definitions[text])
                self._ui.search_item_btn.setDisabled(True)
            else:
                self._ui.search_item_btn.setDisabled(False)

    def _on_search_clicked(self) -> None:
        """
        Protected: Triggered when the search button is clicked.
        Fetches the definition, updates cache and UI.
        """
        word = self._ui.search_item.text().strip()
        if not word:
            return

        self._current_word = word

        if word in self._definitions:
            self._display_definitions(self._definitions[word])
            return

        try:
            definitions = Dictionary.fetch_definitions(word)
            if definitions:
                Dictionary.add_definition(word, definitions)
                self._definitions[word] = definitions
                self.__init_completer()
                self._display_definitions(definitions)
                Log.info("Fetched and added new definition for: %s", word)
            else:
                item = QListWidgetItem("❗ No definitions found for this word.")
                item.setForeground(Qt.gray)
                self._ui.listWidget.addItem(item)
                Log.warning("No definitions found for: %s", word)
        except Exception as e:
            Log.error("Failed to fetch definition for '%s': %s", word, str(e))
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def _display_definitions(self, definitions: List[Dict[str, Any]]) -> None:
        """
        Protected: Populate the result list widget with definition and examples.

        Args:
            definitions (List[Dict[str, Any]]): List of definitions with optional examples.
        """
        self._ui.listWidget.clear()
        for idx, definition in enumerate(definitions, 1):
            item_text = f"{idx}. {definition['definition']}\n"
            if definition.get("examples"):
                item_text += "   Examples:\n"
                for ex in definition["examples"]:
                    item_text += f"   - {ex}\n"
            item = QListWidgetItem(item_text)
            item.setToolTip(item_text)
            self._ui.listWidget.addItem(item)
