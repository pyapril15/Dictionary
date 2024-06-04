from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Paths
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
DICTIONARY_PATH = DATA_DIR / 'dictionary.json'
LOG_FILE_PATH = LOGS_DIR / 'dictionary.log'

# Resources
STYLESHEET_PATH = BASE_DIR / 'resources' / 'stylesheet.qss'
APP_ICON_PATH = BASE_DIR / 'resources' / 'app_icon.ico'
SEARCH_ICON_PATH = BASE_DIR / 'resources' / 'search_icon.svg'

print(1, BASE_DIR, type(BASE_DIR))
print(2, DATA_DIR, type(DATA_DIR))
print(3, LOGS_DIR, type(LOGS_DIR))
print(4, DICTIONARY_PATH, type(DICTIONARY_PATH))
print(5, LOG_FILE_PATH, type(LOG_FILE_PATH))
print(6, STYLESHEET_PATH, type(STYLESHEET_PATH))
print(7, APP_ICON_PATH, type(APP_ICON_PATH))
print(8, SEARCH_ICON_PATH, type(SEARCH_ICON_PATH))
