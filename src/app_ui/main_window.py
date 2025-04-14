"""
main_window.py - Main UI controller for the Dictionary application.

Responsibilities:
- Initialize and manage the main window UI.
- Handle user input and execute dictionary search logic.
- Load and cache definitions from WordNet or local storage.
- Log all actions using a centralized logging system.

Author: Praveen Yadav
Date: 2025-04-13
"""

from typing import Dict, List, Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QCompleter, QListWidgetItem, QMessageBox

from src.app_logic.app_config import AppConfig
from src.app_logic.dictionary import Dictionary
from src.app_logic.log import Log
from src.app_ui.ui_main_window import Ui_Form


class IMainWindow:
    """
    Interface for main window controllers.

    Provides method signatures for interaction between UI and logic layers.
    """

    def load_cached_definitions(self) -> None: raise NotImplementedError
    def setup_ui(self) -> None: raise NotImplementedError
    def connect_signals(self) -> None: raise NotImplementedError
    def display_definitions(self, definitions: List[Dict[str, Any]]) -> None: raise NotImplementedError
    def on_search_clicked(self) -> None: raise NotImplementedError
    def on_text_changed(self, text: str) -> None: raise NotImplementedError


class MainWindow(QWidget, IMainWindow):
    """
    MainWindow implements IMainWindow and acts as the controller
    for the application UI. Handles user input, dictionary logic,
    and UI updates.
    """

    def __init__(self, config: AppConfig, log: Log) -> None:
        """
        Initializes the MainWindow.

        Args:
            config (AppConfig): App settings/config object.
            log (Log): Centralized logger instance.
        """
        super().__init__()
        self._config = config                  # protected
        self._log = log                        # protected
        self._ui = Ui_Form()                   # protected
        self._dictionary = Dictionary(config, log)
        self._definitions: Dict[str, List[Dict[str, Any]]] = {}
        self._current_word: Optional[str] = None

        # Internal loggers
        self.__logger_app = log.app           # private
        self.__logger_logic = log.logic       # private

        try:
            self.__logger_app.info("Initializing MainWindow.")
            self.setup_ui()
            self.connect_signals()
            self.load_cached_definitions()
            self.__init_completer()
            self.__logger_app.info("MainWindow initialized successfully.")
        except Exception as e:
            self.__logger_app.critical(f"Initialization error: {e}", exc_info=True)
            QMessageBox.critical(self, "Initialization Error", f"Initialization failed: {e}")

    def setup_ui(self) -> None:
        """
        Set up UI elements including layout and icons.
        """
        self.__logger_app.debug("Setting up UI.")
        try:
            self._ui.setupUi(self)
            self._ui.search_item_btn.setIcon(QIcon(self._config.search_icon_path))
            self._ui.search_item_btn.setDisabled(True)
        except Exception as e:
            self.__logger_app.error(f"UI setup error: {e}", exc_info=True)
            raise

    def connect_signals(self) -> None:
        """
        Connect UI signals to corresponding slots/handlers.
        """
        self.__logger_app.debug("Connecting signals.")
        try:
            self._ui.search_item.textChanged.connect(self.on_text_changed)
            self._ui.search_item_btn.clicked.connect(self.on_search_clicked)
        except Exception as e:
            self.__logger_app.error(f"Signal connection failed: {e}", exc_info=True)
            raise

    def load_cached_definitions(self) -> None:
        """
        Load dictionary entries previously stored in cache.
        """
        self.__logger_logic.info("Loading cached definitions.")
        try:
            self._definitions = self._dictionary.load_cache()
            self.__logger_logic.info("Cache loaded successfully.")
        except Exception as e:
            self.__logger_logic.error(f"Cache load error: {e}", exc_info=True)
            QMessageBox.critical(self, "Load Error", "Could not load cached definitions.")

    def __init_completer(self) -> None:
        """
        Private helper to initialize autocompletion using cached words.
        """
        self.__logger_app.debug("Initializing completer.")
        try:
            completer = QCompleter(sorted(self._definitions.keys(), key=str.lower), self)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self._ui.search_item.setCompleter(completer)
        except Exception as e:
            self.__logger_app.error(f"Completer error: {e}", exc_info=True)

    def on_text_changed(self, text: str) -> None:
        """
        Triggered when user types into the search field.

        Args:
            text (str): Input string from the search field.
        """
        self.__logger_app.debug(f"Text changed: '{text}'")
        try:
            self._ui.listWidget.clear()
            cleaned_text = text.strip()

            if not cleaned_text:
                self._ui.search_item_btn.setDisabled(True)
                return

            if cleaned_text in self._definitions:
                self.__logger_logic.info(f"Found '{cleaned_text}' in cache.")
                self.display_definitions(self._definitions[cleaned_text])
                self._ui.search_item_btn.setDisabled(True)
            else:
                self.__logger_logic.debug(f"'{cleaned_text}' not in cache.")
                self._ui.search_item_btn.setDisabled(False)
        except Exception as e:
            self.__logger_logic.error(f"Text change error: {e}", exc_info=True)

    def on_search_clicked(self) -> None:
        """
        Fetch definition for the current word when user clicks search.
        """
        word = self._ui.search_item.text().strip()
        if not word:
            self.__logger_app.warning("Empty search clicked.")
            return

        self.__logger_logic.info(f"Searching for '{word}'")
        self._current_word = word

        try:
            if word in self._definitions:
                self.__logger_logic.debug(f"'{word}' already cached.")
                self.display_definitions(self._definitions[word])
                return

            definitions = self._dictionary.fetch(word)
            if definitions:
                self._dictionary.add(word, definitions)
                self._definitions[word] = definitions
                self.__init_completer()
                self.display_definitions(definitions)
                self.__logger_logic.info(f"Fetched and cached '{word}'")
            else:
                self.__show_no_definitions_found(word)
        except Exception as e:
            self.__logger_logic.error(f"Search error for '{word}': {e}", exc_info=True)
            QMessageBox.critical(self, "Search Error", f"An error occurred: {e}")

    def __show_no_definitions_found(self, word: str) -> None:
        """
        Display warning when no definitions are found.

        Args:
            word (str): Word not found in dictionary.
        """
        self.__logger_logic.warning(f"No definitions found for '{word}'")
        item = QListWidgetItem("❗ No definitions found for this word.")
        item.setForeground(Qt.gray)
        self._ui.listWidget.addItem(item)

    def display_definitions(self, definitions: List[Dict[str, Any]]) -> None:
        """
        Render definitions on the list widget.

        Args:
            definitions (List[Dict[str, Any]]): List of definitions to show.
        """
        self.__logger_app.debug(f"Displaying {len(definitions)} definitions.")
        try:
            self._ui.listWidget.clear()
            for idx, definition in enumerate(definitions, 1):
                text = f"{idx}. {definition['definition']}\n"
                examples = definition.get("examples", [])
                if examples:
                    text += "   Examples:\n"
                    for example in examples:
                        text += f"   - {example}\n"

                item = QListWidgetItem(text)
                item.setToolTip(text)
                self._ui.listWidget.addItem(item)
        except Exception as e:
            self.__logger_app.error(f"Display error: {e}", exc_info=True)
