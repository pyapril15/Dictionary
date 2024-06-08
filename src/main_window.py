"""
Module for managing the main application window.
"""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QCompleter, QListWidgetItem, QMessageBox
from .dictionary import fetch_definitions, load_definitions, save_definitions
from .config import SEARCH_ICON_PATH
from .logger import logger
from .ui_main_window import Ui_Form


class MainWindow(QWidget):
    """
    Class representing the main application window.
    """

    def __init__(self):
        """
        Initialize the main window.
        """
        super().__init__()

        # Set up the user interface
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Set icon for search button
        self.ui.search_item_btn.setIcon(QIcon(SEARCH_ICON_PATH))

        # Load dictionary definitions
        self.definitions = load_definitions()
        self.init_completer()

        # Connect signals to slots
        self.ui.search_item.textChanged.connect(self.on_text_changed)
        self.ui.search_item_btn.clicked.connect(self.search_word)

    def init_completer(self):
        """
        Initialize completer with dictionary keys.
        """
        completer = QCompleter(self.definitions.keys(), self)
        self.ui.search_item.setCompleter(completer)

    def on_text_changed(self, text):
        """
        Slot for handling text changed event.
        """
        self.ui.listWidget.clear()
        if text in self.definitions:
            self.display_definitions(self.definitions[text])
            self.ui.search_item_btn.setDisabled(True)
        else:
            self.ui.search_item_btn.setDisabled(False)

    def display_definitions(self, definitions):
        """
        Display definitions in the list widget.
        """
        for idx, definition in enumerate(definitions, 1):
            item_text = f"{idx}. {definition['definition']}\n"
            if definition['examples']:
                item_text += "   Examples:\n"
                for example in definition['examples']:
                    item_text += f"   - {example}\n"
            self.ui.listWidget.addItem(QListWidgetItem(item_text))

    def search_word(self):
        """
        Search for the word entered by the user.
        """
        word = self.ui.search_item.text()
        if word in self.definitions:
            self.display_definitions(self.definitions[word])
        else:
            try:
                word_definitions = fetch_definitions(word)
                if word_definitions:
                    self.definitions[word] = word_definitions
                    save_definitions(self.definitions)
                    self.init_completer()
                    self.display_definitions(word_definitions)
                else:
                    self.ui.listWidget.addItem(QListWidgetItem("Word not found in the dictionary."))
            except Exception as e:
                logger.error(f"Error fetching definitions for '{word}': {e}")
                QMessageBox.critical(self, "Error", f"An error occurred while fetching definitions for '{word}': {e}")
