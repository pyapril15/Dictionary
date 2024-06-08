"""
Module for setting up logging configuration.
"""

import logging
from .config import LOG_FILE

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,  # Set the log file path
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Set the log message format
)

logger = logging.getLogger('Dictionary')  # Get the logger object for the application
