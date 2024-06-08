"""
Module for handling configuration settings.
"""

import os
from pathlib import Path
# target_dir = os.path.join(os.environ['ProgramFiles'], 'YourApplication')
# Define base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Define directories
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Define file paths
DICTIONARY_FILE = DATA_DIR / "dictionary.json"
LOG_FILE = LOGS_DIR / "dictionary.log"

# Define resource paths
APP_ICON_PATH = str(BASE_DIR / "resources" / "app_icon.ico")
SEARCH_ICON_PATH = str(BASE_DIR / "resources" / "search_icon.svg")
STYLE_SHEET = str(BASE_DIR / "resources" / "stylesheet.qss")

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Ensure dictionary.json exists
if not DICTIONARY_FILE.exists():
    DICTIONARY_FILE.write_text('{}')
