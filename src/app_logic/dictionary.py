"""
dictionary.py - Word definition lookup service using WordNet with local JSON caching.

Responsibilities:
- Fetch definitions from WordNet.
- Manage a thread-safe, Singleton dictionary service.
- Load/save local JSON-based cache.
- Log all operations for diagnostics and audit.
"""

import functools
import json
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

import nltk
from nltk.corpus import wordnet as wn

from src.app_logic.app_config import AppConfig
from src.app_logic.log import Log
from src.utils.meta import SingletonMeta


class AbstractDictionaryService(ABC):
    """
    Abstract base class for dictionary operations.

    Subclasses must implement methods for:
    - Fetching definitions.
    - Loading/saving cache.
    - Managing cache entries.
    """

    @abstractmethod
    def fetch_definitions(self, word: str) -> Optional[List[Dict[str, Any]]]:
        pass

    @abstractmethod
    def load_cached_definitions(self) -> Dict[str, List[Dict[str, Any]]]:
        pass

    @abstractmethod
    def save_cached_definitions(self) -> None:
        pass

    @abstractmethod
    def add_to_cache(self, word: str, definitions: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def get_cached_words(self) -> List[str]:
        pass


class _DictionaryService(AbstractDictionaryService, metaclass=SingletonMeta):
    """
    Concrete implementation of AbstractDictionaryService using WordNet and local JSON caching.

    This Singleton manages consistent dictionary access and cache persistence.
    """

    def __init__(self, config: AppConfig, log: Log) -> None:
        self._config = config
        self._log_app = log.app
        self._log_dictionary = log.dictionary
        self._log_logic = log.logic
        self._definitions_cache: Dict[str, List[Dict[str, Any]]] = {}

        self._log_app.debug("Initializing DictionaryService...")
        self._initialize_wordnet()
        self.load_cached_definitions()

    def _initialize_wordnet(self) -> None:
        """
        Ensures the WordNet corpus is available. Downloads it if missing.
        """
        self._log_dictionary.debug("Checking WordNet availability...")
        try:
            wn.ensure_loaded()
            self._log_dictionary.info("WordNet is available.")
        except LookupError:
            self._log_dictionary.warning("WordNet not found. Attempting download...")
            try:
                nltk.download('wordnet')
                wn.ensure_loaded()
                self._log_dictionary.info("WordNet downloaded successfully.")
            except Exception as e:
                self._log_dictionary.error(f"Failed to load WordNet: {e}", exc_info=True)

    @functools.lru_cache(maxsize=None)
    def fetch_definitions(self, word: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch definitions and usage examples for a given word using WordNet.

        Args:
            word (str): Word to define.

        Returns:
            Optional[List[Dict[str, Any]]]: Definitions if found; otherwise None.
        """
        if not word:
            self._log_dictionary.warning("Empty word provided for lookup.")
            return None

        self._log_dictionary.debug(f"Fetching definitions for '{word}'")
        try:
            synsets = wn.synsets(word)
            if not synsets:
                self._log_dictionary.info(f"No definitions found for '{word}'")
                return None

            definitions = [
                {"definition": syn.definition(), "examples": syn.examples()}
                for syn in synsets
            ]
            self._log_dictionary.debug(f"Found {len(definitions)} definitions for '{word}'")
            return definitions
        except Exception as e:
            self._log_logic.error(f"Error fetching definitions for '{word}': {e}", exc_info=True)
            return None

    def load_cached_definitions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load cached definitions from disk.

        Returns:
            dict: Cached definitions dictionary.
        """
        cache_file = self._config.dictionary_file
        self._log_dictionary.debug(f"Loading cache from {cache_file}")
        try:
            with open(cache_file, 'r', encoding='utf-8') as file:
                self._definitions_cache = json.load(file)
                self._log_dictionary.info(f"Loaded cache with {len(self._definitions_cache)} entries.")
        except FileNotFoundError:
            self._log_dictionary.warning("Cache file not found. Starting fresh.")
        except json.JSONDecodeError as e:
            self._log_logic.error(f"Cache file corrupted: {e}", exc_info=True)
        except IOError as e:
            self._log_logic.error(f"Error reading cache file: {e}", exc_info=True)
        return self._definitions_cache

    def save_cached_definitions(self) -> None:
        """
        Save the current definitions cache to disk.
        """
        cache_file = self._config.dictionary_file
        self._log_dictionary.debug(f"Saving cache to {cache_file}")
        try:
            with open(cache_file, 'w', encoding='utf-8') as file:
                json.dump(self._definitions_cache, file, indent=4, ensure_ascii=False)
                self._log_dictionary.info("Cache saved successfully.")
        except IOError as e:
            self._log_logic.error(f"Failed to save cache: {e}", exc_info=True)

    def add_to_cache(self, word: str, definitions: List[Dict[str, Any]]) -> None:
        """
        Add a word and its definitions to the cache and persist to disk.

        Args:
            word (str): Word to cache.
            definitions (List[Dict[str, Any]]): Corresponding definitions.
        """
        if not word or not definitions:
            self._log_dictionary.warning("Attempted to add invalid word or empty definitions.")
            return

        self._log_dictionary.debug(f"Caching '{word}' with {len(definitions)} definitions.")
        try:
            self._definitions_cache[word] = definitions
            self.save_cached_definitions()
            self._log_dictionary.info(f"'{word}' successfully cached.")
        except Exception as e:
            self._log_logic.error(f"Failed to cache '{word}': {e}", exc_info=True)

    def get_cached_words(self) -> List[str]:
        """
        Retrieve a list of all cached words.

        Returns:
            List[str]: Cached word list.
        """
        word_count = len(self._definitions_cache)
        self._log_dictionary.debug(f"Retrieving {word_count} cached words.")
        return list(self._definitions_cache.keys())


class Dictionary(_DictionaryService):
    """
    Public interface to the dictionary system.

    Provides simplified method aliases for core dictionary operations.
    """

    def __init__(self, config: AppConfig, log: Log) -> None:
        super().__init__(config, log)

    def fetch(self, word: str) -> Optional[List[Dict[str, Any]]]:
        """Wrapper for fetch_definitions()."""
        return self.fetch_definitions(word)

    def load_cache(self) -> Dict[str, List[Dict[str, Any]]]:
        """Wrapper for load_cached_definitions()."""
        return self.load_cached_definitions()

    def save_cache(self) -> None:
        """Wrapper for save_cached_definitions()."""
        self.save_cached_definitions()

    def add(self, word: str, definitions: List[Dict[str, Any]]) -> None:
        """Wrapper for add_to_cache()."""
        self.add_to_cache(word, definitions)

    def words(self) -> List[str]:
        """Wrapper for get_cached_words()."""
        return self.get_cached_words()
