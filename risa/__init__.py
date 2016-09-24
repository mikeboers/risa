import logging

from . import config

# Setup logging.
logging.basicConfig(level=config.LOG_LEVEL)
