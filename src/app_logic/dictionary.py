"""
Module for managing dictionary operations using OOP principles.
Handles fetching, caching, loading, and saving word definitions via WordNet.
"""

import json
import functools
import nltk
from nltk.corpus import wordnet as wn
from threading import Lock
from typing import Optional, List, Dict, Any

from src.app_logic import Log
from src.app_logic import AppConfig


class _SingletonMeta(type):
    """
    Thread-safe Singleton metaclass to ensure a single instance of DictionaryManager.
    """
    _instances: dict[type, object] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs) -> object:
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class _DictionaryManager(metaclass=_SingletonMeta):
    """
    Singleton class responsible for handling dictionary operations such as
    fetching definitions from WordNet, loading/saving them to file, and managing cache.
    """

    def __init__(self) -> None:
        self._config: AppConfig = AppConfig()
        self._definitions_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._ensure_wordnet()

    @staticmethod
    def _ensure_wordnet() -> None:
        try:
            wn.ensure_loaded()
            Log.info("WordNet corpus is available.")
        except LookupError:
            Log.warning("WordNet not found. Downloading...")
            nltk.download('wordnet')

    @functools.lru_cache(maxsize=None)
    def fetch_definitions(self, word: str) -> Optional[List[Dict[str, Any]]]:
        Log.debug(f"Fetching definitions for: {word}")
        synsets = wn.synsets(word)
        definitions = [
            {"definition": syn.definition(), "examples": syn.examples()}
            for syn in synsets
        ]
        return definitions if definitions else None

    def load_definitions(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            with open(self._config.dictionary_file, 'r', encoding='utf-8') as f:
                self._definitions_cache = json.load(f)
                Log.info("Definitions loaded successfully.")
        except (json.JSONDecodeError, IOError) as e:
            Log.error(f"Failed to read definitions: {e}")
            self._definitions_cache = {}

        return self._definitions_cache

    def save_definitions(self) -> None:
        try:
            with open(self._config.dictionary_file, 'w', encoding='utf-8') as f:
                json.dump(self._definitions_cache, f, indent=4)
                Log.info("Definitions saved successfully.")
        except IOError as e:
            Log.error(f"Failed to write definitions: {e}")

    def add_definition(self, word: str, definitions: List[Dict[str, Any]]) -> None:
        Log.debug(f"Adding definition for word: {word}")
        self._definitions_cache[word] = definitions
        self.save_definitions()

    def get_all_words(self) -> List[str]:
        return list(self._definitions_cache.keys())


# === Static proxy for clean access ===
class Dictionary:
    @staticmethod
    def get() -> _DictionaryManager:
        return _DictionaryManager()

    @staticmethod
    def fetch_definitions(word: str) -> Optional[List[Dict[str, Any]]]:
        return Dictionary.get().fetch_definitions(word)

    @staticmethod
    def load_definitions() -> Dict[str, List[Dict[str, Any]]]:
        return Dictionary.get().load_definitions()

    @staticmethod
    def save_definitions() -> None:
        Dictionary.get().save_definitions()

    @staticmethod
    def add_definition(word: str, definitions: List[Dict[str, Any]]) -> None:
        Dictionary.get().add_definition(word, definitions)

    @staticmethod
    def get_all_words() -> List[str]:
        return Dictionary.get().get_all_words()
