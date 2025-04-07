import logging
import sys


def setup_logging(level_str: str = 'INFO') -> None:
    level = logging.getLevelName(level_str)

    logging.basicConfig(
        level=level,
        stream=sys.stdout,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    # Set the logging level of "aiogram.event" to "WARNING"
    # because there is too much spam coming in with the INFO level
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
