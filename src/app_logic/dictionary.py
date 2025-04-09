"""
Module for managing dictionary operations using OOP principles.
"""

import json
import functools
import nltk
from nltk.corpus import wordnet as wn
from threading import Lock
from src.app_logic.logger import logger
from src.app_logic.config import AppConfig


class _SingletonMeta(type):
    """
    Thread-safe Singleton metaclass to ensure a single instance of DictionaryManager.
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DictionaryManager(metaclass=_SingletonMeta):
    """
    Singleton class responsible for handling dictionary operations.
    """

    def __init__(self):
        self._config = AppConfig()
        self._definitions_cache = {}
        self._ensure_wordnet()

    @staticmethod
    def _ensure_wordnet():
        """
        Ensures WordNet data is available.
        """
        try:
            wn.ensure_loaded()
            logger.info("WordNet corpus is available.")
        except LookupError:
            logger.warning("WordNet not found. Downloading...")
            nltk.download('wordnet')

    @functools.lru_cache(maxsize=None)
    def fetch_definitions(self, word):
        """
        Public method to fetch definitions for a word using WordNet.

        Args:
            word (str): The word to fetch definitions for.

        Returns:
            list: List of dictionaries with definition and examples.
        """
        logger.debug(f"Fetching definitions for: {word}")
        synsets = wn.synsets(word)
        definitions = [
            {"definition": synset.definition(), "examples": synset.examples()}
            for synset in synsets
        ]
        return definitions if definitions else None

    def load_definitions(self):
        """
        Load cached definitions from JSON file.

        Returns:
            dict: Loaded definitions' dictionary.
        """
        try:
            with open(self._config.dictionary_file, 'r', encoding='utf-8') as f:
                self._definitions_cache = json.load(f)
                logger.info("Definitions loaded successfully.")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read definitions: {e}")
            self._definitions_cache = {}

        return self._definitions_cache

    def save_definitions(self):
        """
        Save current definitions to the JSON file.
        """
        try:
            with open(self._config.dictionary_file, 'w', encoding='utf-8') as f:
                json.dump(self._definitions_cache, f, indent=4)
                logger.info("Definitions saved successfully.")
        except IOError as e:
            logger.error(f"Failed to write definitions: {e}")

    def add_definition(self, word, definitions):
        """
        Add a new word and its definitions to the cache and save.

        Args:
            word (str): Word to add.
            definitions (list): Definitions to add.
        """
        logger.debug(f"Adding definition for word: {word}")
        self._definitions_cache[word] = definitions
        self.save_definitions()

    def get_all_words(self):
        """
        Get all known words in the dictionary.

        Returns:
            list: List of all words in the dictionary.
        """
        return list(self._definitions_cache.keys())


# Public instance for reuse
dictionary_manager = DictionaryManager()
