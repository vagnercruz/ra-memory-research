"""Filesystem persistence for project directories."""

import json
import logging
from pathlib import Path

from ramr.domain.exceptions import (
    InvalidProjectFileError,
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
)
from ramr.models.project import Project

logger = logging.getLogger(__name__)

PROJECT_FILE_NAME = "project.json"
PROJECT_SUBDIRECTORIES = ("snapshots", "exports", "notes", "cache")


class ProjectRepository:
    """Reads and writes portable project directories.

    A project directory contains ``project.json`` plus the standard
    subdirectories (snapshots, exports, notes, cache). Everything the
    project needs lives inside its directory so it can be moved or shared.
    """

    def create(self, project: Project) -> None:
        """Create the directory scaffold and write the project file.

        Raises:
            ProjectAlreadyExistsError: if the directory already holds a project.
        """
        project_file = project.root_directory / PROJECT_FILE_NAME
        if project_file.exists():
            raise ProjectAlreadyExistsError(
                f"A project already exists at: {project.root_directory}"
            )

        project.root_directory.mkdir(parents=True, exist_ok=True)
        for subdirectory in PROJECT_SUBDIRECTORIES:
            (project.root_directory / subdirectory).mkdir(exist_ok=True)

        self.save(project)
        logger.info("Created project '%s' at %s", project.name, project.root_directory)

    def load(self, root_directory: Path) -> Project:
        """Load the project stored in ``root_directory``.

        Raises:
            ProjectNotFoundError: if the directory has no project file.
            InvalidProjectFileError: if the project file cannot be parsed.
        """
        project_file = root_directory / PROJECT_FILE_NAME
        if not project_file.exists():
            raise ProjectNotFoundError(f"No {PROJECT_FILE_NAME} found in: {root_directory}")

        try:
            data = json.loads(project_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise InvalidProjectFileError(f"Cannot read {project_file}: {error}") from error

        if not isinstance(data, dict):
            raise InvalidProjectFileError(f"{project_file} does not contain a JSON object")

        project = Project.from_dict(data, root_directory=root_directory)
        logger.info("Loaded project '%s' from %s", project.name, root_directory)
        return project

    def save(self, project: Project) -> None:
        """Write the project file inside the project directory."""
        project_file = project.root_directory / PROJECT_FILE_NAME
        content = json.dumps(project.to_dict(), indent=2)
        project_file.write_text(content, encoding="utf-8")
        logger.debug("Saved project file: %s", project_file)
