import sys

from loguru import logger


def setup_logging():
    logger.remove()
    logger.add(sys.stderr, level='DEBUG', colorize=True)
