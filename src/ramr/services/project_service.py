"""Use cases for creating, opening, and closing research projects."""

import logging
from collections.abc import Callable
from pathlib import Path

from ramr.domain.exceptions import InvalidProjectNameError
from ramr.infrastructure.database.project_database import ProjectDatabase
from ramr.infrastructure.filesystem.project_repository import (
    PROJECT_FILE_NAME,
    ProjectRepository,
)
from ramr.infrastructure.filesystem.recent_projects import RecentProjectsStore
from ramr.models.project import Project

logger = logging.getLogger(__name__)

# Characters Windows forbids in directory names.
INVALID_NAME_CHARACTERS = '<>:"/\\|?*'

DatabaseFactory = Callable[[Path], ProjectDatabase]


class ProjectService:
    """Owns the currently open project and its database connection.

    The UI talks to this service instead of touching repositories directly;
    the service keeps project switching, persistence, and the recent list
    consistent in one place.
    """

    def __init__(
        self,
        repository: ProjectRepository,
        recent_projects: RecentProjectsStore,
        database_factory: DatabaseFactory = ProjectDatabase.for_project_directory,
    ) -> None:
        self._repository = repository
        self._recent_projects = recent_projects
        self._database_factory = database_factory
        self._current_project: Project | None = None
        self._database: ProjectDatabase | None = None

    @property
    def current_project(self) -> Project | None:
        return self._current_project

    @property
    def database(self) -> ProjectDatabase | None:
        """Database of the open project, or None when no project is open."""
        return self._database

    @property
    def has_open_project(self) -> bool:
        return self._current_project is not None

    def create_project(
        self, name: str, system: str, parent_directory: Path, notes: str = ""
    ) -> Project:
        """Create a new project directory under ``parent_directory`` and open it.

        Raises:
            InvalidProjectNameError: if the name is empty or not a valid directory name.
            ProjectAlreadyExistsError: if the target directory already holds a project.
        """
        validated_name = self._validate_name(name)

        project = Project(
            name=validated_name,
            system=system.strip(),
            root_directory=parent_directory / validated_name,
            notes=notes,
        )
        self._repository.create(project)
        self._switch_to(project)
        return project

    def open_project(self, root_directory: Path) -> Project:
        """Open the project stored in ``root_directory``.

        Raises:
            ProjectNotFoundError: if the directory has no project file.
            InvalidProjectFileError: if the project file cannot be parsed.
        """
        project = self._repository.load(root_directory)
        self._switch_to(project)
        return project

    def save_current_project(self) -> None:
        """Persist the open project's metadata; no-op when nothing is open."""
        if self._current_project is None:
            return
        self._current_project.touch()
        self._repository.save(self._current_project)

    def close_project(self) -> None:
        """Save and close the open project; no-op when nothing is open."""
        if self._current_project is None:
            return

        self.save_current_project()
        if self._database is not None:
            self._database.close()
            self._database = None

        logger.info("Closed project '%s'", self._current_project.name)
        self._current_project = None

    def recent_projects(self) -> list[Path]:
        """Recently opened project directories that still exist on disk."""
        return [
            directory
            for directory in self._recent_projects.list()
            if (directory / PROJECT_FILE_NAME).is_file()
        ]

    def _switch_to(self, project: Project) -> None:
        self.close_project()

        database = self._database_factory(project.root_directory)
        database.open()

        self._current_project = project
        self._database = database
        self._recent_projects.add(project.root_directory)
        logger.info("Project '%s' is now open", project.name)

    def _validate_name(self, name: str) -> str:
        stripped = name.strip()
        if not stripped:
            raise InvalidProjectNameError("Project name must not be empty.")
        invalid = sorted({char for char in stripped if char in INVALID_NAME_CHARACTERS})
        if invalid:
            raise InvalidProjectNameError(
                f"Project name contains characters not allowed in directory names: {invalid}"
            )
        if stripped.endswith("."):
            raise InvalidProjectNameError("Project name must not end with a dot.")
        return stripped
