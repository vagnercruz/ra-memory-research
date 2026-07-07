"""Tests for the Project model."""

from datetime import UTC
from pathlib import Path

import pytest

from ramr.domain.exceptions import InvalidProjectFileError
from ramr.models.project import PROJECT_SCHEMA_VERSION, Project


def make_project(tmp_path: Path) -> Project:
    return Project(
        name="Castlevania",
        system="PlayStation 2",
        root_directory=tmp_path / "Castlevania",
        notes="Boss HP research",
    )


def test_new_project_gets_current_schema_and_utc_timestamps(tmp_path: Path) -> None:
    project = make_project(tmp_path)

    assert project.schema_version == PROJECT_SCHEMA_VERSION
    assert project.created_at.tzinfo is UTC
    assert project.modified_at.tzinfo is UTC


def test_serialization_round_trip_preserves_fields(tmp_path: Path) -> None:
    project = make_project(tmp_path)

    restored = Project.from_dict(project.to_dict(), root_directory=project.root_directory)

    assert restored == project


def test_serialization_excludes_root_directory(tmp_path: Path) -> None:
    data = make_project(tmp_path).to_dict()

    assert "root_directory" not in data


def test_touch_advances_modified_timestamp(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    before = project.modified_at

    project.touch()

    assert project.modified_at >= before
    assert project.created_at <= project.modified_at


def test_from_dict_rejects_missing_fields(tmp_path: Path) -> None:
    with pytest.raises(InvalidProjectFileError, match="required fields"):
        Project.from_dict({"name": "Incomplete"}, root_directory=tmp_path)


def test_from_dict_rejects_malformed_timestamp(tmp_path: Path) -> None:
    data = make_project(tmp_path).to_dict()
    data["created_at"] = "not-a-date"

    with pytest.raises(InvalidProjectFileError, match="malformed"):
        Project.from_dict(data, root_directory=tmp_path)
