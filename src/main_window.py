from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QCompleter, QListWidgetItem, QMessageBox
from src.dictionary_manager import fetch_definitions, load_definitions, save_definitions
import config
from src.logger_setup import logger
from .ui_main_window import Ui_Form


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.dictionary_path = config.DICTIONARY_PATH

        self.ui.search_item_btn.setIcon(QIcon(str(config.SEARCH_ICON_PATH)))  # Convert Path to string

        self.definitions = load_definitions(self.dictionary_path)
        self.init_completer()

        self.ui.search_item.textChanged.connect(self.on_text_changed)
        self.ui.search_item_btn.clicked.connect(self.search_word)

    def init_completer(self):
        completer = QCompleter(self.definitions.keys(), self)
        self.ui.search_item.setCompleter(completer)

    def on_text_changed(self, text):
        self.ui.listWidget.clear()
        if text in self.definitions:
            self.display_definitions(self.definitions[text])
            self.ui.search_item_btn.setDisabled(True)
        else:
            self.ui.search_item_btn.setDisabled(False)

    def display_definitions(self, definitions):
        for idx, definition in enumerate(definitions, 1):
            item_text = f"{idx}. {definition['definition']}\n"
            if definition['examples']:
                item_text += "   Examples:\n"
                for example in definition['examples']:
                    item_text += f"   - {example}\n"
            self.ui.listWidget.addItem(QListWidgetItem(item_text))

    def search_word(self):
        word = self.ui.search_item.text()
        if word in self.definitions:
            self.display_definitions(self.definitions[word])
        else:
            try:
                word_definitions = fetch_definitions(word)
                if word_definitions:
                    self.definitions[word] = word_definitions
                    save_definitions(self.definitions, self.dictionary_path)
                    self.init_completer()
                    self.display_definitions(word_definitions)
                else:
                    self.ui.listWidget.addItem(QListWidgetItem("Word not found in the dictionary."))
            except Exception as e:
                logger.error(f"Error fetching definitions for '{word}': {e}")
                QMessageBox.critical(self, "Error", f"An error occurred while fetching definitions for '{word}': {e}")
