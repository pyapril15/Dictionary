"""
Module for managing dictionary operations.
"""

import json
import nltk
from nltk.corpus import wordnet as wn
import functools
from .logger import logger
from .config import DICTIONARY_FILE


@functools.lru_cache(maxsize=None)
def fetch_definitions(word):
    """
    Fetches definitions for a given word using WordNet.

    Args:
        word (str): The word for which definitions are to be fetched.

    Returns:
        list: A list of dictionaries containing definitions and examples for the word.
    """
    synsets = wn.synsets(word)
    definitions = [
        {"definition": synset.definition(), "examples": synset.examples()}
        for synset in synsets
    ]
    return definitions if definitions else None


def ensure_wordnet_downloaded():
    """
    Ensures that the WordNet corpus is downloaded.
    """
    try:
        wn.ensure_loaded()
    except LookupError:
        logger.info("WordNet not found. Downloading WordNet...")
        nltk.download('wordnet')


def load_definitions():
    """
    Loads dictionary definitions from the JSON file.

    Returns:
        dict: A dictionary containing word definitions.
    """
    try:
        with open(DICTIONARY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading JSON from {DICTIONARY_FILE}: {e}")
        return {}


def save_definitions(definitions):
    """
    Saves dictionary definitions to the JSON file.

    Args:
        definitions (dict): A dictionary containing word definitions.
    """
    try:
        with open(DICTIONARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(definitions, f, indent=4)
    except IOError as e:
        logger.error(f"Error writing JSON to {DICTIONARY_FILE}: {e}")
