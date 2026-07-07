"""Tests for the project repository."""

from pathlib import Path

import pytest

from ramr.domain.exceptions import (
    InvalidProjectFileError,
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
)
from ramr.infrastructure.filesystem.project_repository import (
    PROJECT_FILE_NAME,
    PROJECT_SUBDIRECTORIES,
    ProjectRepository,
)
from ramr.models.project import Project


@pytest.fixture
def repository() -> ProjectRepository:
    return ProjectRepository()


def make_project(tmp_path: Path) -> Project:
    return Project(
        name="Castlevania",
        system="PlayStation 2",
        root_directory=tmp_path / "Castlevania",
    )


def test_create_builds_directory_scaffold(repository: ProjectRepository, tmp_path: Path) -> None:
    project = make_project(tmp_path)

    repository.create(project)

    assert (project.root_directory / PROJECT_FILE_NAME).is_file()
    for subdirectory in PROJECT_SUBDIRECTORIES:
        assert (project.root_directory / subdirectory).is_dir()


def test_create_then_load_round_trips(repository: ProjectRepository, tmp_path: Path) -> None:
    project = make_project(tmp_path)
    repository.create(project)

    loaded = repository.load(project.root_directory)

    assert loaded == project


def test_create_refuses_existing_project(repository: ProjectRepository, tmp_path: Path) -> None:
    project = make_project(tmp_path)
    repository.create(project)

    with pytest.raises(ProjectAlreadyExistsError):
        repository.create(project)


def test_load_missing_directory_raises(repository: ProjectRepository, tmp_path: Path) -> None:
    with pytest.raises(ProjectNotFoundError):
        repository.load(tmp_path / "nowhere")


def test_load_corrupt_file_raises(repository: ProjectRepository, tmp_path: Path) -> None:
    (tmp_path / PROJECT_FILE_NAME).write_text("{ not json", encoding="utf-8")

    with pytest.raises(InvalidProjectFileError):
        repository.load(tmp_path)


def test_load_non_object_json_raises(repository: ProjectRepository, tmp_path: Path) -> None:
    (tmp_path / PROJECT_FILE_NAME).write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(InvalidProjectFileError):
        repository.load(tmp_path)


def test_save_persists_field_changes(repository: ProjectRepository, tmp_path: Path) -> None:
    project = make_project(tmp_path)
    repository.create(project)

    project.notes = "Boss HP is around 0x2001F0"
    project.touch()
    repository.save(project)

    assert repository.load(project.root_directory).notes == project.notes
