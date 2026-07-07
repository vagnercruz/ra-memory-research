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


class EmulatorError(RamrError):
    """Base class for emulator and memory access errors."""


class EmulatorNotFoundError(EmulatorError):
    """No running process matching the provider's known executables was found."""


class NotConnectedError(EmulatorError):
    """A memory operation was requested while no emulator is connected."""


class MemoryReadError(EmulatorError):
    """Reading emulator memory failed."""


class MemoryProviderError(EmulatorError):
    """A memory provider could not complete an operation (e.g. platform or setup)."""
