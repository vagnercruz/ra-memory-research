"""Tests for the logging configuration."""

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from ramr.infrastructure.logging.configuration import (
    LOG_DIRECTORY_NAME,
    LOG_FILE_NAME,
    configure_logging,
)


@pytest.fixture(autouse=True)
def restore_root_logger() -> Iterator[None]:
    """Snapshot the root logger so tests do not leak handlers."""
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level

    yield

    for handler in root_logger.handlers:
        if handler not in original_handlers:
            handler.close()
    root_logger.handlers[:] = original_handlers
    root_logger.setLevel(original_level)


def test_configure_logging_writes_to_log_file(tmp_path: Path) -> None:
    configure_logging(tmp_path)

    logging.getLogger("ramr.test").info("hello")

    log_file = tmp_path / LOG_DIRECTORY_NAME / LOG_FILE_NAME
    assert log_file.exists()
    assert "hello" in log_file.read_text(encoding="utf-8")


def test_configure_logging_replaces_handlers_instead_of_stacking(tmp_path: Path) -> None:
    configure_logging(tmp_path)
    handler_count = len(logging.getLogger().handlers)

    configure_logging(tmp_path)

    assert len(logging.getLogger().handlers) == handler_count


def test_configure_logging_honors_level(tmp_path: Path) -> None:
    configure_logging(tmp_path, level=logging.WARNING)

    logging.getLogger("ramr.test").info("filtered out")
    logging.getLogger("ramr.test").warning("kept")

    log_file = tmp_path / LOG_DIRECTORY_NAME / LOG_FILE_NAME
    content = log_file.read_text(encoding="utf-8")
    assert "filtered out" not in content
    assert "kept" in content
