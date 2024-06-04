import os
import json
import nltk
from nltk.corpus import wordnet as wn
from src.logger_setup import logger
import config
import functools


def create_directory(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory at {path}")


def create_dictionary_file(path):
    if not path.exists():
        try:
            with path.open('w', encoding='utf-8') as f:
                json.dump({}, f)
            logger.info(f"Created new file at {path}")
        except IOError as e:
            logger.error(f"Error creating new file at {path}: {e}")
            return {}


@functools.lru_cache(maxsize=None)
def fetch_definitions(word):
    synsets = wn.synsets(word)
    definitions = [
        {"definition": synset.definition(), "examples": synset.examples()}
        for synset in synsets
    ]
    return definitions if definitions else None


def ensure_wordnet_downloaded():
    try:
        wn.ensure_loaded()
    except LookupError:
        logger.info("WordNet not found. Downloading WordNet...")
        nltk.download('wordnet')


def load_definitions(file_path):
    try:
        with file_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading JSON from {file_path}: {e}")
        return {}


def save_definitions(definitions, file_path):
    try:
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(definitions, f, indent=4)
    except IOError as e:
        logger.error(f"Error writing JSON to {file_path}: {e}")


def create_dictionary(file_path, words):
    ensure_wordnet_downloaded()
    definitions = load_definitions(file_path)
    for word in words:
        if word not in definitions:
            word_definitions = fetch_definitions(word)
            if word_definitions:
                definitions[word] = word_definitions
                logger.info(f"Fetched definitions for '{word}': {word_definitions}")
            else:
                logger.warning(f"No definitions found for '{word}'")
    save_definitions(definitions, file_path)
    logger.info(f"Definitions saved to {file_path}")
