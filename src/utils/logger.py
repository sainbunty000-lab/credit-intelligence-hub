import logging
import sys


def setup_logger(name: str = "scraper") -> logging.Logger:
    """
    Configure and return a consistent logger across the project
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Prevent duplicate handlers

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Default logger instance
logger = setup_logger()
