"""Tests for the project service."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from ramr.domain.exceptions import InvalidProjectNameError, ProjectAlreadyExistsError
from ramr.infrastructure.filesystem.project_repository import ProjectRepository
from ramr.infrastructure.filesystem.recent_projects import RecentProjectsStore
from ramr.services.project_service import ProjectService


@pytest.fixture
def service(tmp_path: Path) -> Iterator[ProjectService]:
    service = ProjectService(
        repository=ProjectRepository(),
        recent_projects=RecentProjectsStore(tmp_path / "recent_projects.json"),
    )
    yield service
    service.close_project()


def test_create_project_opens_it(service: ProjectService, tmp_path: Path) -> None:
    project = service.create_project("Castlevania", "PlayStation 2", tmp_path)

    assert service.current_project is project
    assert service.database is not None
    assert service.database.is_open
    assert project.root_directory == tmp_path / "Castlevania"


def test_create_project_strips_and_validates_name(service: ProjectService, tmp_path: Path) -> None:
    project = service.create_project("  Castlevania  ", " PlayStation 2 ", tmp_path)

    assert project.name == "Castlevania"
    assert project.system == "PlayStation 2"


@pytest.mark.parametrize("bad_name", ["", "   ", "a<b", "disc?", "half/half", "trailing."])
def test_create_project_rejects_invalid_names(
    service: ProjectService, tmp_path: Path, bad_name: str
) -> None:
    with pytest.raises(InvalidProjectNameError):
        service.create_project(bad_name, "PlayStation 2", tmp_path)


def test_create_project_refuses_duplicate_directory(
    service: ProjectService, tmp_path: Path
) -> None:
    service.create_project("Castlevania", "PlayStation 2", tmp_path)

    with pytest.raises(ProjectAlreadyExistsError):
        service.create_project("Castlevania", "PlayStation 2", tmp_path)


def test_open_project_switches_and_closes_previous_database(
    service: ProjectService, tmp_path: Path
) -> None:
    first = service.create_project("First", "SNES", tmp_path)
    first_database = service.database
    service.create_project("Second", "SNES", tmp_path)

    assert first_database is not None
    assert not first_database.is_open
    assert service.current_project is not None
    assert service.current_project.name == "Second"

    reopened = service.open_project(first.root_directory)

    assert reopened.name == "First"


def test_close_project_saves_pending_changes(service: ProjectService, tmp_path: Path) -> None:
    project = service.create_project("Castlevania", "PlayStation 2", tmp_path)
    project.notes = "HP candidate at 0x2001F0"

    service.close_project()

    assert service.current_project is None
    assert service.database is None
    reloaded = ProjectRepository().load(tmp_path / "Castlevania")
    assert reloaded.notes == "HP candidate at 0x2001F0"


def test_close_without_open_project_is_harmless(service: ProjectService) -> None:
    service.close_project()

    assert service.current_project is None


def test_recent_projects_lists_most_recent_first(service: ProjectService, tmp_path: Path) -> None:
    first = service.create_project("First", "SNES", tmp_path)
    second = service.create_project("Second", "SNES", tmp_path)

    assert service.recent_projects() == [
        second.root_directory.resolve(),
        first.root_directory.resolve(),
    ]


def test_recent_projects_omits_deleted_directories(service: ProjectService, tmp_path: Path) -> None:
    project = service.create_project("Ephemeral", "SNES", tmp_path)
    service.close_project()

    (project.root_directory / "project.json").unlink()

    assert service.recent_projects() == []
