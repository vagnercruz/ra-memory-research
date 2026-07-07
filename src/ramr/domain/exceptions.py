"""Application exception hierarchy."""


class RamrError(Exception):
    """Base class for all application errors."""


class ProjectError(RamrError):
    """Base class for project-related errors."""


class InvalidProjectNameError(ProjectError):
    """The project name is empty or contains characters invalid in a directory name."""


class ProjectAlreadyExistsError(ProjectError):
    """A project already exists at the target directory."""


class ProjectNotFoundError(ProjectError):
    """The directory does not contain a project file."""


class InvalidProjectFileError(ProjectError):
    """The project file exists but cannot be parsed or misses required fields."""
