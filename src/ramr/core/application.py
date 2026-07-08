"""Application bootstrap: Qt application, logging, services, and main window."""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication

from ramr.core.settings import ApplicationSettings
from ramr.infrastructure.filesystem.project_repository import ProjectRepository
from ramr.infrastructure.filesystem.recent_projects import RecentProjectsStore
from ramr.infrastructure.logging.configuration import configure_logging
from ramr.infrastructure.memory.registry import build_default_registry
from ramr.services.emulator_service import EmulatorService
from ramr.services.project_service import ProjectService
from ramr.ui.main_window import MainWindow

logger = logging.getLogger(__name__)

RECENT_PROJECTS_FILE_NAME = "recent_projects.json"


class Application:
    """Wires application-level services and starts the Qt event loop."""

    def __init__(self, settings: ApplicationSettings | None = None) -> None:
        self.settings = settings or ApplicationSettings()

        self.qt_application = QApplication(sys.argv)
        self.qt_application.setApplicationName(self.settings.application_name)
        self.qt_application.setOrganizationName(self.settings.organization_name)
        self.qt_application.setApplicationVersion(self.settings.version)

        data_directory = self._data_directory()
        configure_logging(data_directory)
        logger.info("Starting %s %s", self.settings.application_name, self.settings.version)

        self.project_service = ProjectService(
            repository=ProjectRepository(),
            recent_projects=RecentProjectsStore(data_directory / RECENT_PROJECTS_FILE_NAME),
        )
        self.emulator_service = EmulatorService(build_default_registry())

        self.main_window = MainWindow(self.settings, self.project_service, self.emulator_service)

    def run(self) -> int:
        """Show the main window, run the event loop, and return its exit code."""
        self.main_window.show()
        exit_code = self.qt_application.exec()
        logger.info("Application exited with code %d", exit_code)
        return exit_code

    @staticmethod
    def _data_directory() -> Path:
        """Per-user writable directory for logs and application data."""
        location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        return Path(location)


def main() -> None:
    """Entry point used by the ``ramr`` script and ``main.py``."""
    application = Application()
    sys.exit(application.run())
