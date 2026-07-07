"""Root logging configuration for the application."""

import logging
import logging.handlers
from pathlib import Path

LOG_DIRECTORY_NAME = "logs"
LOG_FILE_NAME = "ramr.log"
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
LOG_FILE_MAX_BYTES = 1_048_576
LOG_FILE_BACKUP_COUNT = 5


def configure_logging(base_directory: Path, level: int = logging.INFO) -> None:
    """Configure the root logger with console and rotating file handlers.

    Log files are written to ``base_directory / logs``. Calling this again
    replaces the previously installed handlers instead of stacking new ones,
    so repeated configuration (e.g. in tests) stays safe.
    """
    log_directory = base_directory / LOG_DIRECTORY_NAME
    log_directory.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        log_directory / LOG_FILE_NAME,
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for handler in root_logger.handlers:
        handler.close()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
