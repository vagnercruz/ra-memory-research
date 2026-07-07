"""Tests for the project database."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from ramr.infrastructure.database.project_database import (
    DATABASE_FILE_NAME,
    ProjectDatabase,
)


@pytest.fixture
def database(tmp_path: Path) -> Iterator[ProjectDatabase]:
    database = ProjectDatabase.for_project_directory(tmp_path)
    yield database
    database.close()


def test_open_creates_database_file(database: ProjectDatabase, tmp_path: Path) -> None:
    database.open()

    assert (tmp_path / DATABASE_FILE_NAME).is_file()


def test_open_migrates_to_latest_schema(database: ProjectDatabase) -> None:
    database.open()

    assert database.schema_version() == 1


def test_reopening_does_not_rerun_migrations(database: ProjectDatabase, tmp_path: Path) -> None:
    database.open()
    database.set_metadata("game_hash", "abc123")
    database.close()

    reopened = ProjectDatabase.for_project_directory(tmp_path)
    reopened.open()
    try:
        assert reopened.schema_version() == 1
        assert reopened.get_metadata("game_hash") == "abc123"
    finally:
        reopened.close()


def test_metadata_upsert_overwrites_value(database: ProjectDatabase) -> None:
    database.open()

    database.set_metadata("emulator", "PCSX2")
    database.set_metadata("emulator", "BizHawk")

    assert database.get_metadata("emulator") == "BizHawk"


def test_metadata_missing_key_returns_none(database: ProjectDatabase) -> None:
    database.open()

    assert database.get_metadata("absent") is None


def test_connection_requires_open(database: ProjectDatabase) -> None:
    with pytest.raises(RuntimeError, match="not open"):
        _ = database.connection


def test_open_twice_is_harmless(database: ProjectDatabase) -> None:
    database.open()
    first_connection = database.connection

    database.open()

    assert database.connection is first_connection


def test_close_twice_is_harmless(database: ProjectDatabase) -> None:
    database.open()

    database.close()
    database.close()

    assert not database.is_open
