"""Application bootstrap: Qt application, logging, and main window."""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication

from ramr.core.settings import ApplicationSettings
from ramr.infrastructure.logging.configuration import configure_logging
from ramr.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


class Application:
    """Wires application-level services and starts the Qt event loop."""

    def __init__(self, settings: ApplicationSettings | None = None) -> None:
        self.settings = settings or ApplicationSettings()

        self.qt_application = QApplication(sys.argv)
        self.qt_application.setApplicationName(self.settings.application_name)
        self.qt_application.setOrganizationName(self.settings.organization_name)
        self.qt_application.setApplicationVersion(self.settings.version)

        configure_logging(self._data_directory())
        logger.info("Starting %s %s", self.settings.application_name, self.settings.version)

        self.main_window = MainWindow(self.settings)

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
