"""Main application window."""

import logging
from pathlib import Path

from PySide6.QtCore import QStandardPaths, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from ramr.core import constants
from ramr.core.settings import ApplicationSettings
from ramr.domain.exceptions import ProjectError
from ramr.services.project_service import ProjectService
from ramr.ui.dialogs.new_project_dialog import NewProjectDialog
from ramr.ui.docks.inspector_dock import InspectorDock
from ramr.ui.docks.project_dock import ProjectDock
from ramr.ui.menu_bar import MenuBarBuilder
from ramr.ui.status_bar import StatusBar
from ramr.ui.workspace import Workspace

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Top-level window hosting the central workspace and dockable panels.

    Presentation only: project actions delegate to :class:`ProjectService`
    and the window updates its views from the result.
    """

    def __init__(self, settings: ApplicationSettings, project_service: ProjectService) -> None:
        super().__init__()

        self.settings = settings
        self.project_service = project_service

        self.setMinimumSize(constants.WINDOW_MINIMUM_WIDTH, constants.WINDOW_MINIMUM_HEIGHT)

        self.workspace = Workspace()
        self.setCentralWidget(self.workspace)

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        self.project_dock = ProjectDock()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_dock)

        self.inspector_dock = InspectorDock()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)

        self.menus = MenuBarBuilder.build(self)
        self._refresh_project_views()

    def create_new_project(self) -> None:
        """Ask for project data and create it through the service."""
        dialog = NewProjectDialog(self._default_projects_directory(), parent=self)
        if dialog.exec() != NewProjectDialog.DialogCode.Accepted:
            return

        try:
            project = self.project_service.create_project(
                name=dialog.project_name,
                system=dialog.system_name,
                parent_directory=dialog.parent_directory,
                notes=dialog.notes,
            )
        except ProjectError as error:
            self._show_project_error("Could not create the project.", error)
            return

        self._refresh_project_views()
        self.status_bar.showMessage(f"Project '{project.name}' created")

    def open_project_with_picker(self) -> None:
        """Ask for a project directory and open it."""
        directory = QFileDialog.getExistingDirectory(
            self, "Open Project", str(self._default_projects_directory())
        )
        if directory:
            self.open_project_from_path(Path(directory))

    def open_project_from_path(self, directory: Path) -> None:
        """Open the project stored at ``directory``."""
        try:
            project = self.project_service.open_project(directory)
        except ProjectError as error:
            self._show_project_error("Could not open the project.", error)
            return

        self._refresh_project_views()
        self.status_bar.showMessage(f"Project '{project.name}' opened")

    def close_current_project(self) -> None:
        """Save and close the open project."""
        self.project_service.close_project()
        self._refresh_project_views()
        self.status_bar.showMessage("Project closed")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 (Qt naming)
        """Persist the open project before the window closes."""
        self.project_service.close_project()
        super().closeEvent(event)

    def _refresh_project_views(self) -> None:
        project = self.project_service.current_project
        if project is None:
            self.setWindowTitle(self.settings.application_name)
            self.project_dock.clear_project()
        else:
            self.setWindowTitle(f"{project.name} — {self.settings.application_name}")
            self.project_dock.show_project(project)

    def _show_project_error(self, summary: str, error: ProjectError) -> None:
        logger.warning("%s %s", summary, error)
        QMessageBox.warning(self, self.settings.application_name, f"{summary}\n\n{error}")

    @staticmethod
    def _default_projects_directory() -> Path:
        location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        return Path(location)
