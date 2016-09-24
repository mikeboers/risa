import logging

# Setup logging.
logging.basicConfig()


from . import config
logging.getLogger().setLevel(config.LOG_LEVEL)

